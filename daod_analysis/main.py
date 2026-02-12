import argparse
import os
import sys
import subprocess
import glob
import pandas as pd
from daod_analysis import plotter
from daod_analysis import fluctuation
from daod_analysis import clean
import numpy as np

    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True, help="Path to the workspace directory")
    parser.add_argument("--project", required=False, help="Name of the project")
    
    # ---  choices ----
    parser.add_argument("--mode", choices=["create", "run_collect", "fluctuation", "clean", "plot"], required=True)
    parser.add_argument("--cores", default="8")
    parser.add_argument("--proc", default="1")
    parser.add_argument("--runs", default="5")
    parser.add_argument("--maxevents", default="7000")

    args = parser.parse_args()
    ws_abs = os.path.abspath(args.workspace)
    
    # --- Project Requirement  ---
    proj_abs = os.path.join(ws_abs, args.project) if args.project else None

    # --- MODE: CREATE ---
    if args.mode == "create":
        if not proj_abs:
            print(" Error: --project is required for 'create' mode.")
            sys.exit(1)
        data_dir = os.path.join(proj_abs, "data")
        try:
            os.makedirs(data_dir, exist_ok=True)
            print(f" Project structure initialized.")
            print(f" Location: {proj_abs}")
            print(f" Data folder created: {data_dir}")
            print(f"\n Next Step: Move your .pool.root files into the data folder using:")
            print(f"   mv your_file.pool.root {data_dir}/")
        except Exception as e:
            print(f" Error creating project: {e}")
            sys.exit(1)

    # --- MODE: RUN COLLECT ---
    elif args.mode == "run_collect":
        if not proj_abs:
            print(" Error: --project is required for 'run_collect' mode.")
            sys.exit(1)

        # 1. Environment
        if "AtlasProject" not in os.environ and "Athena_VERSION" not in os.environ:
            print(" Error: Athena environment not detected.")
            print(" 'run_collect' must be run on a machine with ATLAS software.")
            print(" Did you forget to run: setupATLAS && asetup Athena,main--dev3LCG,latest?")
            sys.exit(1)

        # 2. Directory 
        if not os.path.exists(proj_abs):
            print(f" Error: Project directory '{proj_abs}' not found.")
            print(f"Please run with '--mode create' first or create: {os.path.join(proj_abs, 'data/')}")
            sys.exit(1)

        data_dir = os.path.join(proj_abs, "data")
        if not os.path.exists(data_dir):
            print(f" Error: Data folder missing at '{data_dir}'.")
            sys.exit(1)

        # 3. Execute
        subprocess.run([
            "bash", "derivation_mp.sh", 
            data_dir, proj_abs, 
            args.proc, args.cores, args.runs, args.maxevents
        ], check=True)

    # ---MODE: FLUCTUATION ---
    elif args.mode == "fluctuation":
        
        fluctuation.check_fluctuation_and_aggregate(ws_abs)
    
    # ---MODE: CLEAN ---
    elif args.mode == "clean":
        print(f" Starting cleanup for workspace: {ws_abs}")
        clean.clean(ws_abs)
    
    # --- MODE: PLOT ---
    elif args.mode == "plot":
        plotter.run_bulk_plotting(ws_abs)

if __name__ == "__main__":
    main()