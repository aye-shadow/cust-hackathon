import requests
import json
import datetime


# === FUNCTION ===
def identify_species(image_path, lat, lng, token="eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyX2lkIjo5MzE0MTIyLCJleHAiOjE3NDc2NDA0MjZ9._fpBi77Tg9NUs9wKO1MPO3z00DuIoxZz_0dzO-EXe4YW1yS2tpLa0zzdOzBE_IGx_KQROePe5eA1R0Z7q1t7WQ"):
    url = "https://api.inaturalist.org/v1/computervision/score_image"
    
    # Prepare request
    files = {'image': open(image_path, 'rb')}
    params = {}
    if lat and lng:
        params['lat'] = lat
        params['lng'] = lng
        params['date'] = datetime.date.today().isoformat()

    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    print("🔍 Sending image to iNaturalist...")
    response = requests.post(url, files=files, params=params, headers=headers)

    if response.status_code != 200:
        print("❌ Error:", response.status_code, response.text)
        return []  # Return empty list instead of None

    data = response.json()
    
    # 🔎 Raw response preview
    print("\n📦 Raw response (first result):")
    print(json.dumps(data["results"][0], indent=2))

    # Process results
    processed_results = []
    for result in data.get("results", []):
        taxon = result.get("taxon", {})
        name = taxon.get("preferred_common_name") or taxon.get("name") or "Unknown"
        rank = taxon.get("rank", "unknown")
        score = result.get("score", 0.0) * 100
        processed_results.append({
            "name": name,
            "rank": rank,
            "confidence": score
        })
        print(f"- {name} ({rank}) — Confidence: {score:.2f}%")
    
    return processed_results

