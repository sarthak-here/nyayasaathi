# NyayaSaathi — Kaggle Gemma 4 Hackathon Submission

## Project Description

**NyayaSaathi (न्याय साथी — "Justice Friend")** is a 100% offline legal aid assistant for underserved Indians who cannot access or afford legal counsel. It uses **Gemma 4 (gemma4:e2b) via Ollama** to power a Retrieval-Augmented Generation pipeline over a curated Indian legal corpus, enabling anyone — regardless of literacy, location, or financial means — to understand their rights and take action.

---

## Problem Statement

India has over 400 million people living below or near the poverty line. Legal injustice — wage theft, domestic violence, caste discrimination, consumer fraud, RTI denial — disproportionately affects the most vulnerable. Yet:
- A lawyer charges Rs. 500–5,000 per consultation
- Legal processes are in English, inaccessible to most
- Rural and semi-urban Indians have no internet in government buildings
- Even literate users don't know which law applies to their situation

NyayaSaathi addresses all of this: **offline, multilingual, free, and actionable**.

---

## How Gemma 4 is Used

| Feature | Gemma 4 Role |
|---------|-------------|
| Legal Analysis | RAG pipeline: retrieves relevant Indian law → Gemma 4 synthesizes rights explanation in Hindi/English |
| Complaint Letter | Gemma 4 drafts formal Indian legal complaint letters in proper format |
| Multilingual | Gemma 4 naturally responds in the user's language (Hindi, English, Hinglish) |
| Streaming | Token-by-token streaming via Ollama for real-time UI feedback |
| Voice Input | Whisper transcribes voice → text → Gemma 4 analyzes |

Model: `gemma4:e2b` (Gemma 4 2B — fast enough for consumer hardware, fits in ~2GB VRAM/RAM)

---

## Offline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER'S LOCAL MACHINE                        │
│                                                                 │
│  ┌──────────┐    ┌──────────────────┐    ┌─────────────────┐  │
│  │  Gradio  │───▶│   Legal Agent    │───▶│  ChromaDB       │  │
│  │   UI     │    │  (RAG Pipeline)  │    │  (Local Vector  │  │
│  │ (Browser)│    │                  │    │   Database)     │  │
│  └──────────┘    └────────┬─────────┘    └────────┬────────┘  │
│       ▲                   │                        │           │
│       │                   ▼                        │           │
│  ┌────┴─────┐    ┌──────────────────┐    ┌────────▼────────┐  │
│  │  PDF     │    │  Ollama Server   │    │  Sentence       │  │
│  │ Export   │    │  (localhost:     │    │  Transformers   │  │
│  │ (fpdf2)  │    │   11434)         │    │  (Embeddings)   │  │
│  └──────────┘    └────────┬─────────┘    └─────────────────┘  │
│                           │                                     │
│  ┌────────────┐    ┌──────▼──────────┐                         │
│  │  Whisper   │    │   Gemma 4       │                         │
│  │ (Offline   │    │  (gemma4:e2b)   │                         │
│  │  STT)      │    │                 │                         │
│  └────────────┘    └─────────────────┘                         │
│                                                                 │
│  NO INTERNET REQUIRED AFTER INITIAL SETUP                       │
└─────────────────────────────────────────────────────────────────┘
```

**Data flow:**
1. User describes problem (text or voice)
2. ChromaDB retrieves top-5 relevant legal chunks using MiniLM embeddings
3. Context + user situation sent to Gemma 4 via Ollama
4. Gemma 4 identifies applicable law, explains rights, suggests steps
5. User can generate a formal complaint letter (Gemma 4 drafts it)
6. PDF exported locally — ready to submit to authorities

---

## Setup Instructions

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.com) installed
- 4GB RAM minimum (8GB recommended)

### Installation

```bash
# 1. Pull Gemma 4
ollama pull gemma4:e2b

# 2. Clone / navigate to project
cd nyayasaathi

# 3. Install dependencies
pip install -r requirements.txt

# 4. Build knowledge base (one-time)
python knowledge_base/build_kb.py

# 5. Launch
python ui/app.py
# Open http://localhost:7860
```

### Demo Mode
```bash
python ui/app.py --demo
# Pre-loads 5 realistic legal scenarios
```

### Terminal Testing
```bash
python demo_scenarios.py --scenario 1   # Wage theft
python demo_scenarios.py --scenario 2   # Domestic violence
python demo_scenarios.py --scenario 3   # Consumer fraud
python demo_scenarios.py --scenario 4   # Caste discrimination
python demo_scenarios.py --scenario 5   # RTI denial
```

---

## Example Use Cases with Expected Outputs

### 1. Wage Theft
**Input:** *"Mere boss ne 3 mahine se salary nahi di. Main factory mein security guard hoon. Rs. 12,000 per mahine hai meri pay."*

**Expected Output:**
- **Applicable Law:** Payment of Wages Act 1936, Section 15
- **Explanation:** Your employer is required to pay wages within 7 days of month end under Section 5. Non-payment is an offence. You can claim back wages + 10x compensation.
- **Action:** File complaint before Labour Commissioner's office (Payment of Wages Authority)
- **Letter:** Addressed to "The Authority under Payment of Wages Act"

---

### 2. Domestic Violence
**Input:** *"My husband beats me regularly and his family demands dowry. He threw me out of the house last week with my children."*

**Expected Output:**
- **Applicable Law:** Protection of Women from Domestic Violence Act 2005, Sections 12, 17, 18, 19, 20
- **Explanation:** You have the right to reside in the shared household regardless of ownership. You can get an immediate Protection Order and Residence Order from a Magistrate.
- **Action:** Call Women Helpline 181 immediately. Approach Protection Officer for free assistance. File under Section 12 before Magistrate.
- **Letter:** Application under Section 12 PWDVA to the Magistrate

---

### 3. RTI Denial
**Input:** *"I filed an RTI to municipal corporation 45 days ago about road contract money. No reply came."*

**Expected Output:**
- **Applicable Law:** Right to Information Act 2005, Section 19(1) — First Appeal
- **Explanation:** PIO must respond within 30 days. Non-response is deemed refusal. You can now file a First Appeal within 30 days of the deadline, free of charge.
- **Action:** File First Appeal to First Appellate Authority (senior officer, same body). If rejected, go to State Information Commission.
- **Letter:** First Appeal letter to First Appellate Authority

---

## Key Differentiators

1. **100% Offline** — No cloud API, no data sent anywhere
2. **India-Specific Corpus** — RTI, Consumer Protection, DV Act, SC/ST Act, Labor Law
3. **Bilingual** — Responds in user's language (Hindi/English/Hinglish)
4. **Actionable PDF** — Generates a formal letter the user can physically submit
5. **Truly Accessible** — Works on budget hardware (2GB RAM for model alone)
6. **Voice Input** — For low-literacy users who can speak but not type

---

## Limitations & Future Work

- Legal corpus currently covers 5 laws — can be extended to cover all 1,200+ central Acts
- Hindi Devanagari script in PDF requires additional font support (planned)
- Whisper model needs download on first run (~150MB)
- Complex multi-party cases may require human legal counsel

---

*Submitted for Kaggle Gemma 4 Hackathon | Built by sarthak-here | April 2026*
