import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="CityPark OS - Backoffice", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    .card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; border-top: 4px solid #0f172a;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# BANCO DE DADOS DINÂMICO (Memória)
# Aqui é onde o sistema guarda as informações que você cadastrar
# ==========================================
if 'db_unidades' not in st.session_state:
    st.session_state.db_unidades = [
        {"id": 1, "nome": "Florianópolis - Matriz", "endereco": "Rua Cônego Bernardo, 101 - Trindade", "cnpj": "29.145.696/0001-26"},
        {"id": 2, "nome": "Itajaí - Centro", "endereco": "Rua Exemplo, 200 - Centro", "cnpj": "00.000.000/0000-00"}
    ]
if 'db_tabelas' not in st.session_state:
    st.session_state.db_tabelas = [
        {"unidade": "Florianópolis - Matriz", "nome_tabela": "ROTATIVO", "valor": 15.00},
        {"unidade": "Florianópolis - Matriz", "nome_tabela": "LA BOHEME", "valor": 4.00},
        {"unidade": "Itajaí - Centro", "nome_tabela": "ROTATIVO", "valor": 12.00}
    ]
if 'db_usuarios' not in st.session_state:
    st.session_state.db_usuarios = ["Alairton João", "Daniel Ramos Cardoso"]

# ==========================================
# NAVEGAÇÃO PRINCIPAL (Gerente vs Operador)
# ==========================================
st.sidebar.image("https://www.google.com/s2/favicons?domain=cityparkestacionamentos.com&sz=256", width=100)
modo_acesso = st.sidebar.radio("🔑 Tipo de Acesso", ["Painel do Gestor (Admin)", "Tela do Operador (PDV)"])
st.sidebar.divider()

if modo_acesso == "Painel do Gestor (Admin)":
    st.title("⚙️ Painel Gerencial CityPark")
    
    tab_unidades, tab_tabelas, tab_equipe = st.tabs(["🏢 Gestão de Pátios", "💰 Tabelas e Convênios", "👥 Controle de Equipe"])
    
    # --- 1. GESTÃO DE PÁTIOS E ENDEREÇOS ---
    with tab_unidades:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Cadastrar Novo Pátio")
        c1, c2, c3 = st.columns([2, 3, 1])
        nova_unid_nome = c1.text_input("Nome da Unidade (Ex: Palhoça - Shopping)")
        nova_unid_end = c2.text_input("Endereço Completo para o Recibo")
        nova_unid_cnpj = c3.text_input("CNPJ Local")
        
        if st.button("➕ Adicionar Unidade", type="primary"):
            if nova_unid_nome and nova_unid_end:
                st.session_state.db_unidades.append({
                    "id": len(st.session_state.db_unidades) + 1,
                    "nome": nova_unid_nome, "endereco": nova_unid_end, "cnpj": nova_unid_cnpj
                })
                st.success(f"Unidade '{nova_unid_nome}' cadastrada com sucesso!")
                st.rerun()
        
        st.write("---")
        st.subheader("Unidades Ativas")
        st.dataframe(pd.DataFrame(st.session_state.db_unidades), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 2. GESTÃO DE TABELAS DE PREÇO ---
    with tab_tabelas:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Cadastrar Nova Regra/Convênio")
        nomes_unidades = [u["nome"] for u in st.session_state.db_unidades]
        
        c_unid, c_tab, c_val = st.columns(3)
        unid_alvo = c_unid.selectbox("Vincular a qual unidade?", nomes_unidades)
        nome_tab = c_tab.text_input("Nome da Tabela (Ex: Shima Sushi)")
        valor_tab = c_val.number_input("Valor Padrão (R$)", min_value=0.0, format="%.2f")
        
        if st.button("➕ Adicionar Tabela", type="primary"):
            if nome_tab:
                st.session_state.db_tabelas.append({"unidade": unid_alvo, "nome_tabela": nome_tab.upper(), "valor": valor_tab})
                st.success("Tabela cadastrada!")
                st.rerun()
                
        st.write("---")
        st.subheader("Tabelas Ativas por Unidade")
        st.dataframe(pd.DataFrame(st.session_state.db_tabelas), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 3. GESTÃO DE EQUIPE ---
    with tab_equipe:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Cadastrar Colaborador")
        novo_operador = st.text_input("Nome do Funcionário")
        if st.button("➕ Adicionar Operador", type="primary"):
            if novo_operador and novo_operador not in st.session_state.db_usuarios:
                st.session_state.db_usuarios.append(novo_operador)
                st.success("Operador adicionado!")
                st.rerun()
                
        st.write("---")
        st.write("**Lista de Colaboradores Autorizados:**")
        for usr in st.session_state.db_usuarios:
            st.write(f"- 👤 {usr}")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TELA DO OPERADOR (PDV Dinâmico)
# ==========================================
elif modo_acesso == "Tela do Operador (PDV)":
    # O PDV agora puxa as informações cadastradas lá no painel do gestor
    nomes_unidades = [u["nome"] for u in st.session_state.db_unidades]
    
    st.sidebar.subheader("Configuração do Turno")
    unidade_pdv = st.sidebar.selectbox("📍 Unidade de Operação", nomes_unidades)
    operador_pdv = st.sidebar.selectbox("👤 Operador Logado", st.session_state.db_usuarios)
    
    # Filtra as tabelas de preço apenas para a unidade que o operador selecionou
    tabelas_desta_unidade = [t["nome_tabela"] for t in st.session_state.db_tabelas if t["unidade"] == unidade_pdv]
    
    st.title(f"🚗 PDV - {unidade_pdv}")
    st.write(f"Bem-vindo(a), **{operador_pdv}**! Selecione a placa e a tabela abaixo.")
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    placa = st.text_input("Placa do Veículo", placeholder="ABC-1234").upper()
    
    c1, c2 = st.columns(2)
    tabela_selecionada = c1.selectbox("Tabela de Cobrança / Convênio", tabelas_desta_unidade if tabelas_desta_unidade else ["Nenhuma tabela cadastrada"])
    forma_pagamento = c2.selectbox("Forma de Pagamento", ["Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"])
    
    if st.button("GERAR RECIBO DE SAÍDA", use_container_width=True):
        # Busca os dados exatos da unidade selecionada para imprimir no recibo
        dados_unidade = next((u for u in st.session_state.db_unidades if u["nome"] == unidade_pdv), None)
        valor_cobrado = next((t["valor"] for t in st.session_state.db_tabelas if t["nome_tabela"] == tabela_selecionada and t["unidade"] == unidade_pdv), 0.0)
        
        st.success("Cobrança registrada! Imprimindo recibo...")
        st.code(f"""
        -----------------------------------
        CITYPARK ESTACIONAMENTOS LTDA
        {dados_unidade['endereco']}
        CNPJ: {dados_unidade['cnpj']}
        -----------------------------------
        PLACA: {placa}
        TABELA: {tabela_selecionada}
        PAGAMENTO: {forma_pagamento}
        OPERADOR: {operador_pdv}
        -----------------------------------
        TOTAL: R$ {valor_cobrado:.2f}
        -----------------------------------
        """, language="text")
    st.markdown('</div>', unsafe_allow_html=True)
