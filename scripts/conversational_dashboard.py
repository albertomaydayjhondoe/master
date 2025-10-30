st.set_page_config(page_title="Community Manager Conversacional", layout="centered")
st.title("🤖 Community Manager ML - Chat")
st.write("Envía preguntas o comandos para recibir recomendaciones ML personalizadas para tu canal artístico.")
st.info("Puedes pedir: recomendaciones de contenido, horarios óptimos, análisis de campañas, optimización de presupuesto, etc.")

import streamlit as st
import requests
import os

st.set_page_config(page_title="Asesor Artístico ML", layout="centered")
st.title("🎨🤖 Asesor Artístico ML - Chat")

API_URL = os.getenv("ML_CORE_API_URL", "https://your-railway-backend-url/".rstrip("/"))

if "history" not in st.session_state:
    st.session_state["history"] = []
if "admin" not in st.session_state:
    st.session_state["admin"] = False

menu = st.sidebar.selectbox("Menú", ["Artista (chat)", "Admin"])

ADMIN_PASS = os.getenv("DASHBOARD_ADMIN_PASS", "Bac2317")
if menu == "Admin":
    pwd = st.sidebar.text_input("Contraseña admin", type="password")
    if pwd == ADMIN_PASS:
        st.session_state["admin"] = True
        st.success("Acceso admin concedido.")
        st.subheader("Panel de administración")
        st.write("- Ver logs de conversación")
        st.write("- Configurar parámetros ML")
        st.write("- (Personaliza aquí más opciones de admin)")
        st.write(st.session_state["history"])
    else:
        st.session_state["admin"] = False
        st.warning("Introduce la contraseña para acceder al panel admin.")
else:
    st.write("Bienvenido/a. Soy tu asesor ML para proyectos artísticos. Hazme preguntas sobre promoción, campañas, horarios, contenido, presupuesto, etc. (nivel tecnológico: medio)")
    user_input = st.text_input("¿En qué puedo ayudarte hoy?", "", key="input")
    if st.button("Enviar", key="send") and user_input:
        st.session_state["history"].append(("Artista", user_input))
        # Respuesta dummy para funcionamiento sin backend
        answer = "Respuesta de prueba: el backend no está disponible."
        st.session_state["history"].append(("Asesor ML", answer))
    for speaker, msg in st.session_state["history"]:
        st.markdown(f"**{speaker}:** {msg}")
    st.info("Puedes pedir: recomendaciones de contenido, horarios óptimos, análisis de campañas, optimización de presupuesto, etc. El asesor responde adaptado a artistas con nivel tecnológico medio.")
