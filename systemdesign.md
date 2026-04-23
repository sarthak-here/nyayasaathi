# NyayaSaathi — System Design

## What It Does
An AI-powered legal assistant for Indian citizens. Users describe their legal problem in plain language; the system retrieves relevant Indian laws from a local vector database and uses Gemma 4 (running locally via Ollama) to provide legal guidance and draft formal complaint letters — fully offline after setup.

---

## Architecture

```
User (Browser)
      |
      v
+--------------------------------------------------+
|              api/server.py (FastAPI)             |
|              REST endpoints + SSE streaming      |
+--------------------------------------------------+
      |
      v
+--------------------------------------------------+
|           core/legal_agent.py                   |
|                                                  |
|  1. Embed user query                             |
|     (sentence-transformers/all-MiniLM-L6-v2)    |
|                                                  |
|  2. ChromaDB vector similarity search            |
|     top-K relevant law chunks retrieved          |
|                                                  |
|  3. Prompt construction:                         |
|     [system] + [law context] + [user query]      |
|                                                  |
|  4. Ollama (Gemma 4) local inference             |
|     Streaming JSON: analysis + citations         |
+--------------------------------------------------+
      |
      v
+--------------------------------------------------+
|        core/letter_generator.py (optional)      |
|  Structured prompt -> Gemma 4                    |
|  Output: formal Indian complaint letter          |
|  (Facts / Legal Basis / Prayer sections)         |
|        +                                         |
|        core/pdf_export.py -> downloadable PDF    |
+--------------------------------------------------+
      |
      v
   frontend/index.html (streamed response)
```

---

## Knowledge Base Build (One-time Setup)

```
knowledge_base/docs/  (20+ .txt files)
  constitution_fundamental_rights.txt
  consumer_protection_act_2019.txt
  cyber_crimes_it_act.txt
  bns_crimes_against_women.txt
  digital_personal_data_protection.txt
  ... (20+ Indian Acts and Sections)
        |
        v
  build_kb.py
  - Chunk each file (500 tokens, 50-token overlap)
  - Embed chunks with all-MiniLM-L6-v2
  - Store in ChromaDB (./chroma_db, persistent on disk)
```

---

## Input

| Input | Example |
|---|---|
| Legal query | "My landlord is not returning my deposit" |
| Multi-turn follow-up | Conversation context retained in session |
| Letter generation | Name + facts + desired relief |

---

## Data Flow (query to answer)

```
Query: "My online seller didn't refund me after 30 days"
        |
  Embed -> [0.23, -0.41, 0.87, ...]
        |
  ChromaDB.query(top_k=5)
        |
  Returns: consumer_protection_act_2019.txt chunks
           (Section 47, online purchase, 30-day refund rule)
        |
  Prompt to Gemma 4 (Ollama, local):
    System: "You are a legal advisor for Indian citizens."
    Context: [retrieved law chunks]
    Query: [user question]
    Output format: JSON {analysis, applicable_law,
                   sections[], recommended_action, severity}
        |
  Gemma 4 -> streaming JSON tokens -> SSE -> browser
        |
  Optional: "Generate Complaint Letter" button
        |
  letter_generator.py -> structured prompt -> Gemma 4
  -> Indian legal format letter -> pdf_export.py -> PDF download
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| Fully local (Ollama + ChromaDB) | Legal queries are sensitive — no data sent to external APIs |
| 20+ curated law documents | LLM training data is outdated; exact Act text is needed for citations |
| Streaming SSE | Legal answers are long; streaming gives immediate feedback |
| JSON-structured LLM output | Frontend can parse severity, sections, and actions as separate UI components |
| Sentence-transformer embeddings | Lightweight, CPU-compatible, strong semantic matching for legal text |

---

## Interview Conclusion

NyayaSaathi is a privacy-first RAG application that addresses a real access-to-justice gap: most Indian citizens cannot afford legal consultation. The architecture is a local retrieval-augmented generation pipeline where the retriever is ChromaDB storing embeddings of 20+ Indian law documents, and the generator is Gemma 4 running on-device via Ollama. The critical design constraint is full offline operation — sending legal queries to external APIs would be a non-starter for the target audience. The letter generator adds a structured output layer that forces the LLM to produce complaint letters in the exact format (Facts / Legal Basis / Prayer) accepted by Indian consumer forums and courts. If I were scaling this, I would add a cross-encoder re-ranking step after retrieval to improve context precision, and a citation overlay in the UI that links every AI statement back to its source section.
