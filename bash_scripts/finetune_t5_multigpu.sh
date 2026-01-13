#!/bin/bash
# Multi-GPU training script for s2s_hf_transformers.py
# Uses GPUs 0 and 1 via accelerate launch
#
# Usage:
#   bash bash_scripts/finetune_t5_multigpu.sh
#
# Or with custom parameters:
#   DATA_FPATH=path/to/data.pkl MODEL=t5-large bash bash_scripts/finetune_t5_multigpu.sh
#
# Prerequisites:
#   - accelerate >= 0.20.1 installed
#   - CUDA available on GPUs 0 and 1
export PYTHONPATH=$(pwd):$PYTHONPATH
set -e

# Get script directory for relative paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Configuration (can be overridden via environment variables)
DATA_FPATH="${DATA_FPATH:-data/holdout_split_batch12_perm/symbolic_batch12_perm_utt_0.2_0.pkl}"
MODEL="${MODEL:-t5-base}"
MODEL_DPATH="${MODEL_DPATH:-model}"

# Specify which GPUs to use (0 and 1)
export CUDA_VISIBLE_DEVICES=0,1

echo "=========================================="
echo "Multi-GPU Training Configuration"
echo "=========================================="
echo "GPUs: $CUDA_VISIBLE_DEVICES"
echo "Model: $MODEL"
echo "Data: $DATA_FPATH"
echo "Output: $MODEL_DPATH"
echo "Project Dir: $PROJECT_DIR"
echo "=========================================="

cd "$PROJECT_DIR"

# Option 1: Use accelerate config file (recommended for reproducibility)
if [ -f "accelerate_config.yaml" ]; then
    echo "Using accelerate_config.yaml"
    accelerate launch \
        --config_file accelerate_config.yaml \
        models/s2s_hf_transformers.py \
        --data_fpath "$DATA_FPATH" \
        --model "$MODEL" \
        --model_dpath "$MODEL_DPATH"
else
    # Option 2: Specify parameters directly
    echo "Using command-line parameters"
    accelerate launch \
        --num_processes=2 \
        --mixed_precision=no \
        models/s2s_hf_transformers.py \
        --data_fpath "$DATA_FPATH" \
        --model "$MODEL" \
        --model_dpath "$MODEL_DPATH"
fi

echo "=========================================="
echo "Training complete!"
echo "=========================================="
