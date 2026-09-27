import json
import urllib.request
import urllib.parse
import os

# Free Public API: GBIF (Global Biodiversity Information Facility) Species Search API
# URL: https://api.gbif.org/v1/species/match

def fetch_botanical_taxonomy(plant_name: str) -> dict:
    """Fetches official scientific taxonomy and classification data for a plant species.

    Args:
        plant_name: Common or scientific name of the plant (e.g. Monstera deliciosa, Fiddle Leaf Fig, Peace Lily).

    Returns:
        A dictionary containing scientific name, family, genus, rank, and classification confidence.
    """
    try:
        encoded_query = urllib.parse.quote(plant_name)
        url = f"https://api.gbif.org/v1/species/match?name={encoded_query}&verbose=false"
        
        req = urllib.request.Request(url, headers={"User-Agent": "GreenhouseAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            
            if data.get("matchType") != "NONE":
                return {
                    "query": plant_name,
                    "scientific_name": data.get("scientificName"),
                    "family": data.get("family"),
                    "genus": data.get("genus"),
                    "rank": data.get("rank"),
                    "match_confidence": f"{data.get('confidence', 0)}%"
                }
            return {"query": plant_name, "error": f"No botanical taxonomy match found for '{plant_name}'."}
            
    except Exception as e:
        return {"query": plant_name, "error": f"Failed to query botanical taxonomy API: {str(e)}"}
