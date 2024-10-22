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

        league_key = 'nfl.l.650587'
        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        teams_url = f'https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/teams'
        teams_response = requests.get(teams_url, headers=headers)
        if teams_response.status_code == 200:
            teams_data = teams_response.json()
            st.write("Teams Data:", teams_data)
            
            my_team = None
            for team in teams_data['fantasy_content']['league'][1]['teams']:
                team_key = team['team'][0][0]['team_key']
                team_name = team['team'][0][2]['name']
                
                st.write(f"Found Team: {team_name}")
                
                if team_name == "The Alli Show":
                    my_team = team_key
                    st.write(f"This is your team: {team_name}")
                    break

            if my_team:
                roster_url = f'https://fantasysports.yahooapis.com/fantasy/v2/team/{my_team}/roster'
                roster_response = requests.get(roster_url, headers=headers)
                if roster_response.status_code == 200:
                    roster_data = roster_response.json()
                    st.write(f"Your Team Roster:", roster_data)
                    
                    players = []
                    for player in roster_data['fantasy_content']['team'][1]['roster']['0']['players']:
                        player_name = player['player'][0][2]['name']['full']
                        position = player['player'][0][1]['primary_position']
                        players.append({'Name': player_name, 'Position': position})
                    
                    st.write(players)

            else:
                st.write("Your team was not found in the league data.")

        else:
            st.write(f"Error fetching teams data: {teams_response.status_code}")

    except Exception as e:
        st.write(f"Error fetching access token: {e}")
else:
    st.write("Waiting for authorization...")