import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import gdown
import matplotlib.pyplot as plt
import os

# Configuración de la página
st.set_page_config(
    page_title='Analítica de negocio',
        page_icon=':chart_with_upwards_trend:', # This is an emoji shortcode. Could be a URL too.
        )


# --- 1. DESCARGA Y CARGA DE DATOS ---

@st.cache_data
def load_data():
    # Fuente 1: Histórico de ventas
    file1_id = '1hyEqmcdNLdfZ6n_XKQkkWqNo3EooUh35'
    path1 = 'df_TOP5.xlsx'
    if not os.path.exists(path1):
        gdown.download(id=file1_id, output=path1, quiet=True)
    df_hist = pd.read_excel(path1)
    df_hist['Semana'] = pd.to_datetime(df_hist['Semana'])

    # Fuente 2: Predicciones
    file2_id = '1lYm1Qau0vt6K9et1mogijG6Lq8QDSP2H'
    path2 = 'df_predict.xlsx'
    if not os.path.exists(path2):
        gdown.download(id=file2_id, output=path2, quiet=True)
    df_pred = pd.read_excel(path2)
    df_pred['Semana'] = pd.to_datetime(df_pred['Semana'])
    
    return df_hist, df_pred

df_hist, df_pred = load_data()

# --- 2. ESTRUCTURA DE PESTAÑAS ---
tab1, tab2 = st.tabs(["PRONÓSTICO", "DASHBOARD ESTRATÉGICO"])

with tab1:
    st.header("PROYECCIÓN DE DEMANDA")

    # --- 1. FECHAS DEL PRONÓSTICO DE DEMANDA ---
    # Extraemos fechas límite
    fecha_min = df_pred['Semana'].min()
    fecha_max = df_pred['Semana'].max()

    # Calculamos el número de semanas totales
    # Usamos .days // 7 para obtener el número entero de semanas
    semanas_totales = (fecha_max - fecha_min).days // 7 + 1 

    st.subheader("FECHAS DEL PRONÓSTICO DE DEMANDA")

    # Diccionario para meses en español (opcional, para asegurar el idioma)
    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
        7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }

    # Formateamos las cadenas de fecha
    f_min_str = f"{fecha_min.day} de {meses[fecha_min.month]} {fecha_min.year}"
    f_max_str = f"{fecha_max.day} de {meses[fecha_max.month]} {fecha_max.year}"

    # Mostramos el mensaje final
    st.info(f"📅 Predicción desde: **{f_min_str}**, hasta: **{f_max_str}** ({semanas_totales} semanas totales)")

    # --- SECCIÓN 2: DEMANDA PROYECTADA: GRÁFICO ---
    st.subheader("DEMANDA PROYECTADA")
    
    fig, ax = plt.subplots(figsize=(10, 4))
    # Histórico (Fuente 1)
    ax.plot(df_hist['Semana'], df_hist['Weekly_Sales'], label='Demanda Real (Histórico)', color='#1f77b4')
    # Predicción (Fuente 2)
    ax.plot(df_pred['Semana'], df_pred['TOP5_Total'], label='Predicción Futura', color='#ff7f0e')
    
    ax.set_xlabel("Semana")
    ax.set_ylabel("Unidades")
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # --- 3. TOP 5 SKUs CON MAYOR DEMANDA PROYECTADA (CONGRUENCIA GLOBAL) ---
    st.subheader("TOP 5 SKUs CON MAYOR DEMANDA PROYECTADA")

    skus = ['ISD-007T-0006', 'ISD-007T-0007', 'ISD-007T-0008', 'ISD-007T-0009', 'ISD-007T-0010']

    # 1. Calculamos la suma decimal exacta de cada SKU y el total objetivo
    sumas_decimales = [df_pred[sku].sum() for sku in skus]
    total_objetivo_global = round(df_pred['TOP5_Total'].sum())

    # 2. Aplicamos Método del Residuo Mayor (Hare-Niemeyer) sobre los totales
    # Paso A: Suelo (parte entera)
    valores_enteros = [int(np.floor(s)) for s in sumas_decimales]
    # Paso B: Diferencia contra el total del modelo
    diferencia = total_objetivo_global - sum(valores_enteros)
    # Paso C: Residuos decimales
    residuos = [s - np.floor(s) for s in sumas_decimales]
    # Paso D: Repartir unidades sobrantes a los decimales más altos
    indices_residuos = np.argsort(residuos)[::-1]
    for i in range(int(diferencia)):
        valores_enteros[indices_residuos[i]] += 1

    # 3. Crear el DataFrame de 2 columnas x 6 filas (incluyendo encabezado)
    df_top5_resumen = pd.DataFrame({
        'SKU ID': skus,
        'Cantidad Total Proyectada': [f"{v:,.0f}" for v in valores_enteros]
    })

    # 4. Visualización limpia en Streamlit
    st.dataframe(
        df_top5_resumen,
        use_container_width=True,
        hide_index=True,
        column_config={
            "SKU ID": st.column_config.Column("SKU ID", width="medium"),
            "Cantidad Total Proyectada": st.column_config.Column("Cantidad Total Proyectada", width="medium")
        }
    )
    # --- SECCIÓN 4: MÉTRICAS DE VALIDACIÓN ---
    st.markdown("---")
    st.subheader("VALIDACIÓN DEL MODELO DE PREDICCIÓN")
    
    # Confianza: Promedio de WAPE_TopDown_Total
    confianza_neta = 1 - df_pred['WAPE_TopDown_Total'].mean()
    
    st.metric(label="CONFIANZA EN EL PRONÓSTICO", value=f"{confianza_neta:.2%}")

with tab2:
    # --- SECCIÓN: POWER BI (Nuevo Enlace) ---
    
    # Hemos actualizado el src y ajustado el width al 100% para mejor visualización
    powerbi_iframe = """
    <iframe title="Dashboard Tesis" 
            width="100%" 
            height="500" 
            src="https://app.powerbi.com/view?r=eyJrIjoiYWE5NjBiNWMtNGYyMi00ODQxLTg1YTEtZjY1NmMzZTQ0ZWEzIiwidCI6ImI3YWY4Y2FmLTgzZDgtNDY0NC04NWFlLTMxN2M1NDUyMjNjMSIsImMiOjR9" 
            frameborder="0" 
            allowFullScreen="true">
    </iframe>
    """
    
    # El height aquí debe ser un poco mayor al del iframe para evitar scrolls dobles
    components.html(powerbi_iframe, height=550, scrolling=True)