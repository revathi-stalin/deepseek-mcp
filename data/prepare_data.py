"""
Data preparation script for DeepSeek-V3 fine-tuning
Converts various data formats into training-ready JSONL format
"""

import json
import argparse
from pathlib import Path


def prepare_qa_format(data_file, output_file):
    """Convert Q&A format to instruction format"""
    examples = []
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        example = {
            "instruction": item.get("question", item.get("instruction", "")),
            "input": item.get("context", ""),
            "output": item.get("answer", item.get("response", item.get("output", "")))
        }
        examples.append(example)

    with open(output_file, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    print(f"Converted {len(examples)} examples to {output_file}")


def prepare_document_format(data_file, output_file):
    """Convert document format to instruction format"""
    examples = []
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        example = {
            "instruction": f"Summarize and explain: {item.get('title', '')}",
            "input": item.get("content", "")[:2000],  # Truncate long content
            "output": item.get("summary", item.get("explanation", ""))
        }
        examples.append(example)

    with open(output_file, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    print(f"Converted {len(examples)} documents to {output_file}")


def prepare_conversation_format(data_file, output_file):
    """Convert conversation format to instruction format"""
    examples = []
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for conv in data:
        messages = conv.get("messages", [])
        for i in range(0, len(messages) - 1, 2):
            if i + 1 < len(messages):
                example = {
                    "instruction": messages[i].get("content", ""),
                    "input": "",
                    "output": messages[i + 1].get("content", "")
                }
                examples.append(example)

    with open(output_file, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    print(f"Converted {len(examples)} conversation turns to {output_file}")


def split_data(input_file, train_ratio=0.9):
    """Split data into train and validation sets"""
    examples = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            examples.append(json.loads(line))

    split_idx = int(len(examples) * train_ratio)

    train_file = input_file.replace('.jsonl', '_train.jsonl')
    val_file = input_file.replace('.jsonl', '_val.jsonl')

    with open(train_file, 'w', encoding='utf-8') as f:
        for example in examples[:split_idx]:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    with open(val_file, 'w', encoding='utf-8') as f:
        for example in examples[split_idx:]:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    print(f"Split data: {len(examples[:split_idx])} train, {len(examples[split_idx:])} validation")


def main():
    parser = argparse.ArgumentParser(description="Prepare data for DeepSeek fine-tuning")
    parser.add_argument("--input", type=str, required=True, help="Input data file")
    parser.add_argument("--output", type=str, required=True, help="Output JSONL file")
    parser.add_argument("--format", type=str, choices=["qa", "doc", "conv"],
                        default="qa", help="Input data format")
    parser.add_argument("--split", action="store_true", help="Split into train/val")

    args = parser.parse_args()

    if args.format == "qa":
        prepare_qa_format(args.input, args.output)
    elif args.format == "doc":
        prepare_document_format(args.input, args.output)
    elif args.format == "conv":
        prepare_conversation_format(args.input, args.output)

    if args.split:
        split_data(args.output)


if __name__ == "__main__":
    main()
