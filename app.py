import streamlit as st
import requests

# Configuración Base de la API (Ajusta el puerto según tu VS)
API_BASE_URL = "http://gimnasio.tryasp.net/api"
st.set_page_config(page_title="Gimnasio Pro - Gestión", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .valido { background-color: #00FF00; color: #000000; padding: 20px; border-radius: 10px; text-align: center; border: 5px solid #000; }
    .denegado { background-color: #FF0000; color: #000000; padding: 20px; border-radius: 10px; text-align: center; border: 5px solid #000; }
    .stButton>button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE SESIÓN ---
if "token" not in st.session_state:
    st.session_state.token = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# --- LÓGICA DE LOGIN ---
def login():
    st.title("🔐 Ingreso al Sistema")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        btn_login = st.form_submit_button("ENTRAR")
        
        if btn_login:
            try:
                # verify=False solo para desarrollo si usas certificados self-signed
                res = requests.post(f"{API_BASE_URL}/Usuarios/login", 
                                    json={"email": email, "password": password}, verify=False)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data["token"]
                    st.session_state.user_role = data["usuario"]["rolNombre"]
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# --- PANTALLA PRINCIPAL ---
def main_app():
    st.sidebar.title(f"👤 {st.session_state.user_role}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.token = None
        st.rerun()

    tab1, tab2 = st.tabs(["🛡️ Control de Acceso", "🔍 Buscador de Socios"])

    # HEADER PARA PETICIONES AUTORIZADAS
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    # --- TAB 1: VALIDACIÓN DE ACCESO ---
    with tab1:
        st.subheader("Verificación de Membresía")
        with st.form("validador"):
            entrada_id = st.text_input("Ingrese ID del Socio")
            btn_check = st.form_submit_button("VALIDAR")
            
            if btn_check and entrada_id:
                res = requests.get(f"{API_BASE_URL}/Usuarios/{entrada_id}/validar-acceso-id", 
                                   headers=headers, verify=False)
                if res.status_code == 200:
                    info = res.json()
                    if info["status"] == "Concedido":
                        st.markdown(f'<div class="valido"><h1>ACCESO PERMITIDO</h1><p>{info["mensaje"]}</p></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="denegado"><h1>ACCESO DENEGADO</h1><p>{info["mensaje"]}</p></div>', unsafe_allow_html=True)
                else:
                    st.warning("No se pudo validar. Verifique el ID.")

    # --- TAB 2: BUSCADOR (SOLO ADMIN Y EMPLEADO) ---
    with tab2:
        if st.session_state.user_role in ["Admin", "Empleado"]:
            st.subheader("Buscador de Socios Activos")
            res_socios = requests.get(f"{API_BASE_URL}/Usuarios/socios", headers=headers, verify=False)
            
            if res_socios.status_code == 200:
                socios = res_socios.json()
                busqueda = st.text_input("Filtrar por nombre o DNI")
                
                # Filtrado simple en frontend
                filtered = [s for s in socios if busqueda.lower() in s["nombre"].lower() or busqueda in s["dni"]]
                
                st.table(filtered)
            else:
                st.error("No tienes permisos para ver esta lista.")
        else:
            st.info("🔒 El buscador solo está disponible para personal del gimnasio.")

# Renderizar Login o App
if st.session_state.token is None:
    login()
else:
    main_app()

