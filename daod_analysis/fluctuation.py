import os
import re 
import pandas as pd
import numpy as np

def check_fluctuation_and_aggregate(workspace_path):
    master_name = "All_Compression_Algo_metrics.csv"
    master_path = os.path.join(workspace_path, master_name)
    
    all_csv_files = []
    print(f"\n[SCAN] Searching workspace: {workspace_path}")

    # 1. Search recursively for algorithm result CSVs
    for root, dirs, files in os.walk(workspace_path, followlinks=True):
        for fname in files:
            # Skip the master file itself and other non-data CSVs
            if fname == master_name or "fluctuation" in fname.lower() or "worker" in fname.lower():
                continue
            if not fname.endswith(".csv"):
                continue
            
            full_path = os.path.join(root, fname)
            all_csv_files.append(full_path)
            print(f" [+] Found: {os.path.relpath(full_path, workspace_path)}")

    if not all_csv_files:
        print(f" [!] No CSV files found to aggregate.")
        return

    try:
        # 2. Aggregate all data
        df_list = [pd.read_csv(f) for f in all_csv_files]
        master_df = pd.concat(df_list, ignore_index=True)
        master_df.to_csv(master_path, index=False)
        print(f"\n [OK] Aggregated all runs into: {master_path}")

        # 3. Define Grouping Columns (The Conditions)
        # These columns define a "unique" test setup
        group_cols = ["Algo", "AODtype", "Level", "Cores", "Processors", "Total_events"]
        
        # 4. Identify Numeric Metrics (The Measurements)
        # We calculate fluctuation ONLY on these
        numeric_cols = master_df.select_dtypes(include=[np.number]).columns.tolist()
        
        # REMOVE setup/metadata columns from the math list
        for col in group_cols + ['Run_ID']:
            if col in numeric_cols:
                numeric_cols.remove(col)

        # 5. Calculate Mean and Std Dev per group
        # as_index=False ensures our group_cols stay as normal columns
        mean_df = master_df.groupby(group_cols, as_index=False)[numeric_cols].mean()
        std_df = master_df.groupby(group_cols, as_index=False)[numeric_cols].std()
        
        # 6. Calculate % Fluctuation (Coefficient of Variation)
        report_df = mean_df.copy()
        
        for col in numeric_cols:
            # (Standard Deviation / Mean) * 100
            # 1e-9 prevents division by zero if mean is 0
            report_df[col] = (std_df[col] / (mean_df[col] + 1e-9)) * 100
        
        # Round percentages to 2 decimal places for readability
        report_df = report_df.round(2)

        # 7. Stability Check
        threshold = 5.0
        print("\n" + "="*60)
        print(" GLOBAL STABILITY ANALYSIS (Fluctuation %)")
        print("="*60)
        
        unstable_configs = []
        for col in numeric_cols:
            # Find rows where this specific metric exceeds the 5% threshold
            if (report_df[col] > threshold).any():
                unstable_configs.append(col)
        
        if unstable_configs:
            print(f" ALERT: High fluctuation (> {threshold}%) detected in:")
            for metric in unstable_configs:
                print(f"  -> {metric}")
        else:
            print(f" SUCCESS: All configurations are stable (< {threshold}%).")
        print("="*60)

        # 8. Save the Report
        report_path = os.path.join(workspace_path, "global_fluctuation_report.csv")
        report_df.to_csv(report_path, index=False)
        print(f" Report saved: {report_path}\n")

    except Exception as e:
        print(f" [!] Error during fluctuation analysis: {e}")