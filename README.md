# ATLAS DAOD Lossless Compression Analysis

This repository contains the framework and scripts for evaluating lossless compression performance on ATLAS Derived Analysis Object Data (DAOD). The project focuses on benchmarking I/O throughput and storage efficiency using different compression algorithms like ZSTD, Zlib and LZ4 within the new data format known as RNTuple.

<br>


## Project Overview

As we prepare for the High-Luminosity LHC (HL-LHC), data volume is expected to increase by an order of magnitude. This study explores:

    -  Storage Optimization: Comparing LZMA (default) vs. ZSTD,LZ4 and Zlib.

    - I/O Throughput: Measuring the speed of the derivation process in multiprocessing workflows.

    - Physics Integrity: Validating that lossless compression maintains 100% data fidelity for analysis.
 
 <br>
 

## Core Objectives

This project evaluates the performance impact of switching from the legacy TTree storage format (using LZMA compression) to the next generation RNTuple data format.  We investigate whether RNTuple, combined with alternative lossless algorithms (such as ZSTD, Zlib and LZ4), can provide measurable benefits for DAOD (Derived Analysis Object Data) workflows. Given that major ATLAS production tools now support RNTuple, this study aims to quantify potential gains in I/O throughput and storage efficiency for end user analysis.

<br>


## Methodology

We execute the derivation job using different AOD input files at various compression levels (1, 5, and 9). 

     - Input Formats: ZSTD, ZLIB, and LZ4 at compression levels 1, 5, and 9 with Rntuple.

     - Reference Baseline: LZMA TTree (Level 1) is used as the standard against which all RNTuple configurations are compared.
    
Each input file has a different size, with **LZMA producing the smallest file** and **LZ4 the largest**. This repository provides a detailed analysis of how input file size I/O performance.

The derivation job outputs is **DAOD ZSTD level 5**, which is the default compression algorithm and level used in ATLAS DAOD studies. During the run, metrics are collected at the worker level.

<br>

### Multiprocessing Setup

The derivation job is **multiprocessing**, and we vary the number of cores to understand how core count affects performance metrics. Specifically, we run the job with 1, 4, 8, 16, and 32 cores. The number of workers scales with the number of cores, for example, 1 core runs 1 worker, 4 cores run 4 workers, and so on.



Each worker processes a subset of events. To ensure fair comparison across different core counts, the **maximum number of events is scaled with the number of cores**. For example, if we set 7,000 events for 1 core, then for 4 cores we set 28,000 events, so each worker processes approximately 7,000 events. This keeps the per worker load consistent across runs.

### Metrics Collection

We focus on **job-level metrics** rather than individual worker metrics. Key metrics include:

* **Read throughput:** Calculated as the total number of events processed divided by the slowest worker’s read time (the worker with the highest `CObjr` time). This gives the number of events read per millisecond.

$$Read_{Throughput } = \frac{Events_{total}}{Max_CObjr}$$

* **Job throughput:** Total number of events processed divided by the total loop time, representing events processed per millisecond.

$$Job_{Throughput} = \frac{Events_{total}}{Loop_time}$$

* **Memory usage:** Tracked from the `prmon.summary.Derivation.json` file generated during the run.

<br>

## Setup

This setup is built as a modular pipeline consisting of three primary modes. Each node represents a specific stage of the analysis process.

    - ** The Collection Mode (run_collect) :** This is the only part of the project that interacts directly with ATLAS software. It executes derivation jobs in the athena environment and automatically extracts real-time metrics like Throughput and Memory.
    
    - ** The Fluctuation Mode (fluctuation): ** this node ensures the data you collected is actually scientifically stable with no noise. It reads the raw results from the Collection Node and performs statistical validation by calculating the Mean, Standard Deviation percentage. If the results fluctuate by more than 5%, this node flags the data as unstable.
    
    - The Plotting Mode (plot): This turns numbers into insights. It shows the Visualization of the performance comparison between formats (RNTuple vs. TTree) and generates PDF/PNG graphs showing performance trends and error bars derived from the Fluctuation Node.
    


### Choose Your Setup
Because the Collection Mode has different requirements than the Analysis Nodes (flutuaction and plot), you have two options for setup:

    - Option 1: Full Pipeline (Athena Environment): Use this if you need to run the Collection Node to generate new data on LXPLUS or aiatlas machine. [View Athena Setup Guide](setup/athena_setup.md).
    
    - Option 2: Analysis Only (Standard Python): Use this if you already have CSV files(you can use the one provided in the workspace folder) and only want to run the Fluctuation and Plotting nodes on your local machine [View Python Setup Guide](setup/python_setup.md).