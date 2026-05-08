from Backend.services.legal_agent import extract_json


def test_extract_json_from_code_block():
    text = '```json\n{"applicable_law": "RTI Act 2005", "explanation": "You have the right to information.", "recommended_action": ["File first appeal"], "can_generate_letter": true, "letter_recipient": "First Appellate Authority"}\n```'
    result = extract_json(text)
    assert result["applicable_law"] == "RTI Act 2005"
    assert result["can_generate_letter"] is True


def test_extract_json_bare_object():
    text = '{"applicable_law": "Payment of Wages Act 1936", "explanation": "Your employer must pay wages.", "recommended_action": ["File complaint"], "can_generate_letter": false, "letter_recipient": null}'
    result = extract_json(text)
    assert result["applicable_law"] == "Payment of Wages Act 1936"
    assert result["can_generate_letter"] is False


def test_extract_json_fallback_on_invalid():
    text = "This is plain text with no JSON structure at all."
    result = extract_json(text)
    assert "explanation" in result
    assert result["can_generate_letter"] is False
