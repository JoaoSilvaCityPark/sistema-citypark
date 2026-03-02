import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO E CSS BLINDADO ---
st.set_page_config(page_title="CityPark OS - Enterprise", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    [data-testid="stSidebar"] { background-color: #0f172a; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: white; border-radius: 8px 8px 0 0; padding: 0 20px; font-weight: bold; color: #0f172a; }
    .metric-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-left: 5px solid #2563eb; }
    .metric-card h4 { color: #64748b !important; margin: 0; font-size: 13px; text-transform: uppercase; }
    .metric-card h2 { color: #0f172a !important; margin: 5px 0 0 0; font-size: 28px; font-weight: 800; }
    .op-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- REGRAS DA CITYPARK ---
UNIDADES = {
    "Florianópolis": {"vagas": 50, "hora_carro": 15.0, "hora_moto": 10.0},
    "Itajaí": {"vagas": 30, "hora_carro": 12.0, "hora_moto": 8.0}
}

CONVENIOS = ["Nenhum", "Shima Sushi (Isento)", "Mensalista", "Loja Parceira (10% OFF)"]

# --- BANCO DE DADOS VIRTUAL (SESSÃO) ---
if 'patio' not in st.session_state: st.session_state.patio = []
if 'historico' not in st.session_state: st.session_state.historico = []

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://www.google.com/s2/favicons?domain=cityparkestacionamentos.com&sz=256", width=100)
    st.title("CityPark OS")
    unidade = st.selectbox("📍 Unidade Operacional", list(UNIDADES.keys()))
    operador = st.selectbox("👤 Operador de Caixa", ["Alairton João", "Daniel Ramos Cardoso"])
    
    # Caixa atual simplificado na barra
    receita_hoje = sum(item['valor'] for item in st.session_state.historico if item['unidade'] == unidade)
    st.write("---")
    st.metric("💰 Caixa (Turno)", f"R$ {receita_hoje:.2f}")

# --- ESTRUTURA DE ABAS (TABS) ---
st.markdown(f"<h2 style='color: #0f172a;'>Painel Central - {unidade}</h2>", unsafe_allow_html=True)
tab_op, tab_dash, tab_config = st.tabs(["🚗 OPERAÇÃO DE PÁTIO", "📊 VISÃO GERENCIAL", "🤝 CLIENTES & CONVÊNIOS"])

# ==========================================
# ABA 1: OPERAÇÃO (CAIXA)
# ==========================================
with tab_op:
    col_entrada, col_saida = st.columns([1, 1.5])
    
    with col_entrada:
        st.markdown('<div class="op-card"><h3>🏁 Movimentação</h3>', unsafe_allow_html=True)
        placa = st.text_input("PLACA", placeholder="EX: ABC-1234").upper()
        tipo_veiculo = st.radio("Tipo", ["Carro", "Moto"], horizontal=True)
        
        veiculo_no_patio = next((v for v in st.session_state.patio if v["placa"] == placa), None)
        
        st.write("")
        if veiculo_no_patio:
            st.error(f"Veículo no pátio. Entrada: {veiculo_no_patio['entrada'].strftime('%H:%M')}")
            convenio_sel = st.selectbox("Convênio / Desconto", CONVENIOS)
            forma_pag = st.selectbox("Pagamento", ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"])
            
            # Cálculo Base (Simulação)
            valor_cobrado = UNIDADES[unidade]["hora_carro"] if veiculo_no_patio['tipo'] == "Carro" else UNIDADES[unidade]["hora_moto"]
            if convenio_sel == "Shima Sushi (Isento)" or convenio_sel == "Mensalista": valor_cobrado = 0.0
            elif convenio_sel == "Loja Parceira (10% OFF)": valor_cobrado *= 0.9
            
            st.markdown(f"<h2>Total: R$ {valor_cobrado:.2f}</h2>", unsafe_allow_html=True)
            
            if st.button("🔴 DAR SAÍDA E IMPRIMIR RECIBO", type="primary", use_container_width=True):
                # Salva no histórico para o painel gerencial
                st.session_state.historico.append({
                    "placa": placa, "entrada": veiculo_no_patio['entrada'], "saida": datetime.now(),
                    "valor": valor_cobrado, "pagamento": forma_pag, "unidade": unidade, "operador": operador
                })
                # Remove do pátio
                st.session_state.patio = [v for v in st.session_state.patio if v["placa"] != placa]
                st.success("Saída registrada com sucesso!")
                st.rerun()
        else:
            if st.button("🟢 LIBERAR ENTRADA", type="primary", use_container_width=True):
                if placa:
                    st.session_state.patio.append({"placa": placa, "tipo": tipo_veiculo, "entrada": datetime.now(), "unidade": unidade})
                    st.success("Entrada Registrada!")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_saida:
        st.markdown('<div class="op-card"><h3>📋 Veículos no Local</h3>', unsafe_allow_html=True)
        vagas_ocup = len([v for v in st.session_state.patio if v['unidade'] == unidade])
        st.progress(vagas_ocup / UNIDADES[unidade]["vagas"], text=f"Ocupação: {vagas_ocup} de {UNIDADES[unidade]['vagas']} vagas")
        
        if st.session_state.patio:
            df_patio = pd.DataFrame(st.session_state.patio)
            df_u = df_patio[df_patio['unidade'] == unidade].copy()
            if not df_u.empty:
                df_u['entrada'] = df_u['entrada'].dt.strftime('%H:%M')
                df_u = df_u.rename(columns={"placa": "PLACA", "tipo": "TIPO", "entrada": "HORA"})
                st.dataframe(df_u[['PLACA', 'TIPO', 'HORA']], use_container_width=True, hide_index=True)
        else:
            st.info("Pátio vazio.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# ABA 2: VISÃO GERENCIAL (O Diferencial)
# ==========================================
with tab_dash:
    st.markdown("### 📈 Desempenho Financeiro e Operacional")
    
    # Filtra histórico pela unidade atual
    hist_unidade = [h for h in st.session_state.historico if h['unidade'] == unidade]
    total_receita = sum(h['valor'] for h in hist_unidade)
    total_tickets = len(hist_unidade)
    ticket_medio = total_receita / total_tickets if total_tickets > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f'<div class="metric-card"><h4>Receita Bruta</h4><h2>R$ {total_receita:.2f}</h2></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card"><h4>Tickets Fechados</h4><h2>{total_tickets}</h2></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card"><h4>Ticket Médio</h4><h2>R$ {ticket_medio:.2f}</h2></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="metric-card"><h4>Isenções/Convênios</h4><h2>{len([h for h in hist_unidade if h["valor"] == 0])}</h2></div>', unsafe_allow_html=True)
    
    st.write("---")
    st.markdown("#### Fluxo de Caixa Diário")
    if hist_unidade:
        df_grafico = pd.DataFrame(hist_unidade)
        # Agrupa os valores pelo horário de saída
        df_grafico['Hora'] = df_grafico['saida'].dt.strftime('%H:%M')
        grafico_dados = df_grafico.groupby('Hora')['valor'].sum().reset_index()
        st.area_chart(grafico_dados.set_index('Hora'), color="#2563eb")
    else:
        st.info("Registre algumas saídas para visualizar o gráfico de fluxo de caixa (similar ao Jump Park).")

# ==========================================
# ABA 3: CLIENTES E CONVÊNIOS
# ==========================================
with tab_config:
    st.markdown("### 🤝 Gestão de Parcerias")
    st.write("Módulo preparado para cadastro de placas mensalistas e relatórios de parceiros (Ex: Shima Sushi).")
    st.info("Em breve: Integração automática de emissão de boletos para mensalistas.")
