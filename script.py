import io
import json
import requests
import base64
from requests.auth import HTTPBasicAuth
from datetime import date
from cover.image import create_recaman_image


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, access_token):
        self.token = access_token

    def __call__(self, r):
        r.headers["authorization"] = f"Bearer {self.token}"
        return r


class SpotifyAPI:
    def __init__(self, refresh_token, client_id, client_secret, api_url):
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_url = api_url

        self.access_token = self.get_access_token()

    def get_access_token(self):
        """Gets access token for the user"""
        r = requests.post(
            "https://accounts.spotify.com/api/token",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            }
        )

        if r.status_code == 200:
            body = r.json()
            print("Get Access Token")
            return body['access_token']

    def get_top_tracks_uris(self):
        """Gets the users top tracks of the last 4 weeks"""
        r = requests.get(
            f"{self.api_url}/me/top/tracks",
            auth=BearerAuth(self.access_token),
            params={
                "limit": 30,
                "time_range": "short_term"
            }
        )

        if r.status_code == 200:
            body = r.json()
            track_items = body['items']
            track_uris = [x['uri'] for x in track_items]
            print("Get Track URIs")
            return track_uris
        elif r.status_code == 401:
            self.access_token = self.get_access_token()
            self.get_top_tracks_uris()

    def get_user_id(self):
        """Gets the Spotify ID of the user"""
        r = requests.get(
            f"{self.api_url}/me",
            auth=BearerAuth(self.access_token)
        )

        if r.status_code == 200:
            body = r.json()
            user_id = body['id']
            print("Get User ID")
            return user_id
        elif r.status_code == 401:
            self.access_token = self.get_access_token
            self.get_user_id()

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
            self.access_token = self.get_access_token()
            self.create_playlist(user_id)

    def add_tracks_to_playlist(self, playlist_id, track_uris):
        """Adds tracks to a playlist"""
        r = requests.post(
            f"{self.api_url}/playlists/{playlist_id}/tracks",
            json={"uris": track_uris},
            auth=BearerAuth(self.access_token)
        )

        if r.status_code == 401:
            self.access_token = self.get_access_token()
            self.add_tracks_to_playlist(playlist_id, track_uris)
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
            self.access_token = self.get_access_token()
            self.add_playlist_image(playlist_id)

    def create_monthly_top_list(self):
        top_tracks_uris = self.get_top_tracks_uris()
        user_id = self.get_user_id()
        playlist_id = self.create_playlist(user_id)
        self.add_playlist_image(playlist_id)
        self.add_tracks_to_playlist(playlist_id, top_tracks_uris)


if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.load(f)

    for token in config["tokens"]:
        SpotifyAPI(
            token["refresh_token"],
            config['client_id'],
            config['client_secret'],
            config['spotify_api_url']
        ).create_monthly_top_list()
