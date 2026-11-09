# NyayaSaathi — Kuku AI Generalist Assignment, Problem 2

A **conversational consumer-grievance companion for India** built with Python and Streamlit. Scope is intentionally narrow: retail / e-commerce purchases, defective goods, failed delivery and refunds. This is **not** a lawyer, a legal advice service, or legal representation.

## Run on Windows PowerShell

1. Extract the ZIP. Open VS Code in the folder that contains `app.py` and `requirements.txt`.
2. Run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open **http://localhost:8501**. If you want an isolated environment instead:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Do **not** use Unix `/c:/Users/...` paths in PowerShell.

## Usage

- Start with a purchase/refund story (English or Hindi).
- The assistant checks scope and high-stakes topics and collects missing facts, one at a time.
- Ask follow-up questions about evidence, next steps, deadlines, or the legal process.
- Review/edit all eight factual fields in the case workspace and generate a **seller grievance draft**.
- Download a TXT letter or case JSON; **nothing is sent or filed on your behalf**.
- An optional LLM can suggest structured facts, which **must be explicitly accepted** by the user. There is no need for a model or API key to run the default app.

## Optional voice and model configuration

- Voice: `python -m pip install -r requirements-voice-optional.txt`. `faster-whisper` runs speech transcription locally, after potentially downloading a model on first use. An audio transcription has to be pasted into chat. It may require a compatible Python version and FFmpeg-related libraries.
- Optional external model: sidebar toggle, user-provided HTTPS OpenAI-compatible base URL + API key + model. It **only extracts potential facts**, not legal reasoning, source citations or final decisions. It costs money if your provider charges you. It sends (partially redacted) text to that provider; do not use real personal details.

## What AI does versus rules

- **Deterministic free mode**: phrase-based triage, limited fact extraction, turn-based missing-field collection, FAQ responses from a fixed official source list, and complaint rendering. It is useful but cannot understand every utterance. It is **not a fully generative chatbot** in default mode.
- **Optional model**: a swappable JSON extraction adapter in `llm_adapter.py`. All fields are treated as suggestions pending confirmation. An LLM is **never used to invent case law, procedural guarantees, statute names or legal outcomes**.
- **Human review**: always before a document is used; urgent/court/criminal issues are blocked and referred for legal help.

## Tests and raw evidence

```powershell
python -m unittest discover -s tests -v
python generate_raw_outputs.py
```

`test_cases.json` contains 12 **synthetic** inputs. `raw_outputs/` contains their direct, unedited deterministic engine responses (`T01`–`T12`). Each includes triage, missing fields, guidance, legal sources and any generated draft. Tests cover refusals, Hindi, missing facts, scope, safe redaction, and the case summary. These are **engine tests only**, not a guarantee of frontend or model accuracy; run a manual browser check before submission.

## Limits, evaluation and privacy

- The app does not determine jurisdiction, compensation, legal entitlement, or claim success; complex matters need qualified counsel.
- Keyword scope/triage may be over- or under-inclusive. It does not validate a seller's identity, evidence authenticity, or whether a statement is true.
- The default mode is neither a general-purpose AI legal expert nor an autonomous filing system.
- Local Streamlit sessions are ephemeral; no persistent database. Optional LLM sends text externally, despite partial redaction. Use fictitious details in demos.
- Test cases are synthetic; live effectiveness needs user testing and review by a legal professional.

## Verified official links (checked 8 November 2026)

- [Consumer Protection Act, 2019 — India Code](https://www.indiacode.nic.in/indiacode/handle/123456789/15256?sam_handle=123456789%2F1362&view_type=browse)
- [National Consumer Helpline — Department of Consumer Affairs](https://consumeraffairs.gov.in/pages/nch) — 1915
- [National Consumer Helpline portal](https://consumerhelpline.gov.in/)
- [e-Jagriti portal](https://e-jagriti.gov.in/)
- [National Legal Services Authority](https://nalsa.gov.in/)

## Free deployment on Streamlit Community Cloud

1. Create a **public repository containing only this safe demo code**, the `test_cases.json`, sanitized synthetic outputs, the `README.md`, and the two-page `solution_doc.pdf`.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and connect the repository (entrypoint `app.py`).
3. Share the deployed URL. Test it in a private/incognito window. For public deployment, **do not commit any API keys or real user facts**.
4. Submit that URL, `solution_doc.pdf`, and a link to the `raw_outputs/` directory in Kuku's placement form.

## Submission reminder

Kuku requires **one problem, one submission**, and a PDF of **up to two pages**. The optional walkthrough can be up to three minutes. Avoid submitting private screenplay packs from Problem 1.
