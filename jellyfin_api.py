import os
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()


class JellyfinClient:
    """Minimal Jellyfin client holding connection details."""

    def __init__(self, base_url, api_key, user_id=None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        # optional: restrict to one user's sessions. Accepts either the
        # Jellyfin user GUID or the human username (Sessions reports both).
        self.user_id = user_id


def create_jellyfin_client():
    # Create a Jellyfin client from environment variables.
    base_url = os.getenv("JELLYFIN_URL")
    api_key = os.getenv("JELLYFIN_API_KEY")
    user_id = os.getenv("JELLYFIN_USER_ID")  # optional

    if not base_url or not api_key:
        raise RuntimeError(
            "JELLYFIN_URL and JELLYFIN_API_KEY must be set to use the Jellyfin source."
        )
    return JellyfinClient(base_url, api_key, user_id)


def get_currently_playing_song(client):
    # Ask Jellyfin which sessions exist; a session that is actively playing
    # something carries a "NowPlayingItem". Mirrors spotify_api's return shape.
    response = requests.get(
        f"{client.base_url}/Sessions",
        headers={"X-Emby-Token": client.api_key},
        timeout=5,
    )
    response.raise_for_status()
    sessions = response.json()

    for session in sessions:
        item = session.get("NowPlayingItem")
        if not item:
            continue

        # Optionally restrict to a specific user's playback. Match the
        # configured value against either the user GUID or the username so
        # that a friendly name like "admin" works as well as the raw id.
        if client.user_id:
            wanted = client.user_id.strip().lower()
            ids = {
                str(session.get("UserId", "")).lower(),
                str(session.get("UserName", "")).lower(),
            }
            if wanted not in ids:
                continue

        # A music-rating app only cares about audio, not movies/TV.
        if item.get("Type") not in ("Audio", None):
            continue

        song_title = item.get("Name")
        artists = item.get("Artists") or []
        artist_name = ", ".join(artists) if artists else item.get("AlbumArtist")

        if song_title:
            return song_title, artist_name

    return None, None
