# Quick Start: Fine-tune DeepSeek-V3

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Prepare Your Data

### Option A: Use the example data
```bash
# Already provided in data/example_training_data.jsonl
```

### Option B: Convert your own data
```bash
# For Q&A format
python data/prepare_data.py --input your_data.json --output data/training_data.jsonl --format qa --split

# For document format
python data/prepare_data.py --input docs.json --output data/training_data.jsonl --format doc --split
```

### Data Format
```json
{
  "instruction": "Your question or task",
  "input": "Optional context or input data",
  "output": "Expected response or answer"
}
```

## Step 3: Configure Training

Edit `train.py` to adjust:
- `MODEL_NAME`: Path to DeepSeek-V3 model
- `DATA_PATH`: Your training data path
- `LORA_CONFIG`: LoRA hyperparameters
- `TRAINING_CONFIG`: Training settings

## Step 4: Start Training

### Single GPU (not recommended for V3)
```bash
python train.py
```

### Multi-GPU with Accelerate
```bash
accelerate launch --num_processes=4 train.py
```

### Multi-GPU with DeepSpeed (Recommended)
```bash
deepspeed --num_gpus=8 train.py --deepspeed deepspeed_config.json
```

## Step 5: Monitor Training

```bash
# Monitor GPU usage
watch -n 1 nvidia-smi

# View training logs
tail -f logs/training.log
```

## Step 6: Test Your Model

```bash
python inference.py
```

## Tips

1. **Start Small**: Test with DeepSeek-Coder-V2 first before V3
2. **Use LoRA**: Much more efficient than full fine-tuning
3. **Batch Size**: Adjust based on GPU memory
4. **Learning Rate**: 2e-4 works well for most cases
5. **Save Frequently**: Set `save_steps` to avoid losing progress

## Common Issues

**Out of Memory:**
- Reduce `per_device_train_batch_size`
- Increase `gradient_accumulation_steps`
- Enable `gradient_checkpointing`

**Slow Training:**
- Increase `per_device_train_batch_size`
- Use more GPUs
- Reduce `max_length` for tokenization

**Poor Results:**
- Check data quality
- Increase training epochs
- Adjust learning rate
- Try higher LoRA rank
