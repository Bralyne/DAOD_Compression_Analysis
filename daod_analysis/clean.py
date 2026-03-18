import pandas as pd
import os
import numpy as np

def clean(workspace_path, noise_threshold=5.0):
    master_path = os.path.join(workspace_path, "All_Compression_Algo_metrics.csv")
    if not os.path.exists(master_path):
        print(" Error: Master CSV not found. Please run the fluctuation mode first")
        return

    df = pd.read_csv(master_path)
    group_cols = ["Algo", "AODtype", "Level", "Cores"]
    # We check stability for all key performance indicators
    check_metrics = ["Job_Throughput(events/ms)", "Job_Read_Throughput(events/ms)", "RSS_max_GB", "VMem_max_GB"]
    
    cleaned_rows = []
    rerun_list = []

    for name, group in df.groupby(group_cols):
        algo, aod, lvl, core = name
        current_subset = group.copy()
        is_stable = False
        
        2
        while len(current_subset) >= 2:
            # Calculate fluctuation for all metrics in this subset
            means = current_subset[check_metrics].mean()
            stds = current_subset[check_metrics].std()
            noises = (stds / (means + 1e-9) * 100)

            # Check if EVERY metric is under the threshold
            if (noises <= noise_threshold).all():
                is_stable = True
                break
            else:
                # Still noisy: Find and remove the SINGLE worst outlier in this group
                
                medians = current_subset[check_metrics].median()
                # (Value - Median) / Median gives a relative distance
                distances = ((current_subset[check_metrics] - medians).abs() / (medians + 1e-9)).sum(axis=1)
                worst_row_index = distances.idxmax()
                current_subset = current_subset.drop(worst_row_index)

        if is_stable:
            cleaned_rows.append(current_subset)
            if len(current_subset) < len(group):
                print(f" [+] Stabilized {algo}_{aod}_L{lvl}_C{core}: Kept {len(current_subset)}/{len(group)} runs.")
        else:
            
            rerun_list.append(f"Algo: {algo}, Type: {aod}, Level: {lvl}, Core: {core}")

    # Final Save
    if cleaned_rows:
        pd.concat(cleaned_rows, ignore_index=True).to_csv(master_path, index=False)
    
    if rerun_list:
        print("\n" + "!"*60)
        print(" UNSTABLE DATA - DELETED FROM MASTER (RERUN REQUIRED):")
        for item in rerun_list:
            print(f"  -> {item}")
        print("!"*60)