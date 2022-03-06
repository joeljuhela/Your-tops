import io
import json
import requests
import base64
from requests.auth import HTTPBasicAuth
from datetime import date
from cover.image import create_recaman_image

from settings import CLIENT_ID, CLIENT_SECRET, SPOTIFY_API_URL


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, access_token):
        self.token = access_token

    def __call__(self, r):
        r.headers["authorization"] = f"Bearer {self.token}"
        return r


class SpotifyAPI:
    def __init__(self, access_token):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.api_url = SPOTIFY_API_URL
        self.access_token = access_token

    def get_user_top_items(self, top_type, time_range):
        """
        Gets users top items, for options of top_type and time_range, see
        https://developer.spotify.com/console/get-current-user-top-artists-and-tracks/
        """
        r = requests.get(
            f"{self.api_url}/me/top/{top_type}",
            auth=BearerAuth(self.access_token),
            params={
                "limit": 30,
                "time_range": time_range
            }
        )
        if r.status_code == 200:
            body = r.json()
            return body['items']
        else:
            print('Failed to get items')

    def get_top_tracks_uris(self):
        """Gets the users top tracks of the last 4 weeks"""
        tracks = self.get_user_top_items("tracks", "short_term")
        uris = [x['uri'] for x in tracks]
        return uris

    def get_user(self):
        """Gets the Spotify User associated with the access token"""
        r = requests.get(
            f"{self.api_url}/me",
            auth=BearerAuth(self.access_token)
        )

        if r.status_code == 200:
            body = r.json()
            print("Get User")
            return body
        elif r.status_code == 401:
            print("Failed to get User Id")

    def create_playlist(self, user_id):
        """Creates a new private playlist and returns the id"""
        today = date.today()
        name = f"Your Top Tracks {today.strftime('%B')} {today.year}"
        r = requests.post(
            f"{self.api_url}/users/{user_id}/playlists",
            json={
                "name": name,
                "public": False,
                "description": "Created by Your Tops script"
            },
            auth=BearerAuth(self.access_token),
        )

        if r.status_code == 201:
            body = r.json()
            playlist_id = body['id']
            print("Create a new playlist")
            return playlist_id
        elif r.status_code == 401:
            print("Failed to create a playlist")

    def add_tracks_to_playlist(self, playlist_id, track_uris):
        """Adds tracks to a playlist"""
        r = requests.post(
            f"{self.api_url}/playlists/{playlist_id}/tracks",
            json={"uris": track_uris},
            auth=BearerAuth(self.access_token)
        )

        if r.status_code == 401:
            print("Failed to add tracks to playlist")
        else:
            print("Add tracks to playlist")

    def add_playlist_image(self, playlist_id):
        buf = io.BytesIO()
        create_recaman_image(buf, 65, False)
        b64_string = base64.b64encode(buf.read()).decode('utf-8')
        r = requests.put(
            f"{self.api_url}/playlists/{playlist_id}/images",
            data=b64_string,
            headers={
                'content-type': 'image/jpeg'
            },
            auth=BearerAuth(self.access_token)
        )
        buf.close()

        if r.status_code == 401:
            print('Failed to Add Playlist Image')
        else:
            print('Add Playlist Image')

    def create_monthly_top_list(self):
        top_tracks_uris = self.get_top_tracks_uris()
        user = self.get_user()
        playlist_id = self.create_playlist(user['id'])
        self.add_playlist_image(playlist_id)
        self.add_tracks_to_playlist(playlist_id, top_tracks_uris)


def get_access_token(refresh_token):
    """Gets access token for the user"""
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
    )

    if r.status_code == 200:
        body = r.json()
        print("Get Access Token")
        return body['access_token']


if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.load(f)

    for token in config["tokens"]:
        user_access_token = get_access_token(token['refresh_token'])

        SpotifyAPI(
            user_access_token,
        ).create_monthly_top_list()
