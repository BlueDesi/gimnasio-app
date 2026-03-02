import streamlit as st
import requests

# Configuración de página
st.set_page_config(page_title="Control de Acceso Gimnasio", layout="centered")

# Estilos CSS (Fondo sólido, letras negras, diseño gigante)
st.markdown("""
    <style>
    .valido {
        background-color: #00FF00; color: #000000; padding: 30px;
        border-radius: 15px; text-align: center; border: 8px solid #000000;
    }
    .denegado {
        background-color: #FF0000; color: #000000; padding: 30px;
        border-radius: 15px; text-align: center; border: 8px solid #000000;
    }
    .nombre-socio { font-size: 35px !important; font-weight: 900; margin-bottom: 5px; text-transform: uppercase; line-height: 1.1; }
    .big-font { font-size: 55px !important; font-weight: 900; margin: 0; }
    .sub-font { font-size: 24px !important; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Sistema de Acceso")

# --- BLOQUE 1: BÚSQUEDA POR ID ---
st.subheader("Opcion A: Por ID de Usuario")
with st.form("form_id", clear_on_submit=True):
    user_id = st.number_input("Ingrese ID numérico", min_value=0, step=1, format="%d")
    btn_id = st.form_submit_button("VALIDAR POR ID", use_container_width=True)

if btn_id and user_id > 0:
    try:
        # Se obtienen datos del perfil del usuario (nombre, apellido, diasRestantes)
        res_user = requests.get(f"http://gimnasio.tryasp.net/api/Usuarios/{user_id}", timeout=5)
        # Se valida el acceso
        res_acc = requests.get(f"http://gimnasio.tryasp.net/api/Usuarios/{user_id}/validar-acceso-id", timeout=5)
        
        if res_acc.status_code == 200 and res_user.status_code == 200:
            u = res_user.json()
            nombre = f"{u.get('nombre', '')} {u.get('apellido', '')}"
            dias = u.get('diasRestantes', 0)
            vence = u.get('fechaVencimiento', 'N/A').split('T')[0]
            
            st.markdown(f"""<div class="valido">
                <p class="nombre-socio">{nombre}</p>
                <p class="big-font">VÁLIDO</p>
                <p class="sub-font">DÍAS RESTANTES: {dias}<br>VENCE: {vence}</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="denegado"><p class="big-font">NO VÁLIDO</p><p class="sub-font">ACCESO DENEGADO O ID INEXISTENTE</p></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error: {e}")

st.write("---")

# --- BLOQUE 2: BÚSQUEDA POR DNI ---
st.subheader("Opcion B: Por DNI")
with st.form("form_dni", clear_on_submit=True):
    user_dni = st.text_input("Ingrese DNI")
    btn_dni = st.form_submit_button("VALIDAR POR DNI", use_container_width=True)

if btn_dni and user_dni:
    try:
        # El endpoint de DNI ya devuelve nombre, apellido y diasRestantes
        res_dni = requests.get(f"http://gimnasio.tryasp.net/api/Membresias/validar/{user_dni}", timeout=5)
        
        if res_dni.status_code == 200:
            d = res_dni.json()
            nombre = f"{d.get('nombre', '')} {d.get('apellido', '')}"
            dias = d.get('diasRestantes', 0)
            
            if d.get("accesoPermitido"):
                st.markdown(f"""<div class="valido">
                    <p class="nombre-socio">{nombre}</p>
                    <p class="big-font">VÁLIDO</p>
                    <p class="sub-font">DÍAS RESTANTES: {dias}</p>
                </div>""", unsafe_allow_html=True)
            else:
                msg = d.get('mensaje', 'ACCESO DENEGADO')
                st.markdown(f"""<div class="denegado">
                    <p class="nombre-socio">{nombre if nombre.strip() else "Socio Desconocido"}</p>
                    <p class="big-font">NO VÁLIDO</p>
                    <p class="sub-font">{msg}</p>
                </div>""", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error: {e}")