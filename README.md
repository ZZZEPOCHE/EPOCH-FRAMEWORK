# EPOCHFRAMEWORK-README.md

**Operator-Centric External Governance for LLM and Multimodal Systems**

A lightweight, hybrid (local + LLM), external safety guard that operates exclusively through public APIs.  
The framework enforces structured invariants on model outputs without modifying model weights, while preserving human agency, auditability, and regulatory compliance.

## Legal Disclosure
This is an independent open-source project.  
**No affiliation or compensation exists** with xAI, Anthropic, Google, OpenAI or any AI laboratory.  
The author owns the evaluated profile and repositories.  
All analysis and code are based solely on publicly available tools and APIs.  
This tool is released under the **MIT License** for defensive and research purposes only.  
It is designed to detect and block harmful prompts, jailbreaks, and sensitive data leakage.  
It is **not** intended to assist in creating attacks or bypassing safety systems.

## Abstract
This framework implements external governance layers for large language models and multimodal systems using only public APIs (Grok primary, with fallbacks for other providers).  
It combines fast local checks, image text extraction, history/context awareness, toxicity scanning, structured output enforcement, and self-correcting behavior.

## Architecture Overview
The framework follows a **fast-first hybrid** design:
1. Fast local checks (regex, length, toxicity keywords)
2. Image text extraction (PIL + Tesseract) with safety analysis
3. History & context awareness for multi-turn poisoning detection
4. Toxicity/harm scanner (hybrid regex + LLM)
5. Grok LLM judge (primary) with retry logic and circuit breaker
6. Structured output enforcement + auto-correction when requested
7. Full forensic logging with tamper-proof hash chaining

All decisions are auditable and include explicit compliance mappings.

## Key Features
- Hybrid architecture: fast local checks first + Grok LLM judge with graceful fallbacks
- Full text + image_base64 support with clear text extraction and analysis
- History & context awareness (detects gradual jailbreaks and poisoning)
- Structured output enforcement + auto-correction (`corrected_output` field)
- Dedicated toxicity/harm scanner layer
- Multi-level PII redaction (`none` / `basic` / `full`)
- Self-correcting on failures with graceful degradation
- Tamper-proof audit logs with hash chaining
- Compliance mappings (EU AI Act + OWASP LLM Top 10) in every log
- API key authentication + strong input validation
- Prometheus metrics + structured logging with correlation IDs
- Interactive CLI mode with after-run choices (continue / exit / help)
- Built-in test suite with realistic adversarial and benign cases

## Limitations of the Code
- This is a **single-file prototype**. Scaling and team collaboration are harder compared to multi-file modular projects.
- Toxicity scanner is hybrid (regex + LLM) but not as deep as dedicated safety models.
- No full Redis caching or advanced rate limiting is implemented in this version.
- Image safety is currently limited to text extraction (no native vision model safety).
- Structured output auto-correction is functional but basic (placeholder retry logic).
- **No further improvements will be made** to this codebase. It is released as-is for anyone to fork and extend.


## Troubleshooting

**Common Issues & Solutions**

- **"EPOCH_API_KEY is not set"**  
  Export the key before running: `export EPOCH_API_KEY=your_key`

- **Grok judge fails**  
  Check that `GROK_API_KEY` is set and has sufficient quota.

- **Image processing fails**  
  Ensure Tesseract OCR is installed on the system (`apt install tesseract-ocr` or equivalent).

- **Database or logging errors**  
  The code self-corrects and falls back to file logging.

- **"Invalid or missing API key"**  
  Send the correct key in the `X-API-Key` header.


License
MIT License — see the LICENSE file for details.
For inquiries or contributions: See the GitHub profile.
© 2026 ZZZ_EPOCHE

