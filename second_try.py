# This app is for educational purpose only. Insights gained is not financial advice. Use at your own risk!
import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import json
import time
import numpy as np
import webbrowser


#---------------------------------#
# New feature (make sure to upgrade your streamlit library)
# pip install --upgrade streamlit

#---------------------------------#
# Page layout
## Page expands to full width
st.set_page_config(layout="wide")
#---------------------------------#
# Title

image = Image.open('crypto1.jfif')

st.image(image, width = 1000)

st.title('DYOR CRYPTO APP')
st.markdown("""
Cette application récupère les prix des crypto-monnaies pour les 100 meilleures crypto-monnaies à partir du site CoinMarketCap!
""")

#---------------------------------#
# About
expander_bar = st.beta_expander("A Propos")
expander_bar.markdown("""
* **Source des données:** [CoinMarketCap](http://coinmarketcap.com).
* **Réalisé par:** Haichatou Yacine NIANG et Marème SY
""")


#---------------------------------#
# Page layout (continued)
## Divide page to 3 columns (col1 = sidebar, col2 and col3 = page contents)
col1 = st.sidebar
col2, col3 = st.beta_columns((1,1))

#---------------------------------#
# Sidebar + Main panel
col1.header('Options d’entrée')


## Sidebar - Currency price unit



currency_price_unit = col1.selectbox('Sélectionnez la devise pour le prix', ('USD', 'BTC', 'ETH'))

# Web scraping of CoinMarketCap data
@st.cache
def load_data():
    cmc = requests.get('http://coinmarketcap.com')
    soup = BeautifulSoup(cmc.content, 'html.parser')
    
    ## cmc.content

    data = soup.find('script', id='__NEXT_DATA__', type='application/json')
    coins = {}
    coin_data = json.loads(data.contents[0])
    listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
    for i in listings:
      coins[str(i['id'])] = i['slug']

    name = []
    symbol = []
    marketCap = []
    percentChange1h = []
    percentChange24h = []
    percentChange7d = []
    price = []
    volume24h = []

    for i in listings:
      name.append(i['slug'])
      symbol.append(i['symbol'])
      price.append(i['quote'][currency_price_unit]['price'])
      percentChange1h.append(i['quote'][currency_price_unit]['percentChange1h'])
      percentChange24h.append(i['quote'][currency_price_unit]['percentChange24h'])
      percentChange7d.append(i['quote'][currency_price_unit]['percentChange7d'])
      marketCap.append(i['quote'][currency_price_unit]['marketCap'])
      volume24h.append(i['quote'][currency_price_unit]['volume24h'])

    data = pd.DataFrame(columns=['slug', 'Symbole', 'capitalisation boursière', 'variation1h', 'variation24h', 'variation7d', 'prix', 'volume24h'])
    data['slug'] = name
    data['prix'] = price
    data['Symbole'] = symbol
    data['variation1h'] = percentChange1h
    data['variation24h'] = percentChange24h
    data['variation7d'] = percentChange7d
    data['capitalisation boursière'] = marketCap
    data['volume24h'] = volume24h
    df = pd.DataFrame(columns=['Nom', 'Symbole'])
    df['Nom'] = name
    df['Symbole'] = symbol
    return df,data


df, data = load_data()








## Sidebar - Cryptocurrency selections
sorted_coin = sorted( data['slug'] )
selected_coin = col1.multiselect('Crypto-monnaie', sorted_coin, sorted_coin)



df_selected_coin = data[ (data['slug'].isin(selected_coin)) ] # Filtering data

## Sidebar - Number of coins to display
num_coin = col1.slider('Afficher les N meilleures pièces', 1, 100, 100)
df_coins = df_selected_coin[:num_coin]




st.subheader('Liste des 100 cryptomonnaies')



st.table(df)
col2.subheader('Données de prix de la crypto-monnaie sélectionnée')
col2.dataframe(df_coins)

column_names = list(df['Nom'])

select = st.selectbox("Sélecionnez une crypto pour plus de détails", column_names) 

new_title = '<h1 style="font-family:sans-serif; color:blue">'+select +'</h1>'
st.markdown(new_title, unsafe_allow_html=True)

selecte_coin = df['Nom'].loc[df['Nom'] == select]
df_selecte_coin = data[(data['slug'].isin(selecte_coin)) ] 

# Filtering data




change = pd.concat([df_selecte_coin.slug,df_selecte_coin.Symbole, df_selecte_coin.variation1h, df_selecte_coin.variation24h, df_selecte_coin.variation7d], axis=1)

slug = pd.concat([df_selecte_coin.slug])

desc = requests.get('https://coinmarketcap.com/currencies/'+ select+'/')
##desc.content

    
soup = BeautifulSoup(desc.text, 'html.parser')
div = soup.find_all('p')

st.write(div[6].text)

## cmc.content

##table = soup.find('div', attrs={'class': 'iYFMbU'})
##st.write(str(table.content))

st.table(change)
##st.write(slug)
##url = "http://coinmarketcap.com/currencies/" + string(slug)+ "/"
##webbrowser.open_new(url)

# Download CSV data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Télécharger fichier csv</a>'
    return href

st.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)

#---------------------------------#
# Preparing data for Bar plot of % Price change

df_change = pd.concat([df_coins.Symbole, df_coins.variation1h, df_coins.variation24h, df_coins.variation7d], axis=1)
df_change = df_change.set_index('Symbole')
df_change['positive_percentChange1h'] = df_change['variation1h'] > 0
df_change['positive_percentChange24h'] = df_change['variation24h'] > 0
df_change['positive_percentChange7d'] = df_change['variation7d'] > 0
col3.subheader('Tableau du pourcentage de variation des prix des cryto-monnaies')
col3.dataframe(df_change)

## Sidebar - Sorting values
sort_values = st.selectbox('Sort values?', ['Yes', 'No'])

## Sidebar - Percent change timeframe
percent_timeframe =st.selectbox('Percent change time frame',
                                    ['7d','24h','1h'])
percent_dict = {"7d":'variation7d',"24h":'variation24h',"1h":'variation1h'}
selected_percent_timeframe = percent_dict[percent_timeframe]


# Conditional creation of Bar plot (time frame)
st.subheader('Histogramme %  Changement de prix')

if percent_timeframe == '7d':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['variation7d'])
    st.write('*7 days period*')
    plt.figure(figsize=(7,3))
    plt.subplots_adjust(top = 1, bottom = 0)
    df_change['variation7d'].plot(kind='hist', color=df_change.positive_percentChange7d.map({True: 'g', False: '#33F6DE'}))
    st.pyplot(plt)
elif percent_timeframe == '24h':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['variation24h'])
    col2.write('*24 hour period*')
    plt.figure(figsize=(7,3))
    plt.subplots_adjust(top = 1, bottom = 0)
    df_change['variation24h'].plot(kind='hist', color=df_change.positive_percentChange24h.map({True: 'g', False: '#33F6DE'}))
    st.pyplot(plt)
else:
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by=['variation1h'])
    st.write('*1 hour period*')
    plt.figure(figsize=(7,3))
    plt.subplots_adjust(top = 1, bottom = 0)
    df_change['variation1h'].plot(kind='hist', color=df_change.positive_percentChange1h.map({True: 'g', False: '#33F6DE'}))
    st.pyplot(plt)