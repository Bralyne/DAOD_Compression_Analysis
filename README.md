# # ATLAS Derived Compression Analysis

This repository focuses on addressing the critical data challenges posed by the upcoming High-Luminosity LHC (HL-LHC) upgrade. With expected data volumes increasing by an order of magnitude, traditional storage and I/O methods must be optimized to ensure analysis scalability.


### Core Objectives

The project evaluates the transition from the traditional data storage format known as data format known as RNTuple within the ATLAS experiment. We specifically investigate the performance trade-offs of different lossless algorithms (ZSTD, LZ4 and Zlib) at different compression levels (1, 5 and 9) to replace the default LZMA.


### Technical Focus:

    - Compression Benchmarking: Comparative analysis of ZSTD,Zlib, LZMA and LZ4  with Rntuple against LZMA TTree to undestand their impact on ou stotorage footprint and I/O speed.

    - I/O Throughput: Focusing on Analysis Object Data (AOD) reading during derivation ; a high-intensity, multiprocessing workflow central to ATLAS production.

    - Read Througput: 
    
    - file size: 

By optimizing the data-handling pipeline, this work contributes to the global effort to prepare CERN’s computing infrastructure for the next generation of particle physics discovery.