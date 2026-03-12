import streamlit as st
import requests
import time

# --- CONFIGURACIÓN ---
API_BASE_URL = "https://gimnasio.tryasp.net/api"
st.set_page_config(page_title="Gimnasio Pro Ultra", layout="wide", page_icon="🏋️‍♂️")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .main-header { font-size: 35px; font-weight: bold; color: #1E88E5; padding-bottom: 10px; }
    .valido { background-color: #2ecc71; color: white; padding: 25px; border-radius: 15px; text-align: center; border: 3px solid #27ae60; }
    .denegado { background-color: #e74c3c; color: white; padding: 25px; border-radius: 15px; text-align: center; border: 3px solid #c0392b; }
    .metric-card { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; border: 1px solid #eee; }
    .stButton>button { border-radius: 8px; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if "token" not in st.session_state: st.session_state.token = None
if "user_data" not in st.session_state: st.session_state.user_data = {}
if "ultimo_id_creado" not in st.session_state: st.session_state.ultimo_id_creado = 1

# --- HELPER API ---
def api_call(method, endpoint, data=None):
    headers = {"Authorization": f"Bearer {st.session_state.token}", "Content-Type": "application/json", "accept": "*/*"}
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        if method == "POST": return requests.post(url, json=data, headers=headers)
        if method == "GET": return requests.get(url, headers=headers)
    except Exception as e:
        st.error(f"Error de red: {e}")
        return None

# --- VISTA: LOGIN ---
def login_page():
    st.markdown("<div class='main-header'>🏋️‍♂️ Gimnasio Pro</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            email = st.text_input("Email").strip()
            password = st.text_input("Contraseña", type="password")
            if st.button("INGRESAR", use_container_width=True):
                res = requests.post(f"{API_BASE_URL}/Usuarios/login", json={"email": email, "password": password})
                if res.status_code == 200:
                    st.session_state.token, st.session_state.user_data = res.json()["token"], res.json()["usuario"]
                    st.rerun()
                else: st.error("Credenciales incorrectas")

# --- VISTA: DASHBOARD ---
def admin_dashboard():
    with st.sidebar:
        st.markdown(f"### 👋 {st.session_state.user_data.get('nombre')}")
        menu = st.radio("MENÚ", ["🏢 Molinete", "👥 Socios", "➕ Alta Rápida"])
        if st.button("🚪 Salir", use_container_width=True):
            st.session_state.token = None
            st.rerun()

    if menu == "🏢 Molinete":
        st.header("🛡️ Control de Acceso")
        with st.container(border=True):
            entrada = st.text_input("Ingrese ID del Socio", placeholder="Ej: 2")
            
            if st.button("VALIDAR ENTRADA", use_container_width=True):
                if entrada:
                    # 1. Animación de carga inmediata
                    with st.spinner("Verificando membresía..."):
                        # 2. Validamos acceso
                        res_val = api_call("GET", f"Usuarios/{entrada}/validar-acceso-id")
                        
                        if res_val and res_val.status_code == 200:
                            val_data = res_val.json()
                            
                            # 3. Pedimos los datos del usuario para mostrar los días restantes
                            res_user = api_call("GET", f"Usuarios/{entrada}")
                            user_info = res_user.json() if res_user and res_user.status_code == 200 else {}

                            if val_data.get("status") == "Concedido":
                                st.markdown(f'<div class="valido">✅ ACCESO PERMITIDO<br>{val_data["mensaje"]}</div>', unsafe_allow_html=True)
                                st.balloons()
                                
                                # PANEL DE ESTADO (Métricas rápidas sin clics extra)
                                st.write("###")
                                c1, c2, c3 = st.columns(3)
                                with c1:
                                    st.markdown(f'<div class="metric-card">👤 Socio<br><b>{user_info.get("nombre", "")} {user_info.get("apellido", "")}</b></div>', unsafe_allow_html=True)
                                with c2:
                                    dias = user_info.get("diasRestantes", 0)
                                    color = "#2ecc71" if dias > 5 else "#f1c40f"
                                    st.markdown(f'<div class="metric-card">⏳ Días Restantes<br><b style="color:{color}; font-size: 24px;">{dias}</b></div>', unsafe_allow_html=True)
                                with c3:
                                    vence = user_info.get("fechaVencimiento")
                                    fecha_f = vence.split('T')[0] if vence else "N/A"
                                    st.markdown(f'<div class="metric-card">📅 Vencimiento<br><b>{fecha_f}</b></div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="denegado">❌ ACCESO RECHAZADO<br>{val_data["mensaje"]}</div>', unsafe_allow_html=True)
                        else:
                            st.error("Socio no encontrado.")

    elif menu == "👥 Socios":
        st.header("🔍 Buscador")
        res = api_call("GET", "Usuarios/socios")
        if res and res.status_code == 200:
            search = st.text_input("Filtrar por nombre o DNI").lower()
            filtered = [s for s in res.json() if search in s['nombre'].lower() or search in s['dni']]
            st.dataframe(filtered, use_container_width=True, hide_index=True)

    elif menu == "➕ Alta Rápida":
        st.header("⚡ Registro de Socio")
        col1, col2 = st.columns(2)
        with col1:
            with st.form("form_user"):
                st.subheader("1. Usuario")
                n, a, d = st.text_input("Nombre"), st.text_input("Apellido"), st.text_input("DNI")
                e, p = st.text_input("Email"), st.text_input("Password", type="password")
                rol = st.selectbox("Rol", ["Socio", "Empleado", "Admin"], index=0)
                roles_map = {"Admin": 1, "Empleado": 2, "Socio": 3}
                if st.form_submit_button("REGISTRAR"):
                    r = api_call("POST", "Usuarios", {"nombre":n, "apellido":a, "dni":d, "email":e, "password":p, "idRol":roles_map[rol], "fechaNacimiento":"1990-01-01"})
                    if r and r.status_code in [200, 201]:
                        st.session_state.ultimo_id_creado = r.json().get("id")
                        st.success(f"Creado ID: {st.session_state.ultimo_id_creado}")
        with col2:
            with st.form("form_mem"):
                st.subheader("2. Membresía")
                u_id = st.number_input("ID Socio", value=st.session_state.ultimo_id_creado)
                tipo = st.selectbox("Plan", ["Mensual", "Trimestral", "Anual"])
                if st.form_submit_button("ACTIVAR"):
                    r_m = api_call("POST", "Membresias", {"usuarioId":u_id, "tipo":tipo, "fechaInicio":time.strftime("%Y-%m-%d")})
                    if r_m and r_m.status_code in [200, 201]: st.success("¡Activada!")

if st.session_state.token is None: login_page()
else: admin_dashboard()

