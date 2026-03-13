
# Python Setup

Use this setup if you are working on the terminal of a **local machine** (Laptop, MacBook, etc.) and you already have the CSV files generated from a previous collection run.

### Required Data Files
To use all analysis modes, you need two specific CSV files in your workspace:

* **File Sizes (`file_size.csv`):** A CSV containing file sizes in GB. The header must include `Algo`, `AOD_type`, and columns formatted as `{Events}events_level{N}` (e.g., `7000events_level1`).

* **Performance Metrics (`All_Compression_Algo_metrics.csv`):** A CSV containing execution metrics. Please refer to the version provided in the `workspaces/` folder to ensure your headers match the expected format.


### Using Pre-generated Data

The repository includes existing data generated during our analysis. You can explore the tool immediately without running new ATLAS Athena collection jobs or providing your own CSVs:

* **Workspace Data:** The `workspaces/` folder contains pre-existing `All_Compression_Algo_metrics.csv` and `file_size.csv`.
* **Quick Start:** Simply clone the repository and run any of the **Analysis Modes**. The tool will automatically use the provided CSVs in the workspace to generate reports.

> [!IMPORTANT]
> **Note:** You cannot run the **Collection Mode** in this setup as it requires the ATLAS Athena framework. To collect new data, please refer to the [Athena Setup Guide](daod_analysis/setup/athena_setup.md).

---



## Install Dependencies

Navigate to the root of the project and install the environment using **Poetry** or **Pip**:

```
poetry install

or 


pip install --user -r requirements.txt


```

## Analysis modes

Run these commands from the project root. If you are using Poetry, add prefix the commands with poetry run.


```
python3 -m daod_analysis.main --workspace ./workspaces  --mode fluctuation


```


```

python3 -m daod_analysis.main --workspace ./workspaces --mode plot --metrics

```

```
python3 -m daod_analysis.main --workspace ./workspaces --mode plot --csv_path path/to/your/file_size.csv

```

```
python3 -m daod_analysis.main --workspace ./workspaces --mode plot --gain_loss

```


```
python3 -m daod_analysis.main --workspace ./workspaces --mode plot --impact

```

**Note: We recommnend you to read [View Athena Setup Guide](daod_analysis/setup/athena_setup.md) to understand the code above above and how the data collection and project structure work.**