import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import re


def plotting_metrics(workspace_path):
    plotting_dir = os.path.join(workspace_path, "plotting")
    os.makedirs(plotting_dir, exist_ok=True)
    
    master_csv = os.path.join(workspace_path, "All_Compression_Algo_metrics.csv")
    pdf_path = os.path.join(plotting_dir, "Global_Compression_Report.pdf")

    if not os.path.exists(master_csv):
        print(f" Error: Master CSV not found at {master_csv}")
        return

    df_raw = pd.read_csv(master_csv)

    #  Data Cleaning
    df_raw["Algo"] = df_raw["Algo"].astype(str).str.strip().str.upper()
    df_raw["AODtype"] = df_raw["AODtype"].astype(str).str.strip().str.upper()
    for col in ["Level", "Cores"]:
        if col in df_raw.columns:
            df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce').fillna(0).astype(int)

    algos = sorted(df_raw["Algo"].unique())
    levels = sorted(df_raw["Level"].unique())
    formats = sorted(df_raw["AODtype"].unique())
    cores = sorted(df_raw["Cores"].unique())

    metrics_to_plot = {
        "Job_Throughput(events/ms)": "Job Throughput (events/ms)",
        "Job_Read_Throughput(events/ms)": "Read Throughput (events/ms)",
        "RSS_max_GB": "Resident Memory GB",
        "VMem_max_GB": "Virtual Memory GB",
        "PSS_max_GB": "PSS Memory GB",
        "DAOD_size_GB": "File Size (GB)"
    }
    
    color_map = {"LZMA": "#d62728", "ZSTD": "#2ca02c", "LZ4": "#1f77b4", "ZLIB": "#9467bd"}
    marker_symbols = {1: "o", 5: "s", 9: "^"} 

    with PdfPages(pdf_path) as pdf:
        for csv_col, display_name in metrics_to_plot.items():
            if csv_col not in df_raw.columns: continue

            fig, (ax_line, ax_bar) = plt.subplots(1, 2, figsize=(26, 12))
            plt.subplots_adjust(wspace=0.15, bottom=0.20, top=0.88) 
            
            
            baseline_map = {c: df_raw[(df_raw["Cores"] == c) & (df_raw["Algo"] == "LZMA") & 
                                     (df_raw["Level"] == 1) & (df_raw["AODtype"] == "TTREE")][csv_col].mean() 
                            for c in cores}

            combinations = [(a, l, f) for a in algos for l in levels for f in formats]
            n_combos = len(combinations)
            bar_width = 0.8 / n_combos
            x_ticks = np.arange(len(cores))
            max_val_found = df_raw[csv_col].replace([np.inf, -np.inf], np.nan).max()
            if np.isnan(max_val_found) or max_val_found == 0: max_val_found = 1

            for idx, (algo, lvl, fmt) in enumerate(combinations):
                subset = df_raw[(df_raw["Algo"] == algo) & (df_raw["Level"] == lvl) & (df_raw["AODtype"] == fmt)]
                if subset.empty: continue
                
                df_p = subset.groupby("Cores")[csv_col].mean().reset_index()
                color = color_map.get(algo, "#7f7f7f")
                marker = marker_symbols.get(lvl, "D")

                
                l_style = "-" if "RNTUPLE" in fmt else "--"
                ax_line.plot(df_p["Cores"], df_p[csv_col], marker=marker, linestyle=l_style, 
                              color=color, linewidth=2, markersize=10, markeredgecolor='white')

                # Bar Plot
                means = subset.groupby("Cores")[csv_col].mean().reindex(cores).fillna(0).values
                offset = (idx - (n_combos - 1) / 2) * bar_width
                ax_bar.bar(x_ticks + offset, means, bar_width, color=color, 
                           edgecolor='black', alpha=0.8, hatch='////' if "TTREE" in fmt else '', zorder=3)
                
                for c_idx, h in enumerate(means):
                    if h > 0:
                        ax_bar.plot(x_ticks[c_idx] + offset, h * 0.98, marker=marker, color='black', markersize=5, zorder=5)
                        
                        ref_val = baseline_map.get(cores[c_idx])
                        if ref_val and not np.isnan(ref_val) and ref_val > 0:
                           
                            if algo == "LZMA" and lvl == 1 and fmt == "TTREE":
                                ax_bar.text(x_ticks[c_idx] + offset, h + (max_val_found * 0.02), 
                                            "Ref.", color='red', ha='center', va='bottom', 
                                            fontsize=10, fontweight='bold', rotation=45)
                            else:
                                gain = ((h - ref_val) / ref_val) * 100
                                ax_bar.text(x_ticks[c_idx] + offset, h + (max_val_found * 0.01), 
                                            f"{gain:+.1f}%", ha='center', va='bottom', 
                                            fontsize=8, rotation=45) # Inclined rotation

            
            ax_line.set_xticks(cores)
            ax_line.set_xticklabels(cores, fontsize=12, fontweight="bold")
            ax_line.set_ylabel(display_name, fontsize=14, fontweight="bold")
            ax_line.yaxis.grid(True, linestyle=":", color="black", alpha=0.4)
            ax_line.text(1.0, -0.06, "Cores", transform=ax_line.transAxes, ha='right', fontsize=14, fontweight='bold')
            ax_line.set_title("Scaling Trends", fontsize=16, fontweight='bold', pad=40)

            
            ax_bar.set_ylabel(display_name, fontsize=14, fontweight="bold")
            ax_bar.yaxis.grid(True, linestyle=":", color="black", alpha=0.4)
            ax_bar.set_ylim(0, max_val_found * 1.4)
            ax_bar.set_xticks(x_ticks)
            ax_bar.set_xticklabels([]) 
            ax_bar.set_title("Performance Comparison", fontsize=16, fontweight='bold', pad=40)

            
            bracket_y = -0.12     
            tick_y_top = -0.08    
            for i, core_val in enumerate(cores):
                ax_bar.plot([i - 0.42, i + 0.42], [bracket_y, bracket_y], transform=ax_bar.get_xaxis_transform(), color='black', lw=2, clip_on=False)
                ax_bar.plot([i - 0.42, i - 0.42], [bracket_y, tick_y_top], transform=ax_bar.get_xaxis_transform(), color='black', lw=2, clip_on=False)
                ax_bar.plot([i + 0.42, i + 0.42], [bracket_y, tick_y_top], transform=ax_bar.get_xaxis_transform(), color='black', lw=2, clip_on=False)
                ax_bar.text(i, bracket_y - 0.02, f"Core {core_val}", transform=ax_bar.get_xaxis_transform(), ha='center', va='top', fontsize=12, fontweight='bold')

            for c_idx, core_val in enumerate(cores):
                ref_val = baseline_map.get(core_val)
                if ref_val and not np.isnan(ref_val) and ref_val > 0:
                    ax_bar.hlines(ref_val, c_idx-0.45, c_idx+0.45, colors='red', linestyles='--', linewidth=2, zorder=4)

           
            algo_legend = [Patch(facecolor=color_map[a], label=a, edgecolor="black") for a in algos if a in color_map]
            fmt_legend = [Patch(facecolor="white", edgecolor="black", hatch='////', label='TTREE'), Patch(facecolor="white", edgecolor="black", label='RNTUPLE')]
            lvl_legend = [Line2D([0], [0], marker=marker_symbols[l], color='w', markerfacecolor='k', markersize=8, label=f"Lvl {l}") for l in levels if l in marker_symbols]
            
            ax_line.legend(handles=[Line2D([0],[0],color='k',ls='-',label='RNtuple'), Line2D([0],[0],color='k',ls='--',label='TTree')] + algo_legend, loc='upper center', ncol=6, frameon=True, edgecolor="black", bbox_to_anchor=(0.5, 0.99))
            ax_bar.legend(handles=algo_legend + fmt_legend + lvl_legend, loc='upper center', ncol=5, frameon=True, edgecolor="black", bbox_to_anchor=(0.5, 0.99))
            plt.suptitle(f"Global Analysis: {display_name}", fontsize=22, y=0.95, fontweight='bold')
            
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

    print(f" Global report generated: {pdf_path}")
    

def scan_directory_for_sizes(search_path):
    """
    Recursively scans search_path for .pool.root files.
    Extracts metadata and returns a DataFrame ready for plotting.
    """
    data_list = []
    print(f"\n--- Scanning Directory: {search_path} ---")

    if not os.path.exists(search_path):
        print(f" [!] Error: Path '{search_path}' does not exist.")
        return None

    for root, _, files in os.walk(search_path):
        for filename in files:
            if filename.endswith(".pool.root"):
                
                pattern = r"([a-z0-9]+)_([a-z0-9]+)_(\d+)events\.level(\d+)"
                match = re.search(pattern, filename.lower())
                
                if match:
                    algo, fmt, num_events, lvl = match.groups()
                    file_path = os.path.join(root, filename)
                    
                    try:
                        size_gb = os.path.getsize(file_path) / (1024**3)
                        data_list.append({
                            'Algo': algo,
                            'AOD_type': fmt,
                            'Level': int(lvl),
                            'Events': num_events,
                            'Size': size_gb
                        })
                        print(f" [+] Found: {filename} -> {size_gb:.4f} GB")
                    except OSError as e:
                        print(f" [!] Could not read {filename}: {e}")

    if not data_list:
        print(" [!] No matching files found.")
        return None

    # Convert to DataFrame
    df_long = pd.DataFrame(data_list)
    
    # Create the column name format expected by the plotter: "7000events_level1"
    df_long['ColName'] = df_long['Events'].astype(str) + "events_level" + df_long['Level'].astype(str)
    
    # Pivot from rows to columns
    df_wide = df_long.pivot(index=['Algo', 'AOD_type'], columns='ColName', values='Size').reset_index()
    return df_wide

def plotting_filesize(workspace_path, csv_path=None, data_path=None):
    """
    Generates the Global File Size Report PDF.
    Standardizes CSV naming to 'file_size.csv' for consistency.
    """
    plotting_dir = os.path.join(workspace_path, "plotting")
    os.makedirs(plotting_dir, exist_ok=True)
    pdf_path = os.path.join(plotting_dir, "Global_File_Size_Report.pdf")
    local_csv_name = "file_size.csv"
    
    df = None

   
    if csv_path and os.path.exists(csv_path):
        print(f" [OK] Loading user-provided CSV: {csv_path}")
        df = pd.read_csv(csv_path)
    
    
    elif data_path:
        df = scan_directory_for_sizes(data_path)
        if df is not None:
            save_path = os.path.join(workspace_path, local_csv_name)
            df.to_csv(save_path, index=False)
            print(f" Scan complete and pivoted. CSV saved to: {save_path}")

    
    else:
        local_csv = os.path.join(workspace_path, local_csv_name)
        if os.path.exists(local_csv):
            print(f" [OK] Loading existing local CSV: {local_csv}")
            df = pd.read_csv(local_csv)
        else:
            print(f" [!] Error: No data source found. Provide --data_path or --csv_path.")
            return

    if df is None: return

    
    df['Algo'] = df['Algo'].astype(str).str.lower()
    df['AOD_type'] = df['AOD_type'].astype(str).str.lower()

    
    event_pattern = re.compile(r'(\d+)events')
    cols_with_events = [c for c in df.columns if event_pattern.search(c)]
    event_counts = sorted(list(set(int(event_pattern.search(c).group(1)) for c in cols_with_events)))

    if not event_counts:
        print(" [!] Error: CSV does not contain properly formatted event columns (e.g., '7000events_level1').")
        return

    algorithms = ["zlib", "zstd", "lzma", "lz4"]
    levels = [1, 5, 9]
    formats = ["ttree", "rntuple"]
    colors = {"zlib": "#7b7fcf", "zstd": "#ffd27f", "lzma": "#7fbf7f", "lz4": "#e57373"}
    hatches = {"ttree": "///", "rntuple": ""}

    with PdfPages(pdf_path) as pdf:
        for num_events in event_counts:
            plot_data_per_level = {lvl: [] for lvl in levels}
            found_any_data = False
            ref_value = 0
            max_in_this_plot = 0

            
            for lvl in levels:
                for algo in algorithms:
                    for fmt in formats:
                        col_name = f"{num_events}events_level{lvl}"
                        if col_name in df.columns:
                            val_series = df.loc[(df['Algo'] == algo) & (df['AOD_type'] == fmt), col_name]
                            if not val_series.empty and not pd.isna(val_series.values[0]):
                                val = float(val_series.values[0])
                                plot_data_per_level[lvl].append({'val': val, 'algo': algo, 'fmt': fmt, 'lvl': lvl})
                                found_any_data = True
                                if val > max_in_this_plot: max_in_this_plot = val
                                if algo == "lzma" and fmt == "ttree" and lvl == 1: ref_value = val

            if not found_any_data or ref_value == 0:
                print(f" [?] Skipping {num_events} events: Data or Reference (LZMA L1 TTree) missing.")
                continue

            
            fig, ax = plt.subplots(figsize=(14, 8))
            plt.subplots_adjust(bottom=0.22, top=0.85) 
            
            bar_width, group_spacing = 0.22, 3.0
            x_centers = np.arange(len(levels)) * group_spacing

            for l_idx, lvl in enumerate(levels):
                valid_bars = plot_data_per_level[lvl]
                if not valid_bars: continue
                
                num_bars = len(valid_bars)
                start_offset = -((num_bars - 1) * bar_width) / 2
                
               
                g_start = x_centers[l_idx] + start_offset - (bar_width/2)
                g_end = x_centers[l_idx] + (start_offset + (num_bars-1)*bar_width) + (bar_width/2)
                ax.plot([g_start, g_start, g_end, g_end], [-0.04, -0.08, -0.08, -0.04], 
                        color='black', transform=ax.get_xaxis_transform(), clip_on=False, lw=1.5)

                for b_idx, bar in enumerate(valid_bars):
                    curr_x = x_centers[l_idx] + start_offset + (b_idx * bar_width)
                    ax.bar(curr_x, bar['val'], bar_width, color=colors[bar['algo']], 
                           hatch=hatches[bar['fmt']], edgecolor="black", zorder=3)

                    
                    if not (bar['algo'] == "lzma" and bar['fmt'] == "ttree" and bar['lvl'] == 1):
                        diff_pct = ((bar['val'] - ref_value) / ref_value) * 100
                        ax.text(curr_x, bar['val'] + (max_in_this_plot * 0.01), f"{diff_pct:+.1f}%", 
                                ha="center", va="bottom", fontsize=9, fontweight='bold', rotation=45)
                    else:
                        ax.text(curr_x, bar['val'] + (max_in_this_plot * 0.02), "Ref.", color="red", 
                                ha="center", va="bottom", fontsize=11, fontweight="bold", rotation=45)

            ax.axhline(ref_value, color="red", linestyle="--", alpha=0.7)
            ax.set_xticks(x_centers)
            ax.set_xticklabels([f"Level {l}" for l in levels], fontsize=12, fontweight="bold")
            ax.set_ylabel("Filesize (GB)", fontsize=14, fontweight="bold")
            ax.set_title(f"AOD File Size Relative Change: {num_events} Events", fontsize=16, pad=45)
            ax.set_ylim(0, max_in_this_plot * 1.3)
            ax.yaxis.grid(True, linestyle=":", alpha=0.6)

            
            legend_handles = [Patch(facecolor=colors[a], label=a.upper(), edgecolor="black") for a in algorithms] + \
                             [Patch(facecolor="white", edgecolor="black", hatch=hatches[f], label=f.upper()) for f in formats]
            ax.legend(handles=legend_handles, loc='lower center', ncol=6, bbox_to_anchor=(0.5, 1.05), frameon=False)

            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

    print(f"\n File size report generated: {pdf_path}")



def plotting_gain_loss(ws_abs):
    """Generates gain/loss plots grouped by category and saves them to the plotting folder."""
    
    
    CATEGORIES = {
        "Throughput": ["Job_Throughput(events/ms)", "Job_Read_Throughput(events/ms)"],
        "Memory": ["VMem_max_GB", "RSS_max_GB", "PSS_max_GB"]
    }
    COLORS = {"ZSTD": "#ffd27f", "LZMA": "#7fbf7f", "LZ4": "#e57373", "ZLIB": "#9fa8da"}
    LEVEL_MARKERS = {1: "o", 5: "s", 9: "^"}
    LEVEL_STYLES = {1: "-", 5: "--", 9: ":"}
    

    # Setup the directory path
    plotting_dir = os.path.join(ws_abs, "plotting")
    os.makedirs(plotting_dir, exist_ok=True)
    
    csv_path = os.path.join(ws_abs, "All_Compression_Algo_metrics.csv")
    pdf_path = os.path.join(plotting_dir, "performance_gain_loss.pdf") 

    if not os.path.exists(csv_path):
        print(f" Error: {csv_path} not found.")
        return

    # Load and clean data
    df = pd.read_csv(csv_path)
    df['Algo'] = df['Algo'].astype(str).str.strip().str.upper()
    df['AODtype'] = df['AODtype'].astype(str).str.strip().str.upper()
    
    algorithms = ["ZLIB", "ZSTD", "LZMA", "LZ4"]
    core_counts = sorted(df["Cores"].unique())

    with PdfPages(pdf_path) as pdf:
        for cat_name, metrics in CATEGORIES.items():
            for metric in metrics:
                if metric not in df.columns:
                    continue
                    
                print(f" 📊 Plotting [{cat_name}] {metric}...")
                fig, ax = plt.subplots(figsize=(10, 7))
                all_gains = []

                # Reference Data: LZMA + TTREE + Level 1
                ref_row = df[(df["Algo"] == "LZMA") & (df["AODtype"] == "TTREE") & (df["Level"] == 1)]
                if ref_row.empty:
                    print(f"   No LZMA TTREE L1 reference for {metric}. Skipping.")
                    continue
                
                ref_per_core = ref_row.groupby("Cores")[metric].mean()

                
                for algo in algorithms:
                    for lvl in [1, 5, 9]:
                        combo_df = df[(df["Algo"] == algo) & (df["AODtype"] == "RNTUPLE") & (df["Level"] == lvl)]
                        gains, valid_cores = [], []
                        
                        for core in core_counts:
                            row = combo_df[combo_df["Cores"] == core]
                            if not row.empty and core in ref_per_core.index:
                                val = row[metric].mean()
                                ref_val = ref_per_core.loc[core]
                                if ref_val != 0:
                                    g = (val - ref_val) / ref_val * 100
                                    gains.append(g)
                                    all_gains.append(g)
                                    valid_cores.append(core)
                        
                        if gains:
                            ax.plot(valid_cores, gains, 
                                    marker=LEVEL_MARKERS.get(lvl, "o"),
                                    linestyle=LEVEL_STYLES.get(lvl, "-"), 
                                    color=COLORS.get(algo, "#ccc"),
                                    linewidth=2, markersize=8, alpha=0.8)

               
                ax.axhline(0, color="red", linestyle="--", linewidth=2.5)
                ax.text(0.01, 1, "Ref", transform=ax.get_yaxis_transform(), 
                        color="red", fontweight="bold", va="bottom", ha="left")

                #  Legend
                algo_h = [mpatches.Patch(facecolor=COLORS[a], edgecolor='black', label=a) for a in algorithms]
                lvl_h = [Line2D([0], [0], color='black', marker=m, linestyle='None', label=f'L{l}') 
                         for l, m in LEVEL_MARKERS.items()]
                ref_h = [Line2D([0], [0], color='red', linestyle='--', label='Ref (LZMA TTree L1)')]
                
                ax.legend(handles=algo_h + lvl_h + ref_h, loc='upper center', bbox_to_anchor=(0.5, 0.98),
                          ncol=4, frameon=True, edgecolor='black', fancybox=False, fontsize=9, borderpad=1.0)

                
                for spine in ax.spines.values():
                    spine.set_edgecolor('black')
                    spine.set_linewidth(1.2)

                
                if all_gains:
                    d_min, d_max = min(all_gains + [0]), max(all_gains + [0])
                    ax.set_ylim(d_min - ((d_max-d_min) * 0.15), d_max + ((d_max-d_min) * 0.6))

                ax.set_xlabel("Number of Cores", fontweight='bold')
                ax.set_ylabel("Gain / Loss (%) vs LZMA TTree L1", fontweight='bold')
                ax.set_title(f"{cat_name}: {metric}", fontsize=14, fontweight='bold', pad=20)
                ax.set_xticks(core_counts)
                ax.grid(True, linestyle=":", alpha=0.5)

                plt.tight_layout()
                pdf.savefig(fig) 
                plt.close(fig)   

    print(f" Success: Gain/Loss report generated at: {pdf_path}")
    


def plotting_impact_analysis(ws_abs):
    """
    Generates a multi-page PDF measuring the impact of file size on various performance metrics.
    Evaluates impact per core with an integrated boxed legend.
    """
    METRICS = {
        "Job_Throughput(events/ms)": "Overall Throughput",
        "Job_Read_Throughput(events/ms)": "Read Throughput",
        "VMem_max_GB": "Virtual Memory",
        "RSS_max_GB": "Resident Set Size (RSS)"
    }
    COLORS = {"ZSTD": "#ffd27f", "LZMA": "#7fbf7f", "LZ4": "#e57373", "ZLIB": "#9fa8da"}
    MARKERS = {1: "o", 5: "s", 9: "^"}
    
    plotting_dir = os.path.join(ws_abs, "plotting")
    os.makedirs(plotting_dir, exist_ok=True)
    perf_csv = os.path.join(ws_abs, "All_Compression_Algo_metrics.csv")
    size_csv = os.path.join(ws_abs, "file_size.csv")
    pdf_path = os.path.join(plotting_dir, "size_impact_analysis.pdf")

    if not (os.path.exists(perf_csv) and os.path.exists(size_csv)):
        print(f" Error: Required CSVs missing in {ws_abs}")
        return

    df_perf = pd.read_csv(perf_csv)
    df_size = pd.read_csv(size_csv)
    
    df_perf['Algo'] = df_perf['Algo'].str.upper().str.strip()
    df_perf['AODtype'] = df_perf['AODtype'].str.upper().str.strip()
    
    df_size_long = df_size.melt(id_vars=['Algo', 'AOD_type'], var_name='Metadata', value_name='Size_GB')
    df_size_long['Level'] = df_size_long['Metadata'].str.extract(r'level(\d+)').astype(int)
    df_size_long['Algo'] = df_size_long['Algo'].str.upper().str.strip()
    df_size_long['AODtype'] = df_size_long['AOD_type'].str.upper().str.strip()

    core_counts = sorted(df_perf['Cores'].unique())

    with PdfPages(pdf_path) as pdf:
        for metric_col, metric_label in METRICS.items():
            if metric_col not in df_perf.columns:
                continue
            
            for core in core_counts:
                print(f" Impact Analysis: {metric_label} @ {core} Core(s)...")

                ref_perf_df = df_perf[(df_perf['Algo']=='LZMA') & (df_perf['AODtype']=='TTREE') & 
                                     (df_perf['Level']==1) & (df_perf['Cores']==core)]
                
                if ref_perf_df.empty:
                    print(f"  Skip: No reference data for {core} cores.")
                    continue
                
                ref_perf = ref_perf_df[metric_col].mean()
                ref_size = df_size_long[(df_size_long['Algo']=='LZMA') & (df_size_long['AODtype']=='TTREE') & 
                                       (df_size_long['Level']==1)]['Size_GB'].mean()

                if ref_perf == 0 or pd.isna(ref_perf):
                    continue

                results = []
                for algo in ["ZSTD", "LZMA", "LZ4", "ZLIB"]:
                    for lvl in [1, 5, 9]:
                        p_val = df_perf[(df_perf['Algo']==algo) & (df_perf['AODtype']=='RNTUPLE') & 
                                        (df_perf['Level']==lvl) & (df_perf['Cores']==core)][metric_col].mean()
                        s_val = df_size_long[(df_size_long['Algo']==algo) & (df_size_long['AODtype']=='RNTUPLE') & 
                                            (df_size_long['Level']==lvl)]['Size_GB'].mean()
                        
                        if pd.notnull(p_val) and pd.notnull(s_val):
                            results.append({
                                'Algo': algo, 'Level': lvl,
                                'S_Gain': (s_val - ref_size) / ref_size * 100,
                                'P_Gain': (p_val - ref_perf) / ref_perf * 100
                            })

                if not results: continue
                df_plot = pd.DataFrame(results).dropna(subset=['S_Gain', 'P_Gain'])
                if df_plot.empty: continue

                fig, ax = plt.subplots(figsize=(10, 8))
                
                plt.subplots_adjust(top=0.82)

                ax.axhline(0, color='red', linestyle='--', lw=1.5, alpha=0.6)
                ax.axvline(0, color='red', linestyle='--', lw=1.5, alpha=0.6)
                ax.scatter(0, 0, color='red', marker='X', s=200, zorder=10)

                for algo in df_plot['Algo'].unique():
                    sub = df_plot[df_plot['Algo'] == algo].sort_values('Level')
                    ax.plot(sub['S_Gain'], sub['P_Gain'], color=COLORS[algo], lw=2, alpha=0.5)
                    for _, row in sub.iterrows():
                        ax.scatter(row['S_Gain'], row['P_Gain'], color=COLORS[algo], 
                                   marker=MARKERS[row['Level']], s=180, edgecolors='black', zorder=5)

               
                algo_h = [mpatches.Patch(facecolor=COLORS[a], edgecolor='black', label=a) for a in COLORS if a in df_plot['Algo'].values]
                lvl_h = [Line2D([0], [0], color='black', marker=m, linestyle='None', markersize=10, label=f'Level {l}') for l, m in MARKERS.items()]
                all_h = algo_h + lvl_h
                
               
                leg = ax.legend(handles=all_h, loc='lower center', bbox_to_anchor=(0.5, 1.0), 
                                ncol=len(all_h), frameon=True, fancybox=False, 
                                edgecolor='black', fontsize=9, handletextpad=0.5)
                
                
                leg.get_frame().set_linewidth(1.0)
                leg.get_frame().set_alpha(1.0)

                
                is_mem = "Mem" in metric_col
                win_txt = "Smaller & Lighter" if is_mem else "Smaller & Faster"
                loss_txt = "Smaller & Heavier" if is_mem else "Smaller & Slower"
                box_style = dict(facecolor='white', alpha=0.8, edgecolor='none')
                
                ax.text(0.02, 0.96, win_txt, transform=ax.transAxes, color='green', fontweight='bold', va='top', ha='left', bbox=box_style)
                ax.text(0.02, 0.04, loss_txt, transform=ax.transAxes, color='orange', fontweight='bold', va='bottom', ha='left', bbox=box_style)
                ax.text(0.98, 0.96, "Larger & Faster", transform=ax.transAxes, color='gray', fontweight='bold', va='top', ha='right', bbox=box_style)
                ax.text(0.98, 0.04, "Larger & Slower", transform=ax.transAxes, color='gray', fontweight='bold', va='bottom', ha='right', bbox=box_style)

                x_abs = df_plot['S_Gain'].abs().max()
                y_abs = df_plot['P_Gain'].abs().max()
                x_lim = (x_abs if pd.notnull(x_abs) and x_abs > 0 else 10) * 1.3
                y_lim = (y_abs if pd.notnull(y_abs) and y_abs > 0 else 10) * 1.3

                ax.set_xlim(-x_lim, x_lim)
                ax.set_ylim(-y_lim, y_lim)

                ax.set_xlabel("File Size Change (%) [Ref: LZMA TTree L1]", fontweight='bold')
                ax.set_ylabel(f"{metric_label} Change (%)", fontweight='bold')
                
                ax.set_title(f"Impact Analysis: {metric_label} ({core} Cores)", fontsize=14, fontweight='bold', pad=45)
                ax.grid(True, linestyle=":", alpha=0.6)

                pdf.savefig(fig)
                plt.close(fig)

    print(f" Success: All Impact plots saved to: {pdf_path}")