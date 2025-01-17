from dash import html
from src.components import (Header, Navbar, Footer)

def AboutPage():
    return html.Div(
        children=[
            Header(),
            Navbar(),
            html.Main(
                children=[
                    html.H2('À Propos de Nous', className='about-title'),
                    html.Div(
                        children=[
                            html.P(
                                "Ce projet a été développé dans le cadre du cours de Python à l'ESIEE Paris,"
                                " où les étudiants devaient utiliser des données ouvertes publiques pour concevoir un"
                                " tableau de bord interactif traitant d'un sujet d'intérêt public."
                            ),
                            html.P(
                                "Notre tableau de bord se concentre sur les transactions immobilières en France,"
                                " en exploitant le jeu de données Demandes de valeurs foncières (DVF) fourni par le"
                                " gouvernement français. Ce jeu de données comprend des informations géolocalisées sur"
                                " les transactions immobilières, enrichies et normalisées pour faciliter l'analyse."
                            ),
                            html.P(
                                "Le projet met en avant les fonctionnalités suivantes :"
                            ),
                            html.Ul(
                                children=[
                                    html.Li("Une carte thermique interactive montrant les tendances des prix au mètre carré à travers la France,"),
                                    html.Li("Un graphique dynamique en ligne pour visualiser les évolutions des prix dans le temps,"),
                                    html.Li("Une distribution histogramme des prix des propriétés,"),
                                    html.Li("Un diagramme circulaire affichant la proportion des différents types de propriétés."),
                                ],
                            ),
                            html.P(
                                "Notre projet met en avant l'importance des données ouvertes pour favoriser la transparence et"
                                " permettre des prises de décision basées sur les données."
                            ),
                            html.P(
                                "Ce tableau de bord a été créé en suivant les meilleures pratiques en programmation Python,"
                                " en prétraitement des données et en visualisation. Il illustre comment les données publiques"
                                " peuvent être exploitées pour extraire des informations et les présenter de manière accessible."
                            ),
                            html.H3("Livrables du Projet"),
                            html.Ul(
                                children=[
                                    html.Li("Un tableau de bord entièrement fonctionnel et interactif lancé via `python main.py`"),
                                    html.Li("Un traitement complet des données grâce à des scripts Python"),
                                    html.Li("Une documentation détaillée, y compris un fichier README et un rapport d'analyse"),
                                ],
                            ),
                            html.P(
                                "Nous remercions nos professeurs et nos camarades à l'ESIEE Paris pour leur accompagnement"
                                " et leur soutien tout au long de ce projet."
                            ),
                        ],
                        className='about-content'
                    ),
                ],
                className='main-content'
            ),
            Footer()
        ],
        className='about-page'
    )