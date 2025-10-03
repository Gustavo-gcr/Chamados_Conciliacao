import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

# --- CARREGAMENTO SEGURO DOS SECRETS DO STREAMLIT ---
try:
    # --- CONFIGURAÇÕES GERAIS DA API ---
    # Carrega as URLs, Token, IDs e o Mapeamento de Atendentes do st.secrets
    API_URL = st.secrets["tomticket"]["api_url"]
    LINK_OPERATOR_URL = st.secrets["tomticket"]["link_operator_url"]
    TOKEN = st.secrets["tomticket"]["token"]
    CUSTOMER_ID = st.secrets["tomticket"]["customer_id"]
    DEPARTMENT_ID = st.secrets["tomticket"]["department_id"]
    PRIORITY = 2 # Prioridade não é um secret, mantida fixa
    
    # --- MAPEAMENTO DE ATENDENTES COM OS NOVOS IDs ---
    # Carrega o dicionário completo do st.secrets
    OPERATOR_MAP = dict(st.secrets["operator_map"])

except KeyError as e:
    st.error(f"❌ Erro ao carregar as chaves do Streamlit Secrets: **{e}**.")
    st.error("Por favor, verifique se seu arquivo `.streamlit/secrets.toml` ou as 'Secrets' do Streamlit Cloud estão configuradas corretamente conforme o exemplo.")
    st.stop() # Interrompe a execução se os secrets não puderem ser carregados


# === HEADERS ===
headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# --- MAPEAMENTO DE CATEGORIAS (BASEADO NO CÓDIGO ANTERIOR) ---
# Este dicionário continua no código, pois não contém dados sensíveis.
CATEGORY_MAP = {
    "Planilha de retorno e analisar todos que estão enviados ao Banco do dia. Mandar no e-mail quando finalizar;": "aa426ddcb6b56b8e1c71ed7047ae3487",
    "Lançamentos do Bloqueio, desbloqueio, estorno, resgate e aplicação;": "54f81eaf6d56ff0e9a3693ad03c0ca20",
    "Subir as contas sem sitex do dia": "97e29d86712718d6e9eb4319e6cef5bb",
    "Analisar débitos. Enviar no meu e-mail as contas que continuaram com erro e estão com dúvidas. Dessa forma, os débitos tem que estar zerado.": "080ed4378a115a19652982ca67ab3f16",
    "Analisar créditos. Enviar no meu e-mail relatório dos valores que não conseguiram identificar. Dessa forma, os créditos tem que estar todos analisados.": "a3618019de9b698a54573a1c6ad29b78",
    "Enviar planilha de Saldos por e-mail;": "dce5772615a4691ed22096f514fbf85e",
    "Lançar tarifa;": "97e29d86712718d6e9eb4319e6cef5bb",
    "Verificar saldo do dia;": "97e29d86712718d6e9eb4319e6cef5bb",
    "Fazer analise das centrais;": "6fddc15f138065d0c1444cfe26eee393",
    "Lançar valores do controle que foram avisados no dia anterior e não foram feitos ainda dentro do molde combinado; Enviar no e-mail valores que não conseguiram identificar o que fazer.": "54f81eaf6d56ff0e9a3693ad03c0ca20" 
}


# --- DADOS DA PLANILHA ---
# Estrutura de dados baseada na imagem que você anexou
data = [
    # Atendente, Nome do Chamado, Horário, Mensagem, Prazo
    ("Mariana", "Planilha de retorno", "Manhã", "Planilha de retorno e analisar todos que estão enviados ao Banco do dia. Mandar no e-mail quando finalizar;", "09:00"),
    ("Brener", "Lançamentos manuais", "Manhã", "Lançamentos do Bloqueio, desbloqueio, estorno, resgate e aplicação;", "10:00"),
    ("Mariana", "Lançamentos manuais", "Manhã", "Lançamentos do Bloqueio, desbloqueio, estorno, resgate e aplicação;", "10:00"),
    ("Brener", "Sem Sitex", "Manhã", "Subir as contas sem sitex do dia", "10:00"),
    ("Mariana", "Sem Sitex", "Manhã", "Subir as contas sem sitex do dia", "10:00"),
    ("Brener", "Analise de débitos", "Manhã", "Analisar débitos. Enviar no meu e-mail as contas que continuaram com erro e estão com dúvidas. Dessa forma, os débitos tem que estar zerado.", "12:00"),
    ("Mariana", "Analise de débitos", "Manhã", "Analisar débitos. Enviar no meu e-mail as contas que continuaram com erro e estão com dúvidas. Dessa forma, os débitos tem que estar zerado.", "12:00"),
    ("Brener", "Analise de créditos", "Tarde", "Analisar créditos. Enviar no meu e-mail relatório dos valores que não conseguiram identificar. Dessa forma, os créditos tem que estar todos analisados.", "16:00"),
    ("Mariana", "Relatório de Saldos", "Tarde", "Enviar planilha de Saldos por e-mail;", "17:00"),
    ("Davi", "Contas Sem Sitex", "Tarde", "Lançar tarifa;", "16:00"),
    ("Yasmin", "Contas Sem Sitex", "Tarde", "Verificar saldo do dia;", "16:00"),
    ("Davi", "Recebimentos das centrais", "Tarde", "Fazer analise das centrais;", "14:00"),
    ("Brener", "Lançamento no controle", "Tarde", "Lançar valores do controle que foram avisados no dia anterior e não foram feitos ainda dentro do molde combinado; Enviar no e-mail valores que não conseguiram identificar o que fazer.", "18:00"),
    ("Mariana", "Lançamento no controle", "Tarde", "Lançar valores do controle que foram avisados no dia anterior e não foram feitos ainda dentro do molde combinado; Enviar no e-mail valores que não conseguiram identificar o que fazer.", "18:00"),
    ("Yasmin", "Lançamento no controle", "Tarde", "Lançar valores do controle que foram avisados no dia anterior e não foram feitos ainda dentro do molde combinado; Enviar no e-mail valores que não conseguiram identificar o que fazer.", "18:00"),
    ("Brener", "Analise de créditos", "Tarde", "Analisar créditos. Enviar no meu e-mail relatório dos valores que não conseguiram identificar. Dessa forma, os créditos tem que estar todos analisados.", "18:00")
]

# Cria o DataFrame
df = pd.DataFrame(data, columns=["Atendente", "Nome", "Horário", "Mensagem", "Prazo"])


# --- FUNÇÕES DE CRIAÇÃO DE CHAMADO ---

def create_ticket(chamado):
    """Cria o chamado e vincula o atendente na API do TomTicket."""
    
    atendente = chamado["Atendente"]
    operator_id = OPERATOR_MAP.get(atendente)
    
    msg_limpa = chamado["Mensagem"].strip() 
    category_id = CATEGORY_MAP.get(msg_limpa, "") 

    if not operator_id:
        st.error(f"❌ Erro: Atendente **{atendente}** não mapeado para um `operator_id` válido. Verifique `operator_map` no secrets.")
        return False
        
    # 1. Criação do Chamado
    data_ticket = {
        "customer_id": CUSTOMER_ID,
        "customer_id_type": "E",
        "department_id": DEPARTMENT_ID,
        "subject": chamado["Nome"] + f" ({atendente}) - Prazo: {chamado['Prazo']}",
        "message": f"{chamado['Mensagem']}\n\nChamado automático gerado às {datetime.now().strftime('%d/%m/%Y %H:%M')}.",
        "category_id": category_id,
        "priority": PRIORITY
    }

    try:
        response = requests.post(API_URL, headers=headers, data=data_ticket, timeout=10)
        
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get("success"):
                ticket_id = resp_json.get("ticket_id") 
                
                # 2. Vinculação do Atendente
                link_data = {
                    "ticket_id": ticket_id,
                    "operator_id": operator_id
                }
                
                link_response = requests.post(LINK_OPERATOR_URL, headers=headers, data=link_data, timeout=10)
                
                if link_response.status_code == 200 and link_response.json().get("success"):
                    st.success(f"✅ **{chamado['Nome']}** ({atendente}) criado e vinculado com sucesso! ")
                    return True
                else:
                    # Continua mesmo se a vinculação falhar, pois o chamado foi criado
                    st.warning(f"⚠️ **{chamado['Nome']}** ({atendente}) criado, mas erro ao vincular atendente.")
                    return False
            else:
                st.error(f"❌ Erro na criação de **{chamado['Nome']}** ({atendente}): {resp_json.get('message')}")
                return False
        else:
            st.error(f"❌ Erro na requisição de criação de **{chamado['Nome']}** ({atendente}): {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro de conexão ao enviar **{chamado['Nome']}** ({atendente}): {e}")
        return False


def run_automation(periodo, chamados_df):
    """Filtra e executa a criação de chamados para um período (Manhã ou Tarde)."""
    st.subheader(f"⚙️ Iniciando criação de chamados: **{periodo.upper()}**")
    
    # Filtra os chamados pelo horário
    chamados_filtrados = chamados_df[chamados_df["Horário"] == periodo].to_dict('records')
    
    if not chamados_filtrados:
        st.info(f"Nenhum chamado encontrado para o período da **{periodo}**.")
        return

    st.write(f"**{len(chamados_filtrados)}** chamado(s) a ser(em) criado(s).")
    
    status_placeholder = st.empty()
    
    for i, chamado in enumerate(chamados_filtrados):
        status_placeholder.info(f"Processando {i+1} de {len(chamados_filtrados)}: **{chamado['Nome']}** ({chamado['Atendente']})...")
        
        create_ticket(chamado)
        
        # Pausa para evitar sobrecarga da API
        time.sleep(1.5) 

    st.balloons()
    status_placeholder.success(f"🎉 Processo concluído para os chamados da **{periodo}**!")


# --- INTERFACE STREAMLIT ---

st.title("🤖 Automação de Chamados Diários (TomTicket)")
st.caption("Selecione o período para criar automaticamente os chamados e vincular os atendentes.")

st.markdown("---")

# Exibe a tabela de referência
st.subheader("📋 Chamados Programados (Referência)")
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")

st.header("Criar Chamados Conciliação:")

col1, col2 = st.columns(2)

with col1:
    if st.button("☀️ Rodar Chamados da Manhã", use_container_width=True, type="primary"):
        # Garante que o estado seja limpo antes de rodar
        st.session_state["executed"] = "Manhã" 
        run_automation("Manhã", df)

with col2:
    if st.button("🌙 Rodar Chamados da Tarde", use_container_width=True, type="secondary"):
        st.session_state["executed"] = "Tarde"
        run_automation("Tarde", df)

st.markdown("---")

if "executed" in st.session_state:
    st.subheader(f"Última Execução: Chamados da **{st.session_state['executed']}**")
    st.info("Verifique os logs acima para o status detalhado de cada chamado.")
else:
    st.info("Aguardando seleção de período (Manhã ou Tarde) para iniciar a automação.")