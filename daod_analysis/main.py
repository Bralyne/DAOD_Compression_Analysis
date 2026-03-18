# Copyright 2026 Bralyne Matoukam
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



import argparse
import os
import sys
import subprocess
import re

def extract_metadata_from_filename(filename):
    """
    Extracts the Algorithm to use as the folder name.
    Example: lzma_ttree_level1.AOD.pool.root -> returns 'LZMA'
    """
    try:
        base = filename.split('.AOD')[0]
        parts = base.split('_')
        # The first part of the file name is the Algorithm (LZMA, ZSTD, etc.)
        algo = parts[0].upper()
        return algo
    except Exception:
        return "UNKNOWN"

def main():
    parser = argparse.ArgumentParser(description="DAOD Analysis Tool")
    
    
    parser.add_argument("--workspace", required=True, help="Path to the base directory")
    parser.add_argument("--mode", choices=["run_collect", "fluctuation", "clean", "plot"], required=True)
    parser.add_argument("--data_path", help="Path to .pool.root file or directory")
    parser.add_argument("--csv_path", help="Path to a specific CSV for file size plotting")
    parser.add_argument("--metrics", action="store_true", help="Plot raw performance metrics")
    parser.add_argument("--gain_loss", action="store_true", help="Plot performance gain/loss %")
    parser.add_argument("--impact", action="store_true", help="Plot Size vs Performance impact analysis")
    
    
    parser.add_argument("--cores", default="8")
    parser.add_argument("--proc", default="1")
    parser.add_argument("--runs", default="5")
    parser.add_argument("--maxevents", default="7000")

    args = parser.parse_args()
    ws_abs = os.path.abspath(args.workspace)
    
   
    if args.mode == "run_collect":
        if not args.data_path:
            print(" Error: --mode run_collect requires --data_path")
            sys.exit(1)
            
        external_data_dir = os.path.abspath(args.data_path)
        if not os.path.exists(external_data_dir):
            print(f"  Error: Path does not exist: {external_data_dir}")
            sys.exit(1)
        
        
    elif args.mode == "fluctuation":
        from daod_analysis import fluctuation
        fluctuation.check_fluctuation_and_aggregate(ws_abs)

   
    elif args.mode == "clean":
        from daod_analysis import clean
        clean.clean(ws_abs)

    
    elif args.mode == "plot":
        from daod_analysis import plotter
        plot_triggered = False

        
        if args.csv_path or args.data_path:
            print(" Plotting file sizes...")
            d_path = os.path.abspath(args.data_path) if args.data_path else None
            plotter.plotting_filesize(ws_abs, csv_path=args.csv_path, data_path=d_path)
            plot_triggered = True

        
        if args.impact:
            print(" Plotting Size vs Performance Impact Analysis (Per Core)...")
            plotter.plotting_impact_analysis(ws_abs)
            plot_triggered = True

       
        if args.gain_loss:
            print("Plotting performance GAIN/LOSS vs Reference...")
            plotter.plotting_gain_loss(ws_abs)
            plot_triggered = True

       
        if args.metrics:
            print("  Plotting raw performance metrics...")
            plotter.plotting_metrics(ws_abs)
            plot_triggered = True

        if not plot_triggered:
            print("  No specific plot requested. Use --impact, --metrics, --gain_loss, or provide data/csv paths.")

if __name__ == "__main__":
    main()