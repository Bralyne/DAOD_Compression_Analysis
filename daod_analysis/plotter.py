#import libraries

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator, FuncFormatter


def run_bulk_plotting(workspace_path):
    plotting_dir = os.path.join(workspace_path, "plotting")
    os.makedirs(plotting_dir, exist_ok=True)
    
    master_csv = os.path.join(workspace_path, "All_Compression_Algo_metrics.csv")
    pdf_path = os.path.join(plotting_dir, "Global_Compression_Report.pdf")

    if not os.path.exists(master_csv):
        print(f"Error: Master CSV not found at {master_csv}")
        return

    df_raw = pd.read_csv(master_csv)

    metrics_to_plot = {
        "Job_Throughput(events/ms)": "Write Throughput (events/ms)",
        "Job_Read_Throughput(events/ms)": "Read Throughput (events/ms)",
        "RSS_max_GB": "Physical Memory (RSS) max GB",
        "DAOD_size_GB": "File Size (GB)"
    }
    for col in metrics_to_plot.keys():
        if col in df_raw.columns:
            df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')

    color_map = {"LZMA": "#d62728", "ZSTD": "#2ca02c", "LZ4": "#1f77b4", "ZLIB": "#9467bd"}
    marker_symbols = {1: "o", 5: "s", 9: "^"} 
    algos = sorted(df_raw["Algo"].unique())
    levels = sorted(df_raw["Level"].unique())
    cores = sorted([int(c) for c in df_raw["Cores"].unique()])

    with PdfPages(pdf_path) as pdf:
        for csv_col, display_name in metrics_to_plot.items():
            if csv_col not in df_raw.columns: continue

            fig, (ax_line, ax_bar) = plt.subplots(1, 2, figsize=(24, 10), sharey=True)
            plt.subplots_adjust(wspace=0.05)
            
            
            for algo in algos:
                for lvl in levels:
                    subset = df_raw[(df_raw["Algo"] == algo) & (df_raw["Level"] == lvl)]
                    if subset.empty: continue
                    df_p = subset.groupby("Cores")[csv_col].mean().reset_index()
                    
                    color = color_map.get(algo.upper(), "#7f7f7f")
                    ax_line.plot(df_p["Cores"], df_p[csv_col], 
                                 marker=marker_symbols.get(lvl, "D"), 
                                 linestyle="-", color=color, linewidth=2, markersize=10,
                                 markeredgecolor='white', markeredgewidth=1) 
            
            
            ax_line.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax_line.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x)}'))
            ax_line.set_title(f"{display_name} Scaling Trends", fontsize=16, fontweight='bold')
            ax_line.set_xlabel("Cores")
            ax_line.set_ylabel(display_name)

            
            n_combos = len(algos) * len(levels)
            bar_width = 0.8 / n_combos
            x_ticks = np.arange(len(cores))

            for i, algo in enumerate(algos):
                for j, lvl in enumerate(levels):
                    subset = df_raw[(df_raw["Algo"] == algo) & (df_raw["Level"] == lvl)]
                    means = subset.groupby("Cores")[csv_col].mean().reindex(cores).fillna(0).values
                    offset = (i * len(levels) + j - (n_combos - 1) / 2) * bar_width
                    
                    is_baseline = (algo.upper() == "LZMA" and lvl == 1)
                    ax_bar.bar(x_ticks + offset, means, bar_width, 
                               color=color_map.get(algo.upper(), "#7f7f7f"), 
                               edgecolor='black', hatch='////' if is_baseline else '', zorder=2)
                    
                    
                    marker = marker_symbols.get(lvl, "D")
                    for core_idx, h in enumerate(means):
                        if h > 0:
                            ax_bar.plot(x_ticks[core_idx] + offset, h * 0.94, 
                                        marker=marker, color='black', 
                                        markeredgecolor='white', markeredgewidth=1, 
                                        markersize=8, zorder=4)

            
            for idx, core_val in enumerate(cores):
                core_ref = df_raw[(df_raw["Cores"] == core_val) & (df_raw["Algo"].str.upper() == "LZMA") & (df_raw["Level"] == 1)]
                if not core_ref.empty:
                    ref_val = core_ref[csv_col].mean()
                    ax_bar.hlines(ref_val, idx - 0.5, idx + 0.5, colors='red', linestyles='--', linewidth=2.5, zorder=3)
                    ax_bar.text(idx, ref_val, ' Ref ', color='red', fontweight='bold', 
                                ha='center', va='bottom', fontsize=11, 
                                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1), zorder=5)

            ax_bar.set_title(f"{display_name} Comparison vs Baseline", fontsize=16, fontweight='bold')
            ax_bar.set_xticks(x_ticks)
            ax_bar.set_xticklabels([str(int(c)) for c in cores])
            ax_bar.set_xlabel("Cores")
            ax_bar.set_xlim(-0.5, len(cores) - 0.5)
            ax_bar.tick_params(axis='y', which='both', left=False, labelleft=False)

            
            algo_legend = [Patch(facecolor=color_map.get(a.upper(), "#7f7f7f"), label=f"Algo: {a}") for a in algos]
            
            lvl_legend = [Line2D([0], [0], marker=marker_symbols[l], color='w', 
                          markerfacecolor='black', markeredgecolor='black', markersize=10, label=f"Level {l}") for l in levels]
            ref_legend = [Line2D([0], [0], color='red', linestyle='--', linewidth=2, label='Baseline (LZMA L1)')]
            
            ax_bar.legend(handles=algo_legend + lvl_legend + ref_legend, 
                          bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

            plt.suptitle(f"Global Compression Analysis: {display_name}", fontsize=22, y=0.98)
            plt.tight_layout(rect=[0, 0, 0.85, 0.95])
            pdf.savefig(fig)
            plt.close(fig)

    print(f" Your plots were generated.")