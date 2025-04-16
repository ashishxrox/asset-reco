import requests

def fetch_locations_from_api(search_term=""):
    url = "https://devapi.monetez.com/api/univerze/v1/alllocationsforMediaPlanner"
    payload = {"name": search_term}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        locations = data.get("data", [])
        return locations
    except Exception as e:
        print(f"Failed to fetch locations: {e}")
        return []
