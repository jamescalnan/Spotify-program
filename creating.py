import requests
import json 
from api_keys import api_token as token
from api_keys import user_id
from rich.console import Console
c = Console()

user_id = user_id
endpoint_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"

request_body = json.dumps({
          "name": "test adding",
          "description": "python",
          "public": False
        })
response = requests.post(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json", 
                        "Authorization":f"Bearer {token}"})



url = response.json()['external_urls']['spotify']
c.print(response.json()['id'])
print(response.status_code)