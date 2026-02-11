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

This project evaluates the performance impact of switching from the legacy TTree storage format (using LZMA compression) to the next generation RNTuple data format. While LZMA is the current ATLAS default for AOD files, its high CPU overhead poses challenges for HL-LHC data rates. We investigate whether RNTuple, combined with alternative lossless algorithms (such as ZSTD, Zlib and LZ4), can provide measurable benefits for DAOD (Derived Analysis Object Data) workflows. Given that major ATLAS production tools now support RNTuple, this study aims to quantify potential gains in I/O throughput and storage efficiency for end user analysis.

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

$$Read_Throughput = \frac{Events_{total}}{Max_CObjr}$$

* **Job throughput:** Total number of events processed divided by the total loop time, representing events processed per millisecond.

$$Job_Throughput = \frac{Events_{total}}{Loop_time}$$

* **Memory usage:** Tracked from the `prmon.summary.Derivation.json` file generated during the run.

<br>

