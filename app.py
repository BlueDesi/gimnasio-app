import streamlit as st
import requests
import time

# --- CONFIGURACIÓN ---
API_BASE_URL = "http://gimnasio.tryasp.net/api"
st.set_page_config(page_title="Gimnasio Pro Ultra", layout="wide", page_icon="🏋️‍♂️")

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 25px; }
    .main-header { font-size: 40px; font-weight: bold; color: #1E88E5; padding-bottom: 20px; }
    .valido { background-color: #2ecc71; color: white; padding: 25px; border-radius: 15px; text-align: center; font-size: 20px; }
    .denegado { background-color: #e74c3c; color: white; padding: 25px; border-radius: 15px; text-align: center; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADO ---
if "token" not in st.session_state:
    st.session_state.token = None
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# --- HELPER: PETICIONES API ---
def api_request(method, endpoint, json=None, use_token=True):
    headers = {"Authorization": f"Bearer {st.session_state.token}"} if use_token else {}
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        if method == "GET":
            return requests.get(url, headers=headers)
        elif method == "POST":
            return requests.post(url, json=json, headers=headers)
    except Exception as e:
        return None

# --- VISTA: LOGIN ---
def login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='main-header'>🏋️‍♂️ Gimnasio Pro Login</div>", unsafe_allow_html=True)
        with st.container(border=True):
            email = st.text_input("Correo Electrónico")
            password = st.text_input("Contraseña", type="password")
            if st.button("INGRESAR SISTEMA", use_container_width=True):
                with st.spinner("Autenticando..."):
                    res = api_request("POST", "Usuarios/login", {"email": email, "password": password}, False)
                    if res and res.status_code == 200:
                        data = res.json()
                        st.session_state.token = data["token"]
                        st.session_state.user_data = data["usuario"]
                        st.toast("¡Bienvenido al sistema!", icon="✅")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Credenciales inválidas")

# --- VISTA: CONTROL DE ACCESO ---
def control_acceso():
    st.header("🛡️ Control de Molinete")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        socio_id = st.text_input("Escanear Código QR o ID Socio")
        if st.button("Validar Entrada", use_container_width=True):
            with st.status("Consultando base de datos...") as status:
                res = api_request("GET", f"Usuarios/{socio_id}/validar-acceso-id")
                if res and res.status_code == 200:
                    info = res.json()
                    status.update(label="Validación completada", state="complete")
                    if info.get("status") == "Concedido":
                        st.markdown(f'<div class="valido"><h1>✅ ACCESO PERMITIDO</h1><p>{info["mensaje"]}</p></div>', unsafe_allow_html=True)
                        st.balloons()
                    else:
                        st.markdown(f'<div class="denegado"><h1>❌ ACCESO DENEGADO</h1><p>{info["mensaje"]}</p></div>', unsafe_allow_html=True)
                else:
                    status.update(label="Error en la consulta", state="error")
                    st.error("Socio no encontrado.")

# --- VISTA: GESTIÓN DE SOCIOS ---
def gestion_socios():
    st.header("➕ Alta de Nuevo Socio")
    
    with st.expander("📝 Formulario de Registro", expanded=True):
        with st.form("nuevo_socio"):
            c1, c2 = st.columns(2)
            nombre = c1.text_input("Nombre")
            apellido = c1.text_input("Apellido")
            dni = c2.text_input("DNI / Cédula")
            email = c2.text_input("Email")
            f_nac = st.date_input("Fecha Nacimiento", value=None)
            
            if st.form_submit_button("REGISTRAR SOCIO"):
                payload = {
                    "nombre": nombre, "apellido": apellido, "dni": dni,
                    "email": email, "idRol": 3, "fechaNacimiento": f_nac.isoformat() if f_nac else None,
                    "password": f"Gym{dni}" # Password por defecto
                }
                with st.spinner("Guardando..."):
                    res = api_request("POST", "Usuarios", payload)
                    if res and res.status_code in [200, 201]:
                        st.success(f"Socio creado con ID: {res.json().get('id')}")
                    else:
                        st.error("Error al crear socio.")

    st.divider()
    st.header("💳 Asignar Membresía")
    with st.form("nueva_memb"):
        c1, c2, c3 = st.columns(3)
        u_id = c1.number_input("ID del Socio", min_value=1)
        tipo = c2.selectbox("Plan", ["Mensual", "Trimestral", "Anual"])
        monto = c3.number_input("Monto Pagado", min_value=0.0)
        
        if st.form_submit_button("ACTIVAR MEMBRESÍA"):
            payload = {"usuarioId": u_id, "tipo": tipo, "monto": monto, "fechaInicio": time.strftime("%Y-%m-%d")}
            res = api_request("POST", "Membresias", payload)
            if res and res.status_code in [200, 201]:
                st.toast("Membresía Activada", icon="🔥")
                st.success("El socio ahora tiene acceso activo.")

# --- VISTA: BUSCADOR ---
def buscador_page():
    st.header("🔍 Listado Global de Socios")
    with st.spinner("Cargando base de datos..."):
        res = api_request("GET", "Usuarios/socios")
        if res and res.status_code == 200:
            df = res.json()
            search = st.text_input("Filtrar por nombre o DNI").lower()
            filtered = [s for s in df if search in s['nombre'].lower() or search in s['dni']]
            st.dataframe(filtered, use_container_width=True)

# --- NAVEGACIÓN (PÁGINAS) ---
def main():
    if st.session_state.token is None:
        login_page()
    else:
        # SIDEBAR PROFESIONAL
        with st.sidebar:
            st.markdown(f"### Bienvenido, \n**{st.session_state.user_data.get('nombre')}**")
            st.caption(f"Rol: {st.session_state.user_data.get('rolNombre')}")
            st.divider()
            
            menu = st.radio("MENÚ PRINCIPAL", ["Molinete", "Gestión Socios", "Buscador"])
            
            st.spacer = st.container(height=200, border=False)
            if st.button("Cerrar Sesión", use_container_width=True, type="secondary"):
                st.session_state.token = None
                st.rerun()

        # ROUTING
        if menu == "Molinete":
            control_acceso()
        elif menu == "Gestión Socios":
            if st.session_state.user_data.get("rolNombre") in ["Admin", "Empleado"]:
                gestion_socios()
            else:
                st.error("No tienes permisos para esta sección.")
        elif menu == "Buscador":
            buscador_page()

if __name__ == "__main__":
    main()



