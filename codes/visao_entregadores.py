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

st.header('Marketplace - Visão entregadores')

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

# Visão gerencial
with tab1:
    # container métricas
    with st.container():
        st.title('Overall metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
            
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3:
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)
            
        with col4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição', pior_condicao)
    
    # container colunas
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Avaliação média por entregador')
            delivery_avg_rating_deliver = (df1.loc[:, ['Delivery_person_ID','Delivery_person_Ratings']]
                                             .groupby('Delivery_person_ID')
                                             .mean())
            delivery_avg_rating_deliver.columns = ['Delivery mean']
            delivery_avg_rating_deliver = delivery_avg_rating_deliver.reset_index()
            st.dataframe(delivery_avg_rating_deliver)
            
        with col2:
            st.markdown('##### Avaliação média por trânsito')
            df_avg_std_rating_by_traffic = (df1.loc[: ,['Delivery_person_Ratings','Road_traffic_density']]
                                               .groupby('Road_traffic_density')
                                               .agg({'Delivery_person_Ratings': ['mean']}))
            df_avg_std_rating_by_traffic.columns = ['delivery mean']
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            st.dataframe(df_avg_std_rating_by_traffic)
            st.markdown('##### Avaliação média por clima')
            df_avg_std_rating_by_weather = (df1.loc[: ,['Delivery_person_Ratings','Weatherconditions']]
                                               .groupby('Weatherconditions')
                                               .agg({'Delivery_person_Ratings': ['mean']}))
            df_avg_std_rating_by_weather.columns = ['Weather mean']
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            st.dataframe(df_avg_std_rating_by_weather)
    
    # container colunas
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                       .groupby(['City', 'Delivery_person_ID'])
                       .mean()
                       .sort_values(['City', 'Time_taken(min)'], ascending=True)
                       .reset_index())

            df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

            df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
            st.dataframe(df3)

        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                    .groupby(['City', 'Delivery_person_ID'])
                    .mean()
                    .sort_values(['City', 'Time_taken(min)'], ascending=False)
                    .reset_index())

            df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

            df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
            st.dataframe(df3)