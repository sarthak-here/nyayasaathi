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

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Gemma 4 (gemma4:e2b) via Ollama |
| Vector DB | ChromaDB (local) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (offline) |
| UI | Gradio |
| PDF Export | fpdf2 |
| Voice Input | OpenAI Whisper (offline) |
| RAG Framework | LangChain |

---

## Project Structure

```
nyayasaathi/
├── knowledge_base/
│   ├── docs/           # Legal text files (RTI, DV Act, etc.)
│   └── build_kb.py     # Indexes docs into ChromaDB
├── core/
│   ├── legal_agent.py  # RAG pipeline + LLM analysis
│   ├── letter_generator.py  # Complaint letter drafting
│   └── pdf_export.py   # PDF generation
├── ui/
│   └── app.py          # Gradio UI
├── output/             # Generated PDFs saved here
├── chroma_db/          # Auto-created vector database
├── demo_scenarios.py   # 5 realistic test cases
├── .env.example        # Environment config template
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
# Edit .env if needed (defaults work out of the box)
```

### 4. Build the legal knowledge base
```bash
python knowledge_base/build_kb.py
```

### 5. Launch the app
```bash
python ui/app.py
```

Open your browser to `http://localhost:7860`

---

## Example Use Cases

1. **Wage Theft** — "Mera boss 3 mahine se salary nahi de raha" → Identifies Payment of Wages Act, generates complaint to Labour Commissioner
2. **Consumer Fraud** — "Amazon ne defective product bheja aur refund nahi de raha" → Consumer Protection Act 2019, NCDRC complaint letter
3. **RTI Denial** — "Maine RTI file ki thi, 30 din ho gaye koi jawab nahi" → RTI Act 2005, first appeal letter to PIO
4. **Domestic Violence** — Identifies DV Act 2005, guides to nearest Legal Services Authority
5. **Caste Discrimination** — SC/ST Atrocities Act 1989, FIR complaint draft

---

## Privacy

- **No internet required** after initial model download
- **No data sent to any server** — everything runs locally
- Your conversations and generated documents stay on your device

---

## Disclaimer

NyayaSaathi provides legal information, not legal advice. For complex matters, please consult a qualified advocate. Free legal aid is available at your district's Legal Services Authority (DLSA).

---

*Built for the Kaggle Gemma 4 Hackathon 2025 | Made with ❤️ for India's underserved*
