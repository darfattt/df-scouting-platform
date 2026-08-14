"""
AI Client - Unified interface for Groq and Gemini scouting report generation.
Groq is the primary provider, with Gemini as a fallback.
"""

import os
import time
from typing import Optional

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except ImportError:
    pass


def _get_groq_api_key() -> Optional[str]:
    """Get Groq API key from environment."""
    return os.getenv("GROQ_API_KEY")


def _get_gemini_api_key() -> Optional[str]:
    """Get Gemini API key from environment."""
    return os.getenv("GEMINI_API_KEY")


def is_configured() -> bool:
    """Check if any AI provider is configured."""
    return bool(_get_groq_api_key()) or bool(_get_gemini_api_key())


def generate_scouting_report(
    prompt: str,
    groq_model: str = "openai/gpt-oss-120b",
    gemini_model: str = "gemini-2.0-flash",
) -> str:
    """
    Generate a scouting report. 
    Tries Groq first, then falls back to Gemini if Groq fails or is unconfigured.

    Args:
        prompt: Fully-constructed prompt with all statistics pre-computed
        groq_model: Groq model name
        gemini_model: Gemini model name (fallback)

    Returns:
        Generated scouting report as markdown string
    """
    
    # 1. Try Groq
    groq_key = _get_groq_api_key()
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            completion = client.chat.completions.create(
                model=groq_model,
                messages=[
                    {"role": "system", "content": "You are a professional football scout analyzing data-driven reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
            )
            report = completion.choices[0].message.content
            if report:
                return report
        except Exception as e:
            # Fall through to Gemini on Groq error
            print(f"Groq failed: {e}. Falling back to Gemini...")

    # 2. Try Gemini (Fallback)
    gemini_key = _get_gemini_api_key()
    if not gemini_key:
        if not groq_key:
            raise ValueError("No AI API keys configured (GROQ_API_KEY or GEMINI_API_KEY).")
        else:
            raise RuntimeError("Groq failed and GEMINI_API_KEY is not configured.")

    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")

    genai.configure(api_key=gemini_key)
    
    # Existing Gemini fallback/retry logic
    models_to_try = [gemini_model, "gemini-2.0-flash-lite", "gemini-1.5-flash-latest", "gemini-pro"]
    seen = set()
    models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]

    last_error = None
    MAX_RETRIES = 3
    RETRY_DELAYS = [5, 15, 30]

    for m in models_to_try:
        for attempt in range(MAX_RETRIES + 1):
            try:
                model = genai.GenerativeModel(m)
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_output_tokens": 1500,
                    },
                )
                return response.text
            except Exception as e:
                err_str = str(e)
                if "404" in err_str or "not found" in err_str.lower() or "not supported" in err_str.lower():
                    last_error = e
                    break
                if "429" in err_str or "quota" in err_str.lower() or "rate" in err_str.lower():
                    last_error = e
                    if attempt < MAX_RETRIES:
                        time.sleep(RETRY_DELAYS[attempt])
                        continue
                    break
                raise RuntimeError(f"Gemini API error ({m}): {err_str}")

    raise RuntimeError(f"All providers (Groq/Gemini) failed. Last Gemini error: {last_error}")
