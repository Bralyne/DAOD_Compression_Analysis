
# ATLAS Athena Setup (Full Pipeline)

This setup is required if you need to run the Collection mode (run_collect). This node executes Athena derivation jobs  and requires an active ATLAS software environment. you will learn step by step how the analysis is made. use this setup if you wnat to run the full pipeline from the derivation job to the analyis plots.

## 1. Environment Activation

After cloning the reprository in your terminal and chamnge directory to DAOD_Compression_Analysis, log into a machine with ATLAS software access (e.g., LXPLUS, aiatlasbm) and run:

```
setupATLAS

asetup Athena,main--dev3LCG,2026-02-22T2100

```

## 2. Input Data Naming Convention

To use this pipeline, your input .pool.root files must follow one of this naming pattern:

```

    ALGO_TYPE_events_levelN.AOD.pool.root
```

Example: lzma_ttree_7000events.level1.AOD.pool.root


## 3. Running Data Collection

The run_collect mode is highly configurable. For a statistically insightful analysis, we recommend processing at least 7000 events per core, though you can use fewer for quick testing.

The run_collect mode triggers the derivation jobs. The script automatically identifies the algorithm from your filename and locates the matching project directory (LZMA, ZSTD, ZLIB, or LZ4) within the workspace folder to save the results.

```

python3 -m daod_analysis.main --mode run_collect --workspace ./workspaces --data_path /path/to/your pool.root --runs 5 --cores 8 --maxevents 7000

```

This command runs the derivation job **5 times** using **8 cores**, **1 processor**, and **100 events**.

If the run number, core count, processor count, or maximum number of events are not specified, the following default values are used:

* **8 cores**
* **5 runs**
* **1 processor**
* **7000 events**
.



**Tip: For reliable Fluctuation mode results, we recommend at least --runs 5. This gives you enough data points to calculate a meaningful Standard Deviation.**


## 3.Analysis modes

Once the collection is finished and the CSV files are generated, you can run the analysis nodes:


### Flutuaction mode:

The fluctuation mode acts as the quality control for the compression results. In high-performance computing, execution metrics can vary slightly between runs due to background noise on the machine or shared storage speeds/cluster. This mode determines if the results are stable and reproducible.

below is how to run the flutuaction mode:

```
python3 -m daod_analysis.main --workspace ./workspaces  --mode fluctuation


```

When running ```--mode fluctuation```, the following steps are performed:

    - Merge: It scans all algorithm subdirectories (LZMA, ZSTD, LZ4 and ZLIB) and merges every individual test into one master file: All_Compression_Algo_metrics.csv.

    - Statistical grouping: It groups identical test configurations (same Algo, Level, Cores, AODtype and Processor) and calculates the Mean and Standard Deviation for every performance metric.

    - Stability Calculation: It calculates the Percentage Fluctuation using the Coefficient of Variation:
    
    $Fluctuation % =\frac{Standard Deviation}{Mean}×100$
    
After the analysis, the mode will also generate a global_fluctuation_report.csv containing the flutuaction values.


### Clean mode:

To ensure that final plots are not skewed by random machine fluctuations (system noise, network lag, etc.), the framework includes a Clean Mode which acts as a quality filter for the benchmarks.

The clean function checks for stability (<5% fluctuation) across five key metrics:

    - Job Throughput (CPU speed)

    -  Read Throughput (I/O speed)

    - RSS Memory (Resident Set Size memory)

    -  VMem (Virtual Memory)
    
    - PSS (Proportional Set Size memory)
    
If a configuration is unstable, the script identifies the worst runs (the rows furthest from the median across all metrics) and removes them one by one.

Example: If you have 6 runs and the fluctuation is above 5%, the mode will check if removing a single "bad" row stabilizes the data. If not, it will try removing a second or third row and so on. iIf the rows vary so much that no combination of at least 2 runs is stable, the clean mode will delete that configuration entirely from the master file. It will then print a message instructing you to rerun that specific configuration to ensure your final analysis is based on reliable data.


When running the clean mode, you will see the following status messages in your terminal:

    -   [+] Stabilized Algo_Type_L#: Kept 4/5 runs. Meaning: One run was an outlier. It was removed, and the remaining 4 are consistent and safe to plot.

    -  SUCCESS: All configurations are stable. Meaning: Your data is high-quality. No outliers were found, and the machine performance was consistent.

    - CRITICAL INSTABILITY - RERUN REQUIRED Meaning: The data for this specific setup was so noisy that even removing outliers couldn't fix it. These rows have been deleted from the Master CSV. You must rerun these specific configurations before plotting.
    
The clean mode should be executed after the fluctuation analysis:

```
python3 -m daod_analysis.main --workspace ./workspaces --mode clean

```

### Plot mode

The tool provides three types of visual analysis: Performance Metrics (Scaling trends and bar plots), File Size Comparison, and Metric Gain/Loss analysis.


**Performance Metrics plots**

To generate reports for Throughput, RSS, VMem, and PSS, run:

```

python3 -m daod_analysis.main --workspace ./workspaces --mode plot --metrics

```

The tool will look for the master csv All_Compression_Algo_metrics.csv containing all  confgurations with their respective metrics. The output will be a pdf saved in  workspaces/plotting/Global_Compression_Report.pdf which contains line charts for scaling trends and bar charts for memory/throughput gains.


**File Size Comparison**
There are two options for generating file size reports. The tool is designed to find the unique event counts in the data automatically. 

    - Option A: Providing a CSV
Provide a CSV containing file sizes (in GB). The header must include Algo, AOD_type, and columns formatted as {Events}events_level{N}. Example Header: Algo, AOD_type, 7000events_level1, 7000events_level5, ...


```
python3 -m daod_analysis.main --workspace ./workspaces --mode plot --csv_path path/to/your/file_size.csv

```
    -Option B: Providing a directory
If a directory path is provided, the tool will scan for .pool.root files, calculate their physical sizes on disk, and generate the plot.

**Files must be named ALGO_TYPE_events_levelN.AOD.pool.root. Example: lzma_ttree_7000events.level1.AOD.pool.root*
    
```
python3 -m daod_analysis.main --workspace ./workspaces --mode plot --data_path path/to/your/aod_directory

```

An automatic CSV (All_File_Sizes.csv) will be generated in the plotting folder for your records, followed by the PDF report.

**loss/gain**

To visualize performance changes relative to the reference configuration (LZMA TTree L1), run:

```
python3 -m daod_analysis.main --workspace ./workspaces --mode plot --gain_loss

```


This generates performance_gain_loss.pdf and displays the percentage improvement or degradation for each algorithm and compression level across all core counts. 


**Impact of file size**

To analyze how file size gain/loss correlate with performance costs or benefits, run:

```
python3 -m daod_analysis.main --workspace ./workspaces --mode plot --impact

```

it will generate size_impact_analysis.pdf. the plots in the pdf utilizes a 4-quadrant scatter plot to categorize configurations ("Smaller & Faster", "Smaller & Slower", Larger & Faster, Larger & Slower).