import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. Configuración de la Página ---
st.set_page_config(
    layout="wide",
    page_title="Dashboard de Rendimiento Estudiantil",
    page_icon="🎓"
)

# --- 2. Título Principal ---
st.title("🎓 Dashboard de Rendimiento Estudiantil")
st.markdown("Análisis interactivo del rendimiento basado en factores demográficos y preparación.")

st.markdown("---")

# --- 3. Carga y Procesamiento de Datos ---
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()
        df['average_subjects'] = df[['math score', 'reading score', 'writing score']].mean(axis=1)
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo '{file_path}'.")
        st.info("Asegúrate de que 'StudentsPerformance.csv' esté en el mismo directorio.")
        return None

df = load_data("StudentsPerformance.csv")

if df is None:
    st.stop()

# --- 4. Barra Lateral de Filtros (Modificada) ---
st.sidebar.header("Filtros Interactivos 🔍")

# Filtro de Género (modificado a st.radio)
# Opciones: 'General' (todos), 'Female', 'Male'
selected_gender = st.sidebar.radio(
    "Seleccionar Género:",
    options=['General', 'Female', 'Male'],
    index=0  # Por defecto, 'General'
)

# --- 5. Aplicar Filtros al DataFrame (Lógica simplificada) ---

if selected_gender == 'General':
    # No aplicar filtro de género, usar todos los datos
    df_filtered = df.copy() 
elif selected_gender == 'Female':
    # Filtrar solo por 'female' (minúsculas, como en el CSV)
    df_filtered = df[df['gender'] == 'female'].copy()
elif selected_gender == 'Male':
    # Filtrar solo por 'male' (minúsculas, como en el CSV)
    df_filtered = df[df['gender'] == 'male'].copy()


# Advertencia si no hay datos (esto es poco probable ahora, pero es buena práctica)
if df_filtered.empty:
    st.warning("No se encontraron datos.")
    st.stop()

# --- 6. Cálculo de Promedios (Tarjetas Informativas) ---
st.header("Resumen de Promedios (Según Filtros)")

# Calcular promedios de las columnas originales
avg_math = df_filtered['math score'].mean()
avg_reading = df_filtered['reading score'].mean()
avg_writing = df_filtered['writing score'].mean()
avg_total = df_filtered['average_subjects'].mean()

# Mostrar en columnas como métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Promedio Matemáticas", f"{avg_math:.2f}")
col2.metric("Promedio Lectura", f"{avg_reading:.2f}")
col3.metric("Promedio Escritura", f"{avg_writing:.2f}")
col4.metric("Promedio General (Avg)", f"{avg_total:.2f}")

st.markdown("---")

# --- 7. Gráficos Visuales ---
st.header("Análisis Visual de Promedios")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    # Gráfico de Pastel (Género vs Promedio)
    st.subheader("Promedio por Género")
    
    # Lógica condicional: Mostrar el gráfico de pastel solo si se selecciona "General"
    if selected_gender == 'General':
        df_gender_avg = df_filtered.groupby('gender')['average_subjects'].mean().reset_index()
        fig_pie = px.pie(
            df_gender_avg,
            names='gender',
            values='average_subjects',
            title="Relación Género vs Promedio General",
            hole=0.3
        )
        fig_pie.update_traces(textinfo='percent+label', pull=[0.05, 0.05])
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        # Si se selecciona "Female" o "Male", mostrar un mensaje
        st.info(f"Mostrando datos solo para: {selected_gender}")
        # Opcional: Mostrar el promedio del género seleccionado
        st.metric(f"Promedio para {selected_gender}", f"{avg_total:.2f}")


with col_graf2:
    # Gráfico de Barras Horizontales (Nivel Educativo vs Promedio)
    st.subheader("Promedio por Nivel Educativo de Padres")
    df_edu_avg = df_filtered.groupby('parental level of education')['average_subjects'].mean().reset_index().sort_values(by="average_subjects")
    
    fig_bar_h = px.bar(
        df_edu_avg,
        x='average_subjects',
        y='parental level of education',
        orientation='h',
        title="Promedio vs Nivel Educativo de Padres"
    )
    fig_bar_h.update_layout(xaxis_title="Promedio General", yaxis_title="Nivel Educativo")
    st.plotly_chart(fig_bar_h, use_container_width=True)

# Gráfico de Barras Verticales (Raza/Etnia vs Promedio)
st.subheader("Promedio por Etnia/Raza")
df_race_avg = df_filtered.groupby('race/ethnicity')['average_subjects'].mean().reset_index()

fig_bar_v = px.bar(
    df_race_avg,
    x='race/ethnicity',
    y='average_subjects',
    title="Promedio vs Etnia/Raza",
    color='race/ethnicity'
)
fig_bar_v.update_layout(xaxis_title="Etnia/Raza", yaxis_title="Promedio General")
st.plotly_chart(fig_bar_v, use_container_width=True)

st.markdown("---")

# --- 8. Tabla de Datos Finales ---
st.header("Datos Detallados (Ordenados por Promedio)")
st.markdown("Tabla filtrada y ordenada de mayor a menor por el promedio general.")

columns_to_show = [
    'gender', 'race/ethnicity', 'parental level of education',
    'lunch', 'test preparation course', 'math score',
    'reading score', 'writing score', 'average_subjects'
]

df_sorted = df_filtered[columns_to_show].sort_values('average_subjects', ascending=False)

st.dataframe(
    df_sorted.style.format({"average_subjects": "{:.2f}"}),
    use_container_width=True
)