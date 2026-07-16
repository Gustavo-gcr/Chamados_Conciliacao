# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

# --- CARREGAMENTO SEGURO DOS SECRETS DO STREAMLIT ---
try:
    API_URL = st.secrets["tomticket"]["api_url"]
    LINK_OPERATOR_URL = st.secrets["tomticket"]["link_operator_url"]
    TOKEN = st.secrets["tomticket"]["token"]
    CUSTOMER_ID = st.secrets["tomticket"]["customer_id"]
    DEPARTMENT_ID = st.secrets["tomticket"]["department_id"]
    PRIORITY = 2

    # --- MAPEAMENTO DE ATENDENTES (Nome -> operator_id do TomTicket) ---
    OPERATOR_MAP = dict(st.secrets["operator_map"])
except KeyError as e:
    st.error(f"❌ Erro ao carregar as chaves do Streamlit Secrets: **{e}**.")
    st.stop()

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# --- MAPEAMENTO DE CATEGORIAS ---
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
DEFAULT_CATEGORY_ID = "97e29d86712718d6e9eb4319e6cef5bb"

# --- DADOS PADRÃO DA PLANILHA ---
DEFAULT_DATA = [
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

COLUNAS = ["Atendente", "Nome", "Horário", "Mensagem", "Prazo"]

# --- ESTADO: a lista de chamados fica editável em session_state ---
if "df_chamados" not in st.session_state:
    st.session_state["df_chamados"] = pd.DataFrame(DEFAULT_DATA, columns=COLUNAS)


# --- FUNÇÕES DE CRIAÇÃO DE CHAMADO ---
def create_ticket(chamado):
    """Cria o chamado e vincula o atendente na API do TomTicket."""

    atendente = chamado["Atendente"]
    operator_id = OPERATOR_MAP.get(atendente)

    msg_limpa = str(chamado["Mensagem"]).strip()
    category_id = CATEGORY_MAP.get(msg_limpa, DEFAULT_CATEGORY_ID)

    if not operator_id:
        st.error(f"❌ Erro: Atendente **{atendente}** não mapeado. Verifique o secrets.")
        return False

    data_ticket = {
        "customer_id": CUSTOMER_ID,
        "customer_id_type": "E",
        "department_id": DEPARTMENT_ID,
        "subject": str(chamado["Nome"]) + f" ({atendente}) - Prazo: {chamado['Prazo']}",
        "message": f"{msg_limpa}\n\nChamado automático gerado às {datetime.now().strftime('%d/%m/%Y %H:%M')}.",
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


def validar_chamados(chamados_df):
    """Valida a lista antes de enviar. Retorna lista de erros."""
    erros = []
    for idx, row in chamados_df.iterrows():
        linha = idx + 1
        if pd.isna(row["Atendente"]) or str(row["Atendente"]).strip() == "":
            erros.append(f"Linha {linha}: sem atendente selecionado.")
        elif row["Atendente"] not in OPERATOR_MAP:
            erros.append(f"Linha {linha}: atendente **{row['Atendente']}** não está no operator_map do secrets.")
        if pd.isna(row["Nome"]) or str(row["Nome"]).strip() == "":
            erros.append(f"Linha {linha}: sem nome do chamado.")
        if pd.isna(row["Mensagem"]) or str(row["Mensagem"]).strip() == "":
            erros.append(f"Linha {linha}: sem mensagem.")
        if row["Horário"] not in ("Manhã", "Tarde"):
            erros.append(f"Linha {linha}: horário deve ser Manhã ou Tarde.")
    return erros


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

# ==========================================================
# TABELA EDITÁVEL: adicionar, editar e excluir chamados
# ==========================================================
st.subheader("📋 Chamados Programados (edite antes de enviar)")
st.caption(
    "✏️ Clique na célula para editar • ➕ Use a última linha (vazia) para adicionar um novo chamado • "
    "🗑️ Selecione a linha (checkbox à esquerda) e pressione **Delete** para excluir."
)

df_editado = st.data_editor(
    st.session_state["df_chamados"],
    num_rows="dynamic",          # permite adicionar e excluir linhas
    use_container_width=True,
    hide_index=True,
    key="editor_chamados",
    column_config={
        "Atendente": st.column_config.SelectboxColumn(
            "Atendente",
            help="Selecione o atendente (o ID do TomTicket é pego automaticamente do secrets)",
            options=sorted(OPERATOR_MAP.keys()),
            required=True,
        ),
        "Nome": st.column_config.TextColumn("Nome do Chamado", required=True),
        "Horário": st.column_config.SelectboxColumn(
            "Período",
            options=["Manhã", "Tarde"],
            required=True,
        ),
        "Mensagem": st.column_config.SelectboxColumn(
            "Mensagem",
            help="Escolha uma mensagem mapeada (define a categoria automaticamente). Mensagens fora da lista usam a categoria padrão.",
            options=sorted(CATEGORY_MAP.keys()),
            required=True,
        ),
        "Prazo": st.column_config.TextColumn("Prazo", help="Ex: 09:00", required=True),
    },
)

# Guarda as edições no estado (persiste entre reruns)
st.session_state["df_chamados"] = df_editado

col_reset, col_info = st.columns([1, 3])
with col_reset:
    if st.button("↩️ Restaurar lista padrão", use_container_width=True):
        st.session_state["df_chamados"] = pd.DataFrame(DEFAULT_DATA, columns=COLUNAS)
        st.rerun()
with col_info:
    manha = int((df_editado["Horário"] == "Manhã").sum())
    tarde = int((df_editado["Horário"] == "Tarde").sum())
    st.info(f"Total: **{len(df_editado)}** chamado(s) — ☀️ Manhã: **{manha}** | 🌙 Tarde: **{tarde}**")

st.markdown("---")

# --- VALIDAÇÃO + EXECUÇÃO ---
erros = validar_chamados(df_editado)
if erros:
    st.error("Corrija os problemas abaixo antes de enviar:")
    for e in erros:
        st.markdown(f"- {e}")

col1, col2 = st.columns(2)
with col1:
    if st.button("☀️ Rodar Manhã", use_container_width=True, type="primary", disabled=bool(erros)):
        run_automation("Manhã", df_editado)
with col2:
    if st.button("🌙 Rodar Tarde", use_container_width=True, type="secondary", disabled=bool(erros)):
        run_automation("Tarde", df_editado)