# Libraries
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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

st.header('Marketplace - Visão restaurantes')

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

tab1, tab2, tab3 = st.tabs(['Visão gerencial', '_', '_'])

# container métricas
with tab1:
    with st.container():
        st.title('Overall metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.markdown('###### Entregadores')
            delivery_unique = df1.loc[:, 'Delivery_person_ID'].nunique()
            col1.metric('Únicos', delivery_unique)
            
        with col2:
            st.markdown('###### Distância')
            cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
            df1['distance'] = (df1.loc[:, cols].apply(lambda x: 
                                      haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
            avg_distance = np.round(df1['distance'].mean(), 1)
            col2.metric('Média entregas', avg_distance)
            
        with col3:
            st.markdown('###### Tempo médio')
            df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': 'mean'})
            df_aux.columns = ['avg_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'], 1)
            col3.metric('Entrega c/festival', df_aux)
            
        with col4:
            st.markdown('###### Tempo médio')
            df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': 'mean'})
            df_aux.columns = ['avg_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'], 1)
            col4.metric('Entrega s/festival', df_aux)
            
        with col5:
            st.markdown('###### Desvio padrão')
            df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': 'std'})
            df_aux.columns = ['std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'], 1)
            col5.metric('Entrega c/festival', df_aux)
            
        with col6:
            st.markdown('###### Desvio padrão')
            df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': 'std'})
            df_aux.columns = ['std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'std_time'], 1)
            col6.metric('Entrega s/festival', df_aux)
     
    # fig interval
    with st.container():
        st.markdown("""---""")
        st.title('Tempo médio de entrega por cidade')
        cols = ['City','Time_taken(min)']
        df_aux = df1.loc[:, cols].groupby('City').agg({'Time_taken(min)': ['mean','std']})
        df_aux.columns = ['avg_time','std_time']
        df_aux = df_aux.reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'],
                                error_y=dict(type='data', array=df_aux['std_time'])))
        st.plotly_chart(fig)
      
    # fig table
    with st.container():
        st.markdown("""---""")
        st.title('Distribuição da distância')
        cols = ['City', 'Time_taken(min)', 'Type_of_order']
        df_aux = df1.loc[:, cols].groupby(['City','Type_of_order']).agg({'Time_taken(min)': ['mean','std']})
        df_aux.columns = ['avg_time','std_time']
        df_aux = df_aux.reset_index()
        st.dataframe(df_aux)
    
    # fig pie
    with st.container():
        st.markdown("""---""")
        st.title('Distribuição de tempo por cidade')
        cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
        df1['distance'] = (df1.loc[:, cols].apply(lambda x: 
                                      haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()

        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
        st.plotly_chart(fig)
    
    # fig sunburst
    with st.container():
        st.markdown("""---""")
        st.title('Desvio padrão por cidade/tráfego')
        cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
        df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean','std']})
        df_aux.columns = ['avg_time','std_time']
        df_aux = df_aux.reset_index()
        fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                              color='std_time', color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_aux['std_time']))
        st.plotly_chart(fig)