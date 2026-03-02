import streamlit as st
import requests

# Configuración de página para que parezca App
st.set_page_config(page_title="Acceso Gimnasio", layout="centered")

st.title("🛡️ Control de Acceso")

# CSS para los cuadros de colores (negro sobre color sólido)
st.markdown("""
    <style>
    .valido {
        background-color: #00FF00;
        color: #000000;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        border: 8px solid #000000;
    }
    .denegado {
        background-color: #FF0000;
        color: #000000;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        border: 8px solid #000000;
    }
    .big-font { font-size: 50px !important; font-weight: 900; }
    .sub-font { font-size: 25px !important; font-weight: bold; }
    </style>
    """, unsafe_allow_index=True)

# Entrada de ID
user_id = st.number_input("Ingrese ID de Usuario", min_value=0, step=1, format="%d")

if st.button("VERIFICAR ACCESO", use_container_width=True):
    if user_id > 0:
        try:
            # 1. Validar Acceso
            res_acceso = requests.get(f"http://gimnasio.tryasp.net/api/Usuarios/{user_id}/validar-acceso-id", timeout=5)
            
            if res_acceso.status_code == 200:
                # 2. Obtener Membresía
                res_memb = requests.get(f"http://gimnasio.tryasp.net/api/Membresias/usuario/{user_id}", timeout=5)
                data = res_memb.json()
                
                if isinstance(data, list) and len(data) > 0:
                    info = data[0]
                    vence = info.get('fechaVencimiento', 'N/A').split('T')[0]
                    dias = info.get('diasRestantes', 0)
                    
                    st.markdown(f"""
                        <div class="valido">
                            <p class="big-font">VÁLIDO</p>
                            <p class="sub-font">VENCE: {vence} | DÍAS: {dias}</p>
                        </div>
                    """, unsafe_allow_index=True)
                else:
                    st.markdown('<div class="denegado"><p class="big-font">NO VÁLIDO</p><p class="sub-font">SIN MEMBRESÍA</p></div>', unsafe_allow_index=True)
            else:
                st.markdown('<div class="denegado"><p class="big-font">NO VÁLIDO</p><p class="sub-font">ACCESO DENEGADO</p></div>', unsafe_allow_index=True)
                
        except Exception:
            st.error("Error de conexión con el servidor.")
    else:
        st.warning("Por favor, ingrese un ID válido.")