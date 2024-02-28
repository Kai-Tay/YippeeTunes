##Dependencies
import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
import boto3

##Webscrap Dependencies
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

## Website Initial Design Stuff
def extract_playlist_id(url):
    # Split the URL by '/'
    parts = url.split('/')
    # The playlist ID is the second-to-last part of the URL
    part = parts[-1].split('?')[0]  # Remove everything after '?'
    return part


st.title("POOPOO💩 (YippeeTunes) spotify recommender!")
user_url = st.text_input("Playlist url?")
url = extract_playlist_id(user_url)

## URL PLAYLIST EXTRACTION
## FUNCTIONS FOR EXTRACTION
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



if st.button("Search"):
    
    st.write("DAPOOPOO IN PROGRESS...")
    st.text("")
    bar = st.progress(10, text="COOKING!")
    st.text("")
    #Auth Stuff
    auth_manager = SpotifyClientCredentials(client_id="21ff73a9b5a94ea8b3a969b906baead1", client_secret="3761e7947ef542149467196a07cf2563")
    sp = spotipy.Spotify(auth_manager=auth_manager)
        
    # Get Playlist Name
    st.write("Obtaining the Following Playlists: ")
    playlist_info = sp.playlist(url)
    name = playlist_info["name"]
    st.write(name)
    st.text("")

    #Get Info in Playlist with PlaylistID 
    track_list = []
    playlist_tracks = sp.playlist(url)
    playlist_tracks = playlist_tracks["tracks"]
    track_list = extract_trackID(playlist_tracks)
    for page in range(0,2):
        if playlist_tracks['next']:
            st.write("More than 100 Songs Detected. WAITT")
            time.sleep(30)
            st.write("Looking at next 100 songs")
            st.text("")
            playlist_tracks = sp.next(playlist_tracks)
            track_list += extract_nexttrackID(playlist_tracks)


    ##Get Other Track Details
    results_tocsv = []
    results_tocsv.append(["id","songName","albumName","albumID","artist","genre","explicit","releaseDate",
                        "danceability","energy","key","loudness","mode","speechiness","acousticness","instrumental","liveness",
                        "valence","tempo","duration_ms","time_signature"])
    count = 0
    for song in track_list:
        time.sleep(1)
        song_info = extract_songInfo(song)
        ##Get Audio Features
        song_features = extract_features(song)
        song_info.extend(song_features)
        results_tocsv.append(song_info)
        count += 1
        ## TRYNA NOT GET BANNED
        if count == 100:
            st.write("Trying not to let spotify kill me. 30s wait :D")
            st.text("")
            time.sleep(30)
            count = 0

    ##Use pandas to convert to dataframe
    userDF = pd.DataFrame(results_tocsv[1:], columns = results_tocsv[0])

    ## WEB SCRAP  
    ## FUNCTION FOR WEBSCRAP!
    def scrap_genre(artistName):
        ##URL of website to scrap
        url = f"https://www.getgenre.com/artist/{artistName}"

        @st.cache_resource
        def get_driver():
            return webdriver.Chrome(ChromeDriverManager().install(), options=options)

        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')

        driver = get_driver()
        # WAIT FOR BUTTON TAG TO LOAD BEFORE CONTINUING
        driver.implicitly_wait(20)
        driver.get(url)

        try:
            classtext = "MuiButtonBase-root MuiButton-root MuiButton-outlined MuiButton-outlinedPrimary MuiButton-sizeMedium MuiButton-outlinedSizeMedium MuiButton-root MuiButton-outlined MuiButton-outlinedPrimary MuiButton-sizeMedium MuiButton-outlinedSizeMedium css-x3ahaf"
            button = driver.find_element_by_xpath(f"//button[contains(@class, '{classtext}')]")
            time.sleep(2)
            # Parse the HTML content of the button with BS4
            html = button.get_attribute("outerHTML")
            driver.close()
            driver.quit()
            st.cache_resource.clear()
            #Use BS4 to read HTML segement and extract Genre Text
            soup = BeautifulSoup(html, "html.parser")
            # Find html button tag with class to obtained genre text
            genre = soup.find('button', class_=classtext).get_text()
            return genre.lower()
        except:
            driver.close()
            driver.quit()
            pass
    
    def download_file_from_s3(access_key, secret_key, bucket_name):
        # Initialize Boto3 S3 client with provided credentials
        s3 = boto3.resource(
            service_name='s3',
            region_name='ap-southeast-2',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
    
        try:
            # Load csv file directly into python
            obj = s3.Bucket(bucket_name).Object('spotify_data_cleaned.csv').get()
            return obj
        except Exception as e:
            st.write(f"Error downloading file: {e}")

    ##Import Dataset
    access_key = 'AKIA33QBIU3Z3MSAVI4M'
    secret_key = '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'
    bucket_name = 'yippeetunes'
    file = download_file_from_s3(access_key, secret_key, bucket_name)
    bar.progress(20, text="COOKING!")
    databaseDF = pd.read_csv(file['Body'], index_col=0)
    bar.progress(50, text="COOKING!")
    databaseDF = databaseDF.dropna()

    #Extract all genres from dataset
    datasetGenres_list = []
    for i in databaseDF["genre"]:
        if i not in datasetGenres_list:
            datasetGenres_list.append(i)

    song_genres_list = []

    ## Dict for scrapped genres to avoid scraping same artist multiple times
    scrap_dict = {}

    ##Find Playlist Songs in Database and replace genre
    for index, row in userDF.iterrows():
        id = row["id"]
        artistName = row["artist"]

        ##List to include all genres from one song
        one_song_genre = []

        ##Check if artistName is already scrapped or tracked
        if artistName in scrap_dict.keys():
            genre = scrap_dict[artistName]
            one_song_genre.append(genre)
        else:
            ##variable to check if song in database
            dataset_genre = databaseDF[databaseDF["id"] == id]

            if not dataset_genre.empty:
                ##METHOD1 - Copying Dataset genre to User Dataset
                one_song_genre = dataset_genre["genre"].to_list()
                for i in one_song_genre:
                    scrap_dict[artistName] = i
            else:
                ##METHOD2 - Web Scraping
                genre = scrap_genre(artistName)
                scrap_dict[artistName] = genre
                if genre != "":
                    one_song_genre.append(genre)

        ##CHECKS IF METHOD 1/2 managed to obtain genre data
        song_genres_list.append(one_song_genre)

    userDF["genre"] = song_genres_list
    st.write("User Playlist Results:")
    st.dataframe(userDF)
    st.text("")
    bar.progress(70, text="COOKING!")

    # (2) Find top 3 genres in playlist
    exploded_df = userDF.explode('genre')

    freq = exploded_df["genre"].value_counts(sort=True)

    genres_count = dict(freq.head(3))
    genre_top3 = list(genres_count.keys())
            
    st.write("Top 3 Genre's of User Playlist:" + str(genre_top3))
    st.text("")
    bar.progress(80, text="COOKING!")
    ##MODEL Handling
    ##FUNCTION FOR MODEL!
    def ohe_prep(df, column, new_name): 
        ''' 
        Create One Hot Encoded features of a specific column
        ---
        Input: 
        df (pandas dataframe): Spotify Dataframe
        column (str): Column to be processed
        new_name (str): new column name to be used
            
        Output: 
        tf_df: One-hot encoded features 
        '''
        
        tf_df = pd.get_dummies(df[column])
        
        feature_names = tf_df.columns
        tf_df.columns = [new_name + "|" + str(i) for i in feature_names]
        tf_df.reset_index(drop = True, inplace = True)  
        return tf_df

    def get_features_database(databaseDF):
        #Select Features
        databaseDF = databaseDF[["id","songName",
                    "danceability","energy","key","loudness","mode","speechiness","acousticness","instrumental","liveness",
                    "valence","tempo","type"]]

        #OHE Features
        key_ohe = ohe_prep(databaseDF, 'key','key') * 0.5
        mode_ohe = ohe_prep(databaseDF, 'mode','mode') * 0.5

        ##Normalise/Scale Audio Columns
        float_cols = databaseDF.dtypes[databaseDF.dtypes == 'float64'].index.values
        floats = databaseDF[float_cols].reset_index(drop = True)
        scaler = MinMaxScaler()
        floats_scaled = pd.DataFrame(scaler.fit_transform(floats), columns = floats.columns) * 0.2

        ##Combine all Features
        final = pd.concat([floats_scaled, key_ohe, mode_ohe, databaseDF["type"]], axis = 1)
        return final

    def generate_rec(databaseDF, database_vector, user_vector, genre_top3):
        #Cosine Similarity
        databaseDF["sim"] = cosine_similarity(database_vector,user_vector)

        #Drop rows with different genre from top 3 genres
        if len(genre_top3) == 1:
            databaseDF = databaseDF[(databaseDF["genre"] == genre_top3[0])]
        elif len(genre_top3) == 2:
            databaseDF = databaseDF[(databaseDF["genre"] == genre_top3[0]) | (databaseDF["genre"] == genre_top3[1])]
        else:
            databaseDF = databaseDF[(databaseDF["genre"] == genre_top3[0]) | (databaseDF["genre"] == genre_top3[1]) | (databaseDF["genre"] == genre_top3[2])]
        #Sort and recommend top 5 with same genres
        rec_top5 = databaseDF.sort_values('sim',ascending = False).head()
        return rec_top5
    

    #Selects database columns that we want
    databaseDF = databaseDF[["id","artist","songName", "genre","danceability","energy","key","loudness","mode","speechiness","acousticness","instrumental","liveness",
            "valence","tempo",]]

    #Create new feature/column of artist_songName
    databaseDF["artist_songName"] = databaseDF["artist"] + "_" + databaseDF["songName"]

    ##Change all values to lowercase
    databaseDF["artist_songName"] = databaseDF["artist_songName"].str.lower()

    #Check for duplicates in database
    databaseDF = databaseDF.drop_duplicates(subset=["artist_songName"],ignore_index= True)

    #Selects user playlust columns that we want
    userDF = userDF[["id","artist","songName","danceability","energy","key","loudness","mode","speechiness","acousticness","instrumental","liveness",
            "valence","tempo",]] 

    #Create new feature/column of artist_songName to remove duplicate later on
    userDF["artist_songName"] = userDF["artist"] + "_" + userDF["songName"]
    ##Change all values to lowercase
    userDF["artist_songName"] = userDF["artist_songName"].str.lower()

    #Check for duplicates in user Playlist
    userDF = userDF.drop_duplicates(subset=["artist_songName"],ignore_index= True)

    #Merge user + dataset dataframe to normalise 
    #Normalise takes min and max in dataframe as reference and change it to 0 and 1 respectively

    #Group the dataframe as we gonna split it again alter
    databaseDF["type"] = "Dataset"
    userDF["type"] = "User"

    #Merge the 2 datasets together
    combinedDF = pd.concat([databaseDF,userDF], ignore_index=True)

    #Check for duplicates between user and Database
    combinedDF = combinedDF.drop_duplicates(subset=["artist_songName"], keep="last",ignore_index= True)

    ##Update databaseDF with removed songs from user Playlist
    databaseDF = combinedDF[(combinedDF["type"]== "Dataset")]

    ##Normalise and get Vectors for Dataset + User
    normalised_vector = get_features_database(combinedDF)

    ##Seperate User from databaseDF 
    database_vector = normalised_vector[normalised_vector["type"] == "Dataset"]
    user_vector = normalised_vector[normalised_vector["type"] == "User"]

    #Drop "type" column
    database_vector = database_vector.drop(columns="type")
    user_vector = user_vector.drop(columns="type")
    databaseDF = databaseDF.drop(columns=["type"])

    ##Single Vector Creation (To be Changed with Clustering Model)
    final_user_vector_list = []
    for i in user_vector.columns:
        final_user_vector_list.append(user_vector[i].sum()/len(user_vector[i]))

    #Putting into a vector dataframe
    final_user_vector = pd.DataFrame(columns=user_vector.columns,)
    final_user_vector.loc[0] = final_user_vector_list

    ##Generate Recc Songs
    result = generate_rec(databaseDF,database_vector,final_user_vector, genre_top3)
    bar.progress(100, text="COOKING!")
    st.write("\nHere's what we cooked!")
    st.dataframe(result)