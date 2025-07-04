import streamlit as st
import pandas as pd
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

USERNAME = "cliente"
PASSWORD = "1234"
session_state = st.session_state

if "logged_in" not in session_state:
    session_state.logged_in = False

if not session_state.logged_in:
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Login"):
        if user == USERNAME and pwd == PASSWORD:
            session_state.logged_in = True
        else:
            st.error("Credenciales incorrectas")
    st.stop()

st.title("Portal de subida de archivos")

# 1) Mostrar plataformas
platform = st.selectbox("Selecciona una plataforma:", ["TikTok", "Meta", "YouTube"])

# 2) Subir archivo
uploaded_file = st.file_uploader("Selecciona un archivo Excel", type=["xls", "xlsx"])

# 3) Botón de validación separado
if uploaded_file:
    if st.button("Validar"):
        try:
            df = pd.read_excel(uploaded_file)
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
            
            if uploaded_columns == required_columns:
                st.success("El archivo se ha subido correctamente ✅")
                
                # Subir a Google Drive
                gauth = GoogleAuth()
                gauth.LocalWebserverAuth()
                drive = GoogleDrive(gauth)

                temp_filename = uploaded_file.name
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.read())

                folder_id = "TU_FOLDER_ID"
                file_drive = drive.CreateFile({
                    "title": f"{platform}_{uploaded_file.name}",
                    "parents": [{"id": folder_id}]
                })
                file_drive.SetContentFile(temp_filename)
                file_drive.Upload()
                st.success(f"Archivo subido a Google Drive en la carpeta para {platform}.")
            else:
                st.error("No validado ❌. Las columnas no coinciden exactamente con las requeridas.")
        except Exception as e:
            st.error(f"No validado ❌. Error al leer el archivo Excel: {e}")
