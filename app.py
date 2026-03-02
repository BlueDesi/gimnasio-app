import streamlit as st
import requests

st.set_page_config(page_title="Control de Acceso Gimnasio", layout="centered")

# Estilos CSS
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
    .nombre-socio { font-size: 35px !important; font-weight: 900; text-transform: uppercase; margin-bottom: 5px; }
    .big-font { font-size: 55px !important; font-weight: 900; margin: 0; }
    .sub-font { font-size: 24px !important; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Sistema de Acceso")

# --- OPCIÓN A: POR ID ---
st.subheader("Opcion A: Por ID de Usuario")
with st.form("form_id", clear_on_submit=True):
    user_id = st.number_input("Ingrese ID numérico", min_value=0, step=1, format="%d")
    btn_id = st.form_submit_button("VALIDAR POR ID", use_container_width=True)

if btn_id and user_id > 0:
    try:
        res_user = requests.get(f"http://gimnasio.tryasp.net/api/Usuarios/{user_id}", timeout=5)
        res_acc = requests.get(f"http://gimnasio.tryasp.net/api/Usuarios/{user_id}/validar-acceso-id", timeout=5)
        
        if res_user.status_code == 200:
            u = res_user.json()
            nombre = f"{u.get('nombre') or ''} {u.get('apellido') or ''}".strip() or "SOCIO DESCONOCIDO"
            dias = u.get('diasRestantes') if u.get('diasRestantes') is not None else 0
            
            if res_acc.status_code == 200:
                st.markdown(f"""<div class="valido">
                    <p class="nombre-socio">{nombre}</p>
                    <p class="big-font">VÁLIDO</p>
                    <p class="sub-font">DÍAS RESTANTES: {dias}</p>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="denegado">
                    <p class="nombre-socio">{nombre}</p>
                    <p class="big-font">NO VÁLIDO</p>
                    <p class="sub-font">MEMBRESÍA VENCIDA O INACTIVA</p>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="denegado"><p class="big-font">NO VÁLIDO</p><p class="sub-font">ID NO REGISTRADO</p></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error de conexión")

st.write("---")

# --- OPCIÓN B: POR DNI ---
st.subheader("Opcion B: Por DNI")
with st.form("form_dni", clear_on_submit=True):
    user_dni = st.text_input("Ingrese DNI")
    btn_dni = st.form_submit_button("VALIDAR POR DNI", use_container_width=True)

if btn_dni and user_dni:
    try:
        res_dni = requests.get(f"http://gimnasio.tryasp.net/api/Membresias/validar/{user_dni}", timeout=5)
        if res_dni.status_code == 200:
            d = res_dni.json()
            # Limpieza de None en nombre y apellido
            nombre_api = d.get('nombre') or ""
            apellido_api = d.get('apellido') or ""
            nombre_completo = f"{nombre_api} {apellido_api}".strip()
            
            dias = d.get('diasRestantes', 0)
            
            if d.get("accesoPermitido"):
                st.markdown(f"""<div class="valido">
                    <p class="nombre-socio">{nombre_completo or "SOCIO REGISTRADO"}</p>
                    <p class="big-font">VÁLIDO</p>
                    <p class="sub-font">DÍAS RESTANTES: {dias}</p>
                </div>""", unsafe_allow_html=True)
            else:
                # Si el API dice que no, pero trae nombre, lo mostramos; si no, mensaje genérico
                txt_error = d.get('mensaje') or "SIN MEMBRESÍA ACTIVA"
                st.markdown(f"""<div class="denegado">
                    <p class="nombre-socio">{nombre_completo or "DNI NO ENCONTRADO"}</p>
                    <p class="big-font">NO VÁLIDO</p>
                    <p class="sub-font">{txt_error.upper()}</p>
                </div>""", unsafe_allow_html=True)
    except Exception:
        st.error("Error al consultar el servidor")