#!/bin/bash

# Arguments from Python
input_data_dir="$1"
output_dir="$2"
proc="${3:-8}"
cores="${4:-8}"
runs="${5:-5}"
max_events="${6:-7000}"

# Paths and Config
PARSER_DIR="$(pwd)/parser"
log_name="log.Derivation"

echo "------------------------------------------------"
echo "Target Folder: $output_dir"
echo "Config: Proc=$proc, Cores=$cores, Events=$max_events"
echo "------------------------------------------------"

# Find the AOD file
input_aod=$(find "$input_data_dir" -name "*.pool.root" | head -n 1)
if [ -z "$input_aod" ]; then
    echo " Error: No .pool.root file found in $input_data_dir"
    exit 1
fi

# Move to the project folder to contain logs and temp runs
cd "$output_dir" || exit 1

for i in $(seq -f "%02g" 1 "$runs"); do
  rundir="run_$i"
  echo "==> Starting iteration $i"

  mkdir -p "$rundir" && cd "$rundir" || exit 1

  export ATHENA_PROC_NUMBER="$proc"
  export ATHENA_CORE_NUMBER="$cores"

  deriv_args=(
    --inputAODFile "$input_aod"
    --athenaMPMergeTargetSize "DAOD_*:0"
    --multiprocess "True"
    --postInclude "default:AthenaServices.TransformUtils.ExecCondAlgsAtPreFork"
    --preExec "all:flags.Trigger.doEDMVersionConversion = False;"
    --sharedWriter "True"
    --formats "PHYS"
    --outputDAODFile "DAOD.pool.root"
    --multithreadedFileValidation "True"
    --CA "all:True"
    --perfmon "fullmonmt"
    --maxEvents "$max_events"
  )

  # Execute Athena
  Derivation_tf.py "${deriv_args[@]}" > __log_derivation.txt 2>&1
  

  cd .. # Back to project folder

  # Call Parsers (Passing the project folder as an argument)
  python3 "$PARSER_DIR/parse_derivation_mp_metrics.py" "$i" "$proc" "$cores" "$output_dir"
  python3 "$PARSER_DIR/compute_overall_job_metrics.py" "$i" "$proc" "$cores" "$output_dir"

  # Cleanup
  if [ "$i" -lt "$runs" ]; then
    rm -rf "$rundir"
    echo "Sleeping 60s..."
    sleep 60
  fi
done

echo " All $runs runs completed successfully."