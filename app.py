import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÕES VISUAIS (LAYOUT ARROJADO) ---
st.set_page_config(page_title="CityPark OS - Premium", page_icon="🅿️", layout="wide")

# Estilização para visual moderno e cores da CityPark
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #003366; color: white; font-weight: bold; }
    .card { padding: 25px; border-radius: 15px; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border: 1px solid #e1e4e8; }
    h3 { color: #003366; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# Logo e Título (Branding presente em todo o app)
with st.container():
    col_logo, col_tit = st.columns([1, 8])
    with col_logo:
        # Ícone representativo enquanto você não sobe o seu logo oficial
        st.markdown("## 🅿️") 
    with col_tit:
        st.title("CityPark OS - Inteligência em Estacionamentos")

# --- REGRAS DE NEGÓCIO E CONVÊNIOS ---
UNIDADES = {
    "Florianópolis": {"valor_hora": 15.0, "valor_fracao": 5.0},
    "Itajaí": {"valor_hora": 12.0, "valor_fracao": 4.0}
}

CONVENIOS = {
    "Nenhum": 0,
    "Shima Sushi (1h Cortesia)": 60,
    "Convênio Lojista (10% Desc)": 0.10
}

# --- ESTADO DO SISTEMA ---
if 'patio' not in st.session_state: st.session_state.patio = []
if 'historico' not in st.session_state: st.session_state.historico = []

# Menu Lateral com Logo
st.sidebar.markdown("### 🏢 Gestão CityPark")
unidade_ativa = st.sidebar.selectbox("Unidade", list(UNIDADES.keys()))
st.sidebar.divider()
st.sidebar.write(f"**Operador:** Alairton João")

# --- INTERFACE OPERACIONAL ---
c1, c2 = st.columns([1.2, 2])

with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📥 Entrada / Saída")
    placa = st.text_input("Placa", placeholder="Digite a placa...").upper()
    
    veiculo = next((v for v in st.session_state.patio if v["placa"] == placa), None)
    
    if veiculo:
        st.info(f"Veículo no pátio desde às {veiculo['entrada'].strftime('%H:%M')}")
        conv = st.selectbox("Aplicar Convênio", list(CONVENIOS.keys()))
        pag = st.radio("Forma de Pagamento", ["PIX", "Cartão", "Dinheiro"], horizontal=True)
        
        # Lógica de Preço com Convênio
        valor = UNIDADES[unidade_ativa]["valor_hora"]
        if conv == "Shima Sushi (1h Cortesia)": valor = 0.0
        elif conv == "Convênio Lojista (10% Desc)": valor *= 0.9
        
        st.markdown(f"### Total: R$ {valor:.2f}")
        if st.button("Finalizar Saída"):
            st.session_state.patio = [v for v in st.session_state.patio if v["placa"] != placa]
            st.success(f"Saída realizada! Pagamento via {pag}.")
    else:
        if st.button("Registrar Entrada"):
            if placa:
                st.session_state.patio.append({"placa": placa, "entrada": datetime.now(), "unidade": unidade_ativa})
                st.success(f"Entrada registrada: {placa}")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(f"📊 Pátio Ativo - {unidade_ativa}")
    if st.session_state.patio:
        df = pd.DataFrame(st.session_state.patio)
        df_unid = df[df['unidade'] == unidade_ativa].copy()
        if not df_unid.empty:
            df_unid['entrada'] = df_unid['entrada'].dt.strftime('%H:%M')
            st.table(df_unid[['placa', 'entrada']])
        else:
            st.write("Nenhum veículo nesta unidade.")
    else:
        st.write("Pátio vazio.")
    st.markdown('</div>', unsafe_allow_html=True)
