import streamlit as st
import requests

# Configuración de página
st.set_page_config(page_title="Acceso Gimnasio", layout="centered")

# CSS Profesional: Negro sobre fondo sólido (Verde/Rojo)
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
    .nombre-socio { font-size: 38px !important; font-weight: 900; text-transform: uppercase; margin-bottom: 5px; }
    .big-font { font-size: 60px !important; font-weight: 900; margin: 0; }
    .sub-font { font-size: 26px !important; font-weight: bold; margin-top: 10px; }
    .stTextInput>div>div>input { font-size: 25px !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Control de Acceso Real-Time")

# Formulario de entrada única
with st.form("validador_principal", clear_on_submit=True):
    entrada = st.text_input("DNI o ID del Socio", placeholder="Ingrese identificación...")
    submit = st.form_submit_button("VERIFICAR MEMBRESÍA", use_container_width=True)

if submit and entrada:
    dni_para_validar = None
    
    try:
        # Lógica de detección: si es ID (menor a 6 dígitos) o DNI
        if entrada.isdigit() and len(entrada) < 6:
            # Es un ID, buscamos el DNI del usuario
            res_user = requests.get(f"http://gimnasio.tryasp.net/api/Usuarios/{entrada}", timeout=5)
            if res_user.status_code == 200:
                dni_para_validar = res_user.json().get('dni')
            else:
                st.markdown('<div class="denegado"><p class="big-font">ERROR</p><p class="sub-font">ID DE USUARIO NO ENCONTRADO</p></div>', unsafe_allow_html=True)
        else:
            # Asumimos que es DNI directamente
            dni_para_validar = entrada

        # Validación final por DNI (la única que confirma membresía real)
        if dni_para_validar:
            res_memb = requests.get(f"http://gimnasio.tryasp.net/api/Membresias/validar/{dni_para_validar}", timeout=5)
            
            if res_memb.status_code == 200:
                d = res_memb.json()
                nombre = f"{d.get('nombre') or ''} {d.get('apellido') or ''}".strip()
                dias = d.get('diasRestantes', 0)
                
                if d.get("accesoPermitido"):
                    st.markdown(f"""<div class="valido">
                        <p class="nombre-socio">{nombre or "SOCIO ACTIVO"}</p>
                        <p class="big-font">VÁLIDO</p>
                        <p class="sub-font">DÍAS RESTANTES: {dias}</p>
                    </div>""", unsafe_allow_html=True)
                else:
                    msg = d.get('mensaje') or "SIN MEMBRESÍA ACTIVA"
                    st.markdown(f"""<div class="denegado">
                        <p class="nombre-socio">{nombre or "Socio Inactivo"}</p>
                        <p class="big-font">NO VÁLIDO</p>
                        <p class="sub-font">{msg.upper()}</p>
                    </div>""", unsafe_allow_html=True)
            else:
                st.error("Error al consultar el servicio de membresías.")
                
    except Exception as e:
        st.error(f"Falla de comunicación con el servidor.")

st.divider()
st.caption("Configuración: Mostrador / Tablet / Mobile - API v3.0")