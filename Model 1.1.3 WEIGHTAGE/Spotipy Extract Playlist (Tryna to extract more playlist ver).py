import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import os.path as os
import time

# def extract_playlistID(playlists,find_playlist):
#     while True:
#         for playlist in playlists['items']:
#         ##Loop and return playlistID if found
#             if playlist["name"] == find_playlist:
#                 return playlist['id']
#         ##Show next 50 songs
#         if playlists['next']:
#             playlists = sp.next(playlists)
#         else:
#             return None
        
def extract_trackID(playlist_tracks):
    trackID_list = []
    for tracks in playlist_tracks["items"]:
        track_ID = tracks["track"]["id"]
        trackID_list.append(track_ID)
    return trackID_list

def extract_nexttrackID(playlist_tracks):
    trackID_list = []
    for tracks in playlist_tracks["items"]:
        track_ID = tracks["track"]["id"]
        trackID_list.append(track_ID)
    return trackID_list

def extract_songInfo(song):
    info = sp.track(song)
    ##Define features u wanna extract here
    id = song
    songName = info["name"]
    albumName = info["album"]["name"]
    albumID = info["album"]["id"]
    artists = info["artists"][0]["name"]
    for artist in info["artists"]:
        artist_genre = sp.artist(artist["id"])
        genre = artist_genre["genres"]
    explicit = info["explicit"]
    releaseDate = info["album"]["release_date"]
    return [id,songName,albumName,albumID,artists,genre,explicit,releaseDate]

def extract_features(song):
    info = sp.audio_features(song)[0]
    ##Define features u wanna extract here
    danceability = info["danceability"]
    energy = info["energy"]
    key = info["key"]
    loudness = info["loudness"]
    mode = info["mode"]
    speechiness = info["speechiness"]
    acousticness = info["acousticness"]
    instrumental = info["instrumentalness"]
    liveness = info["liveness"]
    valence = info["valence"]
    tempo = info["tempo"]
    duration_ms = info["duration_ms"]
    time_signature = info["time_signature"]
    return [danceability,energy,key,loudness,mode,speechiness,acousticness,instrumental,liveness,
            valence,tempo,duration_ms,time_signature]

#Auth Stuff
SpotifyClientCredentials(client_id="21ff73a9b5a94ea8b3a969b906baead1", client_secret="3761e7947ef542149467196a07cf2563")
sp = spotipy.Spotify(auth_manager=auth_manager)

##INDICATE THE PLAYLIST U WANNA ADD FROM THE USER (IN THIS CASE SPOTIFY IS THE USER AND TOP 50 IS THE PLAYLIST)
# user = "spotify"
# playlists = sp.user_playlists(user, limit=50)

## Hide this if you are inserting your own playlist ID
# for find_playlist in playlists_name:
#     found_ID = extract_playlistID(playlists, find_playlist)
#     if found_ID != None:
#         playlists_ID.append(found_ID)
    
playlists_name = []
playlists_ID = []

## Ask to insert playlist ID
url = input("Insert Spotify Playlist Link: ")
def extract_playlist_id(url):
    # Split the URL by '/'
    parts = url.split('/')
    # The playlist ID is the second-to-last part of the URL
    part = parts[-1].split('?')[0]  # Remove everything after '?'
    return part
url = extract_playlist_id(extract_playlist_id(url))
print(url)

playlists_ID.append(url)
    
# Get Playlist Name

playlist_info = sp.playlist(url)
name = playlist_info["name"]
print(name)
playlists_name.append(name)

##Get Info in Playlist with PlaylistID 
tracksID = {}

track_list = []
playlist_tracks = sp.playlist(playlists_ID[i])
playlist_tracks = playlist_tracks["tracks"]
track_list = extract_trackID(playlist_tracks)
for page in range(0,2):
    if playlist_tracks['next']:
        print("More than 100 Songs Detected. WAITT")
        time.sleep(30)
        print("Looking at next 100 songs")
        playlist_tracks = sp.next(playlist_tracks)
        track_list += extract_nexttrackID(playlist_tracks)
tracksID[playlists_name[i]] = track_list


##Get Other Track Details
results_tocsv = []
results_tocsv.append(["id","songName","albumName","albumID","artist","genre","explicit","releaseDate",
                     "danceability","energy","key","loudness","mode","speechiness","acousticness","instrumental","liveness",
                    "valence","tempo","duration_ms","time_signature"])
for i in playlists_name:  
    count = 0
    for song in tracksID[i]:
        time.sleep(1)
        song_info = extract_songInfo(song)
        ##Get Audio Features
        song_features = extract_features(song)
        song_info.extend(song_features)
        results_tocsv.append(song_info)
        count += 1
        
        if count == 100:
            print("Trying not to let spotify kill me. 30s wait :D")
            time.sleep(30)
            count = 0

##Use pandas to convert to dataframe
df = pd.DataFrame(results_tocsv[1:], columns = results_tocsv[0])

##Export to CSV
file_name = "User_Playlist.csv"
if os.exists(file_name):
    df1 = pd.read_csv(file_name, encoding="utf_8_sig")
    df2 = df
    df1 = df1.drop(columns=['Unnamed: 0'])
    merged = pd.concat([df1,df2])
    merged = merged.drop_duplicates(ignore_index=True)
    merged.to_csv(file_name, encoding='utf_8_sig')
else:
    df.to_csv(file_name, encoding='utf_8_sig')
print("20s Cooldown...")
time.sleep(20)

