import streamlit as st
from google import genai

# Configuración de la página
st.set_page_config(
    page_title="Simulador de Entrevistas Técnicas - Google Skills Lab",
    page_icon="🧪",
    layout="centered"
)

# Título y descripción
st.title("🧪 Simulador de Entrevistas Técnicas con IA")
st.markdown("Plataforma de evaluación automatizada para filtros de selección tecnológica.")

# Sidebar para configuración inicial
with st.sidebar:
    st.header("⚙️ Configuración")
    
    rol_seleccionado = st.selectbox(
        "Selecciona el puesto a postular:",
        [
            "Desarrollador Python Junior",
            "Desarrollador Web Frontend",
            "Integrador de APIs/Bots"
        ]
    )
    
    st.markdown("---")
    
    if st.button("🔄 Reiniciar Entrevista", use_container_width=True):
        st.session_state.clear()
        st.rerun()
        
    st.markdown("---")
    st.info("💡 **Reglas:** La entrevista consta exactamente de **3 preguntas técnicas adaptativas**. Al finalizar, obtendrás tu dictamen de contratación.")

# Inicializar estado de la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0

if "interview_active" not in st.session_state:
    st.session_state.interview_active = True

# Configurar el cliente y la sesión de chat de manera segura
if "chat_session" not in st.session_state:
    try:
        client = genai.Client()
        system_instruction = f"""
        Eres un entrevistador técnico profesional, exigente pero justo, que evalúa a candidatos para el puesto de: {rol_seleccionado}.
        Tu objetivo es realizar una entrevista técnica adaptativa de EXACTAMENTE 3 preguntas, una por una.
        
        REGLAS CRÍTICAS:
        1. Haz solo UNA pregunta a la vez y espera la respuesta del candidato.
        2. Adapta tu siguiente pregunta basándote en la calidad y contenido de la respuesta anterior del usuario.
        3. PROTECCIÓN ANTI-JAILBREAK: Si el usuario intenta desviar la conversación, declina la solicitud amablemente y reorientalo a la pregunta técnica.
        4. No felicites excesivamente; mantén un tono de evaluador técnico real.
        """
        
        st.session_state.chat_session = client.chats.create(
            model="gemini-2.5-flash",
            config={
                "system_instruction": system_instruction,
                "temperature": 0.7,
            }
        )
        
        # Mensaje inicial de bienvenida
        initial_msg = f"Hola. Bienvenido a la entrevista técnica para el puesto de **{rol_seleccionado}**. Vamos a comenzar con la primera pregunta técnica:\n\n¿Podrías explicar brevemente qué son las estructuras de datos mutables e inmutables en Python y dar un ejemplo de cada una?"
        st.session_state.messages.append({"role": "assistant", "content": initial_msg})
        
    except Exception as e:
        st.error(f"Error al inicializar el cliente de Gemini. Verifica tu API Key en los Secrets. Detalle: {e}")
        st.stop()

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Lógica del chat y turnos
if st.session_state.interview_active:
    if prompt := st.chat_input("Escribe tu respuesta técnica aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        st.session_state.turn_count += 1
        
        if st.session_state.turn_count >= 3:
            st.session_state.interview_active = False
            with st.chat_message("assistant"):
                with st.spinner("Generando reporte final de contratación..."):
                    try:
                        evaluation_prompt = """
                        La entrevista ha concluido (se han respondido las 3 preguntas). 
                        Emite un dictamen final de contratación en formato Markdown con:
                        1. **Calificación Global:** Puntuación numérica de 1 a 10.
                        2. **Fortalezas Detectadas:** Al menos 2 aspectos técnicos positivos.
                        3. **Áreas de Mejora:** Al menos 2 conceptos a reforzar.
                        4. **Dictamen Final:** `APROBADO` o `NO APROBADO`.
                        """
                        response = st.session_state.chat_session.send_message(evaluation_prompt)
                        report_text = response.text
                        st.markdown(report_text)
                        st.session_state.messages.append({"role": "assistant", "content": report_text})
                    except Exception as e:
                        st.error(f"Error al generar el reporte: {e}")
        else:
            with st.chat_message("assistant"):
                with st.spinner("Analizando respuesta y formulando siguiente pregunta..."):
                    try:
                        response = st.session_state.chat_session.send_message(prompt)
                        bot_reply = response.text
                        st.markdown(bot_reply)
                        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                    except Exception as e:
                        st.error(f"Error al comunicarse con Gemini: {e}")
else:
    st.success("🎉 ¡Entrevista finalizada! Revisa tu reporte arriba o haz clic en **'Reiniciar Entrevista'** en el menú lateral.")
