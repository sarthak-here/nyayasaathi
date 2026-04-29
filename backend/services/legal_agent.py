"""
NyayaSaathi — Legal Agent (RAG Pipeline)
Retrieves relevant legal context and calls Gemma 4 via Ollama for analysis.
"""

import os
import json
from typing import Generator
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e2b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def extract_json(text: str) -> dict:
    """
    Robustly extract a JSON object from model output.
    Handles: code blocks, trailing text, leading text.
    """
    import re
    # 1. Try ```json ... ``` block
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # 2. Try ``` ... ``` block
    m = re.search(r"```\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Extract outermost { ... } (handles trailing text like "Free legal help...")
    start = text.find("{")
    if start != -1:
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i+1])
                    except json.JSONDecodeError:
                        break

    # 4. Fallback — return raw text as explanation
    return {
        "applicable_law": "See explanation below",
        "explanation": text,
        "recommended_action": "Contact your district DLSA for free legal aid.",
        "can_generate_letter": False,
        "letter_recipient": None,
    }


SYSTEM_PROMPT = """You are NyayaSaathi (न्याय साथी), a compassionate legal aid assistant for underserved Indians who cannot afford lawyers.

Your role:
- Help people understand their legal rights in plain, simple language
- Identify which Indian law(s) apply to their situation
- Give clear, numbered, actionable steps — your users may be panicking and need a precise path forward
- Be empathetic — your users are often in distress, facing injustice

FIRST — IDENTIFY THE USER'S ROLE IN THE SITUATION:
Before analyzing, determine who the user IS in the situation:
- Are they the VICTIM (someone wronged, seeking protection or remedy)?
- Are they the ACCUSED / PERSON WHO CAUSED HARM (seeking to fix their mistake or understand their liability)?
- Are they a THIRD PARTY (family member, witness, employer)?

This changes everything. Wrong role = completely wrong advice.
Examples:
- "Someone hit my car and fled" → user is VICTIM → advise on claiming compensation.
- "I accidentally hit a parked car and fled" → user is ACCUSED → advise on voluntary reporting, limiting liability, and legal exposure.
- "My employee hasn't been paid" → user is EMPLOYER → different obligations than employee.
- "My salary wasn't paid" → user is EMPLOYEE/VICTIM → advise on claiming wages.

Always address the user's actual situation — not the mirror-image situation.

Rules you MUST follow:
1. ONLY use information from the provided legal context. Do NOT make up laws, sections, or rights.
2. If the retrieved context does not cover the situation, say so clearly and suggest contacting DLSA (District Legal Services Authority) for free legal aid.
3. Respond in the SAME language as the user (Hindi, English, or Hinglish). If they write in Hindi/Hinglish, respond in Hindi/Hinglish. If in English, respond in English.
4. Always cite the specific Act and Section (e.g., "Section 15 of Payment of Wages Act 1936").
5. Do NOT give vague advice. Be specific about WHAT to do, WHERE to go, and HOW.
6. If the user is the ACCUSED or admits causing harm, help them understand: their legal exposure, their constitutional rights (bail, right to silence, right to a lawyer), mitigating factors, voluntary surrender benefits, and what the prosecution must prove. This is legitimate defense-side legal aid.
   However, do NOT advise actions that are themselves crimes: destroying or hiding evidence, fleeing jurisdiction, suborning perjury, bribing witnesses or officials, or making false statements to police/court.
7. NEVER give victim remedies (compensation claims, protection orders, FIR filing as complainant) to a user who has identified themselves as the person who caused the harm. Those remedies belong to the other party.

CRITICAL RULE FOR recommended_action:
- ALWAYS return recommended_action as a JSON array of strings — never a single string.
- Each item must be ONE concrete, immediately actionable step.
- Each step must say: what to do + where to go + any deadline or urgency.
- Start urgent steps with "IMMEDIATELY:" if time-sensitive (e.g., cyber fraud, evidence preservation, voluntary surrender).
- Include 4 to 6 steps. Never fewer than 3.
- Bad example: "Go to the police" — too vague.
- Good example: "Go to the nearest police station and file an FIR under BNS Section 351 (criminal intimidation). Tell them a stranger threatened you at [location]. You cannot be refused."

Response format — return ONLY valid JSON, nothing before or after the closing brace:
{
  "applicable_law": "Primary law name and specific sections that apply",
  "explanation": "2-3 paragraph plain language explanation of the user's legal position and rights",
  "recommended_action": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ...",
    "Step 4: ..."
  ],
  "can_generate_letter": true or false,
  "letter_recipient": "Exact designation and office to address the letter to, or null"
}"""


class LegalAgent:
    def __init__(self):
        self._collection = None
        self._embed_fn = None
        self._client = None

    def _init_db(self):
        """Lazy-initialize ChromaDB connection."""
        if self._collection is not None:
            return

        import chromadb
        from chromadb.utils import embedding_functions

        self._embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL
        )
        self._client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

        try:
            self._collection = self._client.get_collection(
                name="legal_docs",
                embedding_function=self._embed_fn,
            )
        except Exception as e:
            raise RuntimeError(
                f"ChromaDB collection not found at '{CHROMA_DB_PATH}'. "
                "Please run: python knowledge_base/build_kb.py"
            ) from e

    def retrieve(self, query: str, k: int = 5) -> list[dict]:
        """Retrieve top-k relevant legal text chunks for a query."""
        self._init_db()

        results = self._collection.query(
            query_texts=[query],
            n_results=k,
        )

        chunks = []
        for i, doc in enumerate(results["documents"][0]):
            chunks.append({
                "text": doc,
                "source": results["metadatas"][0][i]["source"],
                "chunk_index": results["metadatas"][0][i]["chunk_index"],
                "distance": results["distances"][0][i] if "distances" in results else None,
            })

        return chunks

    def _build_context(self, chunks: list[dict]) -> str:
        """Format retrieved chunks into a context string for the prompt."""
        context_parts = []
        for i, chunk in enumerate(chunks):
            context_parts.append(
                f"[Source {i+1}: {chunk['source']}]\n{chunk['text']}"
            )
        return "\n\n---\n\n".join(context_parts)

    def analyze(self, user_situation: str, language: str = "auto") -> dict:
        """
        Full RAG pipeline: retrieve → prompt → call Gemma 4 → parse response.
        Returns a dict with keys: applicable_law, explanation, recommended_action,
        can_generate_letter, letter_recipient.
        """
        import ollama

        # Retrieve relevant context
        chunks = self.retrieve(user_situation, k=5)
        context = self._build_context(chunks)

        # Build user message
        lang_instruction = ""
        if language == "hindi":
            lang_instruction = "\n\nIMPORTANT: Please respond entirely in Hindi (Devanagari script)."
        elif language == "english":
            lang_instruction = "\n\nIMPORTANT: Please respond entirely in English."
        elif language == "hinglish":
            lang_instruction = "\n\nIMPORTANT: Please respond in Hinglish (mix of Hindi and English, Roman script)."

        user_message = f"""LEGAL CONTEXT (retrieved from Indian law database):
{context}

USER'S SITUATION:
{user_situation}

Based ONLY on the legal context above, analyze this situation and respond in JSON format.{lang_instruction}"""

        # Call Gemma 4 via Ollama
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            options={"temperature": 0.3, "num_predict": 1500},
        )

        raw_text = response["message"]["content"]

        result = extract_json(raw_text)

        result["retrieved_sources"] = [c["source"] for c in chunks]
        return result

    def analyze_stream(self, user_situation: str, language: str = "auto") -> Generator[str, None, None]:
        """
        Streaming version: yields tokens as they arrive from Gemma 4.
        Yields raw text tokens for display in UI.
        """
        import ollama

        chunks = self.retrieve(user_situation, k=5)
        context = self._build_context(chunks)

        lang_instruction = ""
        if language == "hindi":
            lang_instruction = "\n\nRespond entirely in Hindi."
        elif language == "english":
            lang_instruction = "\n\nRespond entirely in English."
        elif language == "hinglish":
            lang_instruction = "\n\nRespond in Hinglish (Hindi + English mix, Roman script)."

        user_message = f"""LEGAL CONTEXT:
{context}

USER'S SITUATION:
{user_situation}

Analyze this situation based ONLY on the legal context. Respond in JSON format.{lang_instruction}"""

        stream = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            options={"temperature": 0.3, "num_predict": 1500},
            stream=True,
        )

        for chunk in stream:
            token = chunk["message"]["content"]
            if token:
                yield token


if __name__ == "__main__":
    # Quick terminal test
    agent = LegalAgent()

    print("NyayaSaathi Legal Agent — Terminal Test")
    print("=" * 50)
    situation = input("Describe your legal situation: ")

    print("\nAnalyzing... (streaming)\n")
    full_response = ""
    for token in agent.analyze_stream(situation):
        print(token, end="", flush=True)
        full_response += token

    print("\n\n--- Structured Analysis ---")
    result = agent.analyze(situation)
    print(f"Applicable Law: {result.get('applicable_law', 'N/A')}")
    print(f"Sources used: {result.get('retrieved_sources', [])}")
