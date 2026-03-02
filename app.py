import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="CityPark OS - Premium", page_icon="🅿️", layout="wide")

# --- ESTILIZAÇÃO INTERFACE APP (CSS PROFISSIONAL) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #041e42; color: white; }
    .stApp { background-color: #f8f9fa; }
    .metric-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #004a99;
    }
    .op-card {
        background-color: white; padding: 30px; border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1); border: 1px solid #e1e4e8;
    }
    .stButton>button {
        width: 100%; border-radius: 10px; height: 3.5em; 
        font-weight: bold; text-transform: uppercase; letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NEGÓCIO ---
UNIDADES = {
    "Florianópolis": {"vaga": 50, "preco": 15.0},
    "Itajaí": {"vaga": 30, "preco": 12.0}
}

if 'patio' not in st.session_state: st.session_state.patio = []
if 'caixa' not in st.session_state: st.session_state.caixa = 0.0

# --- BARRA LATERAL (GESTÃO) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/300/300221.png", width=80) # Placeholder Logo
    st.title("CityPark OS")
    unidade = st.selectbox("📍 Unidade Ativa", list(UNIDADES.keys()))
    st.divider()
    st.write(f"👤 **Operador:** Alairton João")
    st.metric("💰 Caixa do Dia", f"R$ {st.session_state.caixa:.2f}")

# --- CORPO DO APP ---
st.markdown(f"# 🏢 Painel de Controle - {unidade}")

# Linha de Indicadores
c1, c2, c3 = st.columns(3)
vagas_ocupadas = len([v for v in st.session_state.patio if v['unidade'] == unidade])
with c1:
    st.markdown(f'<div class="metric-card"><h4>🚗 Ocupação</h4><h2>{vagas_ocupadas} / {UNIDADES[unidade]["vaga"]}</h2></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><h4>⏱️ Tolerância</h4><h2>3 MIN</h2></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><h4>💵 Valor Hora</h4><h2>R$ {UNIDADES[unidade]["preco"]:.2f}</h2></div>', unsafe_allow_html=True)

st.write("")

# Área de Operação Principal
col_op, col_list = st.columns([1.2, 2])

with col_op:
    st.markdown('<div class="op-card">', unsafe_allow_html=True)
    st.subheader("🏁 Entrada / Saída")
    placa = st.text_input("PLACA", placeholder="Digite a placa...").upper()
    
    veiculo = next((v for v in st.session_state.patio if v["placa"] == placa), None)
    
    if veiculo:
        st.warning(f"Veículo em pátio - Entrada: {veiculo['entrada'].strftime('%H:%M')}")
        pagamento = st.selectbox("Forma de Pagamento", ["PIX", "Cartão", "Dinheiro"])
        if st.button("🔴 FINALIZAR SAÍDA"):
            st.session_state.caixa += UNIDADES[unidade]["preco"]
            st.session_state.patio = [v for v in st.session_state.patio if v["placa"] != placa]
            st.success("Ticket Finalizado!")
            st.rerun()
    else:
        if st.button("🟢 REGISTRAR ENTRADA"):
            if placa:
                st.session_state.patio.append({"placa": placa, "entrada": datetime.now(), "unidade": unidade})
                st.success("Entrada Confirmada!")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_list:
    st.markdown('<div class="op-card">', unsafe_allow_html=True)
    st.subheader("📋 Veículos no Local")
    if st.session_state.patio:
        df = pd.DataFrame(st.session_state.patio)
        df_unid = df[df['unidade'] == unidade].copy()
        if not df_unid.empty:
            df_unid['entrada'] = df_unid['entrada'].dt.strftime('%H:%M')
            st.dataframe(df_unid[['placa', 'entrada']], use_container_width=True, hide_index=True)
        else: st.info("Pátio vazio.")
    else: st.info("Nenhum veículo registrado.")
    st.markdown('</div>', unsafe_allow_html=True)
