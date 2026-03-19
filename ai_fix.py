from openai import OpenAI


def generate_fix(api_key, issue, code):

    client = OpenAI(api_key=api_key)

    print("\n========== GENERATING AI FIX ==========")
    print("Issue:", issue.get("key"))
    print("Rule:", issue.get("rule"))

    prompt = f"""
You are a senior JavaScript engineer fixing a SonarQube issue.

Rule: {issue.get("rule")}
Description: {issue.get("message")}

Only fix the problematic line.

Code:
{code}

Return ONLY the corrected code.
"""

    try:

        response = client.chat.completions.create(
            model="codex-1.3",
            messages=[
                {"role": "system", "content": "You fix SonarQube issues."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:

        error_msg = str(e)

        print("\n❌ OPENAI ERROR")
        print("Issue:", issue.get("key"))

        # Detect quota exceeded
        if "insufficient_quota" in error_msg:
            print("🚨 OpenAI quota exhausted")
            return "QUOTA_EXCEEDED"

        elif "429" in error_msg:
            print("🚨 Rate limit reached")
            return "QUOTA_EXCEEDED"

        else:
            print("Error:", error_msg)
            return None