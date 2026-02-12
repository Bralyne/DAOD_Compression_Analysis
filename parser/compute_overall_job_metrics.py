import os, json, sys
import pandas as pd
import numpy as np

def get_run_dir(project_dir, run_id):
    return os.path.join(project_dir, f"run_{run_id:02g}")

def extract_metadata_from_filename(filename):
    try:
        base = filename.split('.AOD')[0]
        parts = base.split('_')
        algo = parts[0].upper()
        aod_type = "TTree" if "ttree" in parts[1].lower() else "RNtuple"
        level = int(''.join(filter(str.isdigit, parts[2])))
        return algo, aod_type, level, base
    except:
        return "UNKNOWN", "UNKNOWN", 0, "overall_job_metrics"

def load_worker_metrics(project_dir, run_id, proc, cores):
    path = os.path.join(project_dir, "all_workers.csv")
    if not os.path.exists(path):
        print(f"ERROR: {path} not found."); sys.exit(1)
    df = pd.read_csv(path)
    filtered = df[(df["Run_ID"] == run_id) & (df["Processors"] == proc) & (df["Cores"] == cores)]
    if filtered.empty:
        print(f"ERROR: No metrics for Run {run_id} in all_workers.csv"); sys.exit(1)
    return filtered

def load_prmon(project_dir, run_id):
    path = os.path.join(get_run_dir(project_dir, run_id), "prmon.summary.Derivation.json")
    if not os.path.exists(path): return {"VMem_max_GB": np.nan, "RSS_max_GB": np.nan, "PSS_max_GB": np.nan}
    with open(path) as f:
        data = json.load(f)
        mem = data.get("Max", {})
    return {
        "VMem_max_GB": round(mem.get("vmem", 0) / 1024**2, 2),
        "RSS_max_GB":  round(mem.get("rss",  0) / 1024**2, 2),
        "PSS_max_GB":  round(mem.get("pss",  0) / 1024**2, 2),
    }

def detect_daod_size(project_dir, run_id):
    rundir = get_run_dir(project_dir, run_id)
    candidates = [f for f in os.listdir(rundir) if f.startswith("DAOD_") and f.endswith(".pool.root")]
    if not candidates: return np.nan
    return round(os.path.getsize(os.path.join(rundir, candidates[0])) / (1024**3), 4)

if __name__ == "__main__":
    if len(sys.argv) < 5: sys.exit(1)
    run_id, proc, cores, project_dir = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]

    data_folder = os.path.join(project_dir, "data")
    aod_files = [f for f in os.listdir(data_folder) if f.endswith(".pool.root")]
    algo, aod_type, level, file_prefix = extract_metadata_from_filename(aod_files[0]) if aod_files else ("UNKNOWN", "UNKNOWN", 0, "metrics")

    dfw = load_worker_metrics(project_dir, run_id, proc, cores)
    total_events = dfw["Events_processed"].sum()
    slowest_loop = dfw["Loop_time(ms)"].max()
    slowest_read = dfw["cObjR(ms)"].max()

    mem = load_prmon(project_dir, run_id)
    job = {
        "Run_ID": run_id, "Processors": proc, "Cores": cores,
        "Algo": algo, "AODtype": aod_type, "Level": level,
        "Total_events": total_events,
        "Job_Throughput(events/ms)": round(total_events / slowest_loop, 4) if slowest_loop > 0 else np.nan,
        "Job_Read_Throughput(events/ms)": round(total_events / slowest_read, 4) if slowest_read > 0 else np.nan,
        "VMem_max_GB": mem["VMem_max_GB"], "RSS_max_GB": mem["RSS_max_GB"],
        "PSS_max_GB": mem["PSS_max_GB"], "DAOD_size_GB": detect_daod_size(project_dir, run_id),
    }

    out = pd.DataFrame([job])
    csvname = os.path.join(project_dir, f"{file_prefix}.csv")
    out.to_csv(csvname, index=False, mode="a", header=not os.path.exists(csvname))
    print(f"Run {run_id} metadata: {algo}_{aod_type}_L{level} -> Saved to {csvname}")