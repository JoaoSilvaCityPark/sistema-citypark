import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="CityPark OS - Premium", page_icon="🅿️", layout="wide")

# --- CSS BLINDADO (VISUAL DE APP PROFISSIONAL E CORES CITYPARK) ---
st.markdown("""
    <style>
    /* Força o fundo cinza claro e protege contra o Dark Mode nativo */
    .stApp { background-color: #f1f5f9; }
    
    /* Estiliza a Barra Lateral com o Azul Marinho Premium */
    [data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid #1e293b; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    
    /* Garante que os textos fora da barra lateral fiquem escuros e legíveis */
    .stMarkdown, .stText { color: #1e293b !important; }

    /* Cartões de Indicadores (Métricas) */
    .metric-card {
        background-color: #ffffff;
        padding: 20px 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-left: 6px solid #2563eb; /* Azul Destaque CityPark */
        margin-bottom: 20px;
    }
    .metric-card h4 { color: #64748b !important; margin: 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
    .metric-card h2 { color: #0f172a !important; margin: 8px 0 0 0; font-size: 32px; font-weight: 800; }
    
    /* Cartões de Operação (Entrada/Saída) */
    .op-card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    .op-card h3 { color: #0f172a !important; font-weight: 700; margin-bottom: 20px;}
    
    /* Botões Modernos (Estilo Aplicativo) */
    div.stButton > button {
        width: 100%; border-radius: 8px; height: 3.5em; 
        font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;
        border: none; transition: all 0.2s;
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- REGRAS DE NEGÓCIO DA CITYPARK ---
UNIDADES = {
    "Florianópolis": {"vagas": 50, "preco": 15.0},
    "Itajaí": {"vagas": 30, "preco": 12.0}
}

if 'patio' not in st.session_state: st.session_state.patio = []
if 'caixa' not in st.session_state: st.session_state.caixa = 0.0

# --- BARRA LATERAL (GESTÃO) ---
with st.sidebar:
    # Capturando o Logo Oficial direto do site da CityPark
    st.image("https://www.google.com/s2/favicons?domain=cityparkestacionamentos.com&sz=256", width=120)
    st.title("CityPark OS")
    st.write("---")
    unidade = st.selectbox("📍 Unidade Ativa", list(UNIDADES.keys()))
    st.write("---")
    st.write(f"👤 **Operador:** Alairton João")
    st.metric("💰 Caixa do Dia", f"R$ {st.session_state.caixa:.2f}")

# --- CORPO PRINCIPAL DO APLICATIVO ---
st.markdown(f"<h1 style='color: #0f172a;'>🏢 Painel de Controle - {unidade}</h1>", unsafe_allow_html=True)
st.write("")

# 1. LINHA DE INDICADORES (Dashboard)
c1, c2, c3 = st.columns(3)
vagas_ocupadas = len([v for v in st.session_state.patio if v['unidade'] == unidade])

with c1:
    st.markdown(f'<div class="metric-card"><h4>🚗 Ocupação de Pátio</h4><h2>{vagas_ocupadas} / {UNIDADES[unidade]["vagas"]}</h2></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><h4>⏱️ Tempo de Tolerância</h4><h2>3 MINUTOS</h2></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><h4>💵 Valor da 1ª Hora</h4><h2>R$ {UNIDADES[unidade]["preco"]:.2f}</h2></div>', unsafe_allow_html=True)

# 2. ÁREA DE OPERAÇÃO
col_op, col_list = st.columns([1.2, 2])

with col_op:
    st.markdown('<div class="op-card"><h3>🏁 Entrada / Saída</h3>', unsafe_allow_html=True)
    placa = st.text_input("PLACA DO VEÍCULO", placeholder="Ex: ABC-1234").upper()
    
    veiculo = next((v for v in st.session_state.patio if v["placa"] == placa), None)
    st.write("") # Espaço
    
    if veiculo:
        st.error(f"⚠️ Veículo no pátio desde: {veiculo['entrada'].strftime('%H:%M')}")
        pagamento = st.selectbox("Forma de Pagamento", ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"])
        if st.button("🔴 FINALIZAR SAÍDA E COBRAR", type="primary"):
            st.session_state.caixa += UNIDADES[unidade]["preco"]
            st.session_state.patio = [v for v in st.session_state.patio if v["placa"] != placa]
            st.success("Ticket Finalizado com Sucesso!")
            st.rerun()
    else:
        if st.button("🟢 REGISTRAR ENTRADA", type="primary"):
            if placa:
                st.session_state.patio.append({"placa": placa, "entrada": datetime.now(), "unidade": unidade})
                st.success("Veículo liberado para entrar!")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_list:
    st.markdown('<div class="op-card"><h3>📋 Veículos no Pátio Agora</h3>', unsafe_allow_html=True)
    if st.session_state.patio:
        df = pd.DataFrame(st.session_state.patio)
        df_unid = df[df['unidade'] == unidade].copy()
        if not df_unid.empty:
            df_unid['entrada'] = df_unid['entrada'].dt.strftime('%H:%M')
            # Renomeando as colunas para o português correto
            df_unid = df_unid.rename(columns={"placa": "PLACA", "entrada": "HORA DA ENTRADA"})
            st.dataframe(df_unid[['PLACA', 'HORA DA ENTRADA']], use_container_width=True, hide_index=True)
        else: 
            st.info("Pátio vazio no momento.")
    else: 
        st.info("Nenhum veículo registrado no sistema.")
    st.markdown('</div>', unsafe_allow_html=True)
