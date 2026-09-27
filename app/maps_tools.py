import os
import json
import urllib.request
import urllib.parse
import logging

logger = logging.getLogger(__name__)

def geocode_address(address: str) -> dict:
    """Turns an address or location description into geographical coordinates (lat, lng).

    Args:
        address: Street address or city name (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'San Francisco, CA').

    Returns:
        A dictionary with formatted address, latitude, and longitude.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key or api_key == "PASTE_KEY_HERE":
        return {
            "address": address,
            "error": "GOOGLE_MAPS_API_KEY is not set in environment or .env. Please provide a valid Google Maps API Key."
        }
        
    try:
        encoded_address = urllib.parse.quote(address)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data.get("status") == "OK" and data.get("results"):
                first_result = data["results"][0]
                loc = first_result["geometry"]["location"]
                return {
                    "input_address": address,
                    "formatted_address": first_result.get("formatted_address"),
                    "location": {
                        "latitude": loc["lat"],
                        "longitude": loc["lng"]
                    }
                }
            return {"address": address, "error": f"Geocoding API status: {data.get('status')}"}
    except Exception as e:
        return {"address": address, "error": f"Geocoding failed: {str(e)}"}


def find_nearby_places(latitude: float, longitude: float, place_type: str = "florist", radius_meters: int = 5000) -> dict:
    """Finds nearby places of a given type near specified coordinates using Places API (New).

    Args:
        latitude: Latitude coordinate.
        longitude: Longitude coordinate.
        place_type: Type of place to search for (e.g. 'florist', 'park', 'store', 'nursery').
        radius_meters: Radius to search in meters (default 5000).

    Returns:
        A list of nearby places with name, formatted address, and coordinates.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key or api_key == "PASTE_KEY_HERE":
        return {
            "error": "GOOGLE_MAPS_API_KEY is not set in environment or .env. Please provide a valid Google Maps API Key."
        }

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location"
    }
    
    payload = {
        "includedTypes": [place_type],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": float(radius_meters)
            }
        }
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            results = []
            for p in data.get("places", []):
                results.append({
                    "name": p.get("displayName", {}).get("text", "Unknown"),
                    "formatted_address": p.get("formattedAddress", ""),
                    "location": p.get("location", {})
                })
            return {
                "latitude": latitude,
                "longitude": longitude,
                "place_type": place_type,
                "places": results
            }
    except Exception as e:
        return {"error": f"Places API (New) search failed: {str(e)}"}
