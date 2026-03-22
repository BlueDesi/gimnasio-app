import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
API_BASE_URL = "https://gimnasio.tryasp.net/api"
st.set_page_config(page_title="Gimnasio Pro Ultra", layout="wide", page_icon="🏋️‍♂️")

# --- URL DE LA IMAGEN ---
IMAGE_URL = "https://drive.google.com/thumbnail?id=1PsTkl-oaniJO687yUEo8Y5-gyU1YWfDa&sz=w1200"

# --- INICIALIZACIÓN ---
if "token" not in st.session_state: st.session_state.token = None
if "user_data" not in st.session_state: st.session_state.user_data = {}
if "edit_user" not in st.session_state: st.session_state.edit_user = None

# --- ESTILOS CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;700;900&display=swap');
    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', sans-serif;
        background-color: #000000;
        color: #FFFFFF;
    }}
    h1, h2, h3, .main-header {{
        font-family: 'Bebas Neue', sans-serif;
        letter-spacing: 2px;
    }}
    .main-header {{ 
        font-size: 50px; color: #00D4FF; text-align: center; margin-bottom: 30px; text-transform: uppercase;
    }}
    .metric-card {{ 
        background-color: #111111; padding: 25px; border-radius: 10px; border-left: 5px solid #00D4FF; text-align: center; margin-bottom: 15px;
    }}
    .metric-value {{ font-family: 'Bebas Neue', sans-serif; font-size: 45px; margin-top: 5px; }}
    .molinete-container {{ 
        background-color: #050505; padding: 40px; border-radius: 15px; border: 2px solid #00D4FF; text-align: center;
        box-shadow: 0px 0px 20px rgba(0, 212, 255, 0.2);
    }}
    .stButton>button {{ 
        border-radius: 4px; font-weight: 900; text-transform: uppercase; background-color: #00D4FF; color: black; border: none; height: 3.5em; width: 100%;
    }}
    div.stButton > button:first-child[aria-label="SALIR"], 
    div.stButton > button:first-child[aria-label="CERRAR SESIÓN"],
    div.stButton > button:first-child[aria-label="❌ ELIMINAR"] {{
        background-color: #E50914 !important; color: white !important;
    }}
    input {{ background-color: #222222 !important; color: white !important; border: none !important; border-bottom: 2px solid #444444 !important; }}
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
        if method == "DELETE": return requests.delete(url, headers=headers)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def logout():
    st.session_state.token = None
    st.session_state.user_data = {}
    st.session_state.edit_user = None
    st.rerun()

# --- VISTAS ---
def login_page():
    st.image(IMAGE_URL, use_container_width=True)
    st.markdown("<h1 style='text-align: center; color: #00D4FF;'> GIMNASIO ULTRA </h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.container(border=True):
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            if st.button("INGRESAR AL SISTEMA"):
                res = requests.post(f"{API_BASE_URL}/Usuarios/login", json={"email": email, "password": password})
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data["token"]
                    st.session_state.user_data = data["usuario"]
                    st.rerun()
                else: st.error("Credenciales incorrectas")

def socio_dashboard():
    st.image(IMAGE_URL, use_container_width=True)
    user = st.session_state.user_data
    st.markdown(f"<div class='main-header'>Panel de Socio: {user.get('nombre')}</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    vigente = user.get("membresiaVigente", False)
    with c1: st.markdown(f"<div class='metric-card'><div class='metric-value'>{user.get('nombre')}</div><p>DNI: {user.get('dni')}</p></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:{'#00FF00' if vigente else '#FF0000'}'>{'ACTIVA' if vigente else 'VENCIDA'}</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#00D4FF'>{user.get('diasRestantes', 0)}</div><p>DÍAS</p></div>", unsafe_allow_html=True)
    if st.button("CERRAR SESIÓN"): logout()

def admin_dashboard():
    with st.sidebar:
        st.title("🛡️ STAFF")
        menu = st.radio("Menú", ["Molinete", "Lista de Miembros", "Alta Nuevo Socio", "Gestión Usuarios", "Cargar Cuota"])
        if st.button("SALIR"): logout()

    st.image(IMAGE_URL, use_container_width=True)

    if menu == "Molinete":
        st.header("Control de Acceso")
        bus_val = st.text_input("Ingrese ID o DNI del Socio")
        if st.button("VALIDAR ENTRADA"):
            res = api_call("GET", "Usuarios/socios")
            if res and res.status_code == 200:
                socio = next((s for s in res.json() if str(s['dni']) == bus_val or str(s['id']) == bus_val), None)
                if socio:
                    color_m = "#00D4FF" if socio['membresiaVigente'] else "#FF0000"
                    st.markdown(f'<div class="molinete-container" style="border-color: {color_m}"><div style="font-family: \'Bebas Neue\'; font-size: 55px;">{socio["nombre"]} {socio["apellido"]}</div><div style="font-family: \'Bebas Neue\'; font-size: 40px; color: {color_m};">{socio["diasRestantes"]} DÍAS RESTANTES</div></div>', unsafe_allow_html=True)
                else: st.error("No encontrado")

    elif menu == "Lista de Miembros":
        st.header("Listados de Personal")
        t1, t2, t3 = st.tabs(["Socios", "Empleados", "Admins"])
        with t1:
            res = api_call("GET", "Usuarios/socios")
            if res and res.status_code == 200:
                df = pd.DataFrame(res.json())
                bus = st.text_input("Buscar Socio", key="sk").lower()
                if bus: df = df[df['dni'].astype(str).str.contains(bus) | df['apellido'].str.lower().str.contains(bus)]
                st.dataframe(df[['id', 'nombre', 'apellido', 'dni', 'membresiaVigente', 'diasRestantes']], use_container_width=True)
        with t2:
            res = api_call("GET", "Usuarios/empleados")
            if res and res.status_code == 200:
                st.dataframe(pd.DataFrame(res.json())[['id', 'nombre', 'apellido', 'email']], use_container_width=True)
        with t3:
            res = api_call("GET", "Usuarios/admins")
            if res and res.status_code == 200:
                st.dataframe(pd.DataFrame(res.json())[['id', 'nombre', 'apellido', 'email']], use_container_width=True)

    elif menu == "Alta Nuevo Socio":
        st.header("Nuevo Socio")
        with st.form("f1"):
            c1, c2 = st.columns(2)
            n, a = c1.text_input("Nombre"), c2.text_input("Apellido")
            d, e = c1.text_input("DNI"), c2.text_input("Email")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("REGISTRAR"):
                payload = {"nombre": n, "apellido": a, "dni": d, "email": e, "password": p, "rolId": 3, "fechaNacimiento": "2000-01-01"}
                if api_call("POST", "Usuarios", payload).status_code in [200, 201]: st.success("OK")

    elif menu == "Gestión Usuarios":
        st.header("Editar / Eliminar")
        bus_u = st.text_input("ID o DNI")
        if st.button("BUSCAR"):
            res = api_call("GET", "Usuarios")
            if res:
                st.session_state.edit_user = next((s for s in res.json() if str(s['id']) == bus_u or str(s['dni']) == bus_u), None)
        
        if st.session_state.edit_user:
            u = st.session_state.edit_user
            with st.form("f2"):
                ne, ae = st.text_input("Nombre", u['nombre']), st.text_input("Apellido", u['apellido'])
                if st.form_submit_button("GUARDAR"):
                    u.update({"nombre": ne, "apellido": ae})
                    if api_call("PUT", f"Usuarios/{u['id']}", u).status_code in [200, 204]: 
                        st.success("Actualizado"); st.rerun()

    elif menu == "Cargar Cuota":
        st.header("Cobro de Cuota")
        sid = st.number_input("ID Socio", min_value=1)
        m = st.selectbox("Meses", [1, 3, 6, 12])
        if st.button("PROCESAR PAGO"):
            if api_call("POST", "Membresias", {"usuarioId": int(sid), "meses": m}).status_code in [200, 201]:
                st.balloons(); st.success("Pago acreditado")

# --- MAIN ---
if st.session_state.token is None: login_page()
else:
    rol = st.session_state.user_data.get("rolNombre", "").lower()
    admin_dashboard() if rol in ["admin", "empleado"] else socio_dashboard()
