import json


def extract_json_ld(content):
    data = []
    for script in content.find_all("script", type="application/ld+json"):
        try:
            parsed = json.loads(script.string)

        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(parsed, list):
            data.extend(parsed)
        elif isinstance(parsed, dict):
            data.append(parsed)
    return data
