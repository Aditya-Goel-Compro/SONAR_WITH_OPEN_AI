from openai import OpenAI
import json


def generate_fix(api_key, issue, code):

    client = OpenAI(api_key=api_key)

    print("\n========== GENERATING AI FIX ==========")
    print("Issue:", issue.get("key"))
    print("Rule:", issue.get("rule"))

    prompt = f"""
You are a senior TypeScript engineer.

Fix ONLY the issue using best practices.

STRICT RULES:
- Modify ONLY the problematic line
- Do NOT refactor whole code
- Do NOT add explanation

Return STRICT JSON:
{{
    "fixed_code": "<code>"
}}

Code:
{code}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Expert TypeScript Sonar fixer"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(content)
            return parsed  # ✅ always return dict
        except:
            print("⚠ Invalid JSON, wrapping manually")
            return {"fixed_code": content}

    except Exception as e:

        error_msg = str(e)

        print("\n❌ OPENAI ERROR")

        if "insufficient_quota" in error_msg or "429" in error_msg:
            print("🚨 Quota/Rate limit hit")
            return "QUOTA_EXCEEDED"

        print("Error:", error_msg)
        return None