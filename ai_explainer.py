from groq import Groq
import streamlit as st

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

_cache = {}

def explain_error(error: dict) -> str:
    cache_key = f"{error['field']}|{error['error_type']}|{error['bad_value']}"
    if cache_key in _cache:
        return _cache[cache_key]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""You are a senior SAP SuccessFactors Employee Central consultant
explaining a data migration error to an HR manager who is not technical.

Field name: {error['field']}
Error type: {error['error_type']}
Problematic value: {error['bad_value']}
Technical reason: {error['description']}

Write exactly 2 sentences:
Sentence 1: Why this error will cause the SAP import to fail (plain English, no jargon).
Sentence 2: The exact action the HR team should take to fix this cell.

Be specific. Be concise. Do not start with the word I."""
            }],
            max_tokens=150
        )
        explanation = response.choices[0].message.content.strip()
    except Exception as e:
        explanation = f"Could not generate explanation: {str(e)}"

    _cache[cache_key] = explanation
    return explanation
