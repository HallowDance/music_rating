import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

def create_spotify_client():
    # Set your Spotify credentials as environment variables
    os.environ["SPOTIPY_CLIENT_ID"] = "2314a5baf151457885b04665720ae742"
    os.environ["SPOTIPY_CLIENT_SECRET"] = "814ef862141f4b2fb9b95d262b5d88f4"
    os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8080"  # Redirect URI for authentication

    # Create a Spotify API client with OAuth authentication
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-read-currently-playing user-read-playback-state"))

    return sp

def get_currently_playing_song(sp):
    # Get the currently playing track
    currently_playing = sp.current_playback()

    if currently_playing is not None and "item" in currently_playing:
        track_info = currently_playing["item"]
        song_title = track_info["name"]
        artist_name = track_info["artists"][0]["name"]
        return song_title, artist_name

    return None, None

def main():
    sp = create_spotify_client()
    last_song_title, last_artist_name = None, None

    print("Listening for Spotify song notifications...")

    try:
        while True:
            song_title, artist_name = get_currently_playing_song(sp)

            # Check if there's a change in the currently playing song
            if song_title != last_song_title or artist_name != last_artist_name:
                if song_title and artist_name:
                    print(f"Currently playing: {song_title} - {artist_name}")
                else:
                    print("No song currently playing.")

                # Update the last known song information
                last_song_title, last_artist_name = song_title, artist_name

            # Wait for a few seconds before checking again
            time.sleep(10)
    except KeyboardInterrupt:
        print("Script interrupted.")
        pass

if __name__ == "__main__":
    main()
