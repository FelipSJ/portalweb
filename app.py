import streamlit as st
import pandas as pd
import re
import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

session_state = st.session_state

# Usuarios y contraseñas
USERS = {
    "cliente": {
        "password": "1234",
        "platforms": ["TikTok", "Meta", "YouTube"]
    },
    "ING_iprospect": {
        "password": "iprospect_ing_202",
        "platforms": ["YouTube"]
    }
}

if "logged_in" not in session_state:
    session_state.logged_in = False

if not session_state.logged_in:
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Login"):
        if user in USERS and pwd == USERS[user]["password"]:
            session_state.logged_in = True
            session_state.current_user = user
        else:
            st.error("Credenciales incorrectas")
    st.stop()

st.title("Portal de subida de archivos")

current_user = session_state.get("current_user")
if current_user is None:
    st.stop()

# Mostrar plataformas según el usuario logueado
platforms = USERS[current_user]["platforms"]
if len(platforms) == 1:
    platform = platforms[0]
    st.write(f"Plataforma asignada: **{platform}**")
else:
    platform = st.selectbox("Selecciona una plataforma:", platforms)

# Subida de archivo CSV
uploaded_file = st.file_uploader("Selecciona un archivo CSV", type=["csv"])

if uploaded_file:
    if st.button("Validar"):
        try:
            df = pd.read_csv(uploaded_file)
            required_columns = [
                "Día", "Estado de los anuncios", "URL final", "URL de baliza", "Título",
                "Título largo 1", "Título largo 2", "Título largo 3", "Título largo 4", "Título largo 5",
                "Título 1", "Título 2", "Título 3", "Título 4", "Título 5", "Descripción 1", "Descripción 2",
                "Descripción 3", "Descripción 4", "Descripción 5", "Texto de llamada a la acción",
                "Texto de llamada a la acción 1", "Texto de llamada a la acción 2", "Texto de llamada a la acción 3",
                "Texto de llamada a la acción 4", "Texto de llamada a la acción 5", "Título de la llamada a la acción",
                "ID de vídeo", "Banner complementario", "Nombre del anuncio", "ad.display_url", "Ruta 1", "Ruta 2",
                "URL final para móviles", "Plantilla de seguimiento", "Sufijo de URL final", "Parámetro personalizado",
                "Campaña", "Grupo de anuncios", "Estado", "Motivos del estado", "Tipo de anuncio",
                "Eficacia del anuncio", "Mejoras en la eficacia del anuncio", "Impr.", "Clics", "Tasa de interacción",
                "Interacciones", "Me gusta obtenidos", "Vídeo", "Veces que se ha compartido",
                "Vídeo reproducido hasta el 25 %", "Vídeo reproducido hasta el 50 %", "Vídeo reproducido hasta el 75 %",
                "Vídeo reproducido al 100 %", "Vistas"
            ]
            uploaded_columns = df.columns.tolist()
            
            # 1) Validar columnas
            if uploaded_columns != required_columns:
                st.error("No validado ❌. Las columnas no coinciden exactamente con las requeridas.")
                st.stop()
            
            # 2) Validar nombre del archivo (solo para ING_iprospect en YouTube)
            if current_user == "ING_iprospect" and platform == "YouTube":
                filename = uploaded_file.name
                now = datetime.datetime.now()
                current_month = f"{now.month:02d}"
                current_year = f"{now.year%100:02d}"  # dos cifras
                months_es = ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO",
                             "JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]
                current_month_name = months_es[now.month-1].upper()
                expected_pattern = f"{current_month}_ING_YT_FCC_PROYECTO_{current_month_name}{current_year}\\.csv"
                
                if not re.fullmatch(expected_pattern, filename):
                    st.error(f"No validado ❌. El archivo debe llamarse exactamente como: {expected_pattern}")
                    st.stop()
            
            # 3) Si todo pasa, subir a Drive
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()
            drive = GoogleDrive(gauth)

            temp_filename = uploaded_file.name
            with open(temp_filename, "wb") as f:
                f.write(uploaded_file.read())

            folder_id = "1UU1yCA1DdeMU_-w2kDF18sEI41JRlfxt"  # carpeta ING YouTube
            file_drive = drive.CreateFile({
                "title": uploaded_file.name,
                "parents": [{"id": folder_id}]
            })
            file_drive.SetContentFile(temp_filename)
            file_drive.Upload()
            st.success("El archivo se ha subido correctamente ✅")
            st.success("Archivo subido a Google Drive en la carpeta asignada para YouTube.")

        except Exception as e:
            st.error(f"No validado ❌. Error al procesar el archivo: {e}")
