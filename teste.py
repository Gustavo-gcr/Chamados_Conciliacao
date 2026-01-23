# import streamlit as st
# import pandas as pd
# import requests
# from datetime import datetime
# import time

# # --- CARREGAMENTO SEGURO DOS SECRETS DO STREAMLIT ---
# try:
#     # --- CONFIGURAÇÕES GERAIS DA API ---
#     API_URL = st.secrets["tomticket"]["api_url"]
#     LINK_OPERATOR_URL = st.secrets["tomticket"]["link_operator_url"]
#     TOKEN = st.secrets["tomticket"]["token"]
#     CUSTOMER_ID = st.secrets["tomticket"]["customer_id"]
#     DEPARTMENT_ID = st.secrets["tomticket"]["department_id"]
#     PRIORITY = 2 
    
#     # --- MAPEAMENTO DE ATENDENTES ---
#     OPERATOR_MAP = dict(st.secrets["operator_map"])

# except KeyError as e:
#     st.error(f"❌ Erro ao carregar as chaves do Streamlit Secrets: **{e}**.")
#     st.stop() 


# # === HEADERS ===
# headers = {
#     "Authorization": f"Bearer {TOKEN}"
# }

# # --- MAPEAMENTO DE CATEGORIAS ---
# # Não foi necessário alterar nada aqui, pois as mensagens da Yasmin já existiam no mapeamento.
# CATEGORY_MAP = {
#     "Planilha de retorno e analisar todos que estão enviados ao Banco do dia. Mandar no e-mail quando finalizar;": "aa426ddcb6b56b8e1c71ed7047ae3487",
#     "Lançamentos do Bloqueio, desbloqueio, estorno, resgate e aplicação;": "54f81eaf6d56ff0e9a3693ad03c0ca20",
#     "Subir as contas sem sitex do dia": "97e29d86712718d6e9eb4319e6cef5bb",
#     "Analisar débitos. Enviar no meu e-mail as contas que continuaram com erro e estão com dúvidas. Dessa forma, os débitos tem que estar zerado.": "080ed4378a115a19652982ca67ab3f16",
#     "Analisar créditos. Enviar no meu e-mail relatório dos valores que não conseguiram identificar. Dessa forma, os créditos tem que estar todos analisados.": "a3618019de9b698a54573a1c6ad29b78",
#     "Enviar planilha de Saldos por e-mail;": "dce5772615a4691ed22096f514fbf85e",
#     "Lançar tarifa;": "97e29d86712718d6e9eb4319e6cef5bb",
#     "Verificar saldo do dia;": "97e29d86712718d6e9eb4319e6cef5bb",
#     "Fazer analise das centrais;": "6fddc15f138065d0c1444cfe26eee393",
#     "Lançar valores do controle que foram avisados no dia anterior e não foram feitos ainda dentro do molde combinado; Enviar no e-mail valores que não conseguiram identificar o que fazer.": "54f81eaf6d56ff0e9a3693ad03c0ca20" 
# }


# # --- DADOS DA PLANILHA (ATUALIZADO) ---
# data = [
#     # ==========================
#     # --- PERÍODO DA MANHÃ ---
#     # ==========================
    
#     # 09:00
#     ("Mariana", "Planilha de retorno", "Manhã", "Planilha de retorno e analisar todos que estão enviados ao Banco do dia. Mandar no e-mail quando finalizar;", "09:00"),
    
#     # 10:00 - Lançamentos Manuais
#     ("Yasmin", "Lançamentos manuais", "Manhã", "Lançamentos do Bloqueio, desbloqueio, estorno, resgate e aplicação;", "10:00"),
#     ("Brener", "Lançamentos manuais", "Manhã", "Lançamentos do Bloqueio, desbloqueio, estorno, resgate e aplicação;", "10:00"),
#     ("Mariana", "Lançamentos manuais", "Manhã", "Lançamentos do Bloqueio, desbloqueio, estorno, resgate e aplicação;", "10:00"),
    
#     # 10:00 - Sem Sitex
#     ("Yasmin", "Sem Sitex", "Manhã", "Subir as contas sem sitex do dia", "10:00"),
#     ("Brener", "Sem Sitex", "Manhã", "Subir as contas sem sitex do dia", "10:00"),
#     ("Mariana", "Sem Sitex", "Manhã", "Subir as contas sem sitex do dia", "10:00"),
    
#     # 12:00 - Análise de Débitos
#     ("Yasmin", "Analise de débitos", "Manhã", "Analisar débitos. Enviar no meu e-mail as contas que continuaram com erro e estão com dúvidas. Dessa forma, os débitos tem que estar zerado.", "12:00"),
#     ("Brener", "Analise de débitos", "Manhã", "Analisar débitos. Enviar no meu e-mail as contas que continuaram com erro e estão com dúvidas. Dessa forma, os débitos tem que estar zerado.", "12:00"),
#     ("Mariana", "Analise de débitos", "Manhã", "Analisar débitos. Enviar no meu e-mail as contas que continuaram com erro e estão com dúvidas. Dessa forma, os débitos tem que estar zerado.", "12:00"),


#     # ==========================
#     # --- PERÍODO DA TARDE ---
#     # ==========================

#     # 14:00
#     ("Davi", "Recebimentos das centrais", "Tarde", "Fazer analise das centrais;", "14:00"),

#     # 16:00
#     ("Davi", "Contas Sem Sitex", "Tarde", "Lançar tarifa;", "16:00"),
#     ("Brener", "Analise de créditos", "Tarde", "Analisar créditos. Enviar no meu e-mail relatório dos valores que não conseguiram identificar. Dessa forma, os créditos tem que estar todos analisados.", "16:00"),

#     # 17:00 - Relatório de Saldos
#     ("Yasmin", "Relatório de Saldos", "Tarde", "Enviar planilha de Saldos por e-mail;", "17:00"),
#     ("Mariana", "Relatório de Saldos", "Tarde", "Enviar planilha de Saldos por e-mail;", "17:00"),

#     # 18:00 - Lançamento no Controle
#     ("Yasmin", "Lançamento no controle", "Tarde", "Lançar valores do controle que foram avisados no dia anterior e não foram feitos ainda dentro do molde combinado; Enviar no e-mail valores que não conseguiram identificar o que fazer.", "18:00"),
#     ("Brener", "Lançamento no controle", "Tarde", "Lançar valores do controle que foram avisados no dia anterior e não foram feitos ainda dentro do molde combinado; Enviar no e-mail valores que não conseguiram identificar o que fazer.", "18:00"),
#     ("Mariana", "Lançamento no controle", "Tarde", "Lançar valores do controle que foram avisados no dia anterior e não foram feitos ainda dentro do molde combinado; Enviar no e-mail valores que não conseguiram identificar o que fazer.", "18:00"),
    
#     # 18:00 - Outros
#     ("Brener", "Analise de créditos", "Tarde", "Analisar créditos. Enviar no meu e-mail relatório dos valores que não conseguiram identificar. Dessa forma, os créditos tem que estar todos analisados.", "18:00")
# ]
# # Cria o DataFrame
# df = pd.DataFrame(data, columns=["Atendente", "Nome", "Horário", "Mensagem", "Prazo"])


# # --- FUNÇÕES DE CRIAÇÃO DE CHAMADO ---

# def create_ticket(chamado):
#     """Cria o chamado e vincula o atendente na API do TomTicket."""
    
#     atendente = chamado["Atendente"]
#     operator_id = OPERATOR_MAP.get(atendente)
    
#     msg_limpa = chamado["Mensagem"].strip() 
#     category_id = CATEGORY_MAP.get(msg_limpa, "") 

#     if not operator_id:
#         st.error(f"❌ Erro: Atendente **{atendente}** não mapeado para um `operator_id` válido. Verifique `operator_map` no secrets.")
#         return False
        
#     # 1. Criação do Chamado
#     data_ticket = {
#         "customer_id": CUSTOMER_ID,
#         "customer_id_type": "E",
#         "department_id": DEPARTMENT_ID,
#         "subject": chamado["Nome"] + f" ({atendente}) - Prazo: {chamado['Prazo']}",
#         "message": f"{chamado['Mensagem']}\n\nChamado automático gerado às {datetime.now().strftime('%d/%m/%Y %H:%M')}.",
#         "category_id": category_id,
#         "priority": PRIORITY
#     }

#     try:
#         response = requests.post(API_URL, headers=headers, data=data_ticket, timeout=10)
        
#         if response.status_code == 200:
#             resp_json = response.json()
#             if resp_json.get("success"):
#                 ticket_id = resp_json.get("ticket_id") 
                
#                 # 2. Vinculação do Atendente
#                 link_data = {
#                     "ticket_id": ticket_id,
#                     "operator_id": operator_id
#                 }
                
#                 link_response = requests.post(LINK_OPERATOR_URL, headers=headers, data=link_data, timeout=10)
                
#                 if link_response.status_code == 200 and link_response.json().get("success"):
#                     st.success(f"✅ **{chamado['Nome']}** ({atendente}) criado e vinculado com sucesso! ")
#                     return True
#                 else:
#                     st.warning(f"⚠️ **{chamado['Nome']}** ({atendente}) criado, mas erro ao vincular atendente.")
#                     return False
#             else:
#                 st.error(f"❌ Erro na criação de **{chamado['Nome']}** ({atendente}): {resp_json.get('message')}")
#                 return False
#         else:
#             st.error(f"❌ Erro na requisição de criação de **{chamado['Nome']}** ({atendente}): {response.status_code}")
#             return False
            
#     except requests.exceptions.RequestException as e:
#         st.error(f"❌ Erro de conexão ao enviar **{chamado['Nome']}** ({atendente}): {e}")
#         return False


# def run_automation(periodo, chamados_df):
#     """Filtra e executa a criação de chamados para um período (Manhã ou Tarde)."""
#     st.subheader(f"⚙️ Iniciando criação de chamados: **{periodo.upper()}**")
    
#     # Filtra os chamados pelo horário
#     chamados_filtrados = chamados_df[chamados_df["Horário"] == periodo].to_dict('records')
    
#     if not chamados_filtrados:
#         st.info(f"Nenhum chamado encontrado para o período da **{periodo}**.")
#         return

#     st.write(f"**{len(chamados_filtrados)}** chamado(s) a ser(em) criado(s).")
    
#     status_placeholder = st.empty()
    
#     for i, chamado in enumerate(chamados_filtrados):
#         status_placeholder.info(f"Processando {i+1} de {len(chamados_filtrados)}: **{chamado['Nome']}** ({chamado['Atendente']})...")
        
#         create_ticket(chamado)
        
#         # Pausa para evitar sobrecarga da API
#         time.sleep(1.5) 

#     st.balloons()
#     status_placeholder.success(f"🎉 Processo concluído para os chamados da **{periodo}**!")


# # --- INTERFACE STREAMLIT ---

# st.title("🤖 Automação de Chamados Diários (TomTicket)")
# st.caption("Selecione o período para criar automaticamente os chamados e vincular os atendentes.")

# st.markdown("---")

# # Exibe a tabela de referência
# st.subheader("📋 Chamados Programados (Referência)")
# st.dataframe(df, use_container_width=True, hide_index=True)

# st.markdown("---")

# st.header("Criar Chamados Conciliação:")

# col1, col2 = st.columns(2)

# with col1:
#     if st.button("☀️ Rodar Chamados da Manhã", use_container_width=True, type="primary"):
#         st.session_state["executed"] = "Manhã" 
#         run_automation("Manhã", df)

# with col2:
#     if st.button("🌙 Rodar Chamados da Tarde", use_container_width=True, type="secondary"):
#         st.session_state["executed"] = "Tarde"
#         run_automation("Tarde", df)

# st.markdown("---")

# if "executed" in st.session_state:
#     st.subheader(f"Última Execução: Chamados da **{st.session_state['executed']}**")
#     st.info("Verifique os logs acima para o status detalhado de cada chamado.")
# else:
#     st.info("Aguardando seleção de período (Manhã ou Tarde) para iniciar a automação.")
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

# --- CARREGAMENTO SEGURO DOS SECRETS DO STREAMLIT ---
try:
    # --- CONFIGURAÇÕES GERAIS DA API ---
    API_URL = st.secrets["tomticket"]["api_url"]
    LINK_OPERATOR_URL = st.secrets["tomticket"]["link_operator_url"]
    TOKEN = st.secrets["tomticket"]["token"]
    CUSTOMER_ID = st.secrets["tomticket"]["customer_id"]
    DEPARTMENT_ID = st.secrets["tomticket"]["department_id"]
    PRIORITY = 2 
    
    # --- MAPEAMENTO DE ATENDENTES ---
    OPERATOR_MAP = dict(st.secrets["operator_map"])

except KeyError as e:
    st.error(f"❌ Erro ao carregar as chaves do Streamlit Secrets: **{e}**.")
    st.stop() 


# === HEADERS ===
headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# --- MAPEAMENTO DE CATEGORIAS (ATUALIZADO CONFORME PLANILHA) ---
CATEGORY_MAP = {
    "Planilha de retorno e analisar todos que estão enviados ao bando do dia.": "aa426ddcb6b56b8e1c71ed7047ae3487",
    "Lançamentos do bloqueio, desbloqueio, estorno, resgate e aplicação": "54f81eaf6d56ff0e9a3693ad03c0ca20",
    "Analisar débitos. Me informar por e-mail as contas que continuaram com erro ou que estão com dúvidas": "080ed4378a115a19652982ca67ab3f16",
    "Fazer analise das centrais": "6fddc15f138065d0c1444cfe26eee393",
    "Verificar se houveram respostas no forms e realizar o procedimento de verificar documentação": "97e29d86712718d6e9eb4319e6cef5bb",
    "Enviar no meu e-mail relatórios com os valores que não conseguiram identificar": "a3618019de9b698a54573a1c6ad29b78",
    "Lançar no controle valores que foram informados no dia anterior": "54f81eaf6d56ff0e9a3693ad03c0ca20",
    "Envia planilha de Saldo por e-mail": "dce5772615a4691ed22096f514fbf85e",
    "Atualizar as informações necessárias no dia referente a planilha de controle de contas": "97e29d86712718d6e9eb4319e6cef5bb"
}


# --- DADOS DA PLANILHA (IMPORTADOS DO SEU CSV) ---
data = [
    # MANHÃ
    ("Mariana", "Planilha de Retorno", "Manhã", "Planilha de retorno e analisar todos que estão enviados ao bando do dia.", "09:00"),
    ("Yasmin", "Lançamentos Manuais", "Manhã", "Lançamentos do bloqueio, desbloqueio, estorno, resgate e aplicação", "10:00"),
    ("Brener", "Lançamentos Manuais", "Manhã", "Lançamentos do bloqueio, desbloqueio, estorno, resgate e aplicação", "10:00"),
    ("Mariana", "Lançamentos Manuais", "Manhã", "Lançamentos do bloqueio, desbloqueio, estorno, resgate e aplicação", "10:00"),
    ("Yasmin", "Analise de débitos", "Manhã", "Analisar débitos. Me informar por e-mail as contas que continuaram com erro ou que estão com dúvidas", "12:00"),
    ("Brener", "Analise de débitos", "Manhã", "Analisar débitos. Me informar por e-mail as contas que continuaram com erro ou que estão com dúvidas", "12:00"),
    ("Mariana", "Analise de débitos", "Manhã", "Analisar débitos. Me informar por e-mail as contas que continuaram com erro ou que estão com dúvidas", "12:00"),
    
    # TARDE
    ("Davi", "Recebimentos das centrais", "Tarde", "Fazer analise das centrais", "14:00"),
    ("Davi", "Procuração", "Tarde", "Verificar se houveram respostas no forms e realizar o procedimento de verificar documentação", "16:00"),
    ("Yasmin", "Analise de créditos", "Tarde", "Enviar no meu e-mail relatórios com os valores que não conseguiram identificar", "16:00"),
    ("Brener", "Analise de créditos", "Tarde", "Enviar no meu e-mail relatórios com os valores que não conseguiram identificar", "16:00"),
    ("Mariana", "Analise de créditos", "Tarde", "Enviar no meu e-mail relatórios com os valores que não conseguiram identificar", "16:00"),
    ("Yasmin", "Controle", "Tarde", "Lançar no controle valores que foram informados no dia anterior", "17:00"),
    ("Brener", "Controle", "Tarde", "Lançar no controle valores que foram informados no dia anterior", "17:00"),
    ("Mariana", "Controle", "Tarde", "Lançar no controle valores que foram informados no dia anterior", "17:00"),
    ("Brener", "Planilha de Saldo", "Tarde", "Envia planilha de Saldo por e-mail", "17:00"),
    ("Yasmin", "Planilha de controle de conta", "Tarde", "Atualizar as informações necessárias no dia referente a planilha de controle de contas", "17:00")
]

# Cria o DataFrame
df = pd.DataFrame(data, columns=["Atendente", "Nome", "Horário", "Mensagem", "Prazo"])


# --- FUNÇÕES DE CRIAÇÃO DE CHAMADO ---

def create_ticket(chamado):
    """Cria o chamado e vincula o atendente na API do TomTicket."""
    
    atendente = chamado["Atendente"]
    operator_id = OPERATOR_MAP.get(atendente)
    
    msg_limpa = chamado["Mensagem"].strip() 
    category_id = CATEGORY_MAP.get(msg_limpa, "97e29d86712718d6e9eb4319e6cef5bb") # ID padrão se não achar

    if not operator_id:
        st.error(f"❌ Erro: Atendente **{atendente}** não mapeado. Verifique o secrets.")
        return False
        
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
                
                link_data = {
                    "ticket_id": ticket_id,
                    "operator_id": operator_id
                }
                
                link_response = requests.post(LINK_OPERATOR_URL, headers=headers, data=link_data, timeout=10)
                
                if link_response.status_code == 200 and link_response.json().get("success"):
                    st.success(f"✅ **{chamado['Nome']}** ({atendente}) criado!")
                    return True
                else:
                    st.warning(f"⚠️ **{chamado['Nome']}** criado, mas não vinculado.")
                    return False
            else:
                st.error(f"❌ Erro na API: {resp_json.get('message')}")
                return False
        else:
            st.error(f"❌ Erro de conexão: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro: {e}")
        return False


def run_automation(periodo, chamados_df):
    """Filtra e executa a criação de chamados."""
    st.subheader(f"⚙️ Iniciando: **{periodo.upper()}**")
    
    chamados_filtrados = chamados_df[chamados_df["Horário"] == periodo].to_dict('records')
    
    if not chamados_filtrados:
        st.info(f"Nenhum chamado para o período da **{periodo}**.")
        return

    status_placeholder = st.empty()
    
    for i, chamado in enumerate(chamados_filtrados):
        status_placeholder.info(f"Processando {i+1} de {len(chamados_filtrados)}: **{chamado['Nome']}**...")
        create_ticket(chamado)
        time.sleep(1.2) 

    st.balloons()
    status_placeholder.success(f"🎉 Concluído para o período da **{periodo}**!")


# --- INTERFACE STREAMLIT ---

st.title("🤖 Automação TomTicket - Conciliação")
st.markdown("---")

st.subheader("📋 Chamados Programados (Conforme Planilha)")
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("☀️ Rodar Manhã", use_container_width=True, type="primary"):
        run_automation("Manhã", df)

with col2:
    if st.button("🌙 Rodar Tarde", use_container_width=True, type="secondary"):
        run_automation("Tarde", df)