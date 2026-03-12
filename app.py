import streamlit as st
import requests

# --- CONFIGURACIÓN ---
API_BASE_URL = "http://gimnasio.tryasp.net/api"
st.set_page_config(page_title="Gimnasio Pro - Gestión", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .valido { background-color: #2ecc71; color: white; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #27ae60; }
    .denegado { background-color: #e74c3c; color: white; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #c0392b; }
    .stButton>button { width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE SESIÓN ---
if "token" not in st.session_state:
    st.session_state.token = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None

# --- LÓGICA DE LOGIN ---
def login():
    st.title("🔐 Gimnasio Pro - Acceso")
    
    # Centrar el formulario
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Correo Electrónico").strip()
            password = st.text_input("Contraseña", type="password")
            btn_login = st.form_submit_button("INGRESAR")
            
            if btn_login:
                if not email or not password:
                    st.warning("Por favor, complete todos los campos.")
                    return

                try:
                    # Petición a la API real
                    res = requests.post(
                        f"{API_BASE_URL}/Usuarios/login", 
                        json={"email": email, "password": password}
                    )
                    
                    if res.status_code == 200:
                        data = res.json()
                        # Guardamos datos según la estructura de tu JSON real
                        st.session_state.token = data["token"]
                        st.session_state.user_role = data["usuario"]["rolNombre"]
                        st.session_state.user_name = data["usuario"]["nombre"]
                        st.success(f"¡Bienvenido/a {st.session_state.user_name}!")
                        st.rerun()
                    elif res.status_code == 401:
                        st.error("Credenciales incorrectas. Verifique email y contraseña.")
                    else:
                        st.error(f"Error de servidor: {res.status_code}")
                except Exception as e:
                    st.error(f"No se pudo conectar con la API: {e}")

# --- PANTALLA PRINCIPAL ---
def main_app():
    # Sidebar de navegación
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    st.sidebar.write(f"Rol: **{st.session_state.user_role}**")
    
    if st.sidebar.button("Cerrar Sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.sidebar.divider()
    st.sidebar.info("Gimnasio Pro v1.0 - Conectado a tryasp.net")

    tab1, tab2 = st.tabs(["🛡️ Control de Acceso", "🔍 Buscador de Socios"])
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    # --- TAB 1: VALIDACIÓN DE ACCESO ---
    with tab1:
        st.subheader("Verificación de Membresía")
        with st.form("validador"):
            entrada_id = st.text_input("Ingrese ID del Socio")
            btn_check = st.form_submit_button("VALIDAR ENTRADA")
            
            if btn_check and entrada_id:
                try:
                    # Endpoint: /api/Usuarios/{id}/validar-acceso-id
                    res = requests.get(
                        f"{API_BASE_URL}/Usuarios/{entrada_id}/validar-acceso-id", 
                        headers=headers
                    )
                    
                    if res.status_code == 200:
                        info = res.json()
                        # Lógica basada en el campo 'status' de tu API
                        if info.get("status") == "Concedido":
                            st.markdown(f'<div class="valido"><h1>✅ ACCESO PERMITIDO</h1><p>{info["mensaje"]}</p></div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="denegado"><h1>❌ ACCESO DENEGADO</h1><p>{info["mensaje"]}</p></div>', unsafe_allow_html=True)
                    else:
                        st.warning(f"Socio no encontrado o error en consulta (Status: {res.status_code})")
                except Exception as e:
                    st.error(f"Error de red: {e}")

    # --- TAB 2: BUSCADOR (ADMIN Y EMPLEADO) ---
    with tab2:
        if st.session_state.user_role in ["Admin", "Empleado"]:
            st.subheader("Buscador de Socios Activos")
            
            # Botón para refrescar datos
            if st.button("🔄 Actualizar Lista"):
                st.cache_data.clear()

            try:
                res_socios = requests.get(f"{API_BASE_URL}/Usuarios/socios", headers=headers)
                
                if res_socios.status_code == 200:
                    socios = res_socios.json()
                    busqueda = st.text_input("Buscar por Nombre, Apellido o DNI").lower()
                    
                    # Filtrado en caliente
                    filtered = [
                        s for s in socios 
                        if busqueda in s["nombre"].lower() or 
                           busqueda in s["apellido"].lower() or 
                           busqueda in s["dni"]
                    ]
                    
                    if filtered:
                        # Mostramos los campos más importantes
                        st.dataframe(
                            filtered, 
                            column_order=("id", "nombre", "apellido", "dni", "email", "rolNombre"),
                            use_container_width=True
                        )
                    else:
                        st.write("No se encontraron socios con ese criterio.")
                else:
                    st.error("Error al obtener la lista de socios.")
            except Exception as e:
                st.error(f"Error al cargar socios: {e}")
        else:
            st.info("🔒 El buscador solo está disponible para personal autorizado.")

# --- LÓGICA DE ARRANQUE ---
if st.session_state.token is None:
    login()
else:
    main_app()


