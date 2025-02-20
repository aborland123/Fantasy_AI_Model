import streamlit as st
from requests_oauthlib import OAuth2Session
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import os

client_id = st.secrets["CLIENT_ID"]
client_secret = st.secrets["CLIENT_SECRET"]

redirect_uri = 'https://fantasyfootballai.streamlit.app/'

st.title('Fantasy Football AI')

authorization_base_url = 'https://api.login.yahoo.com/oauth2/request_auth'
token_url = 'https://api.login.yahoo.com/oauth2/get_token'

yahoo = OAuth2Session(client_id, redirect_uri=redirect_uri)

authorization_url, state = yahoo.authorization_url(authorization_base_url)
st.write(f"Please go to [this link]({authorization_url}) to authorize access.")

redirect_response = st.experimental_get_query_params()
if 'code' in redirect_response:
    authorization_code = redirect_response['code'][0]
    try:
        token = yahoo.fetch_token(token_url, client_secret=client_secret, code=authorization_code, include_client_id=True)
        st.write("Authentication successful! Access token received.")
        st.write(f"Access Token: {token['access_token']}")

        headers = {'Authorization': f"Bearer {token['access_token']}", 'Accept': 'application/json'}
        response = requests.get('https://fantasysports.yahooapis.com/fantasy/v2/league/nfl.l.650587/teams', headers=headers)

        if response.status_code == 200:
            st.write(f"Teams API Response Status Code: {response.status_code}")
            root = ET.fromstring(response.content)

            teams_data = []
            for team in root.findall('.//team'):
                team_key = team.find('.//team_key').text
                team_name = team.find('.//name').text
                waiver_priority = team.find('.//waiver_priority').text
                num_moves = team.find('.//number_of_moves').text
                draft_grade = team.find('.//draft_grade').text if team.find('.//draft_grade') is not None else "N/A"

                teams_data.append([team_key, team_name, waiver_priority, num_moves, draft_grade])

            df = pd.DataFrame(teams_data, columns=['Team Key', 'Team Name', 'Waiver Priority', 'Number of Moves', 'Draft Grade'])

            csv_filename = 'fantasy_teams.csv'
            df.to_csv(csv_filename, index=False)
            st.write(f"Data exported successfully to CSV: {csv_filename}")

            st.write("Team Data:")
            st.dataframe(df)

        else:
            st.write(f"Error fetching teams: {response.status_code}")
            st.write(response.text)

    except Exception as e:
        st.write(f"Error fetching access token: {e}")

else:
    st.write("Waiting for authorization...")