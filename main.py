import json
import string
from api_keys import api_token as token
from api_keys import user_id
from rich.console import Console
import requests, time

c = Console()


def string_filter(str_input: str):
    return str_input.lower().strip().translate(str.maketrans('', '', string.punctuation))

def get_song_uri(q: str, content_type: str = "track", artist: str = ""):
    query = f'https://api.spotify.com/v1/search?q={q}&type={content_type}'

    response = requests.get(query, 
                headers={"Content-Type":"application/json", 
                            "Authorization":f"Bearer {token}"})

    json_response = response.json()
    uris = []

    for item in json_response['tracks']['items']:
        #c.print(item)
        #input()
        song_name = string_filter(item['name'])
        artist_name = string_filter(item['artists'][0]['name'])
        if ((song_name == string_filter(q) and artist_name == string_filter(artist))
            or (song_name == string_filter(artist) and artist == string_filter(q))
            or (song_name in string_filter(q) and artist_name in string_filter(artist))
            or (artist_name in string_filter(q) and song_name in string_filter(artist))):
            uris.append(item['uri'])

    return list(set(uris))

def get_song_info(file_name: str):
    file = open(file_name, "r", encoding="utf8").read().split("\n")
    song_info = []
    
    for line in file:
        if " - " not in line: continue
        try:
            split_line = line.split(" ")
            artist, song_name = " ".join(split_line[1:]).split(" - ")
            song_info.append((artist, song_name))
        except ValueError:
            c.print(f"Error with {line}")
            input()

    return song_info


def get_playlists(user_id):
    endpoint_url = f"https://api.spotify.com/v1/users/{user_id}/playlists?limit=50"
    response = requests.get(endpoint_url, 
            headers={"Content-Type":"application/json", 
                        "Authorization":f"Bearer {token}"})
    json_response = response.json()
    info = []
    for item in json_response['items']:
        info.append((item['name'], item['id']))
    
    return info[:20]

songs = get_song_info("song_names.txt")
padding_number = len(str(len(songs))) + 6
c.clear()
all_uris = []

for i, song in enumerate(songs):
    padding = f"({i + 1}/{len(songs)})"
    with c.status(f"searching for {song[1]}", spinner="point"):
        potential_uri = get_song_uri(song[1], "track", song[0])
    if len(potential_uri) == 0:
        c.print(f"[*] [grey]({i + 1}/{len(songs)}){' ' * (padding_number - len(padding))}Failed to find: [red]{song[1]}")
    else:
        suffix = f"Found: [green]{song[1]}"
        c.print(f"[*] [grey]({i + 1}/{len(songs)}){' ' * (padding_number - len(padding))}Found: [green]{song[1]}")
        all_uris.append(potential_uri[0])

if len(all_uris) == 0:
    c.print(f"\n\nNo songs to add")
else:
    playlist_id = ""
    
    time.sleep(0.3)
    c.clear()

    c.print("[*] Press 1 to make a new playlist, press 2 to add to existing playlist")
    choice = c.input("\n[*] ")
    c.clear()
    
    if choice == "1":
        playlist_name = c.input("[*] name of playlist: ")
        endpoint_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        request_body = json.dumps({
          "name": playlist_name,
          "description": "",
          "public": False
        })
        response = requests.post(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json", 
                                "Authorization":f"Bearer {token}"})
        url = response.json()['external_urls']['spotify']
        if response.status_code == 201:
            c.print("\n[*] Playlist successfully created")
            playlist_id = (response.json()['id'])
            c.print(f"[*] Playlist ID: [cyan]{playlist_id}")
            c.print(f"[*] Added {len(all_uris)} song{'s' if len(all_uris) > 1 else ''} to [green]{playlist_name}")
        else:
            c.print(f"[*] [red]Error code: {response.status_code}")
    else:
        with c.status("Searching for playlists...", spinner="point"):
            playlist_info = get_playlists(user_id)
        
        c.print("[*] Available playlists:\n")
        for i, item in enumerate(playlist_info):
            c.print(f"[*] {i + 1}{' ' * (1 if i <= 8 else 0)} : {item[0]}")
        
        user_choice = int(c.input(f"\n[*] Playlist number: ")) - 1
        playlist_id = playlist_info[user_choice][1]
        c.clear()
        c.print(f"[*] Added {len(all_uris)} song{'s' if len(all_uris) > 1 else ''} to [green]{playlist_info[int(user_choice)][0]}")
    
    endpoint_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    request_body = json.dumps({"uris" : all_uris})
    response = requests.post(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json", 
                            "Authorization":f"Bearer {token}"})

    c.print("[*] Program closing")