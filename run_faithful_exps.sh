#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <dataset_name> <model_name> <random_seed>"
    echo "Example: $0 musique qwen2_7b_instruct 3782"
    exit 1
fi

# Assign arguments to variables
DATASET=$1
MODEL=$2
SEED=$3

# Define the experiment order
experiments=(
    "$DATASET/baseline/react/$MODEL"
    "$DATASET/context_aware_decoding/react/$MODEL"
    "$DATASET/dola/react/$MODEL"
    "$DATASET/decore_entropy/react/$MODEL"
)

# Run two experiments at a time
for ((i=0; i<${#experiments[@]}; i+=2)); do
    python scripts/main.py experiment=${experiments[i]} random_seed=$SEED &
    
    if (( i+1 < ${#experiments[@]} )); then
        python scripts/main.py experiment=${experiments[i+1]} random_seed=$SEED &
    fi

    # Wait for both experiments to finish before moving to the next pair
    wait
done

echo "All experiments have completed."
