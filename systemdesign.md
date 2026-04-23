# NyayaSaathi - System Design

## What It Does
An AI-powered legal assistant for Indian citizens. Users describe their problem in plain
language; the system retrieves relevant Indian laws from a local vector database and uses
Gemma 4 (via Ollama, fully local) to provide legal guidance and draft formal complaint
letters. No data leaves the device.

---

## Architecture

```
User (Browser)
      |
      v
+--------------------------------------------------+
|          api/server.py (FastAPI + SSE)           |
+--------------------------------------------------+
      |
      v
+--------------------------------------------------+
|          core/legal_agent.py                     |
|                                                  |
|  1. Embed query with all-MiniLM-L6-v2            |
|  2. ChromaDB similarity search (top-K chunks)    |
|  3. Build prompt: system + law context + query   |
|  4. Ollama (Gemma 4) local streaming inference   |
|  5. JSON output: analysis + citations            |
+--------------------------------------------------+
      |
      v
+--------------------------------------------------+
|        core/letter_generator.py (optional)       |
|  Structured prompt -> Gemma 4                    |
|  Output: formal Indian complaint letter          |
|  Sections: Facts / Legal Basis / Prayer          |
|        +                                         |
|  core/pdf_export.py -> downloadable PDF          |
+--------------------------------------------------+

Knowledge Base Build (one-time):
  knowledge_base/docs/ (20+ Indian law .txt files)
  -> build_kb.py -> chunk -> embed -> ChromaDB
```

---

## Input

| Input                  | Example                                          |
|------------------------|--------------------------------------------------|
| Legal query            | "My landlord is not returning my deposit"        |
| Follow-up              | Multi-turn conversation                          |
| Letter generation      | Name + facts + relief -> complaint letter        |

---

## Data Flow

```
Query: "My online seller did not refund me after 30 days"
        |
  Embed -> [0.23, -0.41, 0.87, ...]    (all-MiniLM-L6-v2)
        |
  ChromaDB.query(top_k=5)
        |
  Returns: consumer_protection_act_2019.txt chunks
           (Section 47, online purchase, refund rules)
        |
  Prompt to Gemma 4 (Ollama, local):
    System: "You are a legal advisor for Indian citizens."
    Context: [retrieved law chunks]
    Query:   [user question]
    Output:  JSON {analysis, applicable_law,
             sections[], recommended_action, severity}
        |
  Gemma 4 -> streaming tokens -> SSE -> browser
        |
  Optional: "Generate Complaint Letter"
        |
  letter_generator.py -> structured letter prompt
  -> Gemma 4 -> Indian legal format
  -> pdf_export.py -> downloadable PDF
```

---

## Key Design Decisions

| Decision                          | Reason                                           |
|-----------------------------------|--------------------------------------------------|
| Fully local (Ollama + ChromaDB)   | Legal queries are sensitive; nothing leaves device|
| 20+ curated Indian law documents  | LLM training data is outdated; exact Act text needed|
| Streaming SSE                     | Legal answers are long; streaming gives instant feedback|
| JSON-structured LLM output        | Frontend parses severity, sections separately    |
| Sentence-transformer embeddings   | Lightweight, CPU-only, strong semantic matching  |

---

## Interview Conclusion

NyayaSaathi is a privacy-first RAG application addressing a real access-to-justice gap:
most Indian citizens cannot afford legal consultation. The retriever is a local ChromaDB
vector store built from 20+ Indian law documents, and the generator is Gemma 4 running
on-device via Ollama. The critical constraint is full offline operation -- sending legal
queries to external APIs would be a non-starter. The letter generator forces the LLM to
produce complaint letters in the exact format (Facts / Legal Basis / Prayer) accepted by
Indian consumer forums and courts. Scaling: add a cross-encoder re-ranking step after
retrieval, and a citation overlay linking every AI statement to its source section.
