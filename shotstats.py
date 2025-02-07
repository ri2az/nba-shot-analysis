import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail, playercareerstats, commonplayerinfo

# Fonction pour obtenir l'ID d'un joueur
def get_player_id(player_name):
    nba_players = players.get_players()
    for player in nba_players:
        if player_name.lower() == player["full_name"].lower():
            return player["id"]
    return None

# Fonction pour récupérer les données de tirs
def get_shot_chart_data(player_id, season):
    shot_chart = shotchartdetail.ShotChartDetail(
        team_id=0, player_id=player_id, season_nullable=season, context_measure_simple="FGA"
    )
    df = shot_chart.get_data_frames()[0]
    return df

# Fonction pour récupérer les statistiques du joueur
def get_player_stats(player_id, season):
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    df = career.get_data_frames()[0]
    season_stats = df[df["SEASON_ID"] == season]
    
    if not season_stats.empty:
        return season_stats.iloc[0]
    return None

# Fonction pour afficher le terrain
def draw_court(ax=None):
    if ax is None:
        ax = plt.gca()
    court_elements = [
        plt.Circle((0, 0), radius=7.5, linewidth=2, color="black", fill=False),
        plt.Rectangle((-30, -7.5), 60, -1, linewidth=2, color="black"),
        plt.Rectangle((-80, -47.5), 160, 190, linewidth=2, color="black", fill=False),
        plt.Circle((0, 142.5), radius=40, linewidth=2, color="black", fill=False),
        plt.Rectangle((-220, -47.5), 440, 470, linewidth=2, color="black", fill=False),
    ]
    for element in court_elements:
        ax.add_patch(element)
    return ax

# Interface Streamlit
st.title("Analyseur de Tirs NBA")

player_name = st.text_input("Entrez le nom du joueur :", "Luka Dončić")
seasons = [f"{year}-{str(year+1)[-2:]}" for year in range(2000, 2025)]
season_selected = st.selectbox("Sélectionnez une saison :", seasons, index=len(seasons)-1)

if player_name:
    player_id = get_player_id(player_name)
    if player_id:
        st.success(f"Joueur trouvé: {player_name} (ID: {player_id})")
        
        df_shots = get_shot_chart_data(player_id, season_selected)
        player_stats = get_player_stats(player_id, season_selected)

        if player_stats is not None:
            # Tableau des statistiques du joueur
            st.subheader(f"Statistiques de {player_name} ({season_selected})")
            stats_df = pd.DataFrame(player_stats).T[[
                "TEAM_ABBREVIATION", "GP", "MIN", "PTS", "FGM", "FGA", "FG_PCT",
                "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT", "OREB", "DREB",
                "REB", "AST", "TOV", "STL", "BLK", "PF"
            ]]
            stats_df.rename(columns={
                "TEAM_ABBREVIATION": "Équipe",
                "GP": "Matchs joués",
                "MIN": "Minutes moyennes",
                "PTS": "Points",
                "FGM": "Tirs marqués",
                "FGA": "Tirs tentés",
                "FG_PCT": "Précision tirs %",
                "FG3M": "3 PTS marqués",
                "FG3A": "3 PTS tentés",
                "FG3_PCT": "Précision 3PTS %",
                "FTM": "Lancers-francs marqués",
                "FTA": "Lancers-francs tentés",
                "FT_PCT": "Précision LF %",
                "OREB": "Rebonds offensifs",
                "DREB": "Rebonds défensifs",
                "REB": "Rebonds totaux",
                "AST": "Passes décisives",
                "TOV": "Ballons perdus",
                "STL": "Interceptions",
                "BLK": "Contres",
                "PF": "Fautes"
            }, inplace=True)
            
            st.dataframe(stats_df)

            # Explication des sigles
            st.markdown("""
            **Explication des sigles :**  
            - **GP** : Nombre de matchs joués  
            - **MIN** : Minutes moyennes par match  
            - **PTS** : Nombre total de points  
            - **FGM / FGA / FG%** : Tirs marqués / tentés / précision  
            - **3PM / 3PA / 3P%** : Tirs à 3 pts marqués / tentés / précision  
            - **FTM / FTA / FT%** : Lancers-francs marqués / tentés / précision  
            - **OREB / DREB / REB** : Rebonds offensifs / défensifs / totaux  
            - **AST** : Passes décisives  
            - **TOV** : Ballons perdus  
            - **STL** : Interceptions  
            - **BLK** : Contres  
            - **PF** : Fautes  
            """)

            # Shot Chart Classique
            st.subheader("Shot Chart Classique")
            fig, ax = plt.subplots(figsize=(10, 9))
            draw_court(ax)
            sns.scatterplot(x=df_shots["LOC_X"], y=df_shots["LOC_Y"], hue=df_shots["SHOT_MADE_FLAG"], palette=['red', 'green'], ax=ax)
            ax.set_xlabel("Position horizontale du tir")
            ax.set_ylabel("Position verticale du tir")
            ax.set_xlim(-250, 250)
            ax.set_ylim(-47.5, 422.5)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(f"Shot Chart de {player_name} ({season_selected})")
            st.pyplot(fig)

            # Heatmap des tirs
            st.subheader("Heatmap des Tirs")
            fig, ax = plt.subplots(figsize=(10, 9))
            draw_court(ax)
            sns.kdeplot(x=df_shots["LOC_X"], y=df_shots["LOC_Y"], fill=True, cmap="Reds", ax=ax, alpha=0.6)
            ax.set_xlabel("Position horizontale du tir")
            ax.set_ylabel("Position verticale du tir")
            ax.set_xlim(-250, 250)
            ax.set_ylim(-47.5, 422.5)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(f"Heatmap des tirs de {player_name} ({season_selected})")
            st.pyplot(fig)

    else:
        st.error("Joueur non trouvé. Vérifiez l'orthographe !")