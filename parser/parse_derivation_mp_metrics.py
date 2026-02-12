import os
import re
import sys
import pandas as pd
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def parse_worker_log(path):
    metrics = {
        "Events_processed": None, "t_CPU(ms/event)": None,
        "Throughput(events/s)": None, "CPU_Eff(%)": None,
        "VMem_max(GB)": None, "RSS_max(GB)": None,
        "PSS_max(GB)": None, "commitOutput(ms)": 0, "cObjR(ms)": 0,
    }
    try:
        if not os.path.exists(path): return None
        with open(path) as f:
            for line in f:
                if "PerfMonMTSvc" in line:
                    if "Number of events processed" in line:
                        m = re.findall(r"\d+", line)
                        if m: metrics["Events_processed"] = int(m[-1])
                    elif "CPU usage per event" in line:
                        m = re.findall(r"\d+", line)
                        if m: metrics["t_CPU(ms/event)"] = int(m[-1])
                    elif "Events per second" in line:
                        nums = re.findall(r'[\d.]+', line)
                        if nums: metrics["Throughput(events/s)"] = float(nums[-1])
                    elif "CPU utilization efficiency" in line:
                        m = re.findall(r"\d+", line)
                        if m: metrics["CPU_Eff(%)"] = int(m[-1])
                    elif "Max Vmem" in line:
                        m = re.search(r"([\d.]+)\s*(GB|MB)", line)
                        if m:
                            val, unit = float(m.group(1)), m.group(2)
                            metrics["VMem_max(GB)"] = val if unit == "GB" else val / 1024.
                    elif "Max Rss" in line:
                        m = re.search(r"([\d.]+)\s*(GB|MB)", line)
                        if m:
                            val, unit = float(m.group(1)), m.group(2)
                            metrics["RSS_max(GB)"] = val if unit == "GB" else val / 1024.
                elif "commitOutput" in line and "INFO" in line:
                    m = re.findall(r"(\d+) ms", line)
                    if m: metrics["commitOutput(ms)"] += int(m[0])
                elif "cObjR" in line and "INFO" in line:
                    m = re.findall(r"(\d+) ms", line)
                    if m: metrics["cObjR(ms)"] += int(m[0])
    except Exception as e:
        print(f"ERROR reading {path}: {e}")
        return None
    return metrics

def compute_wall_time(df):
    df = df.copy()
    df["Events_processed"] = pd.to_numeric(df["Events_processed"], errors="coerce")
    df["Throughput(events/s)"] = pd.to_numeric(df["Throughput(events/s)"], errors="coerce")
    tp = df["Throughput(events/s)"].replace({0: np.nan})
    df["Wall_time(s)"] = (df["Events_processed"] / tp).round(3)
    return df

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python parse_derivation_mp_metrics.py <run_id> <proc> <cores> <project_dir>")
        sys.exit(1)

    run_id, proc, cores, project_dir = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    run_prefix = os.path.join(project_dir, f"run_{run_id:02g}")
    base_dir = os.path.join(run_prefix, "athenaMP-workers-Derivation-DerivationFramework")

    if not os.path.isdir(base_dir):
        print(f"ERROR: Worker directory not found: {base_dir}")
        sys.exit(1)

    workers = sorted(d for d in os.listdir(base_dir) if d.startswith("worker_") and os.path.isdir(os.path.join(base_dir, d)))
    
    daod_path = os.path.join(run_prefix, "DAOD_PHYS.DAOD.pool.root")
    daod_size_gb = round(os.path.getsize(daod_path) / (1024**3), 4) if os.path.exists(daod_path) else np.nan

    all_rows = []
    for w in workers:
        logfile = os.path.join(base_dir, w, "AthenaMP.log")
        metrics = parse_worker_log(logfile)
        if not metrics: continue
        
        df = pd.DataFrame([metrics])
        df = compute_wall_time(df)
        t_cpu, nev = df.loc[0, "t_CPU(ms/event)"], df.loc[0, "Events_processed"]
        df["Loop_time(ms)"] = t_cpu * nev if pd.notna(t_cpu) and pd.notna(nev) else np.nan
        df["Run_ID"], df["Processors"], df["Cores"], df["Worker"], df["DAOD_size_GB"] = run_id, proc, cores, w, daod_size_gb
        all_rows.append(df)

    if all_rows:
        df_new = pd.concat([df for df in all_rows if not df.empty], ignore_index=True)
        global_csv = os.path.join(project_dir, "all_workers.csv")

        if os.path.exists(global_csv):
            # Load existing data
            df_existing = pd.read_csv(global_csv)
            
            # Create a mask to find old entries for this exact run configuration
            
            mask = (
                (df_existing["Run_ID"] == run_id) & 
                (df_existing["Processors"] == proc) & 
                (df_existing["Cores"] == cores)
            )
            df_cleaned = df_existing[~mask]
            
            # Combine the cleaned old data with the fresh new data
            df_final = pd.concat([df_cleaned, df_new], ignore_index=True)
        else:
            df_final = df_new

        # Save the result, overwriting the file with the updated consolidated version
        df_final.to_csv(global_csv, index=False)
        print(f"Consolidated {len(workers)} workers into all_workers.csv (Overwrote old entries for Run {run_id})")