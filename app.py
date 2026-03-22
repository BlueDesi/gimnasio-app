import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
API_BASE_URL = "https://gimnasio.tryasp.net/api"
st.set_page_config(page_title="Gimnasio Pro Ultra", layout="wide", page_icon="🏋️‍♂️")

# --- INICIALIZACIÓN ---
if "token" not in st.session_state: st.session_state.token = None
if "user_data" not in st.session_state: st.session_state.user_data = {}
if "edit_user" not in st.session_state: st.session_state.edit_user = None

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    .main-header { font-size: 35px; font-weight: 800; color: #00D4FF; text-align: center; margin-bottom: 30px; }
    .metric-card { background-color: #111111; padding: 25px; border-radius: 15px; border: 2px solid #333333; text-align: center; margin-bottom: 15px; }
    .metric-label { color: #AAAAAA; font-size: 14px; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 40px; font-weight: 900; margin-top: 10px; }
    .molinete-container { background-color: #000000; padding: 40px; border-radius: 20px; border: 4px solid #00D4FF; text-align: center; }
    .stButton>button { border-radius: 10px; font-weight: bold; transition: 0.3s; height: 3.5em; }
    input { background-color: #222222 !important; color: white !important; border: 1px solid #444444 !important; }
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
        st.error(f"Error: {e}")
        return None

def logout():
    st.session_state.token = None
    st.session_state.user_data = {}
    st.session_state.edit_user = None
    st.rerun()

# --- VISTA: LOGIN ---
def login_page():
    st.markdown("<h1 style='text-align: center; color: #00D4FF;'>⚡ GIMNASIO ULTRA ⚡</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.container(border=True):
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            if st.button("INGRESAR AL SISTEMA", use_container_width=True):
                res = requests.post(f"{API_BASE_URL}/Usuarios/login", json={"email": email, "password": password})
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data["token"]
                    st.session_state.user_data = data["usuario"]
                    st.rerun()
                else: st.error("Acceso Denegado")

# --- VISTA: SOCIO ---
def socio_dashboard():
    user = st.session_state.user_data
    st.markdown(f"<div class='main-header'>Panel de Socio: {user.get('nombre')}</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='metric-card'><span class='metric-label'>Socio</span><div class='metric-value'>{user.get('nombre')} {user.get('apellido')}</div><p>DNI: {user.get('dni')}</p></div>", unsafe_allow_html=True)
    vigente = user.get("membresiaVigente", False)
    color_v = "#00FF00" if vigente else "#FF0000"
    with c2: st.markdown(f"<div class='metric-card'><span class='metric-label'>Membresía</span><div class='metric-value' style='color:{color_v}'>{'ACTIVA' if vigente else 'VENCIDA'}</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><span class='metric-label'>Días Restantes</span><div class='metric-value' style='color:#00D4FF'>{user.get('diasRestantes', 0)}</div></div>", unsafe_allow_html=True)
    if st.button("CERRAR SESIÓN", use_container_width=True): logout()

# --- VISTA: ADMIN / EMPLEADO ---
def admin_dashboard():
    with st.sidebar:
        st.title("🛡️ STAFF")
        menu = st.radio("Acciones", ["Molinete", "Lista de Miembros", "Alta Nuevo Socio", "Gestión Usuarios", "Cargar Cuota"])
        st.divider()
        if st.button("SALIR", type="primary"): logout()

    if menu == "Molinete":
        st.header("Control de Acceso")
        bus_val = st.text_input("Ingrese ID o DNI del Socio")
        if st.button("VALIDAR ENTRADA"):
            res = api_call("GET", "Usuarios/socios")
            if res and res.status_code == 200:
                socio = next((s for s in res.json() if str(s['dni']) == bus_val or str(s['id']) == bus_val), None)
                if socio:
                    color_m = "#00D4FF" if socio['membresiaVigente'] else "#FF0000"
                    st.markdown(f"""
                        <div class="molinete-container" style="border-color: {color_m}">
                            <div style="font-size: 45px; font-weight: 900;">{socio['nombre']} {socio['apellido']}</div>
                            <div style="font-size: 20px;">ID: {socio['id']} | DNI: {socio['dni']}</div>
                            <div style="font-size: 35px; color: {color_m}; font-weight: bold;">{socio['diasRestantes']} DÍAS RESTANTES</div>
                        </div>
                    """, unsafe_allow_html=True)
                else: st.error("Socio no encontrado.")

    elif menu == "Lista de Miembros":
        st.header("Visualización de Socios")
        res = api_call("GET", "Usuarios/socios")
        if res and res.status_code == 200:
            df = pd.DataFrame(res.json())
            c1, c2 = st.columns([1, 2])
            filtro = c1.selectbox("Estado", ["Todos", "Activos", "Inactivos"])
            busqueda = c2.text_input("🔍 Buscar por ID, DNI o Apellido").lower()
            if filtro == "Activos": df = df[df['membresiaVigente'] == True]
            elif filtro == "Inactivos": df = df[df['membresiaVigente'] == False]
            if busqueda:
                df = df[df['id'].astype(str).str.contains(busqueda) | df['dni'].astype(str).str.contains(busqueda) | df['apellido'].str.lower().str.contains(busqueda)]
            st.dataframe(df[['id', 'nombre', 'apellido', 'dni', 'email', 'membresiaVigente', 'diasRestantes']], use_container_width=True)

    elif menu == "Alta Nuevo Socio":
        st.header("Registrar Miembro")
        with st.form("alta_form"):
            c1, c2 = st.columns(2)
            n, a = c1.text_input("Nombre*"), c2.text_input("Apellido*")
            d, e = c1.text_input("DNI*"), c2.text_input("Email*")
            p = c1.text_input("Contraseña*", type="password")
            fn = c2.date_input("Fecha Nacimiento", value=datetime(2000, 1, 1))
            if st.form_submit_button("REGISTRAR"):
                payload = {"nombre": n, "apellido": a, "dni": d, "email": e, "password": p, "rolId": 3, "fechaNacimiento": fn.isoformat()}
                if api_call("POST", "Usuarios", payload).status_code in [200, 201]: st.success("Socio creado!")
                else: st.error("Error al registrar.")

    elif menu == "Gestión Usuarios":
        st.header("Modificar / Eliminar")
        bus_val = st.text_input("Buscar por ID o DNI para editar")
        if st.button("BUSCAR"):
            res = api_call("GET", "Usuarios/socios")
            found = next((s for s in res.json() if str(s['id']) == bus_val or str(s['dni']) == bus_val), None)
            if found: st.session_state.edit_user = found
            else: st.warning("No encontrado.")
        
        if st.session_state.edit_user:
            u = st.session_state.edit_user
            with st.form("edit_form"):
                st.write(f"Editando ID: {u['id']}")
                n, a = st.text_input("Nombre", value=u['nombre']), st.text_input("Apellido", value=u['apellido'])
                d, e = st.text_input("DNI", value=u['dni']), st.text_input("Email", value=u['email'])
                p = st.text_input("Nueva Contraseña (requerida)", type="password")
                if st.form_submit_button("GUARDAR"):
                    payload = {"id": u['id'], "nombre": n, "apellido": a, "dni": d, "email": e, "password": p, "rolId": 3, "fechaNacimiento": u.get('fechaNacimiento', "2000-01-01")}
                    if api_call("PUT", f"Usuarios/{u['id']}", payload).status_code in [200, 204]:
                        st.success("Actualizado"); st.session_state.edit_user = None; st.rerun()
            if st.button("❌ ELIMINAR"):
                if api_call("DELETE", f"Usuarios/{u['id']}").status_code in [200, 204]:
                    st.success("Eliminado"); st.session_state.edit_user = None; st.rerun()

    elif menu == "Cargar Cuota":
        st.header("Nueva Membresía")
        sid = st.number_input("ID del Socio", min_value=1, step=1)
        c1, c2, c3, c4 = st.columns(4)
        meses = 0
        if c1.button("1 MES"): meses = 1
        if c2.button("3 MESES"): meses = 3
        if c3.button("6 MESES"): meses = 6
        if c4.button("1 AÑO"): meses = 12
        if meses > 0:
            if api_call("POST", "Membresias", {"usuarioId": int(sid), "meses": meses}).status_code in [200, 201]:
                st.balloons(); st.success(f"Activado {meses} mes(es) al ID {sid}")

# --- RUTEO PRINCIPAL ---
if st.session_state.get("token") is None: login_page()
else:
    rol = st.session_state.get("user_data", {}).get("rolNombre", "").lower()
    if rol in ["admin", "empleado"]: admin_dashboard()
    else: socio_dashboard()
