import requests


def get_sonar_issues(sonar_url, sonar_token, project_key):

    url = f"{sonar_url}/api/issues/search"

    params = {
        "componentKeys": project_key,
        "rules": "squid:S3776",
        "types": "CODE_SMELL",
        "ps": 1
    }

    print("\n========== SONAR REQUEST ==========")
    print("Base URL:", url)
    print("Params:", params)

    req = requests.Request("GET", url, params=params).prepare()
    print("Full API URL:", req.url)

    try:
        response = requests.get(
            url,
            auth=(sonar_token, ""),
            params=params,
            timeout=30
        )
    except Exception as e:
        print("❌ Request failed:", e)
        return []

    print("\n========== SONAR RESPONSE ==========")
    print("Status Code:", response.status_code)

    if response.status_code != 200:
        print("❌ Sonar API error")
        print(response.text)
        return []

    data = response.json()

    total = data.get("total", 0)
    issues = data.get("issues", [])

    print("Total Cognitive Complexity Issues:", total)
    print("Issues returned:", len(issues))

    return issues