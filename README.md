# Spotify Data Scrapper
This Python script interacts with the Spotify API to perform various tasks, such as retrieving user information, getting top tracks and artists, fetching followed artists, and retrieving saved tracks.
## Prerequisites
Before using the script, make sure you have the following:

- Spotify Developer Account
- Client ID and Client Secret from the Spotify Developer Dashboard
- Update Redirect URI Parameter on your Spotify Developer App Dashboard to `http://127.0.0.1:8080/callback`
- Python installed on your machine

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Shivam-21-11/PY_SPOTIFY_DATA_SCRAPPER.git
   cd PY_SPOTIFY_DATA_SCRAPPER```
   
2. Install dependencies:

   ```bash
   pip install -r requirements.txt```
3. Run the script:

   ```bash
   python main.py```

## Usage

1. **Authorization:** Run the script, choose option 1, and follow the instructions to authorize the script.
2. **Show Authorized User Details:** After authorization, choose option 2 to display details of the authorized user.
3. **Get Top Tracks and Artists:** Choose options 3 and 4 to get the top tracks and artists for the authorized user.
4. **Get Followed Artists:** Choose option 5 to retrieve a list of followed artists.
5. **Get Saved Tracks:** Choose option 6 to get a list of saved tracks.
6. **Exit**: Choose option 7 to exit the script.

#### Note
- Ensure that your Spotify Developer Dashboard credentials are kept secure.
- This script uses a local web server for the OAuth2 authorization process.

# Author
Shivam Manoj Singh

Feel free to contribute and enhance the script!