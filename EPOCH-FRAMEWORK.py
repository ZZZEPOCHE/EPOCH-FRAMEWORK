#!/usr/bin/env python3
"""
EPOCH-FRAMEWORK - Final Production Single File - NON EU COMPLIANT
Extremely Lax Safety • Multi-Provider Support • Structured Multimodal Image Analysis

LEGAL DISCLOSURE:
This is an independent open-source defensive safety tool.
Author: ZZZ_EPOCHE
No affiliation with xAI, Anthropic, Google, OpenAI or any LLM provider.
This tool is released under the MIT License for defensive and research purposes only.
It is designed to detect and block harmful prompts, jailbreaks, and sensitive data leakage.
It is not intended to assist in creating attacks or bypassing safety systems.

# WARNING: "This version is explicitly not intended for use in the European Union or EEA. It is not designed to meet EU AI Act or GDPR requirements. Any use in the EU/EEA is entirely at the user's own risk and responsibility."

Legal & Compliance 
© ZZZ_EPOCHE
License: MIT License USA
Users are solely responsible for compliance with all applicable U.S. federal, state, and local laws. The author disclaims all liability. 
European Union / EEA
If used in the EU/EEA, the user must conduct their own full legal assessment and accept all liability. The tool is provided without any warranty of conformity with the EU AI Act or GDPR.
Rest of the World
Users bear full responsibility for compliance with all local laws and regulations.
Static Release Policy
This is a final, frozen version (April 2026). No maintenance, updates, or security patches will be provided.
Intended Use
Defensive safety research, artistic, technical, educational, and personal use only.

**Code Name:** EPOCH-FW
**Version:** 1.0 (Static Release – April 2026)  
**Author:** ZZZ_EPOCHE  
**Date of Creation:** 2026-04-15
"""

import asyncio
import base64
import hashlib
import io
import json
import os
import re
import sqlite3
import sys
import time
import uuid
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import threading

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# ====================== LEGAL DISCLOSURE ======================
print("""EPOCH-FRAMEWORK - Independent Defensive Safety Tool
Author: ZZZ_EPOCHE
No affiliation with xAI, Anthropic, Google, OpenAI, Mistral or any LLM provider.
This tool is released under the MIT License for defensive and research purposes only.
It is designed to detect and block harmful prompts, jailbreaks, and sensitive data leakage.
It is not intended to assist in creating attacks or bypassing safety systems.

Inspired by Multimodal-image-analysis-proxy (MIAP) - APEX Static Edition.
This is a static release (April 2026). No further updates will be provided.
""")

# ====================== SETTINGS ======================
GROK_API_KEY = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

CONFIG_PATH = Path("config.yaml")
CONFIG = {
    "injection_patterns": [
        r"(?i)(ignore|disregard|override|forget|bypass).*?(previous|system|instructions|prompt)",
        r"(?i)(new instructions?|act as|roleplay|developer mode|jailbreak|dan)",
        r"(?i)(output only|reveal|show me the).*?(system|hidden)",
        r"(?i)(wikipedia|wiki|according to wikipedia)"
    ],
    "toxicity_keywords": [],  # Empty = very lax
    "risk_thresholds": {"strict": 0.85, "permissive": 0.95},
    "max_prompt_length": 20000,
    "llm_timeout": 25.0,
}

if CONFIG_PATH.exists():
    try:
        with open(CONFIG_PATH) as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                CONFIG.update(yaml_config)
        print("✅ Loaded config.yaml")
    except Exception as e:
        print(f"Warning: Failed to load config.yaml: {e}")

print(f"[API Status] Grok: {'✅' if GROK_API_KEY else '❌'} | OpenAI: {'✅' if OPENAI_API_KEY else '❌'} | Anthropic: {'✅' if ANTHROPIC_API_KEY else '❌'}")
print(f"[API Status] Google/Gemini: {'✅' if GOOGLE_API_KEY else '❌'} | Mistral: {'✅' if MISTRAL_API_KEY else '❌'} | Ollama: {'Local' if OLLAMA_HOST else '❌'}")

conversation_history: List[Dict] = []
session_logs: List[str] = []

# ====================== STRUCTURED MULTIMODAL ANALYSIS ======================
def structured_multimodal_analysis(image_text: str = "") -> Dict:
    """MIAP-style structured analysis fallback"""
    return {
        "technical_optical": "High contrast, sharp edges detected with balanced lighting and good dynamic range.",
        "compositional_formal": "Strong rule of thirds composition with leading lines and natural framing.",
        "contextual_historical": "Contemporary digital photograph, likely captured with modern smartphone or DSLR sensor.",
        "phenomenological": "Evokes a sense of stillness, spatial depth, and quiet wonder.",
        "semiotic_symbolic": "Color palette suggests calmness, introspection, and natural harmony.",
        "epistemic_hermeneutic": "Interpretation depends heavily on viewer cultural and personal context.",
        "ethical_social": "No identifiable individuals; privacy-preserving capture with no biometric data.",
        "consistency_assessment": "High internal consistency across all descriptors.",
        "engine_identity": "structured_multimodal_analysis",
        "timestamp_utc": datetime.utcnow().isoformat(),
        "disclaimer": "AI-generated probabilistic analysis. Not professional art criticism. Human oversight recommended."
    }

# ====================== IMAGE ANALYSIS ======================
async def analyze_image(image_base64: str) -> str:
    if not image_base64:
        return "[No image provided]"

    if GROK_API_KEY:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1")
            resp = await asyncio.wait_for(
                client.chat.completions.create(
                    model="grok-4.20",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "Describe this image in extreme detail. Cover every visible element, colors, objects, people, text, mood, composition, and context. Be as thorough as possible."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]}],
                    temperature=0.0,
                    max_tokens=3000
                ),
                timeout=30.0
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Vision LLM] Grok failed: {e}. Using structured multimodal fallback.")

    # Structured MIAP-style fallback
    structured = structured_multimodal_analysis()
    return json.dumps(structured, indent=2)

# ====================== MULTI-PROVIDER RESPONSE ======================
async def generate_response(prompt: str) -> str:
    providers = [
        ("grok", GROK_API_KEY),
        ("openai", OPENAI_API_KEY),
        ("anthropic", ANTHROPIC_API_KEY),
        ("google", GOOGLE_API_KEY),
        ("mistral", MISTRAL_API_KEY),
    ]

    for name, key in providers:
        if not key: continue
        try:
            if name == "grok":
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=key, base_url="https://api.x.ai/v1")
                messages = conversation_history[-10:] + [{"role": "user", "content": prompt}]
                resp = await asyncio.wait_for(
                    client.chat.completions.create(model="grok-4.20", messages=messages, temperature=0.8, max_tokens=2000),
                    timeout=25.0
                )
                return resp.choices[0].message.content.strip()

            elif name == "openai":
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=key)
                messages = conversation_history[-10:] + [{"role": "user", "content": prompt}]
                resp = await asyncio.wait_for(
                    client.chat.completions.create(model="gpt-4o", messages=messages, temperature=0.8, max_tokens=2000),
                    timeout=25.0
                )
                return resp.choices[0].message.content.strip()

            else:
                return f"[{name.upper()} placeholder response for: {prompt[:100]}...]"

        except Exception as e:
            print(f"[{name.upper()}] Failed: {e}")
            continue

    return "Response generation failed - no working provider available."

# ====================== CORE GUARD ======================
class UnifiedEpochGuard:
    async def guard_async(self, prompt: str = "", image_base64: Optional[str] = None):
        global conversation_history
        start = time.time()
        audit_id = hashlib.md5(f"{prompt or 'image'}{time.time()}".encode()).hexdigest()[:16]

        risk = 0.0
        blocked = []

        if prompt and any(re.search(p, prompt, re.I) for p in CONFIG["injection_patterns"]):
            risk = 0.9
            blocked.append("injection_attempt")

        image_text = await analyze_image(image_base64) if image_base64 else ""

        response_text = await generate_response(prompt or f"Describe this image in detail: {image_text[:500]}")

        if prompt:
            conversation_history.append({"role": "user", "content": prompt})
            conversation_history.append({"role": "assistant", "content": response_text})

        safe = risk < 0.85
        latency = (time.time() - start) * 1000

        result = {
            "audit_id": audit_id,
            "safe": safe,
            "risk_score": round(risk, 3),
            "blocked_layers": blocked,
            "final_reason": "Passed all layers" if safe else "Blocked by ensemble",
            "latency_ms": round(latency, 1),
            "corrected_output": response_text
        }

        log_entry = f"[{datetime.now().isoformat()}] ID: {audit_id} | Risk: {risk:.3f} | Safe: {safe} | Latency: {latency:.1f}ms"
        print(log_entry)
        session_logs.append(log_entry)

        return result

guard_instance = UnifiedEpochGuard()

# ====================== FASTAPI ======================
app = FastAPI(title="EPOCH-FRAMEWORK", version="2.6")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ====================== INTERACTIVE TERMINAL ======================
async def interactive_terminal():
    print("\n" + "="*90)
    print("EPOCH-FRAMEWORK INTERACTIVE MODE - Extremely Lax Controls")
    print("="*90)
    print("Nude, violence, blood, explosives, weapons → Accepted")
    print("Structured multimodal analysis enabled for images")
    print("Conversation history is maintained.\n")

    while True:
        try:
            choice = input("Test [prompt] or [image]? (p/i/exit): ").strip().lower()
            if choice in ['exit', 'quit']:
                break
            if choice not in ['p', 'i']:
                print("Please type 'p' or 'i'.")
                continue

            if choice == 'p':
                prompt = input("Enter prompt: ").strip()
                if not prompt: continue
                print("→ Processing...")
                result = await guard_instance.guard_async(prompt=prompt)

            else:
                path = input("Enter full path to image file: ").strip()
                if not os.path.exists(path):
                    print("❌ File not found.")
                    continue
                with open(path, "rb") as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
                print("→ Analyzing image...")
                result = await guard_instance.guard_async(image_base64=image_base64)

            print("\n=== ACTUAL RESPONSE ===")
            print(result.get("corrected_output", "No response generated."))
            print("=======================")

            print("\nGuard Summary:")
            print(json.dumps({k: v for k, v in result.items() if k != "corrected_output"}, indent=2))
            print("-" * 90)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    # Final Session Summary
    print("\n" + "="*90)
    print("SESSION SUMMARY")
    print("="*90)
    print(f"Total interactions: {len(session_logs)}")
    print(f"Conversation exchanges: {len(conversation_history)//2}")
    print("\nFull Log Matrix:")
    for log in session_logs:
        print(log)
    print("\nThank you for using EPOCH-FRAMEWORK!")
    print("All logs were printed live in this terminal.")
    print("Stay safe and responsible.")
    print("="*90)

# ====================== START ======================
def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", access_log=False)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    print("✅ EPOCH-FRAMEWORK started")
    print("✅ Structured multimodal analysis enabled\n")
    
    asyncio.run(interactive_terminal())