import streamlit as st
import requests
import time

# --- CONFIGURACIÓN ---
API_BASE_URL = "https://gimnasio.tryasp.net/api" # Actualizado a HTTPS según tu Curl
st.set_page_config(page_title="Gimnasio Pro Ultra", layout="wide", page_icon="🏋️‍♂️")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .main-header { font-size: 35px; font-weight: bold; color: #1E88E5; }
    .card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #1E88E5; }
    .valido { background-color: #2ecc71; color: white; padding: 20px; border-radius: 10px; text-align: center; }
    .denegado { background-color: #e74c3c; color: white; padding: 20px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if "token" not in st.session_state:
    st.session_state.token = None
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "ultimo_id_creado" not in st.session_state:
    st.session_state.ultimo_id_creado = 1

# --- HELPER API ---
def api_call(method, endpoint, data=None):
    headers = {"Authorization": f"Bearer {st.session_state.token}", "Content-Type": "application/json"}
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
    st.markdown("<div class='main-header'>🏋️‍♂️ Gimnasio Pro</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.5, 1])
    with col1:
        with st.container(border=True):
            email = st.text_input("Email Admin/Empleado")
            password = st.text_input("Contraseña", type="password")
            if st.button("INGRESAR", use_container_width=True):
                res = requests.post(f"{API_BASE_URL}/Usuarios/login", json={"email": email, "password": password})
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data["token"]
                    st.session_state.user_data = data["usuario"]
                    st.success("Acceso concedido")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")

# --- PÁGINA: GESTIÓN (ADMIN/EMPLEADO) ---
def admin_dashboard():
    with st.sidebar:
        st.title(f"👋 {st.session_state.user_data.get('nombre')}")
        st.write(f"Rol: **{st.session_state.user_data.get('rolNombre')}**")
        st.divider()
        menu = st.radio("MENÚ", ["🏢 Molinete", "👥 Socios", "➕ Alta Rápida"])
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.token = None
            st.rerun()

    # --- PÁGINA: MOLINETE ---
    if menu == "🏢 Molinete":
        st.header("🛡️ Control de Acceso")
        entrada = st.text_input("Escanear ID o DNI del Socio")
        if st.button("VERIFICAR ACCESO"):
            with st.spinner("Validando..."):
                # Usamos el endpoint que confirmaste: /api/Usuarios/{id}/validar-acceso-id
                res = api_call("GET", f"Usuarios/{entrada}/validar-acceso-id")
                if res and res.status_code == 200:
                    info = res.json()
                    if info.get("status") == "Concedido":
                        st.markdown(f'<div class="valido"><h1>✅ PASA</h1><p>{info["mensaje"]}</p></div>', unsafe_allow_html=True)
                        st.balloons()
                    else:
                        st.markdown(f'<div class="denegado"><h1>❌ DENEGADO</h1><p>{info["mensaje"]}</p></div>', unsafe_allow_html=True)
                else:
                    st.error("Error al validar. Asegúrese de ingresar un ID numérico válido.")

    # --- PÁGINA: BUSCADOR ---
    elif menu == "👥 Socios":
        st.header("🔍 Buscador de Socios")
        res = api_call("GET", "Usuarios/socios")
        if res and res.status_code == 200:
            df = res.json()
            search = st.text_input("Buscar por Nombre o DNI").lower()
            filtered = [s for s in df if search in s['nombre'].lower() or search in s['dni']]
            st.dataframe(filtered, use_container_width=True, hide_index=True)

    # --- PÁGINA: ALTA RÁPIDA ---
    elif menu == "➕ Alta Rápida":
        st.header("⚡ Registro Integrado")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("1. Datos del Socio")
            with st.form("form_socio"):
                nom = st.text_input("Nombre")
                ape = st.text_input("Apellido")
                doc = st.text_input("DNI")
                mail = st.text_input("Email")
                pas = st.text_input("Contraseña para el socio", type="password")
                f_nac = st.date_input("Fecha Nacimiento", value=None)
                if st.form_submit_button("CREAR USUARIO"):
                    payload = {
                        "nombre": nom, "apellido": ape, "dni": doc, "email": mail,
                        "password": pas, "idRol": 3, "fechaNacimiento": f_nac.isoformat() if f_nac else "1990-01-01"
                    }
                    r = api_call("POST", "Usuarios", payload)
                    if r and r.status_code in [200, 201]:
                        nuevo_id = r.json().get("id")
                        st.session_state.ultimo_id_creado = nuevo_id
                        st.success(f"Socio Creado con ID: {nuevo_id}")
                    else:
                        st.error(f"Error: {r.text}")

        with col2:
            st.subheader("2. Activar Membresía")
            with st.form("form_memb"):
                # Se autocompleta con el ID recién creado
                u_id = st.number_input("ID Socio", value=st.session_state.ultimo_id_creado)
                tipo = st.selectbox("Plan", ["Mensual", "Trimestral", "Anual"])
                f_ini = st.date_input("Fecha Inicio")
                if st.form_submit_button("GENERAR MEMBRESÍA"):
                    # Eliminado el campo monto según tu instrucción
                    payload_m = {
                        "usuarioId": u_id,
                        "tipo": tipo,
                        "fechaInicio": f_ini.isoformat()
                    }
                    r_m = api_call("POST", "Membresias", payload_m)
                    if r_m and r_m.status_code in [200, 201]:
                        st.success("¡Membresía Activada!")
                        st.toast("Proceso completado", icon="🚀")
                    else:
                        st.error(f"Fallo: {r_m.text}")

# --- ARRANQUE ---
if st.session_state.token is None:
    login_page()
else:
    admin_dashboard()



