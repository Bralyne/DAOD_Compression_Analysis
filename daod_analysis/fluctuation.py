import os
import glob
import pandas as pd
import numpy as np

def check_fluctuation_and_aggregate(workspace_path):
    master_name = "All_Compression_Algo_metrics.csv"
    master_path = os.path.join(workspace_path, master_name)
    
    # Recursive pattern: '**' finds files in any sub-folder depth
    csv_pattern = os.path.join(workspace_path, "**", "*.csv")
    
    # Strict Filter: Only include files that follow the project naming convention
    all_csv_files = []
    for f in glob.glob(csv_pattern, recursive=True):
        fname = os.path.basename(f)
        
        # Skip technical/summary files
        if master_name in fname: continue
        if "fluctuation" in fname: continue
        if "worker" in fname.lower(): continue 
            
        # ONLY include primary data files ( zstd_ttree_level1.csv)
        if "_level" in fname:
            all_csv_files.append(f)

    if not all_csv_files:
        print(f" No project data found in {workspace_path}.")
        return

    print(f" Found {len(all_csv_files)} files. Aggregating into Master CSV...")

    # Aggregate Data
    try:
        df_list = [pd.read_csv(f) for f in all_csv_files]
        master_df = pd.concat(df_list, ignore_index=True)
        master_df.to_csv(master_path, index=False)
        print(f" Master CSV updated: {master_path}")
    except Exception as e:
        print(f" Error during aggregation: {e}")
        return

    # Statistical Calculation (Coefficient of Variation)
    group_cols = ["AODtype", "Cores", "Algo", "Processors", "Level"]
    
    # Drop non metric columns to keep the report clean
    drop_cols = ['Run_ID', 'Total_events']
    calc_df = master_df.drop(columns=[c for c in drop_cols if c in master_df.columns])
    
    grouped = calc_df.groupby(group_cols)

    
    mean_vals = grouped.mean(numeric_only=True)
    std_vals = grouped.std(numeric_only=True)
    
    # Calculate % Fluctuation (CV)
    # 1e-9 prevents division by zero if mean is 0
    std_pct = (std_vals / (mean_vals + 1e-9)) * 100
    std_pct = std_pct.round(2).reset_index()

    # Stability
    metric_cols = [c for c in std_pct.columns if c not in group_cols]
    unstable_metrics = []

    for col in metric_cols:
        # Check if any configuration for this metric fluctuates > 5%
        if (std_pct[col] > 5).any():
            unstable_metrics.append(col)

    # Output Results
    print("-" * 40)
    if unstable_metrics:
        print(f"  STABILITY ALERT: High fluctuation (>5%) in: {', '.join(unstable_metrics)}")
        print(f" RECOMMENDATION: Run 'clean' mode, then 'run_collect' again.")
    else:
        print(" SUCCESS: All metrics are stable (< 5% fluctuation).")
    print("-" * 40)

    # Save the report
    fluct_csv = os.path.join(workspace_path, "fluctuation.csv")
    std_pct.to_csv(fluct_csv, index=False)
    print(f" Stability report saved: {fluct_csv}")