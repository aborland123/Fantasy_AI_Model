import streamlit as st
from requests_oauthlib import OAuth2Session
import requests
import xml.etree.ElementTree as ET


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

        teams_url = f'https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/teams'
        teams_response = requests.get(teams_url, headers=headers)

        st.write(f"Teams API Response Status Code: {teams_response.status_code}")
        st.write(f"Teams API Response Text: {teams_response.text}")

        if teams_response.status_code == 200:
            try:
                # Parse the XML content
                root = ET.fromstring(teams_response.content)
                
                # Find all 'team' elements
                teams = root.findall('.//team')
                team_list = []

                for team in teams:
                    team_name = team.find('name').text if team.find('name') is not None else "N/A"
                    team_key = team.find('team_key').text if team.find('team_key') is not None else "N/A"
                    manager = team.find('managers/manager/nickname').text if team.find('managers/manager/nickname') is not None else "N/A"
                    team_list.append({
                        'Team Name': team_name,
                        'Team Key': team_key,
                        'Manager': manager
                    })

                st.write("Teams in the League:")
                st.write(team_list)

            except ET.ParseError as e:
                st.write(f"Error parsing XML response: {e}")
        else:
            st.write(f"Error fetching teams data: {teams_response.status_code} - {teams_response.text}")

    except Exception as e:
        st.write(f"Error fetching access token: {e}")
else:
    st.write("Waiting for authorization...")