# ================================== BIBLIOTECAS  ===================================
import pandas as pd
import plotly.express as px
import folium
from datetime import datetime
import time
from haversine import haversine
import numpy as np
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import plotly.graph_objects as go
import inflection
import pygwalker as pyg
import seaborn as sns

# ====================== IMPORTAÇÃO / TRATAMENTO DE DADOS ============================
#Importa data set
df = pd.read_csv('C:/Users/miche/Documents/DC/Comunidade DS/PA01/zomato.csv')

def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
}
def country_name(country_id):
    return COUNTRIES[country_id]   

def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]


df = rename_columns(df)
df['country_code'] = df['country_code'].apply(country_name)
df['price_range'] = df['price_range'].apply(create_price_tye)
df['rating_color'] = df['rating_color'].apply(color_name)
df["cuisines"] = df["cuisines"].apply(lambda x: str(x).split(",")[0] if pd.notna(x) else "")
df = df[df["cuisines"] != ""]

# ================================ SIDEBAR ========================================

image = Image.open('FomeZero.jpg')
st.sidebar.image(image)

st.sidebar.markdown( "# Fome Zero!" )
st.sidebar.markdown( "Encontre seu restaurante!" )
st.sidebar.markdown( """---""" )

options = st.sidebar.multiselect(
    'Selecione os países que deseja visualizar restaurantes',
    df['country_code'].unique(),
    'Brazil')

linhas = df['country_code'].isin(options)
df = df.loc[linhas, :]

# ============================== CORPO =============================================

st.title(':red[Fome Zero] 📌')

st.markdown("### Restaurantes | Tipos de Culinárias | Visão Geográfica")

with st.container():
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        qtd_tipo_culinaria = df['cuisines'].nunique()
        col1.metric( "Qtd de Culinárias", qtd_tipo_culinaria)
    
    with col2:
        qtd_tipo_restaurante = df['restaurant_id'].nunique()
        col2.metric( "Qtd Restaurantes", qtd_tipo_restaurante)
    
    with col3:
        qtd_tipo_restaurante_entrega = df['restaurant_id'][df['has_online_delivery'] == 1].count()
        col3.metric( "Qtd Restaurantes com Entregas", qtd_tipo_restaurante_entrega)

    with col4:
        qtd_tipo_restaurante_reserva = df['restaurant_id'][df['has_table_booking'] == 1].count()
        col4.metric( "Qtd Restaurantes com Entregas", qtd_tipo_restaurante_reserva)

    with col5:
        qtd_paises = df['country_code'].nunique()
        col5.metric( "Qtd Países", qtd_paises)

    with col6:
        qtd_cidades = df['city'].nunique()
        col6.metric( "Qtd Cidades", qtd_cidades)

with st.container():
        cols = ['restaurant_name', 'city', 'cuisines', 'price_range', 'votes', 'rating_text']            
        df_aux = df.loc[:, cols]
        #st.dataframe( df_aux )
        
        st.dataframe(
            df_aux, use_container_width=True, height =600, 
            column_config={
                "restaurant_name": "Nome Restaurante",  "city": "Cidade",  "cuisines": "Culinária",
                "price_range": "Cat. Preço", "rating_text": "Cat. Nota",
            },
            hide_index=True, 
        )

with st.container():
        st.header('Visão Geográfica | Restautantes')
        cols = ['restaurant_name', 'cuisines', 'latitude', 'longitude']
        df_aux = df[cols]

        map = folium.Map()        
        for i in range(0,len(df_aux)):
           folium.Marker(
              location=[df_aux.iloc[i]['latitude'],
                        df_aux.iloc[i]['longitude']],
              popup=df_aux.iloc[i][['restaurant_name','cuisines']],
           ).add_to(map)

        map.fit_bounds([[df_aux['latitude'].min(), df_aux['longitude'].min()],
                        [df_aux['latitude'].max(), df_aux['longitude'].max()]])
        
        folium_static (map, width=1024, height=600)
