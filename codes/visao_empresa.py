# Libraries
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from haversine import haversine
import streamlit as st
from PIL import Image

# Import dataset
df = pd.read_csv("train.csv")

# Copy dataset
df1 = df.copy()

# ==========================
#         Cleaning
# ==========================

# conversão de texto para numero
selected = (df1['Delivery_person_Age'] != 'NaN ')
df1 = df1.loc[selected, :]

selected = (df1['Road_traffic_density'] != 'NaN ')
df1 = df1.loc[selected, :]

selected = (df1['City'] != 'NaN ')
df1 = df1.loc[selected, :]

selected = (df1['Festival'] != 'NaN ')
df1 = df1.loc[selected, :]

# conversão string para int
df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

# conversão float
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

# conversão string para data
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

# conversão string para int
selected = (df1['multiple_deliveries'] != 'NaN ')
df1 = df1.loc[selected, :]
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

# removendo os espaços da coluna ID
df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
df1.loc[:, 'Weatherconditions'] = df1.loc[:, 'Weatherconditions'].str.strip()
df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

# limpado a coluna time taken
df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

# ==========================
#          Sidebar
# ==========================

st.header('Marketplace - Visão empresa')

image_path = 'logo.jpg'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury company')
st.sidebar.markdown('## Fastest delivery in Town.')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Quais as condições climáticas')
traffic_options = st.sidebar.multiselect(
    'Opções:',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])
st.sidebar.markdown("""---""")

st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data
selected01 = df1['Order_Date'] < date_slider
df1 = df1.loc[selected01, :]

# Filtro de trânsito
selected02 = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[selected02, :]

# ==========================
#          Layout 
# ==========================

tab1, tab2, tab3 = st.tabs(['Visão gerencial', 'Visão tática', 'Visão Geográfica'])

# Visão gerencial
with tab1:
    # container fig
    with st.container():
        st.markdown('# Orders by day')
        cols = ['ID', 'Order_Date']
        df_aux=df1.loc[:,cols].groupby(['Order_Date']).count().reset_index()

        fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')
        st.plotly_chart(fig, use_container_width=True)
    
    # container colunas
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic order share')
            df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
            df_aux['deliveries_perc'] = df_aux['ID'] / df_aux['ID'].sum()
            fig = px.pie(df_aux, values='deliveries_perc', names='Road_traffic_density')
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.header('Traffic order city')
            df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            df_aux = df_aux.loc[df_aux['City'] != 'NaN ', :]
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
            fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart(fig, use_container_width=True)

# Visão tática            
with tab2:
    with st.container():
        st.markdown('# Order by week')
        df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
        df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
        fig = px.line(df_aux, x='week_of_year', y='ID')
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        st.markdown('# Order share by week')
        df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
        df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index()
        df_aux = pd.merge(df_aux01, df_aux02, how='inner')
        df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
        fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
        st.plotly_chart(fig, use_container_width=True)

# Visão geográfica
with tab3:
    with st.container():
        st.markdown('# Country maps')
        df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
        df_aux = df_aux.loc[df_aux['City'] != 'NaN ', :]
        df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
        df_aux = df_aux.head()
        map = folium.Map()
        for index,location_info in df_aux.iterrows():
            folium.Marker([location_info['Delivery_location_latitude'],
                           location_info['Delivery_location_longitude']],
                           popup=location_info[['City', 'Road_traffic_density']]).add_to(map)

        folium_static(map, width=1024, height=600)