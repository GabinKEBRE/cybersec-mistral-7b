import os, torch
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template
from peft import PeftModel
import uvicorn, time

app = FastAPI(title="CyberSec Mistral API", version="3.0")

app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

security = HTTPBearer()

VALID_KEYS = {
    "demo-key-gabin-2024": {"plan": "demo", "limit": 100},
    "client-pro-001":      {"plan": "pro",  "limit": 1000},
}

usage = {}

def verify_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    key = credentials.credentials
    if key not in VALID_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    usage[key] = usage.get(key, 0) + 1
    if usage[key] > VALID_KEYS[key]["limit"]:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return key

# Chargement modèle
print("Chargement modèle...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="mistralai/Mistral-7B-Instruct-v0.3",
    max_seq_length=2048, dtype=None, load_in_4bit=True,
)
model = PeftModel.from_pretrained(model, "./cybersec_mistral_final")
FastLanguageModel.for_inference(model)
tokenizer = get_chat_template(tokenizer, chat_template="mistral")
print("Modèle prêt !")

class QueryRequest(BaseModel):
    question: str
    max_tokens: int = 500
    temperature: float = 0.7

@app.get("/")
def root():
    return {"status": "online", "model": "cybersec-mistral-7b-v4", "version": "3.0"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "gpu": torch.cuda.get_device_name(0),
        "vram_used_gb": round(torch.cuda.memory_allocated()/1e9, 2),
        "vram_free_gb": round((torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated())/1e9, 2),
    }

@app.post("/v1/query")
def query(req: QueryRequest, api_key: str = Depends(verify_key)):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question vide")

    start = time.time()
    messages = [{"role": "user", "content": req.question}]
    inputs = tokenizer.apply_chat_template(
        messages, tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to("cuda")

    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs,
            max_new_tokens=req.max_tokens,
            temperature=req.temperature,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.1,
        )

    answer = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)

    return {
        "answer": answer,
        "model": "cybersec-mistral-7b-v4",
        "usage": {
            "input_tokens": inputs.shape[1],
            "output_tokens": outputs.shape[1] - inputs.shape[1],
            "latency_ms": round((time.time()-start)*1000)
        }
    }

@app.get("/v1/usage")
def get_usage(api_key: str = Depends(verify_key)):
    return {
        "key": api_key,
        "plan": VALID_KEYS[api_key]["plan"],
        "requests_used": usage.get(api_key, 0),
        "requests_limit": VALID_KEYS[api_key]["limit"],
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)
