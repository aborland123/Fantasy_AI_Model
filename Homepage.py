import streamlit as st
from requests_oauthlib import OAuth2Session
import requests

# allows me to publish to GitHub without exposing API Key. In Streamlit.
client_id = st.secrets["CLIENT_ID"]
client_secret = st.secrets["CLIENT_SECRET"]

redirect_uri = 'https://fantasyfootballai.streamlit.app/'

authorization_base_url = 'https://api.login.yahoo.com/oauth2/request_auth'
token_url = 'https://api.login.yahoo.com/oauth2/get_token'

st.title('Fantasy Football AI')

yahoo = OAuth2Session(client_id, redirect_uri=redirect_uri)

authorization_url, state = yahoo.authorization_url(authorization_base_url)
st.write(f"Please go to [this link]({authorization_url}) to authorize access.")

redirect_response = st.query_params 

st.write("Query Params:", redirect_response)  

if 'code' in redirect_response:
    code = redirect_response['code'][0]
    st.write(f"Authorization code received: {code}") 

    try:
        token = yahoo.fetch_token(token_url, client_secret=client_secret,
                                  code=code, include_client_id=True)
        st.write("Authentication successful! Access token received.")

        access_token = token['access_token']

        league_key = 'YOUR_LEAGUE_KEY'
        league_url = f'https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}'

        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get(league_url, headers=headers)

        if response.status_code == 200:
            league_data = response.json()
            st.write(league_data)
        else:
            st.write(f"Error fetching league data: {response.status_code}")

    except Exception as e:
        st.write(f"Error fetching access token: {e}")
else:
    st.write("Waiting for authorization...")