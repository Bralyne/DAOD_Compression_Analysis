import pandas as pd
import os

def clean(workspace_path, noise_threshold=5.0):
    master_path = os.path.join(workspace_path, "All_Compression_Algo_metrics.csv")
    
    if not os.path.exists(master_path):
        print(" Error: Master CSV not found.")
        return

    df = pd.read_csv(master_path)
    
    # Identify unique configurations
    group_cols = ["Algo", "AODtype", "Level", "Cores"]
    metric_cols = ["Job_Throughput(events/ms)", "RSS_max_GB", "DAOD_size_GB"]
    
    cleaned_rows = []
    rerun_list = []

    # Group by configuration to check stability internally
    for name, group in df.groupby(group_cols):
        algo, aod, lvl, core = name
        
        # Calculate CV (Coefficient of Variation) for the main speed metric
        # CV = (std / mean) * 100
        mean_val = group["Job_Throughput(events/ms)"].mean()
        std_val = group["Job_Throughput(events/ms)"].std()
        
        noise = (std_val / mean_val * 100) if mean_val > 0 else 0

        if noise <= noise_threshold:
            # OPTION A: Configuration is stable
            cleaned_rows.append(group)
        else:
            # OPTION B: Unstable: Try to find a stable pair
            # Sort by deviation from median and keep the two closest ones
            median_val = group["Job_Throughput(events/ms)"].median()
            group['dist'] = (group["Job_Throughput(events/ms)"] - median_val).abs()
            stable_subset = group.sort_values('dist').head(2)
            
            # Check if the new subset is stable
            new_noise = (stable_subset["Job_Throughput(events/ms)"].std() / stable_subset["Job_Throughput(events/ms)"].mean() * 100)
            
            if new_noise <= noise_threshold and len(stable_subset) >= 2:
                cleaned_rows.append(stable_subset.drop(columns=['dist']))
                print(f" Stabilized {algo} {aod} L{lvl} Core {core} by removing outliers.")
            else:
                # OPTION C: Total Failure: Delete and request rerun
                rerun_list.append(f"Algo: {algo}, Type: {aod}, Level: {lvl}, Core: {core}")

    # Finalize the Master CSV
    if cleaned_rows:
        new_master_df = pd.concat(cleaned_rows, ignore_index=True)
        new_master_df.to_csv(master_path, index=False)
        
    # Final Reporting
    if rerun_list:
        print("\n" + "!"*50)
        print(" UNSTABLE DATA DETECTED - PLEASE RERUN THE FOLLOWING:")
        for item in rerun_list:
            print(f"  -> {item}")
        print("!"*50)
        print("\nNote: These configurations were DELETED from the master CSV to protect plot integrity.")
    else:
        print("\n All configurations are now stable. Ready for plotting.")