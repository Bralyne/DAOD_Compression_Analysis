#!/usr/bin/env athena.py
# Run arguments file auto-generated on Thu Feb 12 11:59:26 2026 by:
# JobTransform: Derivation
# Version: $Id: trfExe.py 792052 2017-01-13 13:36:51Z mavogel $
# Import runArgs class
from PyJobTransforms.trfJobOptions import RunArguments
runArgs = RunArguments()
runArgs.trfSubstepName = 'Derivation' 

runArgs.perfmon = 'fullmonmt'
runArgs.skimmingExpression = ''
runArgs.postInclude = ['AthenaServices.TransformUtils.ExecCondAlgsAtPreFork']
runArgs.preExec = ['flags.Trigger.doEDMVersionConversion = False;']
runArgs.formats = ['PHYS']
runArgs.multithreadedFileValidation = True
runArgs.maxEvents = 10

 # Input data
runArgs.inputAODFile = ['/eos/home-b/bkamgama/draft/Run_sleep_10000/Compression_QT/DAOD_Compression_Analysis/workspaces/zstd_level1/data/zstd_rntuple_level1.AOD.pool.root']
runArgs.inputAODFileType = 'AOD'
runArgs.inputAODFileNentries = 60000
runArgs.AODFileIO = 'input'

 # Output data
runArgs.outputDAOD_PHYSFile = 'DAOD_PHYS.DAOD.pool.root'
runArgs.outputDAOD_PHYSFileType = 'AOD'

 # Extra runargs

 # Extra runtime runargs

 # Literal runargs snippets

 # AthenaMP Options. nprocs = 2
runArgs.athenaMPWorkerTopDir = 'athenaMP-workers-Derivation-DerivationFramework'
runArgs.athenaMPOutputReportFile = 'athenaMP-outputs-Derivation-DerivationFramework'
runArgs.athenaMPEventOrdersFile = 'athenamp_eventorders.txt.Derivation'
runArgs.athenaMPCollectSubprocessLogs = True
runArgs.athenaMPStrategy = 'SharedQueue'
runArgs.sharedWriter = True

 # Executor flags
runArgs.totalExecutorSteps = 0

 # Threading flags
runArgs.nprocs = 2
runArgs.threads = 0
runArgs.concurrentEvents = 0

 # Import skeleton and execute it
from DerivationFrameworkConfiguration.DerivationSkeleton import fromRunArgs
fromRunArgs(runArgs)
