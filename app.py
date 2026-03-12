import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
API_BASE_URL = "https://gimnasio.tryasp.net/api"
st.set_page_config(page_title="Gimnasio Pro Ultra", layout="wide", page_icon="🏋️‍♂️")

# --- ESTILOS CSS (INCLUYE ALTO CONTRASTE PARA MOLINETE) ---
st.markdown("""
    <style>
    .main-header { font-size: 30px; font-weight: bold; color: #1E88E5; }
    
    /* Estilo Molinete - Alto Contraste */
    .molinete-container {
        background-color: #87CEEB; 
        color: #000000;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        border: 5px solid #000000;
        margin-top: 20px;
    }
    .molinete-nombre { font-size: 50px; font-weight: 900; text-transform: uppercase; margin-bottom: 10px; }
    .molinete-dias { font-size: 40px; font-weight: 700; }
    
    /* Cards Generales */
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid #ddd;
    }
    .stButton>button { border-radius: 8px; font-weight: bold; height: 3em; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if "token" not in st.session_state:
    st.session_state.token = None
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

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
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# --- VISTA: LOGIN ---
def login_page():
    st.markdown("<h1 style='text-align: center;'>🏋️‍♂️ Sistema de Gimnasio</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.container(border=True):
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            if st.button("INGRESAR", use_container_width=True):
                res = requests.post(f"{API_BASE_URL}/Usuarios/login", json={"email": email, "password": password})
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data["token"]
                    st.session_state.user_data = data["usuario"]
                    st.rerun()
                else:
                    st.error("Acceso denegado")

# --- VISTA: SOCIO ---
def socio_dashboard():
    user = st.session_state.user_data
    st.markdown(f"<div class='main-header'>Hola, {user.get('nombre')}</div>", unsafe_allow_html=True)
    
    try:
        # 1. Llamada a la API
        res = api_call("GET", f"Usuarios/{user.get('id')}")
        
        # SI LA API RESPONDE ERROR (Como ese HTML que me pasaste)
        if res.status_code != 200:
            st.error(f"Error de API: {res.status_code}")
            # Esto te va a mostrar el error exacto si el servidor falla
            return 

        d = res.json()
        
        # 2. Extraemos los datos con valores por defecto para que no explote
        vigente = d.get("membresiaVigente", False)
        dias = d.get("diasRestantes", 0)
        
        # Lógica de colores
        color_estado = "#2ecc71" if vigente else "#e74c3c"
        color_dias = "#f1c40f" if (vigente and dias <= 5) else color_estado
        
        col1, col2 = st.columns(2)
        
        col1.markdown(
            f"<div class='metric-card'>Estado de Membresía<br>"
            f"<h2 style='color:{color_estado}'>{'ACTIVA' if vigente else 'VENCIDA'}</h2></div>", 
            unsafe_allow_html=True
        )
        
        col2.markdown(
            f"<div class='metric-card'>Días Restantes<br>"
            f"<h2 style='color:{color_dias}'>{dias}</h2></div>", 
            unsafe_allow_html=True
        )

        if d.get("fechaVencimiento"):
            fecha_venc = d.get("fechaVencimiento").split("T")[0]
            st.caption(f"Tu suscripción vence el: {fecha_venc}")

    except Exception as e:
        # 3. Si algo falla, esto te dirá QUÉ es lo que falla
        st.error(f"Error en el Dashboard: {e}")
        # Descomenta la línea de abajo para ver la respuesta cruda de la API si falla
        # st.code(res.text)
# --- VISTA: ADMIN / EMPLEADO ---
def admin_dashboard():
    with st.sidebar:
        st.title("Gestión")
        menu = st.radio("Menú", ["Molinete", "Socios", "Alta Membresía"])
        if st.button("Cerrar Sesión"):
            st.session_state.token = None
            st.rerun()

    if menu == "Molinete":
        st.header("🛡️ Control de Acceso")
        dni_input = st.text_input("Ingrese DNI del Socio", placeholder="Ej: 40123456")
        
        if st.button("VALIDAR ENTRADA", use_container_width=True):
            if dni_input:
                res = api_call("GET", f"Usuarios/socios") # Buscamos en la lista de socios
                if res and res.status_code == 200:
                    socio = next((s for s in res.json() if s['dni'] == dni_input), None)
                    
                    if socio:
                        # Bloque de Alto Contraste
                        st.markdown(f"""
                            <div class="molinete-container">
                                <div class="molinete-nombre">{socio['nombre']} {socio['apellido']}</div>
                                <div class="molinete-dias">DÍAS RESTANTES: {socio['diasRestantes']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if socio['membresiaVigente']:
                            st.balloons()
                        else:
                            st.error("ATENCIÓN: Membresía Vencida")
                    else:
                        st.warning("DNI no encontrado en el sistema.")

    elif menu == "Socios":
        st.header("👥 Listado de Socios")
        res = api_call("GET", "Usuarios/socios")
        if res: st.dataframe(res.json(), use_container_width=True)

    elif menu == "Alta Membresía":
        st.header("➕ Nueva Membresía")
        with st.form("form_mem"):
            u_id = st.number_input("ID de Socio", min_value=1)
            meses = st.slider("Meses a acreditar", 1, 12, 1)
            if st.form_submit_button("Activar"):
                r = api_call("POST", "Membresias", {"usuarioId": int(u_id), "meses": meses})
                if r and r.status_code in [200, 201]: st.success("¡Membresía Activada!")

# --- RUTEO ---
if st.session_state.token is None:
    login_page()
else:
    rol = st.session_state.user_data.get("rolNombre", "").lower()
    if rol in ["admin", "empleado"]:
        admin_dashboard()
    else:
        socio_dashboard()


