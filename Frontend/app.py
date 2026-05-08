"""
NyayaSaathi — Gradio UI
Full legal aid interface with streaming, letter generation, and PDF export.
Run: python ui/app.py
"""

import os
import sys
import json
import argparse
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import gradio as gr
from core.legal_agent import LegalAgent
from core.letter_generator import generate_letter_stream, generate_letter
from core.pdf_export import export_to_pdf

agent = LegalAgent()

# ---------------------------------------------------------------------------
# Demo scenarios (used with --demo flag)
# ---------------------------------------------------------------------------
DEMO_SCENARIOS = {
    "Wage Theft": "Main ek factory mein kaam karta hoon. Mere boss ne 3 mahine se salary nahi di. Woh kehte hain company ghata mein chal rahi hai lekin koi likha hua kuch nahi diya. Main kya kar sakta hoon?",
    "Consumer Fraud": "Maine Amazon se ek mobile phone kharida tha 15,000 rupaye mein. Phone defective tha — screen mein problem hai. Maine 3 baar complaint ki lekin woh na refund de rahe hain, na replace kar rahe hain. Mujhe kya karna chahiye?",
    "RTI Denial": "Maine 2 mahine pehle RTI file ki thi apne ward ke road repair ke baare mein. 30 din baad bhi koi jawab nahi aaya. Ab mujhe kya karna chahiye?",
    "Domestic Violence": "My husband beats me regularly and has thrown me out of the house with my two children. His family is also harassing me for dowry. I have nowhere to go. What legal help is available?",
    "Caste Discrimination": "Hamare gaon mein ek upper caste ke aadmi ne humein (SC community) common well se paani lene se roka. Usne gaaliyan di aur hamare saath maarpeet ki. Hum kya kar sakte hain?",
    "Hit and Run (Accused)": "I was driving late at night and accidentally hit a parked car. I panicked and drove away without stopping. Now I am worried about what will happen to me. What should I do?",
    "False 498A Complaint": "My wife has filed a 498A dowry harassment case against me and my parents. The allegations are false — she left on her own after a fight and is using this to get divorce leverage. What are our rights and how do we defend ourselves?",
}

# ---------------------------------------------------------------------------
# Analysis function (streaming)
# ---------------------------------------------------------------------------
def analyze_situation(situation: str, language: str):
    """Stream the legal analysis, then parse and return structured output."""
    if not situation.strip():
        yield (
            "",  # applicable_law
            "Please describe your situation to get legal analysis.",  # explanation
            "",  # recommended_action
            gr.update(visible=False),  # letter_section
        )
        return

    lang_map = {"Auto-detect": "auto", "English": "english", "Hindi": "hindi", "Hinglish": "hinglish"}
    lang_code = lang_map.get(language, "auto")

    from core.legal_agent import extract_json

    # Stream tokens — show a live thinking indicator, not raw JSON
    full_response = ""
    dots = [".", "..", "..."]
    dot_idx = 0
    for token in agent.analyze_stream(situation, language=lang_code):
        full_response += token
        dot_idx = (dot_idx + 1) % (len(dots) * 10)
        yield (
            "Analyzing" + dots[dot_idx // 10],
            "Reading relevant laws and analyzing your situation" + dots[dot_idx // 10],
            "",
            gr.update(visible=False),
        )

    # Parse structured response using the robust extractor
    result = extract_json(full_response)

    applicable_law = result.get("applicable_law", "")
    explanation = result.get("explanation", full_response)
    recommended_action = result.get("recommended_action", "")
    can_generate_letter = result.get("can_generate_letter", False)

    # Format recommended_action list into readable numbered steps
    if isinstance(recommended_action, list):
        recommended_action = "\n".join(f"{i+1}. {step}" for i, step in enumerate(recommended_action))

    yield (
        applicable_law,
        explanation,
        recommended_action,
        gr.update(visible=can_generate_letter),
    )


# ---------------------------------------------------------------------------
# Letter generation function
# ---------------------------------------------------------------------------
def generate_complaint_letter(
    situation: str,
    language: str,
    user_name: str,
    user_address: str,
    user_phone: str,
    respondent: str,
    respondent_address: str,
):
    """Generate a complaint letter and stream it."""
    if not all([situation.strip(), user_name.strip(), user_address.strip(), respondent.strip()]):
        yield "Please fill in all required fields (Name, Address, and Opposite Party).", None
        return

    lang_map = {"Auto-detect": "auto", "English": "english", "Hindi": "hindi", "Hinglish": "hinglish"}
    lang_code = lang_map.get(language, "auto")

    # Get legal analysis for context
    analysis = agent.analyze(situation, language=lang_code)

    # Stream letter generation
    letter_text = ""
    for token in generate_letter_stream(
        situation=situation,
        user_name=user_name,
        user_address=user_address,
        user_phone=user_phone or "Not provided",
        respondent=respondent,
        respondent_address=respondent_address or "Address not known",
        legal_analysis=analysis,
    ):
        letter_text += token
        yield letter_text, None  # No PDF yet

    yield letter_text, None


def download_pdf(letter_text: str, user_name: str):
    """Export letter to PDF and return path for download."""
    if not letter_text.strip():
        return None
    try:
        pdf_path = export_to_pdf(letter_text, user_name=user_name or "Complainant")
        return pdf_path
    except Exception as e:
        return None


# ---------------------------------------------------------------------------
# Voice transcription
# ---------------------------------------------------------------------------
def transcribe_audio(audio_path):
    """Transcribe audio using offline Whisper."""
    if audio_path is None:
        return ""
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"].strip()
    except ImportError:
        return "[Voice input requires openai-whisper. Run: pip install openai-whisper]"
    except Exception as e:
        return f"[Transcription error: {str(e)}]"


# ---------------------------------------------------------------------------
# Demo loader
# ---------------------------------------------------------------------------
def load_demo(scenario_name: str):
    return DEMO_SCENARIOS.get(scenario_name, "")


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
body, .gradio-container {
    background-color: #0f0f0f !important;
    color: #e0e0e0 !important;
    font-family: 'Segoe UI', sans-serif;
}
.gr-button-primary {
    background: linear-gradient(135deg, #1a3a6e, #2563eb) !important;
    border: none !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 8px !important;
}
.gr-button-secondary {
    background: #1e1e1e !important;
    border: 1px solid #444 !important;
    color: #ccc !important;
    border-radius: 8px !important;
}
.app-title {
    text-align: center;
    color: #7fb3f5;
    font-size: 2em;
    font-weight: bold;
    margin-bottom: 4px;
}
.app-subtitle {
    text-align: center;
    color: #888;
    font-size: 0.95em;
    margin-bottom: 20px;
}
.law-box {
    background: #1a2744 !important;
    border-left: 4px solid #2563eb !important;
    border-radius: 6px !important;
    padding: 12px !important;
}
.footer-text {
    text-align: center;
    color: #555;
    font-size: 0.8em;
    margin-top: 30px;
}
"""

GRADIO_THEME = gr.themes.Base(
    primary_hue="blue",
    neutral_hue="gray",
).set(
    body_background_fill="#0f0f0f",
    block_background_fill="#1a1a1a",
    block_border_color="#333",
    input_background_fill="#111",
)


def build_ui(demo_mode: bool = False):
    with gr.Blocks(title="NyayaSaathi — Free Legal Assistant") as demo:

        gr.HTML('<div class="app-title">NyayaSaathi — न्याय साथी</div>')
        gr.HTML('<div class="app-subtitle">Your Free Legal Assistant | Works 100% Offline | Powered by Gemma 4</div>')

        with gr.Row():
            with gr.Column(scale=2):

                # --- Input Section ---
                with gr.Group():
                    gr.Markdown("### Describe Your Problem")
                    situation_input = gr.Textbox(
                        label="Your Situation (Hindi, English, or Hinglish)",
                        placeholder="Apni problem yahan likhein... (e.g., 'Mere boss ne 2 mahine se salary nahi di')\nOr in English: (e.g., 'My landlord is threatening to evict me without notice')",
                        lines=5,
                        max_lines=10,
                    )

                    with gr.Row():
                        language_select = gr.Dropdown(
                            choices=["Auto-detect", "English", "Hindi", "Hinglish"],
                            value="Auto-detect",
                            label="Response Language",
                            scale=1,
                        )
                        analyze_btn = gr.Button(
                            "Analyze My Situation",
                            variant="primary",
                            scale=2,
                        )

                    # Voice input
                    with gr.Accordion("Voice Input (Offline Whisper)", open=False):
                        audio_input = gr.Audio(
                            sources=["microphone"],
                            type="filepath",
                            label="Record your problem",
                        )
                        transcribe_btn = gr.Button("Transcribe Voice", variant="secondary")
                        gr.Markdown("*Transcribed text will auto-fill the situation box above*")

                # Demo loader
                if demo_mode:
                    with gr.Accordion("Demo Scenarios", open=True):
                        demo_select = gr.Dropdown(
                            choices=list(DEMO_SCENARIOS.keys()),
                            label="Load a demo scenario",
                        )
                        load_demo_btn = gr.Button("Load Scenario", variant="secondary")

            with gr.Column(scale=3):

                # --- Analysis Output ---
                with gr.Group():
                    gr.Markdown("### Legal Analysis")
                    applicable_law_out = gr.Textbox(
                        label="Applicable Law",
                        interactive=False,
                        elem_classes=["law-box"],
                    )
                    explanation_out = gr.Textbox(
                        label="Your Rights Explained",
                        lines=6,
                        interactive=False,
                    )
                    action_out = gr.Textbox(
                        label="What You Can Do Next",
                        lines=5,
                        interactive=False,
                    )

        # --- Complaint Letter Section ---
        letter_section = gr.Group(visible=False)
        with letter_section:
            gr.Markdown("---")
            gr.Markdown("### Generate Formal Complaint Letter")
            gr.Markdown("*Fill in your details to generate a letter you can physically submit*")

            with gr.Row():
                with gr.Column():
                    name_input = gr.Textbox(label="Your Full Name *", placeholder="Ramesh Kumar")
                    address_input = gr.Textbox(label="Your Address *", placeholder="123 MG Road, City, State - PIN")
                    phone_input = gr.Textbox(label="Your Phone Number", placeholder="9876543210")

                with gr.Column():
                    respondent_input = gr.Textbox(
                        label="Opposite Party (Who to complain against) *",
                        placeholder="ABC Company / John's Shop / XYZ Authority"
                    )
                    respondent_addr_input = gr.Textbox(
                        label="Opposite Party's Address",
                        placeholder="Leave blank if unknown"
                    )

            generate_letter_btn = gr.Button("Draft Complaint Letter", variant="primary")

            letter_output = gr.Textbox(
                label="Your Complaint Letter",
                lines=20,
                interactive=True,
                placeholder="Your letter will appear here...",
            )

            with gr.Row():
                download_btn = gr.Button("Download as PDF", variant="secondary")
                pdf_file = gr.File(label="PDF Download", visible=True)

        # Footer
        gr.HTML(
            '<div class="footer-text">'
            'Works 100% offline. Your data never leaves your device. '
            'NyayaSaathi provides legal information, not legal advice. '
            'For complex matters, free legal aid is available at your district\'s DLSA.'
            '</div>'
        )

        # --- Event handlers ---
        analyze_btn.click(
            fn=analyze_situation,
            inputs=[situation_input, language_select],
            outputs=[applicable_law_out, explanation_out, action_out, letter_section],
        )

        generate_letter_btn.click(
            fn=generate_complaint_letter,
            inputs=[
                situation_input, language_select,
                name_input, address_input, phone_input,
                respondent_input, respondent_addr_input,
            ],
            outputs=[letter_output, pdf_file],
        )

        download_btn.click(
            fn=download_pdf,
            inputs=[letter_output, name_input],
            outputs=[pdf_file],
        )

        transcribe_btn.click(
            fn=transcribe_audio,
            inputs=[audio_input],
            outputs=[situation_input],
        )

        if demo_mode:
            load_demo_btn.click(
                fn=load_demo,
                inputs=[demo_select],
                outputs=[situation_input],
            )

    return demo


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NyayaSaathi Legal Assistant")
    parser.add_argument("--demo", action="store_true", help="Pre-load demo scenarios")
    parser.add_argument("--port", type=int, default=7860, help="Port to run on")
    parser.add_argument("--share", action="store_true", help="Create public share link")
    args = parser.parse_args()

    app = build_ui(demo_mode=args.demo)
    app.launch(
        server_port=args.port,
        share=args.share,
        theme=GRADIO_THEME,
        css=CUSTOM_CSS,
        show_error=True,
        inbrowser=True,
    )
