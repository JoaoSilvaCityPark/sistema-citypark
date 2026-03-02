import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES DO SISTEMA CITYPARK ---
TOLERANCIA_MINUTOS = 3

# Tabelas de Preços por Unidade (Total liberdade para Alairton ajustar aqui)
UNIDADES = {
    "Florianópolis - Unidade 1": {"valor_hora": 15.0, "valor_fracao": 5.0, "tempo_fracao": 15},
    "Itajaí - Unidade 2": {"valor_hora": 12.0, "valor_fracao": 4.0, "tempo_fracao": 15},
    "Palhoça - Matriz": {"valor_hora": 10.0, "valor_fracao": 3.0, "tempo_fracao": 15}
}

def calcular_valor(entrada, saida, config):
    duracao = saida - entrada
    minutos_totais = int(duracao.total_seconds() / 60)
    
    # REGRA: Tolerância de 3 minutos (Otimização solicitada)
    if minutos_totais <= TOLERANCIA_MINUTOS:
        return 0.0, minutos_totais

    # Lógica de cobrança: 1ª hora cheia + frações subsequentes
    if minutos_totais <= 60:
        return config["valor_hora"], minutos_totais
    else:
        minutos_extras = minutos_totais - 60
        # Calcula quantas frações de 15 min (ou o definido na unidade) passaram
        frações = -(-minutos_extras // config["tempo_fracao"]) 
        valor = config["valor_hora"] + (frações * config["valor_fracao"])
        return valor, minutos_totais

# --- INTERFACE VISUAL (STREAMLIT) ---
st.set_page_config(page_title="CityPark OS", page_icon="🚗", layout="wide")

# Cabeçalho com a identidade da empresa
st.title("🚗 CityPark OS - Gestão de Pátio")
st.markdown(f"**Operador:** {st.sidebar.text_input('Nome do Operador', 'Alairton')}")

# Seleção de Unidade (Filtro lateral)
unidade_sel = st.sidebar.selectbox("Selecione a Unidade de Operação", list(UNIDADES.keys()))
conf = UNIDADES[unidade_sel]

st.sidebar.divider()
st.sidebar.write(f"### Regras da Unidade")
st.sidebar.write(f"📍 **Local:** {unidade_sel}")
st.sidebar.write(f"⏱️ **Tolerância:** {TOLERANCIA_MINUTOS} min")
st.sidebar.write(f"💰 **1ª Hora:** R$ {conf['valor_hora']:.2f}")

# Simulação de Banco de Dados na memória (Session State)
if 'patio' not in st.session_state:
    st.session_state.patio = []
if 'historico' not in st.session_state:
    st.session_state.historico = []

# --- ÁREA DE OPERAÇÃO ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Entrada e Saída")
    placa = st.text_input("Digite a Placa", placeholder="ABC-1234").upper()
    
    btn_registrar = st.button("Registrar Movimentação", use_container_width=True)
    
    if btn_registrar and placa:
        # Verifica se o carro já está no pátio para dar saída
        veiculo_no_patio = next((v for v in st.session_state.patio if v["placa"] == placa), None)
        
        if veiculo_no_patio:
            # PROCESSO DE SAÍDA
            agora = datetime.now()
            valor, tempo = calcular_valor(veiculo_no_patio["entrada"], agora, conf)
            
            # Resultado da Saída
            if valor == 0:
                st.success(f"✅ LIBERADO! Tempo: {tempo} min (Dentro da tolerância)")
            else:
                st.warning(f"💰 VALOR A PAGAR: R$ {valor:.2f}")
                st.info(f"Tempo total: {tempo} minutos")
            
            # Move para o histórico e remove do pátio
            veiculo_no_patio["saida"] = agora
            veiculo_no_patio["valor"] = valor
            st.session_state.historico.append(veiculo_no_patio)
            st.session_state.patio = [v for v in st.session_state.patio if v["placa"] != placa]
        else:
            # PROCESSO DE ENTRADA
            novo_veiculo = {
                "placa": placa,
                "entrada": datetime.now(),
                "unidade": unidade_sel
            }
            st.session_state.patio.append(novo_veiculo)
            st.success(f"📥 Entrada registrada: {placa} às {datetime.now().strftime('%H:%M')}")

with col2:
    st.subheader(f"📊 Veículos no Pátio ({unidade_sel})")
    if st.session_state.patio:
        df_patio = pd.DataFrame(st.session_state.patio)
        # Filtra apenas veículos da unidade selecionada
        df_unidade = df_patio[df_patio['unidade'] == unidade_sel].copy()
        if not df_unidade.empty:
            df_unidade['entrada'] = df_unidade['entrada'].dt.strftime('%H:%M:%S')
            st.dataframe(df_unidade[['placa', 'entrada']], use_container_width=True)
        else:
            st.write("Nenhum veículo nesta unidade.")
    else:
        st.write("O pátio está vazio.")

# --- RELATÓRIO DE FECHAMENTO (FIM DA PÁGINA) ---
st.divider()
if st.checkbox("Ver Resumo de Faturamento do Dia"):
    if st.session_state.historico:
        df_hist = pd.DataFrame(st.session_state.historico)
        total_dia = df_hist[df_hist['unidade'] == unidade_sel]['valor'].sum()
        st.metric("Total Arrecadado (Unidade Atual)", f"R$ {total_dia:.2f}")
    else:
        st.write("Nenhuma saída registrada ainda.")
