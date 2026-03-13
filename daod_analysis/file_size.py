import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.backends.backend_pdf import PdfPages
import os

def generate_combined_pdf(csv_file, output_pdf):
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found.")
        return

    df = pd.read_csv(csv_file)
    df['Algo'] = df['Algo'].str.lower()
    df['AOD_type'] = df['AOD_type'].str.lower()

    
    algorithms = ["zlib", "zstd", "lzma", "lz4"]
    levels = [1, 5, 9]
    formats = ["ttree", "rntuple"]
    event_counts = [7000, 28000, 56000, 112000, 224000]

    colors = {"zlib": "#7b7fcf", "zstd": "#ffd27f", "lzma": "#7fbf7f", "lz4": "#e57373"}
    hatches = {"ttree": "///", "rntuple": ""}

   
    with PdfPages(output_pdf) as pdf:
       
        for num_events in event_counts:
            plot_data_per_level = {lvl: [] for lvl in levels}
            found_any_data = False
            ref_value = 0

            
            for lvl in levels:
                for algo in algorithms:
                    for fmt in formats:
                        col_name = f"{num_events}events_level_{lvl}" if num_events == 112000 else f"{num_events}events_level{lvl}"
                        
                        try:
                            val = df.loc[(df['Algo'] == algo) & (df['AOD_type'] == fmt), col_name]
                            if not val.empty and not pd.isna(val.values[0]):
                                size_gb = float(val.values[0])
                                if size_gb > 0:
                                    plot_data_per_level[lvl].append({
                                        'val': size_gb, 'algo': algo, 'fmt': fmt, 'lvl': lvl
                                    })
                                    found_any_data = True
                                    if algo == "lzma" and fmt == "ttree" and lvl == 1:
                                        ref_value = size_gb
                        except KeyError:
                            continue

            if not found_any_data or ref_value == 0:
                print(f"Skipping {num_events} events: Data or Baseline missing.")
                continue

            
            fig, ax = plt.subplots(figsize=(12, 7))
            
            bar_width = 0.22       
            group_spacing = 3.0    
            x_centers = np.arange(len(levels)) * group_spacing

            
            all_vals = []

            for l_idx, lvl in enumerate(levels):
                valid_bars = plot_data_per_level[lvl]
                num_bars = len(valid_bars)
                if num_bars == 0: continue
                    
                start_offset = -((num_bars - 1) * bar_width) / 2
                
                
                group_x_start = x_centers[l_idx] + start_offset - (bar_width/2)
                group_x_end = x_centers[l_idx] + (start_offset + (num_bars-1)*bar_width) + (bar_width/2)
                ax.plot([group_x_start, group_x_start, group_x_end, group_x_end], 
                        [-0.05, -0.1, -0.1, -0.05], color='black', 
                        transform=ax.get_xaxis_transform(), clip_on=False)

                for b_idx, bar in enumerate(valid_bars):
                    offset = start_offset + (b_idx * bar_width)
                    curr_x = x_centers[l_idx] + offset
                    all_vals.append(bar['val'])
                    
                    ax.bar(curr_x, bar['val'], bar_width, color=colors[bar['algo']], 
                            hatch=hatches[bar['fmt']], edgecolor="black", zorder=3)

                    is_baseline = (bar['algo'] == "lzma" and bar['fmt'] == "ttree" and bar['lvl'] == 1)
                    if not is_baseline:
                        diff_pct = ((bar['val'] - ref_value) / ref_value) * 100
                        ax.text(curr_x, bar['val'] + (ref_value * 0.01), f"{diff_pct:+.1f}%", 
                                 ha="center", va="bottom", fontsize=9, fontweight='bold', 
                                 rotation=60, zorder=4)
                    else:
                        ax.text(curr_x, bar['val'] + (ref_value * 0.02), "Ref.", color="red", 
                                 ha="center", va="bottom", fontsize=11, fontweight="bold", 
                                 rotation=60)

           
            ax.axhline(ref_value, color="red", linestyle="--", linewidth=2, zorder=5)
            ax.yaxis.grid(True, linestyle=":", color="black", alpha=0.8, zorder=0)
            
            ax.set_xticks(x_centers)
            ax.set_xticklabels([f"Level {l}" for l in levels], fontsize=12, fontweight="bold")
            ax.set_xlabel("Compression level", fontsize=14)
            ax.set_ylabel("Filesize (GB)", fontsize=14, fontweight="bold")
            ax.set_title(f"AOD File Size Comparison: {num_events} Events", fontsize=16, pad=30)
            
            
            max_y = max(all_vals) if all_vals else ref_value
            ax.set_ylim(0, max(max_y, ref_value) * 1.35)

            
            algo_patches = [Patch(facecolor=colors[a], label=a.upper(), edgecolor="black") for a in algorithms]
            format_patches = [Patch(facecolor="white", edgecolor="black", hatch=hatches[f], label=f.upper()) for f in formats]
            ax.legend(handles=algo_patches + format_patches, loc='upper center', 
                       ncol=6, frameon=True, edgecolor="black", bbox_to_anchor=(0.5, 1.02))

            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

    print(f"Success: All plots saved to {output_pdf}")

if __name__ == "__main__":
    generate_combined_pdf("file.csv", "AOD_Compression_Results.pdf")