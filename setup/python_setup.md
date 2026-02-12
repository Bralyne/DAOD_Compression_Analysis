
# Python setup


Use this setup if you are working on the ternminal a **local machine** (Laptop, MacBook, etc.) and you already have the CSV files generated from a previous collection run. 

>  **Note:** You cannot run the `run_collect` mode in this setup as it requires the ATLAS Athena framework.

## 1. Install Dependencies

Navigate to the root of the project and install the requirements:

```
pip install --user -r requirements.txt

```

## Analysis modes

```
-m daod_analysis.main --workspace ./workspaces --project lzma_level1 --mode fluctuation

```

```
-m daod_analysis.main --workspace ./workspaces --project lzma_level1 --mode plot

```

**Note: We recommnend you to read [View Athena Setup Guide](daod_analysis/setup/athena_setup.md) to understand the code above above and how the data collection and project structure work.**