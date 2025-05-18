import requests
import os
from typing import List, Dict
from groq import Groq
import json
from datetime import datetime
import aiohttp
import asyncio

# Initialize Groq client
groq_client = Groq(api_key="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")

# iNaturalist API configuration
INATURALIST_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyX2lkIjo5MzE0MTIyLCJleHAiOjE3NDc2NDA0MjZ9._fpBi77Tg9NUs9wKO1MPO3z00DuIoxZz_0dzO-EXe4YW1yS2tpLa0zzdOzBE_IGx_KQROePe5eA1R0Z7q1t7WQ"

async def identify_species(image_path: str, lat: float, lng: float) -> List[Dict]:
    """Identify species using iNaturalist API and enrich with common names using Groq."""
    try:
        # Upload image to iNaturalist
        async with aiohttp.ClientSession() as session:
            with open(image_path, 'rb') as image_file:
                data = aiohttp.FormData()
                data.add_field('image', image_file)
                
                headers = {
                    'Authorization': f'Bearer {INATURALIST_TOKEN}'
                }
                params = {
                    'lat': lat,
                    'lng': lng,
                    'date': datetime.now().strftime("%Y-%m-%d")
                }
                
                print("Sending request to iNaturalist with token:", INATURALIST_TOKEN)  # Debug print
                async with session.post(
                    'https://api.inaturalist.org/v1/computervision/score_image',
                    data=data,
                    headers=headers,
                    params=params
                ) as response:
                    if not response.ok:
                        print(f"iNaturalist API error: {response.status}")
                        text = await response.text()
                        print(f"Response text: {text}")
                        raise Exception(f"iNaturalist API error: {response.status}")
                        
                    json_response = await response.json()
                    results = json_response.get('results', [])
                    print("iNaturalist API response:", json.dumps(results, indent=2))  # Debug print
            
            # Process top 3 suggestions
            suggestions = []
            for result in results[:3]:
                taxon = result.get('taxon', {})
                scientific_name = taxon.get('name', '')
                common_name = taxon.get('preferred_common_name', '')
                
                # If no common name from iNaturalist, try Groq
                if not common_name:
                    common_name = get_common_name(scientific_name)
                
                suggestions.append({
                    'scientific_name': scientific_name,
                    'common_name': common_name,
                    'confidence': result.get('score', 0) * 100
                })
                
            return suggestions
    except Exception as e:
        print(f"Error in species identification: {str(e)}")
        return []

def get_common_name(scientific_name: str) -> str:
    """Get common name for a species using Groq."""
    try:
        prompt = f"What is the common name for the species '{scientific_name}'? Please provide only the most widely used common name, nothing else."
        
        chat_completion = groq_client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            model="mixtral-8x7b-32768",
            temperature=0.1,
            max_tokens=50
        )
        
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error getting common name: {str(e)}")
        return ""

