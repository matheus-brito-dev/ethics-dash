import streamlit as st
import pandas as pd
import time
import plotly.express as px
from geopy.geocoders import Nominatim

# Configuração da página
st.set_page_config(page_title="Ethics Dashboard of Missing Persons", layout="wide")

# === Inicialização ===
geolocator = Nominatim(user_agent="painel-desaparecidos")

FAIXA_MEDIA = {
    '0-11': 5.5,
    '12-17': 14.5,
    '18-29': 23.5,
    '30-44': 37,
    '45-59': 52,
    '60+': 70
}

# === Carregamento de dados ===
@st.cache_data
def load_data():
    return pd.read_csv("csv/base_publica_desaparecidos.csv")

@st.cache_data(show_spinner=False)
def buscar_lat_long(cidade, estado):
    try:
        time.sleep(1)
        location = geolocator.geocode(f"{cidade}, {estado}, Brasil")
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return None, None

# === Funções Analíticas ===
def compute_indicators(df):
    total = df[df['encontrado'] == False].shape[0]
    media_dias = round(df["tempo_desaparecido_dias"].mean(), 1)
    df['idade_media_estimada'] = df['faixa_etaria'].map(FAIXA_MEDIA)
    media_idade = round(df['idade_media_estimada'].mean(), 1)
    return total, media_dias, media_idade

def time_series(df):
    df['data_ocorrido_desaparecimento'] = pd.to_datetime(df['data_ocorrido_desaparecimento'], errors='coerce')
    df_anual = df.groupby(df['data_ocorrido_desaparecimento'].dt.to_period('Y')).size().reset_index(name='quantidade')
    df_anual['data'] = df_anual['data_ocorrido_desaparecimento'].dt.to_timestamp()
    return df_anual

def map_distribution(df):
    df['estado_desaparecimento'] = 'PB'
    df_local = df[['cidade_desaparecimento', 'estado_desaparecimento']].dropna().drop_duplicates()

    df_local[['latitude', 'longitude']] = df_local.apply(
        lambda row: pd.Series(buscar_lat_long(row['cidade_desaparecimento'], row['estado_desaparecimento'])), axis=1
    )

    df_count = df.groupby(['cidade_desaparecimento', 'estado_desaparecimento']).size().reset_index(name='quantidade')
    df_mapa = pd.merge(df_count, df_local, on=['cidade_desaparecimento', 'estado_desaparecimento'], how='left')

    df_mapa = df_mapa.rename(columns={
        'cidade_desaparecimento': 'cidade',
        'estado_desaparecimento': 'estado'
    })

    return df_mapa

# === Componentes Gráficos ===
def show_kpis(df):
    st.subheader("📊 Key Indicators")
    total, media_dias, media_idade = compute_indicators(df)
    col1, col2, col3 = st.columns(3)
    col1.metric("🧍‍♂️ Total of Missing Persons", total)
    col2.metric("📈 Estimated Mean Age", f"{media_idade} years")
    col3.metric("⏱️ Average Time Missing", f"{media_dias} days")

def show_time_series(df):
    st.subheader("📆 Missing Persons Over Time")
    df_anual = time_series(df)
    fig = px.line(df_anual, x="data", y="quantidade", title="Yearly Missing Persons")
    st.plotly_chart(fig, use_container_width=True)

def show_city_map(df):
    st.subheader("🗺️ Geographic Missing Person Distribution by City")
    df_mapa = map_distribution(df)
    fig = px.scatter_mapbox(df_mapa.dropna(subset=['latitude', 'longitude']),
                            lat="latitude", lon="longitude",
                            size="quantidade",
                            hover_name="cidade",
                            color_discrete_sequence=["#FF5733"],
                            zoom=6,
                            mapbox_style="carto-darkmatter",
                            title="Map of Missing Persons")
    st.plotly_chart(fig, use_container_width=True)

def show_filters(df):
    st.subheader("🎛️ Find a Missing Person")

    with st.form("form_filters"):
        uf = st.selectbox("UF:", options=['PB'])
        sexo = st.selectbox("Sex:", options=['Todos'] + sorted(df['sexo'].dropna().unique().tolist()))
        cidade_desaparecimento = st.selectbox("City:", options=['Todos'] + sorted(df['cidade_desaparecimento'].dropna().unique().tolist()))
        faixa_etaria = st.selectbox("Age range:", options=['Todos'] + sorted(df['faixa_etaria'].dropna().unique().tolist()))

        campos = st.multiselect("📋 Select columns to display:",
                                options=df.columns.tolist(),
                                default=["cidade_desaparecimento", "sexo", "faixa_etaria", "data_ocorrido_desaparecimento"])

        submitted = st.form_submit_button("🔍 Apply Filters")

        if submitted:
            df_filtrado = df.copy()
            df_filtrado = df_filtrado[df_filtrado['estado'] == uf]
            if sexo != "Todos":
                df_filtrado = df_filtrado[df_filtrado['sexo'] == sexo]
            if faixa_etaria != "Todos":
                df_filtrado = df_filtrado[df_filtrado['faixa_etaria'] == faixa_etaria]
            if cidade_desaparecimento != "Todos":
                df_filtrado = df_filtrado[df_filtrado["cidade_desaparecimento"] == cidade_desaparecimento]

            # Verificar se nenhum filtro foi aplicado (usuário manteve tudo como 'Todos')
            if sexo == "Todos" and faixa_etaria == "Todos" and cidade_desaparecimento == "Todos":
                st.info("🔎 No filters applied. Showing all records.")
            else:
                st.success("✅ Filters applied.")

            if df_filtrado.empty:
                st.warning("🚫 No results were found with the selected filters.")
            else:
                st.info("✅ Results founded.")
                st.dataframe(df_filtrado[campos])


# === Interface Principal ===
def main():
    st.title("🛡️ Ethics Dashboard of Missing Persons")
    st.markdown("""
    This dashboard shows anonymized and public information about missing persons.  
    It is structured following principles of **LGPD (General Data Protection Law)** and promotes **ethical data display**.
    """)

    df = load_data()

    show_kpis(df)

    col1, col2 = st.columns(2)
    col3, = st.columns(1)
    with col1:
        show_time_series(df)
    with col2:
        show_city_map(df)
    with col3:
        show_filters(df)

# Execução principal
if __name__ == "__main__":
    main()
