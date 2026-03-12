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
    .valido { background-color: #2ecc71; color: white; padding: 25px; border-radius: 15px; text-align: center; font-size: 22px; font-weight: bold; border: 3px solid #27ae60; }
    .denegado { background-color: #e74c3c; color: white; padding: 25px; border-radius: 15px; text-align: center; font-size: 22px; font-weight: bold; border: 3px solid #c0392b; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADO ---
if "token" not in st.session_state:
    st.session_state.token = None
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "ultimo_id_creado" not in st.session_state:
    st.session_state.ultimo_id_creado = 1

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
        st.error(f"Error de red: {e}")
        return None

# --- PÁGINA: LOGIN ---
def login_page():
    st.markdown("<div class='main-header'>🏋️‍♂️ Gimnasio Pro - Sistema de Gestión</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.subheader("🔑 Inicio de Sesión")
            email = st.text_input("Email Admin/Empleado").strip()
            password = st.text_input("Contraseña", type="password")
            
            if st.button("INGRESAR AL SISTEMA", use_container_width=True):
                with st.spinner("Autenticando..."):
                    res = requests.post(f"{API_BASE_URL}/Usuarios/login", json={"email": email, "password": password})
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.token = data["token"]
                        st.session_state.user_data = data["usuario"]
                        st.toast("¡Bienvenido!", icon="✅")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Email o contraseña incorrectos")

# --- PÁGINA: GESTIÓN PRINCIPAL ---
def admin_dashboard():
    # BARRA LATERAL (NAVEGACIÓN)
    with st.sidebar:
        st.markdown(f"### 👋 Hola, {st.session_state.user_data.get('nombre')}")
        st.info(f"Rol: **{st.session_state.user_data.get('rolNombre')}**")
        st.divider()
        menu = st.radio("MENÚ PRINCIPAL", ["🏢 Molinete", "👥 Buscador de Socios", "➕ Alta Rápida"], index=0)
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # --- LÓGICA DE PÁGINAS ---
    
    # 1. MOLINETE (CONTROL DE ACCESO)
    if menu == "🏢 Molinete":
        st.header("🛡️ Control de Acceso en Tiempo Real")
        with st.container(border=True):
            entrada = st.text_input("Escanear ID del Socio (ej: 2, 18, 20)")
            if st.button("VALIDAR ENTRADA", use_container_width=True):
                if entrada:
                    with st.status("Consultando membresía...") as status:
                        res = api_call("GET", f"Usuarios/{entrada}/validar-acceso-id")
                        if res and res.status_code == 200:
                            info = res.json()
                            status.update(label="Consulta finalizada", state="complete")
                            if info.get("status") == "Concedido":
                                st.markdown(f'<div class="valido">✅ ACCESO CONCEDIDO<br><small>{info["mensaje"]}</small></div>', unsafe_allow_html=True)
                                st.balloons()
                            else:
                                st.markdown(f'<div class="denegado">❌ ACCESO DENEGADO<br><small>{info["mensaje"]}</small></div>', unsafe_allow_html=True)
                        else:
                            status.update(label="Error", state="error")
                            st.error(f"Socio con ID {entrada} no encontrado.")

    # 2. BUSCADOR DE SOCIOS
    elif menu == "👥 Buscador de Socios":
        st.header("🔍 Base de Datos de Socios")
        with st.spinner("Cargando lista..."):
            res = api_call("GET", "Usuarios/socios")
            if res and res.status_code == 200:
                df = res.json()
                search = st.text_input("Filtrar por Nombre, Apellido o DNI").lower()
                filtered = [s for s in df if search in s['nombre'].lower() or search in s['apellido'].lower() or search in s['dni']]
                
                st.dataframe(
                    filtered, 
                    column_order=("id", "nombre", "apellido", "dni", "rolNombre", "membresiaVigente", "diasRestantes"),
                    use_container_width=True, 
                    hide_index=True
                )
            else:
                st.error("No se pudo obtener la lista de socios.")

    # 3. ALTA RÁPIDA (USUARIO + MEMBRESÍA)
    elif menu == "➕ Alta Rápida":
        st.header("⚡ Registro de Usuario y Activación")
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container(border=True):
                st.subheader("1. Crear Usuario")
                with st.form("form_alta_usuario"):
                    nom = st.text_input("Nombre")
                    ape = st.text_input("Apellido")
                    doc = st.text_input("DNI")
                    mail = st.text_input("Email")
                    pas = st.text_input("Establecer Contraseña", type="password")
                    
                    # Selector de Roles dinámico
                    rol_nom = st.selectbox("Rol del Usuario", ["Socio", "Empleado", "Admin"])
                    roles_map = {"Admin": 1, "Empleado": 2, "Socio": 3}
                    
                    f_nac = st.date_input("Fecha Nacimiento", value=None)
                    
                    if st.form_submit_button("REGISTRAR EN SISTEMA", use_container_width=True):
                        if not nom or not doc or not mail or not pas:
                            st.error("Faltan campos obligatorios.")
                        else:
                            payload = {
                                "nombre": nom, "apellido": ape, "dni": doc, 
                                "email": mail, "password": pas, "idRol": roles_map[rol_nom],
                                "fechaNacimiento": f_nac.isoformat() if f_nac else "1990-01-01"
                            }
                            with st.spinner("Guardando..."):
                                r = api_call("POST", "Usuarios", payload)
                                if r and r.status_code in [200, 201]:
                                    nuevo_id = r.json().get("id")
                                    st.session_state.ultimo_id_creado = nuevo_id
                                    st.success(f"¡{rol_nom} creado! ID: {nuevo_id}")
                                else:
                                    st.error(f"Error: {r.text}")

        with col2:
            with st.container(border=True):
                st.subheader("2. Activar Membresía")
                st.caption("Solo aplica para usuarios con rol 'Socio'")
                with st.form("form_alta_memb"):
                    # El ID se vincula automáticamente del paso anterior
                    u_id = st.number_input("ID del Socio", value=st.session_state.ultimo_id_creado, step=1)
                    tipo = st.selectbox("Plan de Membresía", ["Mensual", "Trimestral", "Anual"])
                    f_ini = st.date_input("Fecha de Inicio")
                    
                    if st.form_submit_button("ACTIVAR ACCESO", use_container_width=True):
                        payload_m = {
                            "usuarioId": u_id,
                            "tipo": tipo,
                            "fechaInicio": f_ini.isoformat()
                        }
                        with st.spinner("Procesando membresía..."):
                            r_m = api_call("POST", "Membresias", payload_m)
                            if r_m and r_m.status_code in [200, 201]:
                                st.success("✅ Membresía activada correctamente.")
                                st.toast("Socio habilitado", icon="🚀")
                            else:
                                st.error("Error al activar. Verifique si el ID existe y es un Socio.")

# --- FLUJO PRINCIPAL ---
if st.session_state.token is None:
    login_page()
else:
    admin_dashboard()
