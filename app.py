import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
API_BASE_URL = "https://gimnasio.tryasp.net/api"
st.set_page_config(page_title="Gimnasio Pro Ultra", layout="wide", page_icon="🏋️‍♂️")

# --- ESTILOS CSS (DARK MODE & ALTO CONTRASTE) ---
st.markdown("""
    <style>
    /* Fondo General */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* Header Estilo */
    .main-header { font-size: 32px; font-weight: bold; color: #00D4FF; margin-bottom: 20px; }
    
    /* Cards de Información */
    .metric-card {
        background-color: #1A1C23;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #30363D;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-card h2 { margin: 10px 0; font-size: 45px; }
    .metric-label { color: #8B949E; font-size: 16px; font-weight: bold; text-transform: uppercase; }

    /* Molinete Alto Contraste */
    .molinete-container {
        background-color: #000000;
        color: #FFFFFF;
        padding: 30px;
        border-radius: 15px;
        border: 3px solid #00D4FF;
        text-align: center;
    }
    .molinete-nombre { font-size: 40px; font-weight: 800; color: #00D4FF; }

    /* Botones */
    .stButton>button {
        background-color: #238636; color: white; border: none;
        border-radius: 8px; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2EA043; border: 1px solid white; }
    
    /* Inputs */
    input { background-color: #0D1117 !important; color: white !important; border: 1px solid #30363D !important; }
    </style>
""", unsafe_allow_html=True)

# --- HELPER API ---
def api_call(method, endpoint, data=None):
    headers = {
        "Authorization": f"Bearer {st.session_state.token}",
        "Content-Type": "application/json",
        "accept": "*/*"
    }
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        if method == "POST": return requests.post(url, json=data, headers=headers)
        if method == "GET": return requests.get(url, headers=headers)
        if method == "PUT": return requests.put(url, json=data, headers=headers)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def logout():
    st.session_state.token = None
    st.session_state.user_data = {}
    st.rerun()

# --- VISTA: LOGIN ---
def login_page():
    st.markdown("<h1 style='text-align: center; color: white;'>⚡ GIMNASIO ULTRA ⚡</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.container(border=True):
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            if st.button("INICIAR SESIÓN"):
                res = requests.post(f"{API_BASE_URL}/Usuarios/login", json={"email": email, "password": password})
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data["token"]
                    st.session_state.user_data = data["usuario"]
                    st.rerun()
                else:
                    st.error("Credenciales Inválidas")

# --- VISTA: SOCIO ---
def socio_dashboard():
    user = st.session_state.user_data
    st.markdown(f"<div class='main-header'>Bienvenido, {user.get('nombre')}</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    # Datos del usuario
    with col1:
        st.markdown(f"""<div class='metric-card'><span class='metric-label'>Socio</span><br>
                    <h3 style='color:white'>{user.get('nombre')} {user.get('apellido')}</h3>
                    <p>DNI: {user.get('dni')}</p></div>""", unsafe_allow_html=True)
    
    # Estado Membresía
    vigente = user.get("membresiaVigente", False)
    color_status = "#238636" if vigente else "#DA3633"
    with col2:
        st.markdown(f"""<div class='metric-card'><span class='metric-label'>Estado</span><br>
                    <h2 style='color:{color_status}'>{'ACTIVA' if vigente else 'VENCIDA'}</h2></div>""", unsafe_allow_html=True)
    
    # Días restantes
    dias = user.get("diasRestantes", 0)
    with col3:
        st.markdown(f"""<div class='metric-card'><span class='metric-label'>Días Restantes</span><br>
                    <h2 style='color:#00D4FF'>{dias}</h2></div>""", unsafe_allow_html=True)

    if st.button("CERRAR SESIÓN", key="logout_socio"):
        logout()

# --- VISTA: ADMIN / EMPLEADO ---
def admin_dashboard():
    with st.sidebar:
        st.title("🛡️ ADMIN PANEL")
        menu = st.radio("Navegación", ["Molinete", "Gestión de Socios", "Nueva Membresía"])
        st.divider()
        if st.button("CERRAR SESIÓN"): logout()

    if menu == "Molinete":
        st.header("Control de Acceso Veloz")
        dni_search = st.text_input("Escanear o Ingresar DNI")
        if st.button("VALIDAR"):
            res = api_call("GET", "Usuarios/socios")
            if res and res.status_code == 200:
                socio = next((s for s in res.json() if str(s['dni']) == dni_search), None)
                if socio:
                    status_color = "#00D4FF" if socio['membresiaVigente'] else "#DA3633"
                    st.markdown(f"""
                        <div class="molinete-container" style="border-color: {status_color}">
                            <div class="molinete-nombre">{socio['nombre']} {socio['apellido']}</div>
                            <div style="font-size: 20px;">DNI: {socio['dni']}</div>
                            <div style="font-size: 30px; font-weight: bold; color:{status_color}">
                                {socio['diasRestantes']} DÍAS RESTANTES
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("SOCIO NO ENCONTRADO")

    elif menu == "Gestión de Socios":
        st.header("Gestión y Modificación")
        tab1, tab2 = st.tabs(["Listado", "Editar Usuario"])
        
        with tab1:
            res = api_call("GET", "Usuarios/socios")
            if res: st.dataframe(res.json(), use_container_width=True)
            
        with tab2:
            st.subheader("Buscar para editar")
            c1, c2 = st.columns(2)
            search_id = c1.text_input("ID de Usuario")
            search_dni = c2.text_input("O buscar por DNI")
            
            if st.button("BUSCAR"):
                # Lógica de búsqueda
                res = api_call("GET", "Usuarios/socios")
                u_found = next((s for s in res.json() if str(s['id']) == search_id or str(s['dni']) == search_dni), None)
                if u_found:
                    st.session_state.edit_user = u_found
                else:
                    st.warning("No se encontró el usuario.")

            if "edit_user" in st.session_state:
                u = st.session_state.edit_user
                with st.form("edit_form"):
                    st.info(f"Editando a: {u['nombre']} (ID: {u['id']})")
                    new_nom = st.text_input("Nombre", value=u['nombre'])
                    new_ape = st.text_input("Apellido", value=u['apellido'])
                    new_dni = st.text_input("DNI", value=u['dni'])
                    new_email = st.text_input("Email", value=u['email'])
                    new_pass = st.text_input("Password (dejar vacío para no cambiar)", type="password")
                    
                    if st.form_submit_button("GUARDAR CAMBIOS"):
                        update_data = {
                            "nombre": new_nom, "apellido": new_ape, 
                            "dni": new_dni, "email": new_email,
                            "password": new_pass, "rolId": 3 # Por defecto socio
                        }
                        r = api_call("PUT", f"Usuarios/{u['id']}", update_data)
                        if r and r.status_code in [200, 204]:
                            st.success("Usuario actualizado correctamente")
                            del st.session_state.edit_user

    elif menu == "Nueva Membresía":
        st.header("Cargar Membresía")
        with st.container(border=True):
            u_id = st.number_input("ID del Socio", min_value=1, step=1)
            st.write("Seleccione duración:")
            col_m1, col_m3, col_m6, col_m12 = st.columns(4)
            
            meses_final = 0
            if col_m1.button("1 MES"): meses_final = 1
            if col_m3.button("3 MESES"): meses_final = 3
            if col_m6.button("6 MESES"): meses_final = 6
            if col_m12.button("1 AÑO"): meses_final = 12
            
            if meses_final > 0:
                r = api_call("POST", "Membresias", {"usuarioId": int(u_id), "meses": meses_final})
                if r and r.status_code in [200, 201]:
                    st.balloons()
                    st.success(f"¡Activados {meses_final} meses al socio {u_id}!")

# --- RUTEO ---
if st.session_state.token is None:
    login_page()
else:
    rol = st.session_state.user_data.get("rolNombre", "").lower()
    if rol in ["admin", "empleado"]:
        admin_dashboard()
    else:
        socio_dashboard()




