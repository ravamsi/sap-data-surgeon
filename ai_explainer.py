import google.generativeai as genai
import streamlit as st
import time

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

_cache = {}

def explain_error(error: dict) -> str:
    cache_key = f"{error['field']}|{error['error_type']}|{error['bad_value']}"
    if cache_key in _cache:
        return _cache[cache_key]

    prompt = f"""You are a senior SAP SuccessFactors Employee Central consultant
explaining a data migration error to an HR manager who is not technical.

Field name: {error['field']}
Error type: {error['error_type']}
Problematic value: {error['bad_value']}
Technical reason: {error['description']}

Write exactly 2 sentences:
Sentence 1: Why this specific error will cause the SAP import to fail (plain English, no SAP jargon).
Sentence 2: The exact action the HR team should take to fix this cell.

Be specific. Be concise. Do not start with the word 'I'."""

    try:
        response = model.generate_content(prompt)
        explanation = response.text.strip()
        time.sleep(12)  # stay under 5 requests/minute
    except Exception as e:
        explanation = f"Could not generate explanation: {str(e)}"

    _cache[cache_key] = explanation
    return explanation