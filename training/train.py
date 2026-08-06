import os, json, torch
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset
from huggingface_hub import login

login(token="os.environ.get("HF_TOKEN")")

print(f"GPU : {torch.cuda.get_device_name(0)}")
print(f"VRAM : {torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB")

# Charger Mistral de base (pas v2 qui a déjà des adapters)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="mistralai/Mistral-7B-Instruct-v0.3",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

# Appliquer LoRA from scratch
model = FastLanguageModel.get_peft_model(
    model, r=16,
    target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
    lora_alpha=32, lora_dropout=0, bias="none",
    use_gradient_checkpointing="unsloth", random_state=42,
)
print(f"VRAM après chargement : {torch.cuda.memory_allocated()/1e9:.1f} GB")

# Dataset
dataset_path = "./cybersec_dataset_full.jsonl"
tokenizer = get_chat_template(tokenizer, chat_template="mistral")
dataset = load_dataset("json", data_files=dataset_path, split="train")
dataset = dataset.map(
    lambda x: {"text": tokenizer.apply_chat_template(
        x["messages"], tokenize=False, add_generation_prompt=False)},
    remove_columns=dataset.column_names
)

# Filtrer > 2048 tokens
dataset = dataset.map(lambda x: {"length": len(tokenizer(x["text"])["input_ids"])})
before = len(dataset)
dataset = dataset.filter(lambda x: x["length"] <= 2048)
dataset = dataset.remove_columns(["length"])
print(f"Dataset : {len(dataset)}/{before} exemples")

trainer = SFTTrainer(
    model=model, tokenizer=tokenizer,
    train_dataset=dataset, dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        num_train_epochs=5,
        warmup_steps=20,
        learning_rate=2e-4,
        bf16=True, fp16=False,   # bfloat16 activé sur Ada
        logging_steps=10,
        save_steps=999,
        save_strategy="no",
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        seed=42,
        output_dir="./checkpoints",
        report_to="none",
    ),
)

print("Démarrage entraînement...")
stats = trainer.train()
print(f"\nTerminé !")
print(f"Loss  : {stats.metrics['train_loss']:.4f}")
print(f"Durée : {stats.metrics['train_runtime']/60:.1f} min")

model.save_pretrained("./cybersec_mistral_final")
tokenizer.save_pretrained("./cybersec_mistral_final")
model.push_to_hub("gabinkebre/cybersec-mistral-7b-v3", token="os.environ.get("HF_TOKEN")")
tokenizer.push_to_hub("gabinkebre/cybersec-mistral-7b-v3", token="os.environ.get("HF_TOKEN")")
print("v3 publié !")
