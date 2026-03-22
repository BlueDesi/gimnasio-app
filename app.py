import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
API_BASE_URL = "https://gimnasio.tryasp.net/api"
st.set_page_config(page_title="Gimnasio Pro Ultra", layout="wide", page_icon="🏋️‍♂️")

# --- URL DE LA IMAGEN (DRIVE - FORMATO MINIATURA HD) ---
IMAGE_URL = "https://drive.google.com/thumbnail?id=1PsTkl-oaniJO687yUEo8Y5-gyU1YWfDa&sz=w1200"

# --- INICIALIZACIÓN ---
if "token" not in st.session_state: st.session_state.token = None
if "user_data" not in st.session_state: st.session_state.user_data = {}
if "edit_user" not in st.session_state: st.session_state.edit_user = None

# --- ESTILOS CSS (ESTILO NETFLIX / ALTO RENDIMIENTO) ---
st.markdown(f"""
    <style>
    /* Importación de fuentes */
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;700;900&display=swap');

    /* Aplicación general de fuente */
    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', sans-serif;
        background-color: #000000;
        color: #FFFFFF;
    }}

    /* Títulos con Bebas Neue */
    h1, h2, h3, .main-header {{
        font-family: 'Bebas Neue', sans-serif;
        letter-spacing: 2px;
    }}

    .main-header {{ 
        font-size: 50px; 
        color: #00D4FF; 
        text-align: center; 
        margin-bottom: 30px; 
        text-transform: uppercase;
    }}

    /* Estilo de Tarjetas Métricas */
    .metric-card {{ 
        background-color: #111111; 
        padding: 25px; 
        border-radius: 10px; 
        border-left: 5px solid #00D4FF; 
        text-align: center; 
        margin-bottom: 15px; 
    }}
    
    .metric-label {{ 
        color: #AAAAAA; 
        font-size: 12px; 
        font-weight: 900; 
        text-transform: uppercase; 
        letter-spacing: 1px;
    }}
    
    .metric-value {{ 
        font-family: 'Bebas Neue', sans-serif;
        font-size: 45px; 
        margin-top: 5px;
    }}

    /* Contenedor del Molinete */
    .molinete-container {{ 
        background-color: #050505; 
        padding: 40px; 
        border-radius: 15px; 
        border: 2px solid #00D4FF; 
        text-align: center;
        box-shadow: 0px 0px 20px rgba(0, 212, 255, 0.2);
    }}

    /* Botones estilo UI moderna */
    .stButton>button {{ 
        border-radius: 4px; 
        font-family: 'Inter', sans-serif;
        font-weight: 900; 
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.3s; 
        height: 3.5em; 
        background-color: #00D4FF;
        color: black;
        border: none;
    }}
    
    .stButton>button:hover {{
        background-color: #00b8e6;
        color: white;
        transform: scale(1.02);
    }}

    /* Rojo para el botón de Salir */
    div.stButton > button:first-child[aria-label="SALIR"], 
    div.stButton > button:first-child[aria-label="CERRAR SESIÓN"],
    div.stButton > button:first-child[aria-label="❌ ELIMINAR"] {{
        background-color: #E50914 !important;
        color: white !important;
    }}

    /* Inputs oscuros */
    input {{ 
        background-color: #222222 !important; 
        color: white !important; 
        border: none !important;
        border-bottom: 2px solid #444444 !important;
        border-radius: 4px !important;
    }}
    
    input:focus {{
        border-bottom: 2px solid #00D4FF !important;
    }}
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
    # Banner superior
    st.image(IMAGE_URL, use_container_width=True)
    
    st.markdown("<h1 style='text-align: center; color: #00D4FF;'> GIMNASIO ULTRA </h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>Acceso al Sistema</h3>", unsafe_allow_html=True)
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
    st.image(IMAGE_URL, use_container_width=True)
    user = st.session_state.user_data
    st.markdown(f"<div class='main-header'>Panel de Socio: {user.get('nombre')}</div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.markdown(f"<div class='metric-card'><span class='metric-label'>Socio</span><div class='metric-value'>{user.get('nombre')} {user.get('apellido')}</div><p style='color:#666'>DNI: {user.get('dni')}</p></div>", unsafe_allow_html=True)
    
    vigente = user.get("membresiaVigente", False)
    color_v = "#00FF00" if vigente else "#FF0000"
    with c2: 
        st.markdown(f"<div class='metric-card'><span class='metric-label'>Membresía</span><div class='metric-value' style='color:{color_v}'>{'ACTIVA' if vigente else 'VENCIDA'}</div></div>", unsafe_allow_html=True)
    
    with c3: 
        st.markdown(f"<div class='metric-card'><span class='metric-label'>Días Restantes</span><div class='metric-value' style='color:#00D4FF'>{user.get('diasRestantes', 0)}</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("CERRAR SESIÓN", use_container_width=True): logout()

# --- VISTA: ADMIN / EMPLEADO ---
def admin_dashboard():
    with st.sidebar:
        st.title("🛡️ STAFF")
        menu = st.radio("Menú Principal", ["Molinete", "Lista de Miembros", "Alta Nuevo Socio", "Gestión Usuarios", "Cargar Cuota"])
        st.divider()
        if st.button("SALIR", type="primary", use_container_width=True): logout()

    # Banner en el cuerpo principal
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
                    st.markdown(f"""
                        <div class="molinete-container" style="border-color: {color_m}">
                            <div style="font-family: 'Bebas Neue'; font-size: 55px;">{socio['nombre']} {socio['apellido']}</div>
                            <div style="font-size: 20px; color: #AAA;">ID: {socio['id']} | DNI: {socio['dni']}</div>
                            <div style="font-family: 'Bebas Neue'; font-size: 40px; color: {color_m};">{socio['diasRestantes']} DÍAS RESTANTES</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if not socio['membresiaVigente']: st.error("ACCESO DENEGADO - MEMBRESÍA VENCIDA")
                else: st.error("Socio no encontrado.")

    elif menu == "Lista de Miembros":
        st.header("Visualización de Socios")
        res = api_call("GET", "Usuarios/socios")
        if res and res.status_code == 200:
            df = pd.DataFrame(res.json())
            c1, c2 = st.columns([1, 2])
            filtro = c1.selectbox("Filtrar por Estado", ["Todos", "Activos", "Inactivos"])
            busqueda = c2.text_input("🔍 Buscar por ID, DNI o Apellido").lower()
            if filtro == "Activos": df = df[df['membresiaVigente'] == True]
            elif filtro == "Inactivos": df = df[df['membresiaVigente'] == False]
            if busqueda:
                df = df[df['id'].astype(str).str.contains(busqueda) | df['dni'].astype(str).str.contains(busqueda) | df['apellido'].str.lower().str.contains(busqueda)]
            st.dataframe(df[['id', 'nombre', 'apellido', 'dni', 'email', 'membresiaVigente', 'diasRestantes']], use_container_width=True)

    elif menu == "Alta Nuevo Socio":
        st.header("Registrar Nuevo Miembro")
        with st.form("alta_form"):
            c1, c2 = st.columns(2)
            n, a = c1.text_input("Nombre*"), c2.text_input("Apellido*")
            d, e = c1.text_input("DNI*"), c2.text_input("Email*")
            p = c1.text_input("Contraseña*", type="password")
            fn = c2.date_input("Fecha Nacimiento", value=datetime(2000, 1, 1))
            if st.form_submit_button("REGISTRAR SOCIO"):
                payload = {"nombre": n, "apellido": a, "dni": d, "email": e, "password": p, "rolId": 3, "fechaNacimiento": fn.isoformat()}
                if api_call("POST", "Usuarios", payload).status_code in [200, 201]: 
                    st.success("¡Socio registrado con éxito!")
                else: st.error("Error al registrar. Verifique los datos.")

    elif menu == "Gestión Usuarios":
        st.header("Gestión de Personal y Socios")
        
        # Pestañas para organizar el trabajo del Admin
        tab1, tab2 = st.tabs(["👥 Buscar/Editar Usuario", "➕ Alta Staff (Admin/Empleado)"])

        with tab1:
            bus_val = st.text_input("Buscar por ID o DNI para editar/eliminar")
            if st.button("BUSCAR USUARIO"):
                # Buscamos en la lista general de usuarios
                res = api_call("GET", "Usuarios")
                if res and res.status_code == 200:
                    found = next((s for s in res.json() if str(s['id']) == bus_val or str(s['dni']) == bus_val), None)
                    if found: st.session_state.edit_user = found
                    else: st.warning("Usuario no encontrado.")

            if st.session_state.edit_user:
                u = st.session_state.edit_user
                with st.form("edit_form_global"):
                    st.subheader(f"Modificando: {u['nombre']} (Rol: {u['rolNombre']})")
                    c1, c2 = st.columns(2)
                    n = c1.text_input("Nombre", value=u['nombre'])
                    a = c2.text_input("Apellido", value=u['apellido'])
                    d = c1.text_input("DNI", value=u['dni'])
                    e = c2.text_input("Email", value=u['email'])
                    p = st.text_input("Contraseña (Dejar vacío para no cambiar)", type="password")
                    
                    # El admin puede cambiar el rol de cualquiera
                    roles_map = {"Admin": 1, "Empleado": 2, "Socio": 3}
                    current_rol_idx = list(roles_map.keys()).index(u['rolNombre']) if u['rolNombre'] in roles_map else 2
                    nuevo_rol = st.selectbox("Asignar Cargo", options=list(roles_map.keys()), index=current_rol_idx)

                    if st.form_submit_button("GUARDAR CAMBIOS"):
                        payload = {
                            "id": u['id'], "nombre": n, "apellido": a, "dni": d, 
                            "email": e, "password": p if p else "no_change", # Ajustar según tu API
                            "rolId": roles_map[nuevo_rol], 
                            "fechaNacimiento": u.get('fechaNacimiento', "2000-01-01")
                        }
                        if api_call("PUT", f"Usuarios/{u['id']}", payload).status_code in [200, 204]:
                            st.success("Usuario actualizado correctamente."); st.session_state.edit_user = None; st.rerun()

                if st.button("❌ ELIMINAR USUARIO DEFINITIVAMENTE"):
                    if api_call("DELETE", f"Usuarios/{u['id']}").status_code in [200, 204]:
                        st.success("Usuario eliminado"); st.session_state.edit_user = None; st.rerun()

        with tab2:
            # Esta sección es crítica para la seguridad JWT
            st.subheader("Registrar nuevo miembro del Staff")
            with st.form("alta_staff"):
                st.info("⚠️ Los usuarios creados aquí tendrán acceso al panel de control.")
                c1, c2 = st.columns(2)
                st_n = c1.text_input("Nombre*")
                st_a = c2.text_input("Apellido*")
                st_d = c1.text_input("DNI*")
                st_e = c2.text_input("Email Corporativo*")
                st_p = st.text_input("Contraseña de Acceso*", type="password")
                
                # Selección de Rol
                cargo = st.radio("Cargo en el Sistema", ["Empleado", "Admin"], horizontal=True)
                rol_id = 1 if cargo == "Admin" else 2
                
                if st.form_submit_button("CREAR ACCESO STAFF"):
                    if all([st_n, st_a, st_d, st_e, st_p]):
                        payload = {
                            "nombre": st_n, "apellido": st_a, "dni": st_d, 
                            "email": st_e, "password": st_p, "rolId": rol_id, 
                            "fechaNacimiento": "2000-01-01"
                        }
                        res = api_call("POST", "Usuarios", payload)
                        if res and res.status_code in [200, 201]:
                            st.success(f"¡Éxito! {st_n} ahora es {cargo}.")
                        else:
                            st.error("Error al crear. El email o DNI ya podrían existir.")
                    else:
                        st.warning("Completar todos los campos obligatorios.")

    elif menu == "Cargar Cuota":
        st.header("Renovación de Membresía")
        sid = st.number_input("ID del Socio a renovar", min_value=1, step=1)
        st.markdown("Seleccione el plan de suscripción:")
        c1, c2, c3, c4 = st.columns(4)
        meses = 0
        if c1.button("1 MES"): meses = 1
        if c2.button("3 MESES"): meses = 3
        if c3.button("6 MESES"): meses = 6
        if c4.button("1 AÑO"): meses = 12
        if meses > 0:
            if api_call("POST", "Membresias", {"usuarioId": int(sid), "meses": meses}).status_code in [200, 201]:
                st.balloons()
                st.success(f"Membresía activada: {meses} mes(es) añadidos al socio ID {sid}")

# --- RUTEO PRINCIPAL ---
if st.session_state.get("token") is None: 
    login_page()
else:
    rol = st.session_state.get("user_data", {}).get("rolNombre", "").lower()
    if rol in ["admin", "empleado"]: 
        admin_dashboard()
    else: 
        socio_dashboard()
