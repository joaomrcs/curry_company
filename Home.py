import streamlit as st
from PIL import Image

st.set_page_config(page_title='Home', page_icon='🎲')

image = Image.open('logo.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry company')
st.sidebar.markdown('## Fastest delivery in Town.')
st.sidebar.markdown("""---""")

st.write('# Curry company growth dashboard')

st.markdown(
    """
        Growth dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
        ### Como utilizar esse growth dashboard?
        - Visão empresa:
            - Visão gerencial: Métricas gerais de comportamento.
            - Visão tática: Indicadores semanais de crescimento.
            - Visão geográfica: Insight's de geolocalização.
        - Visão entregador:
            - Acompanhamento dos indicadores semanais de crescimento dos entregadores.
        - Visão restaurante:
            - Indicadores semanais de crescimento dos restaurantes.
        ### Ask for help
        - Time de data science no discord.
            - @joaomarcos
    """)