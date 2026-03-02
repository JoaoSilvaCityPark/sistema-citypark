import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO E CSS (VISUAL MOBILE/TABLET) ---
st.set_page_config(page_title="CityPark OS - Operação", page_icon="🅿️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f4f8; }
    [data-testid="stSidebar"] { background-color: #0f172a; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    
    /* Cartões Otimizados para Operação */
    .caixa-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; border-bottom: 4px solid #10b981; }
    .caixa-card h3 { margin: 0; color: #64748b; font-size: 14px; text-transform: uppercase; }
    .caixa-card h2 { margin: 5px 0 0 0; color: #0f172a; font-size: 24px; }
    
    .veiculo-card { background: white; padding: 15px; border-radius: 8px; border-left: 5px solid #3b82f6; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 10px; }
    .veiculo-card h4 { margin: 0; color: #0f172a; font-size: 18px; }
    .veiculo-card p { margin: 2px 0 0 0; color: #64748b; font-size: 14px; }
    
    /* Botões de Ação Rápida */
    .btn-entrada > button { background-color: #10b981; color: white; width: 100%; height: 3em; font-weight: bold; font-size: 16px; border-radius: 8px; }
    .btn-saida > button { background-color: #ef4444; color: white; width: 100%; height: 3em; font-weight: bold; font-size: 16px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- REGRAS CITYPARK ---
UNIDADES = {
    "Florianópolis - Centro": {"vagas": 50, "hora_carro": 15.0, "hora_moto": 10.0},
    "Itajaí - Porto": {"vagas": 30, "hora_carro": 12.0, "hora_moto": 8.0}
}
CONVENIOS = ["Nenhum", "Shima Sushi (Isento)", "Mensalista", "Parceiro (10% OFF)"]
PAGAMENTOS = ["Pix", "Dinheiro", "Crédito", "Débito", "Boleto"]

# --- BANCO DE DADOS (SESSÃO) ---
if 'patio' not in st.session_state: st.session_state.patio = []
if 'historico' not in st.session_state: st.session_state.historico = []

# --- MENU DO OPERADOR ---
with st.sidebar:
    st.image("https://www.google.com/s2/favicons?domain=cityparkestacionamentos.com&sz=256", width=80)
    st.title("CityPark Ponto de Venda")
    unidade = st.selectbox("📍 Unidade", list(UNIDADES.keys()))
    operador = st.selectbox("👤 Operador", ["Alairton João", "Daniel Ramos Cardoso", "Operador Caixa 1"])
    
    vagas_ocupadas = len([v for v in st.session_state.patio if v['unidade'] == unidade])
    st.progress(vagas_ocupadas / UNIDADES[unidade]["vagas"])
    st.write(f"**Disponibilidade:** {UNIDADES[unidade]['vagas'] - vagas_ocupadas} / {UNIDADES[unidade]['vagas']}")

# --- TELA PRINCIPAL (TABS DO OPERADOR) ---
tab_fluxo, tab_detalhes, tab_caixa = st.tabs(["🚗 ENTRADA / SAÍDA", "📋 VEÍCULOS NO PÁTIO", "💰 MEU CAIXA"])

# ==========================================
# 1. FLUXO PRINCIPAL (Foco em velocidade)
# ==========================================
with tab_fluxo:
    st.markdown("### Movimentação Rápida")
    placa = st.text_input("Digite a Placa", placeholder="Ex: ABC-1234").upper()
    
    veiculo = next((v for v in st.session_state.patio if v["placa"] == placa), None)
    
    if veiculo:
        # TELA DE SAÍDA / COBRANÇA
        st.error(f"⚠️ SAÍDA: Veículo no pátio desde às {veiculo['entrada'].strftime('%H:%M')}")
        st.write(f"**Veículo:** {veiculo.get('modelo', 'N/I')} - {veiculo.get('cor', 'N/I')} ({veiculo['tipo']})")
        
        c1, c2 = st.columns(2)
        convenio = c1.selectbox("Tabela / Convênio", CONVENIOS)
        pagamento = c2.selectbox("Forma de Pagamento", PAGAMENTOS)
        
        # Simulação de Cálculo (Sua lógica de tolerância entra aqui)
        valor = UNIDADES[unidade]["hora_carro"] if veiculo['tipo'] == "Carro" else UNIDADES[unidade]["hora_moto"]
        if "Isento" in convenio or "Mensalista" in convenio: valor = 0.0
        elif "10% OFF" in convenio: valor *= 0.9
        
        st.markdown(f"<h1 style='text-align: center; color: #0f172a;'>Total: R$ {valor:.2f}</h1>", unsafe_allow_html=True)
        
        st.markdown('<div class="btn-saida">', unsafe_allow_html=True)
        if st.button("🔴 CONFIRMAR SAÍDA E RECIBO"):
            st.session_state.historico.append({
                "placa": placa, "entrada": veiculo['entrada'], "saida": datetime.now(),
                "valor": valor, "pagamento": pagamento, "unidade": unidade, "operador": operador
            })
            st.session_state.patio = [v for v in st.session_state.patio if v["placa"] != placa]
            st.success("Saída registrada! Pátio atualizado.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # TELA DE ENTRADA (Com campos do Jump Park)
        c_tipo, c_mod, c_cor = st.columns([1, 2, 1])
        tipo = c_tipo.radio("Tipo", ["Carro", "Moto"], horizontal=True)
        modelo = c_mod.text_input("Marca/Modelo (Opcional)", placeholder="Ex: HB20")
        cor = c_cor.text_input("Cor (Opcional)", placeholder="Ex: Branco")
        
        st.write("")
        st.markdown('<div class="btn-entrada">', unsafe_allow_html=True)
        if st.button("🟢 REGISTRAR ENTRADA"):
            if placa:
                st.session_state.patio.append({
                    "placa": placa, "tipo": tipo, "modelo": modelo, "cor": cor, 
                    "entrada": datetime.now(), "unidade": unidade
                })
                st.success("Entrada Registrada!")
                st.rerun()
            else:
                st.warning("Por favor, digite a placa para registrar.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 2. VEÍCULOS NO PÁTIO (Estilo Cartão do Jump)
# ==========================================
with tab_detalhes:
    st.markdown("### Detalhes do Pátio")
    patio_unidade = [v for v in st.session_state.patio if v['unidade'] == unidade]
    
    if patio_unidade:
        for v in reversed(patio_unidade): # Mostra os mais recentes primeiro
            modelo_exib = f" - {v.get('modelo').upper()}" if v.get('modelo') else ""
            cor_exib = f" / {v.get('cor').upper()}" if v.get('cor') else ""
            hora = v['entrada'].strftime('%H:%M:%S')
            
            st.markdown(f"""
            <div class="veiculo-card">
                <h4>{v['placa']}{modelo_exib}{cor_exib}</h4>
                <p>Entrada: Hoje às {hora} | Tabela: ROTATIVO</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Pátio vazio neste momento.")

# ==========================================
# 3. RESUMO DO CAIXA DO OPERADOR
# ==========================================
with tab_caixa:
    hist_op = [h for h in st.session_state.historico if h['unidade'] == unidade and h['operador'] == operador]
    
    dinheiro = sum(h['valor'] for h in hist_op if h['pagamento'] == 'Dinheiro')
    pix = sum(h['valor'] for h in hist_op if h['pagamento'] == 'Pix')
    credito = sum(h['valor'] for h in hist_op if h['pagamento'] == 'Crédito')
    debito = sum(h['valor'] for h in hist_op if h['pagamento'] == 'Débito')
    total = dinheiro + pix + credito + debito
    
    st.markdown(f"### Fechamento Parcial - {operador}")
    st.markdown(f'<div class="caixa-card"><h3>Total em Caixa</h3><h2>R$ {total:.2f}</h2></div>', unsafe_allow_html=True)
    
    st.write("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💵 Dinheiro", f"R$ {dinheiro:.2f}")
    c2.metric("💳 Crédito", f"R$ {credito:.2f}")
    c3.metric("💳 Débito", f"R$ {debito:.2f}")
    c4.metric("📱 Pix", f"R$ {pix:.2f}")
