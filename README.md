[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20324436.svg)](https://doi.org/10.5281/zenodo.20324436)\
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\


# ATLAS DAOD Lossless Compression Analysis

This repository contains the framework and scripts for evaluating lossless compression performance on ATLAS Derived Analysis Object Data (DAOD). The project focuses on benchmarking I/O throughput and storage efficiency using different compression algorithms (including ZSTD, Zlib, LZ4) within the next-generation ROOT **RNTuple** data format.

<br>

## Project Overview

As we prepare for the High-Luminosity LHC (HL-LHC), data volume is expected to increase by an order of magnitude. This study explores:

* **Storage Optimization:** Comparing LZMA (default) vs. ZSTD,LZ4 and Zlib.
* **I/O Throughput:** Measuring the speed of the derivation process in multiprocessing workflows.
* **Physics Integrity:** Validating that lossless compression maintains 100% data fidelity for analysis.



<br>

## Core Objectives

This project evaluates the performance impact of switching from the legacy `TTree` storage format (using LZMA compression) to the next-generation `RNTuple` data format. We investigate whether RNTuple, combined with alternative lossless algorithms, can provide measurable benefits for DAOD (Derived Analysis Object Data) workflows. Given that major ATLAS production tools now support RNTuple, this study aims to quantify potential gains in I/O throughput and storage efficiency for end-user analysis.

<br>

## Methodology

We execute derivation jobs using different AOD input files across various compression levels (1, 5, and 9). 

* **Input Formats:** ZSTD, Zlib, and LZ4 at compression levels 1, 5, and 9 executing inside the RNTuple framework.
* **Reference Baseline:** LZMA TTree (Level 1) is utilized as the standard control baseline against which all RNTuple configurations are evaluated.

Each input file features a distinct physical footprint, with **LZMA producing the smallest file** and **LZ4 the largest**. This repository provides a detailed analysis of how input file size directly dictates resulting I/O performance.

The derivation job outputs are formatted to **DAOD ZSTD level 5**, matching the default configuration used in ATLAS DAOD optimization tracks. During execution, metrics are collected at the individual worker level.

<br>

### Multiprocessing Setup

The derivation job utilizes native **multiprocessing**. We systematically vary the core allocation count to analyze how scaling behavior affects performance metrics. 

Jobs are benchmarked using **1, 4, 8, 16, and 32 cores**. The number of active workers scales 1:1 with the allocated cores (e.g., 4 cores run 4 concurrent workers).

To ensure an unbiased comparison across changing core counts, the **maximum number of events scales proportionally with the core count**. For instance, if 1 core is assigned 7,000 events, a 4-core run is assigned 28,000 events. This guarantees that the workload per individual worker remains a uniform ~7,000 events across all parallel runs.

### Metrics Collection

Analysis focuses primarily on aggregated **job-level metrics** rather than isolated worker threads. Key figures of merit include:

* **Read Throughput:** Evaluated as the total events processed divided by the slowest worker’s read duration (the worker indicating the maximum `CObjr` latency window), yielding events processed per millisecond.

$$\text{Read Throughput} = \frac{\text{Events}_{\text{total}}}{\max(\text{CObjr})}$$

* **Job Throughput:** Total events processed divided by the comprehensive loop time, yielding net events processed per millisecond.

$$\text{Job Throughput} = \frac{\text{Events}_{\text{total}}}{\text{Loop}_{\text{time}}}$$

* **Memory Usage:** Extracted directly via the `prmon.summary.Derivation.json` tracking file generated during runtime execution.

<br>

## Environment Setup

This framework is built as a modular pipeline split into three execution nodes. 

1. **The Collection Mode (`run_collect`):** This is the exclusive segment of the project interacting directly with the ATLAS software stack. It executes derivation jobs inside the native Athena environment and automatically extracts real-time metrics (Throughput and Memory) into localized CSV configurations under `workspaces/project_name/raw_metrics.csv`.
2. **The Fluctuation Mode (`fluctuation`):** This data validation node ensures collected metrics are statistically stable and isolated from multi-tenant server noise. It ingests raw logs from the Collection Node, calculating the Mean and Standard Deviation percentage. If variations fluctuate beyond a 5% threshold, the data run is flagged as unstable. Validated metrics are appended to the master file: `workspaces/All_Compression_Algo_metrics.csv`.
3. **The Plotting Mode (`plot`):** It visualizes performance between formats (RNTuple vs. TTree), calculates relative efficiency gains, identifies file-size impacts, and automatically outputs a pdf report plots under `workspaces/plotting/`.

<br>

### Choose Your Infrastructure Path
Because the data collection environment carries different dependencies than the subsequent analysis engines, you can choose between two setup workflows:

* **Option 1: Full Pipeline (Athena Environment):** Required if you intend to execute the Collection Node to generate fresh metrics on LXPLUS or a dedicated `aiatlas` cluster machine. See the [Athena Setup Guide](setup/athena_setup.md).
* **Option 2: Analysis Only (Standard Python):** Ideal if you are analyzing existing CSV data points (such as the default one available in the workspace folder). This enables you to run the fluctuation and Plotting modules locally on a standard Python configuration. See the [Python Setup Guide](setup/python_setup.md).

<br>

## Serial Job Analysis

The foundational single-core serial job analysis for this study was presented at the **CHEP 2026 Conference**. 

Detailed single-core performance slides and the comprehensive conference overview are available via the [CERN Indico Agenda Page](https://indico.cern.ch/event/1471803/overview). see [Jupiter Notebook](workspaces/Analysis.ipynb) for details analysis.
