# NyayaSaathi — Your Free Legal Assistant
### न्याय साथी — आपका मुफ्त कानूनी सहायक

NyayaSaathi is a **100% offline legal aid assistant** built for underserved Indians who cannot afford legal counsel. Powered by **Gemma 4 via Ollama**, it runs entirely on your local machine — your data never leaves your device.

---

## What It Does

- **Understands your situation** in plain Hindi, English, or Hinglish
- **Identifies applicable Indian laws** — RTI, Consumer Protection, Domestic Violence Act, SC/ST Atrocities Act, Payment of Wages Act, and more
- **Explains your rights** in simple language anyone can understand
- **Drafts formal complaint letters** ready to submit to authorities
- **Exports to PDF** for immediate physical submission
- **Voice input** via offline Whisper transcription
- **Case history** — all past analyses saved locally in your browser

---

## Two UI Options

### Option A — Professional Web Frontend (Recommended)

A full-featured, mobile-responsive web app served via FastAPI:

```bash
python start_web.py
```

Open `http://localhost:8000` — the browser opens automatically.

**Web frontend features:**
- Live streaming legal analysis with token-by-token display
- 12 legal category cards for quick browsing (Wage Theft, Cyber Crime, RERA, etc.)
- 4-step progress tracker (Describe → Analyze → Letter → PDF)
- Case history sidebar (localStorage — no server needed)
- Emergency helplines modal (112, 1091, 1098, 1930, 15100)
- DLSA directory — free legal aid centers for 8 major cities
- Legal awareness ticker with rotating law tips
- Voice recording (wired to Whisper transcription endpoint)
- In-browser editable letter before PDF download
- Model connection status indicator

### Option B — Gradio UI (Simple)

```bash
python ui/app.py
# or with demo scenarios pre-loaded:
python ui/app.py --demo
```

Open `http://localhost:7860`

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Gemma 4 (gemma4:e2b) via Ollama |
| Vector DB | ChromaDB (local) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (offline) |
| Web UI | Vanilla HTML/CSS/JS (no framework) |
| Web API | FastAPI + Uvicorn |
| Simple UI | Gradio |
| PDF Export | fpdf2 |
| Voice Input | OpenAI Whisper (offline) |
| RAG Framework | LangChain |

---

## Project Structure

```
nyayasaathi/
├── knowledge_base/
│   ├── docs/                # 25+ Indian legal text files
│   └── build_kb.py          # Indexes docs into ChromaDB
├── core/
│   ├── legal_agent.py       # RAG pipeline + Gemma 4 analysis
│   ├── letter_generator.py  # Complaint letter drafting
│   └── pdf_export.py        # PDF generation
├── api/
│   └── server.py            # FastAPI REST backend
├── frontend/
│   └── index.html           # Professional web frontend
├── ui/
│   └── app.py               # Gradio UI (alternative)
├── start_web.py             # One-command launcher for web UI
├── output/                  # Generated PDFs saved here
├── chroma_db/               # Auto-created vector database
├── demo_scenarios.py        # Realistic test cases
├── .env.example             # Environment config template
└── requirements.txt
```

---

## Setup

### 1. Install Ollama and pull the model
```bash
# Install Ollama from https://ollama.com
ollama pull gemma4:e2b
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env if needed — defaults work out of the box
```

### 4. Build the legal knowledge base
```bash
python knowledge_base/build_kb.py
```

### 5. Launch the app
```bash
# Web frontend (recommended)
python start_web.py

# OR Gradio UI
python ui/app.py
```

---

## API Endpoints

The FastAPI server exposes these endpoints (docs at `/docs`):

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Model connection status |
| POST | `/api/analyze/stream` | Legal analysis (streaming SSE) |
| POST | `/api/analyze` | Legal analysis (non-streaming) |
| POST | `/api/letter/stream` | Complaint letter generation (streaming SSE) |
| POST | `/api/pdf` | Export letter to PDF download |
| POST | `/api/transcribe` | Voice-to-text via Whisper |

---

## Example Use Cases

1. **Wage Theft** — "Mera boss 3 mahine se salary nahi de raha" → Payment of Wages Act, complaint to Labour Commissioner
2. **Consumer Fraud** — "Amazon ne defective product bheja aur refund nahi de raha" → Consumer Protection Act 2019, NCDRC complaint letter
3. **RTI Denial** — "Maine RTI file ki thi, 30 din ho gaye koi jawab nahi" → RTI Act 2005, first appeal letter to PIO
4. **Domestic Violence** — Identifies DV Act 2005, guides to nearest Legal Services Authority
5. **Caste Discrimination** — SC/ST Atrocities Act 1989, FIR complaint draft
6. **Cyber Fraud** — UPI/online scam → IT Act + BNS sections, complaint to cybercrime.gov.in

---

## Privacy

- **No internet required** after initial model download
- **No data sent to any server** — everything runs locally
- Your conversations and generated documents stay on your device
- Case history stored only in your browser's localStorage

---

## Disclaimer

NyayaSaathi provides legal **information**, not legal **advice**. For complex matters, please consult a qualified advocate. Free legal aid is available at your district's Legal Services Authority (DLSA) — call **15100** (NALSA helpline).

---

*Built for the Kaggle Gemma 4 Hackathon 2025 | Made with ❤️ for India's underserved*
