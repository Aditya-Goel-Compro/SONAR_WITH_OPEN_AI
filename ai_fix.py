from openai import OpenAI
import json


def generate_fix(api_key, issue, code, target_line):

    client = OpenAI(api_key=api_key)

    print("\n========== GENERATING AI FIX ==========")
    print("Issue:", issue.get("key"))
    print("Rule:", issue.get("rule"))

    # extract sonar data
    issue_message = issue.get("message", "")
    rule = issue.get("rule", "")
    severity = issue.get("severity", "")

    prompt = f"""
You are fixing a Sonar issue in code.

SONAR ISSUE:
Rule: {rule}
Message: {issue_message}
Severity: {severity}

TASK:
Fix ONLY the TARGET LINE.

STRICT RULES:
- Modify ONLY the target line
- Do NOT modify other lines
- Do NOT add or remove lines
- Keep original logic same
- If fix is unclear → return the SAME line

OUTPUT FORMAT:
{{"fixed_line": "..."}}

TARGET LINE:
{target_line}

CODE SNIPPET:
{code}
"""

    try:
        print("🚀 Sending to prompt to AI ..." , prompt)

        response = client.chat.completions.create(
            model="gpt-4.1-mini",   # ✅ correct model
            temperature=0,
            max_tokens=120,
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict code fixer. Return only JSON. No explanation."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )

        content = response.choices[0].message.content.strip()

        print("🤖 RAW OUTPUT:", content)

        # 🔒 safe JSON extraction
        if not content.startswith("{"):
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1:
                content = content[start:end + 1]

        parsed = json.loads(content)

        fixed_line = parsed.get("fixed_line")

        # 🚨 final safety guard
        if not fixed_line or len(fixed_line.strip()) == 0:
            print("⚠ Empty fix from AI")
            return None

        return {
            "fixed_line": fixed_line.strip(),
            "prompt": prompt,
            "raw_output": content
        }

    except Exception as e:
        print("\n❌ OPENAI ERROR:", str(e))
        return None