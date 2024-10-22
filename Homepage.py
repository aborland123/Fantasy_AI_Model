import streamlit as st
from requests_oauthlib import OAuth2Session
import requests

# allows me to publish to GitHub without exposing API Key. In Streamlit.
client_id = st.secrets["CLIENT_ID"]
client_secret = st.secrets["CLIENT_SECRET"]

redirect_uri = 'https://fantasyfootballai.streamlit.app/'

st.title('Fantasy Football AI')

authorization_base_url = 'https://api.login.yahoo.com/oauth2/request_auth'
token_url = 'https://api.login.yahoo.com/oauth2/get_token'

yahoo = OAuth2Session(client_id, redirect_uri=redirect_uri)

authorization_url, state = yahoo.authorization_url(authorization_base_url)
st.write(f"Please go to [this link]({authorization_url}) to authorize access.")

redirect_response = st.query_params

if 'code' in redirect_response:
    code = redirect_response['code']
    authorization_code = code[0] if isinstance(code, list) else code

    try:
        token = yahoo.fetch_token(token_url, client_secret=client_secret,
                                  code=authorization_code, include_client_id=True)

        st.write("Authentication successful! Access token received.")

        access_token = token['access_token']
        expires_in = token.get('expires_in', 'Unknown')
        st.write(f"Access Token: {access_token}")
        st.write(f"Token Expires In: {expires_in} seconds")

        league_key = 'nfl.l.650587'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
        }

        st.write(f"League URL: https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/teams")
        st.write(f"Headers: {headers}")

        teams_url = f'https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/teams'
        teams_response = requests.get(teams_url, headers=headers)

        st.write(f"Teams API Response Status Code: {teams_response.status_code}")
        st.write(f"Teams API Response Text: {teams_response.text}")

        if teams_response.status_code == 200:
            try:
                teams_data = teams_response.json()
                st.write("Teams Data:", teams_data)
            except ValueError:
                st.write("Error: Unable to parse JSON response.")
        else:
            st.write(f"Error fetching teams data: {teams_response.status_code} - {teams_response.text}")

    except Exception as e:
        st.write(f"Error fetching access token: {e}")
else:
    st.write("Waiting for authorization...")