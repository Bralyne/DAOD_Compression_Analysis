
# ATLAS Athena Setup (Full Pipeline)

This setup is required if you need to run the Collection mode (run_collect). This node executes Athena derivation jobs  and requires an active ATLAS software environment.

## 1. Environment Activation

Log into a machine with ATLAS software access (e.g., LXPLUS, aiatlasbm) and run:

```
setupATLAS

asetup Athena,main--dev3LCG,latest

```

## 2. Initialize Your Project

You have two options to set up your directory structure. The pipeline expects your files to be located in:

```
workspaces/your_project_name/data/your_file.pool.root

```

### Option A: Automatic Creation (Recommended)

Use the create mode to generate the folder hierarchy automatically:

```
python3 -m daod_analysis.main --workspace ./workspaces --project my_project --mode create

```

Then, move your AOD file into the data folder:


```
mv /path/to/your/input.pool.root ./workspaces/my_project/data/

```

### Option B: Manual Setup

If you prefer to move an existing folder, ensure it follows this structure:


```
workspaces/
└── your_project_name/
    └── data/
        └── your_input_file.pool.root
        
```



## 3. Running Data Collection

The run_collect mode is highly configurable. For a statistically insightful analysis, we recommend processing at least 7000 events per core, though you can use fewer for quick testing.

```

python3 -m daod_analysis.main --workspace ./workspaces --project lzma_level1 --mode run_collect --runs 5 --cores 8 --proc 1 --maxevents 100

```
This command runs the derivation job **5 times** using **8 cores**, **1 processor**, and **100 events**.

If the run number, core count, processor count, or maximum number of events are not specified, the following default values are used:

* **8 cores**
* **5 runs**
* **1 processor**
* **7000 events**

The command instructs Python to execute the `lzma_level1` project located inside the `workspaces` directory.



**Pro-Tip: For reliable Fluctuation mode results, we recommend at least --runs 5. This gives the auditor enough data points to calculate a meaningful Standard Deviation.**


## 3.Analysis modes

Once the collection is finished and the CSV files are generated, you can run the analysis nodes:


### Flutuaction mode:
```
-m daod_analysis.main --workspace ./workspaces --project lzma_level1 --mode fluctuation

```

### Plot mode
```
-m daod_analysis.main --workspace ./workspaces --project lzma_level1 --mode plot

```