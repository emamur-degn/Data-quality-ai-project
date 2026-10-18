import os
from openai import OpenAI

def explain_findings(summary: dict, issues: list, anomalies: int) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Add it to your environment before enabling AI analysis.")

    client = OpenAI(api_key=api_key)
    # Send aggregate statistics only; do not send raw customer records.
    prompt = f"""
You are a data quality engineer. Explain these dataset-level findings in plain English.
Do not claim certainty beyond the evidence. Give:
1. Executive summary
2. Most important likely causes
3. Recommended validation/fixes
4. Follow-up checks
Dataset summary: {summary}
Quality issues (aggregated): {issues[:50]}
Anomaly record count: {anomalies}
"""
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        input=prompt,
    )
    return response.output_text
