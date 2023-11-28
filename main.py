import requests
import os 
import base64
from dotenv import load_dotenv
import psutil
from requests import post , get    
import pandas as pd
import numpy as np 
import urllib.parse as urlparse
import secrets
import webbrowser
import hashlib
import subprocess
from datetime import datetime

client_id = None
client_secret = None
AUTH_URL = None
AUTH_TOKEN_URL = None
API_CALL = None
redirect_uri = None

def check_directory(usr=None):
    if usr is not None:
        dirs = ['./DATA',f'./DATA/{usr}',f'./DATA/{usr}/Artists',f'./DATA/{usr}/Following',f'./DATA/{usr}/Saved Tracks',f'./DATA/{usr}/Tracks']
        for i in dirs:
            if not os.path.exists(i):
                os.mkdir(i)
    else:
        print('Provide User Name')


def get_authorization():
    
    scope = 'user-read-private user-read-email user-library-read user-top-read user-read-recently-played user-follow-read playlist-read-private playlist-read-collaborative user-read-currently-playing'
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode().rstrip('=')

    process=subprocess.Popen(['python', './Callback/app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(AUTH_URL)
    authorization_url = AUTH_URL + '?' + urlparse.urlencode({
        'response_type': 'code',
        'client_id': client_id,
        'scope': scope,
        'redirect_uri': redirect_uri,
        'code_challenge_method': 'S256',
        'code_challenge': code_challenge,
    })
    webbrowser.open(authorization_url)

    auth_code = input('Enter Auth code from the browser : ')
    
    if auth_code is not None:
        response = requests.post(AUTH_TOKEN_URL, data={
            'code': auth_code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'grant_type': 'authorization_code',
            'code_verifier': code_verifier,
        })

        if response.status_code == 200:
            access_token = response.json().get('access_token')
            if access_token:
                header = {"Authorization": f"Bearer {access_token}"}
                process = psutil.Process(process.pid)
                process.terminate()
                return access_token, header
            else:
                process = psutil.Process(process.pid)
                process.terminate()

                raise Exception('Failed To Authenticate: No Access Token')
        else:
            raise Exception(f'Failed To Authenticate: {response.status_code} - {response.text}')
    else:
        raise Exception('Failed To Authenticate: No Auth Code')
    
def get_usr_profile(header):
    response = get('https://api.spotify.com/v1/me',headers=header)
    if response.status_code == 200:
        usr_data = response.json()
        out_data = {key:usr_data[key] for key in ['display_name', 'id', 'followers', 'country', 'product', 'explicit_content', 'email']}
        return out_data
    else:
        raise Exception(f'Failed To Get User Profile: {response.status_code} - {response.text}')

def save_artists(response,usr,limit):
    data = {'id':[],'name':[],'popularity':[],'genres':[],}
    imp_cols = ['genres', 'id', 'name', 'popularity']
    for item in response.json()['items']:
        for i in imp_cols:
            data[i].append(item[i])
    df = pd.DataFrame(data)
    date = datetime.today().date()
    df.to_csv(f'./DATA/{usr}/Artists/TOP_{limit}_artists_{date}.csv',index=False)
    return df['name'].head()

def save_tracks(response,usr,limit):
    imp_cols = ['album', 'artists', 'available_markets', 'disc_number', 'duration_ms', 'explicit',  
     'id', 'is_local', 'name', 'popularity','track_number']
    data = {'album_id':[],'album_name':[],'album_release':[],'album_total_tracks':[],
             'artists':[],'artists_id':[],
               'available_markets':[], 'disc_number':[], 'duration_ms':[], 'explicit':[],  
     'id':[], 'is_local':[], 'name':[], 'popularity':[],'track_number':[]}
    for item in response.json()['items']:
        for i in imp_cols:
            if i == 'album':
                data['album_name'].append(item[i]['name'])
                data['album_id'].append(item[i]['id'])
                data['album_release'].append(item[i]['release_date'])
                data['album_total_tracks'].append(item[i]['total_tracks'])
            elif i == 'artists':
                artist = []
                ids = []
                for j in item[i]:
                    artist.append(j['name'])
                    ids.append(j['id'])
                data['artists'].append(artist)
                data['artists_id'].append(ids)
            else:
                data[i].append(item[i])
    df = pd.DataFrame(data)
    date = datetime.today().date()
    df.to_csv(f'./DATA/{usr}/Tracks/TOP_{limit}_tracks_{date}.csv',index=False)
    return df['name'].head()

def get_top(header,usr=None,type='artists',time_range='long_term',limit=50):
    if usr is None:
        raise ValueError('Please Provide Usr')
    if type not in ['artists','tracks']:
        raise ValueError('Type Only Takes {"artists" , "tracks"}')
    if time_range not in ['long_term','medium_term','short_term']:
        raise ValueError("time_range Only Takes {'long_term','medium_term','short_term'}")
    if limit <= 0 or limit >= 51:
        raise ValueError('Limit value ranges from 0-50')
    response = requests.get(API_CALL+f'/me/top/{type}?time_range={time_range}&limit={limit}',headers=header)
    if type=='artists':
        out = save_artists(response,usr,limit)
    else:
        out = save_tracks(response,usr,limit)
    return out

def get_followed_artists(header,usr=None,limit=50):
    if usr is None:
        raise ValueError('Please Provide Usr')
    if limit <= 0 or limit >= 51:
        raise ValueError('Limit value ranges from 0-50')
    response = requests.get(API_CALL+f"/me/following?type=artist&limit={limit}",headers=header)
    data = {'artist_id':[],'artist_name':[],'artist_genre':[],'artist_popularity':[],'artist_followers':[]}
    imp_cols = {'followers':'artist_followers', 'genres':'artist_genre', 'id':'artist_id', 'name':'artist_name', 'popularity':'artist_popularity'}
    for item in response.json()['artists']['items']:
        for j in imp_cols.keys():
            if j == 'followers':
                data[imp_cols[j]].append(item[j]['total'])
            else:
                data[imp_cols[j]].append(item[j])
    df = pd.DataFrame(data)
    date = datetime.today().date()
    df.to_csv(f'./DATA/{usr}/Following/{date}_followers_list_limit{limit}.csv',index=False)
    return df['artist_name'].head()

def get_user_saved_tracks(header,usr,market='IN',limit=50):
    if usr is None:
        raise ValueError('Please Provide Usr')
    if limit <= 0 or limit >= 51:
        raise ValueError('Limit value ranges from 0-50')
    response = get(API_CALL+f"/me/tracks?market={market}&limit={limit}",headers=header)
    imp_cols = ['album', 'artists', 'id', 'name', 'popularity']
    data = {'album_name':[],'album_id':[],'album_release':[],
            'artists':[],'artist_ids':[],
            'name':[],'id':[],'popularity':[]}
    for item in response.json()['items']:
        track = item['track']
        for j in imp_cols:
            if j == 'album':
                data['album_id'].append(track[j]['id'])
                data['album_name'].append(track[j]['name'])
                data['album_release'].append(track[j]['release_date'])
            elif j == 'artists':
                data['artists'].append([m['name'] for m in track[j]])
                data['artist_ids'].append([m['id'] for m in track[j]])
            else:
                data[j].append(track[j])
    df = pd.DataFrame(data)
    date = datetime.today().date()
    df.to_csv(f'./DATA/{usr}/Saved Tracks/{date}_saved_tracks.csv',index=False)
    return df['name'].head()

def create_env(client_id='',client_secret=''):
    data = {'CLIENT_ID':client_id,'CLIENT_SECRET':client_secret,'AUTH_URL':"https://accounts.spotify.com/authorize",
'AUTH_TOKEN_URL':"https://accounts.spotify.com/api/token",
'API_CALL':"https://api.spotify.com/v1",
'REDIRECT_URI':"http://127.0.0.1:8080/callback"}
    with open('.env','w') as f:
        for key,value in data.items():
            f.write(f'{key}="{value}"\n')
    print("./env created...")

if __name__ == "__main__":
    if not os.path.exists('./.env'):
        create_env()
    load_dotenv()

    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    AUTH_URL = os.getenv('AUTH_URL')
    AUTH_TOKEN_URL = os.getenv('AUTH_TOKEN_URL')
    API_CALL = os.getenv('API_CALL')
    redirect_uri = os.getenv('REDIRECT_URI')

    ath_stat = False
    access_token,header = None , None
    user_profile = None
    usr=None

    while True:
        print("\nMenu:")
        print("1. Authorization")
        print("2. Show Authorized User Details")
        print("3. Get Top Tracks")
        print("4. Get Top Artists")
        print("5. Get Followed Artists")
        print("6. Get Saved Tracks")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ")

        if choice == '1':
            if ath_stat:
                print(f'Already Authorized : {header}')
            else:
                if client_id == "" and client_secret == "":
                    client_id = input('Enter Client Id : ')
                    client_secret = input('Client Secrete : ')
                    create_env(client_id=client_id,client_secret=client_secret)
                access_token,header = get_authorization()
                ath_stat = True
                print('Authorized......')
                user_profile = get_usr_profile(header)
                usr = f"{user_profile['id']}_{user_profile['display_name']}"
                check_directory(usr)


        elif choice == '2':
            if ath_stat and user_profile is not None:
                print(f"Name : {user_profile['display_name']}\nUser-Name : {user_profile['id']}\nEmail : {user_profile['email']}\nCountry : {user_profile['country']}\nFollowers : {user_profile['followers']['total']}\nProduct : {user_profile['product']}\n")
            else:
                print('Please Authorize First')


        elif choice == '3':
            if ath_stat:
                print(get_top(header,usr,'tracks'))
            else:
                print('Please Authorize First')


        elif choice == '4':
            if ath_stat:
                print(get_top(header,usr,'artists'))
            else:
                print('Please Authorize First')


        elif choice == '5':
            if ath_stat:
                print(get_followed_artists(header,usr))
            else:
                print('Please Authorize First')


        elif choice == '6':
            if ath_stat:
                print(get_user_saved_tracks(header,usr))
            else:
                print('Please Authorize First')


        elif choice == '7':
            print('Exiting.........')
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")
    





