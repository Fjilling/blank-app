import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import gdown
import re
import os
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import matplotlib.pyplot as plt



# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Pronóstico',
        page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
        )
        #st.title("Forecasting Mensual de Ventas")

st.title("🎈 Analítica Predictiva")
st.write(
    "para colocar cualquier otro html..."
)


# Input usuario
user_input = st.text_input("Pegue el LINK o FILE_ID de Google Drive")

if user_input:

    # Extraer file_id
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", user_input)
    file_id = match.group(1) if match else user_input

    url = f"https://drive.google.com/uc?id={file_id}"
    file_path = "dataset.csv"

    if not os.path.exists(file_path):
        gdown.download(url, file_path, quiet=True)

    df = pd.read_csv(file_path)
    df['Fecha'] = pd.to_datetime(df['Fecha'])

    df_monthly = df.set_index('Fecha').resample('ME')['Total'].sum()

    model = ExponentialSmoothing(
        df_monthly,
        trend='add',
        seasonal='add',
        seasonal_periods=12
    )

    fit = model.fit()
    forecast = fit.forecast(12)

    fig = plt.figure()
    plt.plot(df_monthly)
    plt.plot(forecast)
    plt.title("Forecast 12 meses")

    st.pyplot(fig)

st.title("Dashboard Tesis")

powerbi_iframe = """
<iframe title="Dashboard Tesis"
        width="100%"
        height="600"
        src="https://app.powerbi.com/view?r=eyJrIjoiNTQyMDExN2UtZjEyYi00YzhkLTk1ZGUtNTc1ODcwMTA3MGRjIiwidCI6ImI3YWY4Y2FmLTgzZDgtNDY0NC04NWFlLTMxN2M1NDUyMjNjMSIsImMiOjR9"
        frameborder="0"
        allowFullScreen="true">
</iframe>
"""

components.html(powerbi_iframe, height=650, scrolling=True)