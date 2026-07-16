# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime
import time

st.set_page_config(page_title="Automação TomTicket", page_icon="🤖", layout="wide")

# ==========================================================
# SECRETS
# ==========================================================
try:
    API_URL = st.secrets["tomticket"]["api_url"]
    LINK_OPERATOR_URL = st.secrets["tomticket"]["link_operator_url"]
    TOKEN = st.secrets["tomticket"]["token"]
    CUSTOMER_ID = st.secrets["tomticket"]["customer_id"]
    DEPARTMENT_ID = st.secrets["tomticket"]["department_id"]
    PRIORITY = 2
    OPERATOR_MAP = dict(st.secrets["operator_map"])  # Nome -> operator_id do TomTicket
except KeyError as e:
    st.error(f"❌ Erro ao carregar as chaves do Streamlit Secrets: **{e}**.")
    st.stop()

headers = {"Authorization": f"Bearer {TOKEN}"}

# ==========================================================
# CATEGORIAS (Mensagem -> category_id)
# ==========================================================
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

# ==========================================================
# PERSISTÊNCIA EM ARQUIVO (as alterações ficam salvas para os próximos meses)
# ==========================================================
ARQUIVO_CHAMADOS = "chamados_config.json"

DEFAULT_CHAMADOS = [
    {"Atendente": "Mariana", "Nome": "Planilha de Retorno", "Horário": "Manhã", "Mensagem": "Planilha de retorno e analisar todos que estão enviados ao bando do dia.", "Prazo": "09:00"},
    {"Atendente": "Yasmin",  "Nome": "Lançamentos Manuais", "Horário": "Manhã", "Mensagem": "Lançamentos do bloqueio, desbloqueio, estorno, resgate e aplicação", "Prazo": "10:00"},
    {"Atendente": "Brener",  "Nome": "Lançamentos Manuais", "Horário": "Manhã", "Mensagem": "Lançamentos do bloqueio, desbloqueio, estorno, resgate e aplicação", "Prazo": "10:00"},
    {"Atendente": "Mariana", "Nome": "Lançamentos Manuais", "Horário": "Manhã", "Mensagem": "Lançamentos do bloqueio, desbloqueio, estorno, resgate e aplicação", "Prazo": "10:00"},
    {"Atendente": "Yasmin",  "Nome": "Analise de débitos", "Horário": "Manhã", "Mensagem": "Analisar débitos. Me informar por e-mail as contas que continuaram com erro ou que estão com dúvidas", "Prazo": "12:00"},
    {"Atendente": "Brener",  "Nome": "Analise de débitos", "Horário": "Manhã", "Mensagem": "Analisar débitos. Me informar por e-mail as contas que continuaram com erro ou que estão com dúvidas", "Prazo": "12:00"},
    {"Atendente": "Mariana", "Nome": "Analise de débitos", "Horário": "Manhã", "Mensagem": "Analisar débitos. Me informar por e-mail as contas que continuaram com erro ou que estão com dúvidas", "Prazo": "12:00"},
    {"Atendente": "Davi",    "Nome": "Recebimentos das centrais", "Horário": "Tarde", "Mensagem": "Fazer analise das centrais", "Prazo": "14:00"},
    {"Atendente": "Davi",    "Nome": "Procuração", "Horário": "Tarde", "Mensagem": "Verificar se houveram respostas no forms e realizar o procedimento de verificar documentação", "Prazo": "16:00"},
    {"Atendente": "Yasmin",  "Nome": "Analise de créditos", "Horário": "Tarde", "Mensagem": "Enviar no meu e-mail relatórios com os valores que não conseguiram identificar", "Prazo": "16:00"},
    {"Atendente": "Brener",  "Nome": "Analise de créditos", "Horário": "Tarde", "Mensagem": "Enviar no meu e-mail relatórios com os valores que não conseguiram identificar", "Prazo": "16:00"},
    {"Atendente": "Mariana", "Nome": "Analise de créditos", "Horário": "Tarde", "Mensagem": "Enviar no meu e-mail relatórios com os valores que não conseguiram identificar", "Prazo": "16:00"},
    {"Atendente": "Yasmin",  "Nome": "Controle", "Horário": "Tarde", "Mensagem": "Lançar no controle valores que foram informados no dia anterior", "Prazo": "17:00"},
    {"Atendente": "Brener",  "Nome": "Controle", "Horário": "Tarde", "Mensagem": "Lançar no controle valores que foram informados no dia anterior", "Prazo": "17:00"},
    {"Atendente": "Mariana", "Nome": "Controle", "Horário": "Tarde", "Mensagem": "Lançar no controle valores que foram informados no dia anterior", "Prazo": "17:00"},
    {"Atendente": "Brener",  "Nome": "Planilha de Saldo", "Horário": "Tarde", "Mensagem": "Envia planilha de Saldo por e-mail", "Prazo": "17:00"},
    {"Atendente": "Yasmin",  "Nome": "Planilha de controle de conta", "Horário": "Tarde", "Mensagem": "Atualizar as informações necessárias no dia referente a planilha de controle de contas", "Prazo": "17:00"},
]


def carregar_chamados():
    """Carrega os chamados do arquivo JSON. Se não existir, cria com o padrão."""
    if os.path.exists(ARQUIVO_CHAMADOS):
        try:
            with open(ARQUIVO_CHAMADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    salvar_chamados(DEFAULT_CHAMADOS)
    return list(DEFAULT_CHAMADOS)


def salvar_chamados(chamados):
    """Salva a lista no arquivo JSON (persiste para os próximos meses)."""
    with open(ARQUIVO_CHAMADOS, "w", encoding="utf-8") as f:
        json.dump(chamados, f, ensure_ascii=False, indent=2)


if "chamados" not in st.session_state:
    st.session_state["chamados"] = carregar_chamados()


# ==========================================================
# API TOMTICKET
# ==========================================================
def create_ticket(chamado):
    atendente = chamado["Atendente"]
    operator_id = OPERATOR_MAP.get(atendente)
    msg_limpa = str(chamado["Mensagem"]).strip()
    category_id = CATEGORY_MAP.get(msg_limpa, DEFAULT_CATEGORY_ID)

    if not operator_id:
        st.error(f"❌ Atendente **{atendente}** não mapeado no secrets.")
        return False

    data_ticket = {
        "customer_id": CUSTOMER_ID,
        "customer_id_type": "E",
        "department_id": DEPARTMENT_ID,
        "subject": f"{chamado['Nome']} ({atendente}) - Prazo: {chamado['Prazo']}",
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
                link_data = {"ticket_id": ticket_id, "operator_id": operator_id}
                link_response = requests.post(LINK_OPERATOR_URL, headers=headers, data=link_data, timeout=10)
                if link_response.status_code == 200 and link_response.json().get("success"):
                    st.success(f"✅ **{chamado['Nome']}** ({atendente}) criado!")
                    return True
                st.warning(f"⚠️ **{chamado['Nome']}** criado, mas não vinculado.")
                return False
            st.error(f"❌ Erro na API: {resp_json.get('message')}")
            return False
        st.error(f"❌ Erro de conexão: {response.status_code}")
        return False
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro: {e}")
        return False


def run_automation(periodo):
    chamados = [c for c in st.session_state["chamados"] if c["Horário"] == periodo]
    if not chamados:
        st.info(f"Nenhum chamado para o período da **{periodo}**.")
        return
    barra = st.progress(0, text=f"Iniciando período da {periodo}...")
    for i, chamado in enumerate(chamados):
        barra.progress((i + 1) / len(chamados), text=f"Processando {i+1}/{len(chamados)}: {chamado['Nome']} ({chamado['Atendente']})")
        create_ticket(chamado)
        time.sleep(1.2)
    barra.progress(1.0, text="Concluído!")
    st.balloons()
    st.success(f"🎉 Concluído para o período da **{periodo}**!")


# ==========================================================
# FORMULÁRIO (usado para adicionar e editar)
# ==========================================================
def formulario_chamado(chamado=None, key_prefix="novo"):
    """Renderiza o formulário. Retorna dict com os valores ou None."""
    padrao = chamado or {}
    atendentes = sorted(OPERATOR_MAP.keys())

    col_a, col_b = st.columns(2)
    with col_a:
        atendente = st.selectbox(
            "👤 Atendente",
            atendentes,
            index=atendentes.index(padrao["Atendente"]) if padrao.get("Atendente") in atendentes else 0,
            key=f"{key_prefix}_atendente",
            help="O ID do TomTicket é vinculado automaticamente pelo nome."
        )
    with col_b:
        turno = st.selectbox(
            "🕑 Turno",
            ["Manhã", "Tarde"],
            index=0 if padrao.get("Horário", "Manhã") == "Manhã" else 1,
            key=f"{key_prefix}_turno",
        )

    col_c, col_d = st.columns(2)
    with col_c:
        nome = st.text_input("📌 Nome do chamado", value=padrao.get("Nome", ""), key=f"{key_prefix}_nome")
    with col_d:
        prazo = st.text_input("⏰ Prazo (ex: 09:00)", value=padrao.get("Prazo", "09:00"), key=f"{key_prefix}_prazo")

    mensagem = st.text_area(
        "💬 Mensagem",
        value=padrao.get("Mensagem", ""),
        key=f"{key_prefix}_msg",
        height=120,
        placeholder="Escreva a mensagem do chamado...",
    )

    return {
        "Atendente": atendente,
        "Nome": nome.strip(),
        "Horário": turno,
        "Mensagem": mensagem.strip(),
        "Prazo": prazo.strip(),
    }


# ==========================================================
# POP-UP DE GERENCIAMENTO
# ==========================================================
@st.dialog("📋 Chamados Programados", width="large")
def dialog_gerenciar():
    modo = st.session_state.get("modo_dialog", "lista")

    # ---------- MODO LISTA ----------
    if modo == "lista":
        if st.button("➕ Adicionar novo chamado", type="primary", use_container_width=True):
            st.session_state["modo_dialog"] = "adicionar"
            st.rerun(scope="fragment")

        st.markdown("")
        for periodo, emoji in [("Manhã", "☀️"), ("Tarde", "🌙")]:
            itens = [(i, c) for i, c in enumerate(st.session_state["chamados"]) if c["Horário"] == periodo]
            st.markdown(f"#### {emoji} {periodo} — {len(itens)} chamado(s)")
            if not itens:
                st.caption("Nenhum chamado neste período.")
            for i, c in itens:
                with st.container(border=True):
                    col_info, col_edit, col_del = st.columns([8, 1, 1])
                    with col_info:
                        st.markdown(f"**{c['Nome']}** &nbsp;·&nbsp; 👤 {c['Atendente']} &nbsp;·&nbsp; ⏰ {c['Prazo']}")
                        st.caption(c["Mensagem"])
                    with col_edit:
                        if st.button("✏️", key=f"edit_{i}", help="Editar este chamado"):
                            st.session_state["modo_dialog"] = "editar"
                            st.session_state["idx_editando"] = i
                            st.rerun(scope="fragment")
                    with col_del:
                        if st.button("🗑️", key=f"del_{i}", help="Excluir este chamado"):
                            st.session_state["chamados"].pop(i)
                            salvar_chamados(st.session_state["chamados"])
                            st.rerun()  # rerun completo: atualiza a página toda

        st.markdown("---")
        if st.button("↩️ Restaurar lista padrão", use_container_width=True):
            st.session_state["chamados"] = list(DEFAULT_CHAMADOS)
            salvar_chamados(st.session_state["chamados"])
            st.rerun()  # rerun completo: atualiza a página toda

    # ---------- MODO ADICIONAR ----------
    elif modo == "adicionar":
        st.markdown("#### ➕ Novo chamado")
        valores = formulario_chamado(key_prefix="novo")
        col_s, col_v = st.columns(2)
        with col_s:
            if st.button("💾 Salvar", type="primary", use_container_width=True):
                if not valores["Nome"] or not valores["Mensagem"]:
                    st.error("Informe o nome e a mensagem do chamado.")
                else:
                    st.session_state["chamados"].append(valores)
                    salvar_chamados(st.session_state["chamados"])
                    st.session_state["modo_dialog"] = "lista"
                    st.rerun()  # rerun completo: atualiza a página toda
        with col_v:
            if st.button("← Voltar", use_container_width=True):
                st.session_state["modo_dialog"] = "lista"
                st.rerun(scope="fragment")

    # ---------- MODO EDITAR ----------
    elif modo == "editar":
        idx = st.session_state.get("idx_editando")
        if idx is None or idx >= len(st.session_state["chamados"]):
            st.session_state["modo_dialog"] = "lista"
            st.rerun(scope="fragment")
        chamado = st.session_state["chamados"][idx]
        st.markdown(f"#### ✏️ Editando: **{chamado['Nome']}**")
        valores = formulario_chamado(chamado, key_prefix=f"edit{idx}")
        col_s, col_x, col_v = st.columns(3)
        with col_s:
            if st.button("💾 Salvar alterações", type="primary", use_container_width=True):
                if not valores["Nome"] or not valores["Mensagem"]:
                    st.error("Informe o nome e a mensagem do chamado.")
                else:
                    st.session_state["chamados"][idx] = valores
                    salvar_chamados(st.session_state["chamados"])
                    st.session_state["modo_dialog"] = "lista"
                    st.rerun()  # rerun completo: atualiza a página toda
        with col_x:
            if st.button("🗑️ Excluir", use_container_width=True):
                st.session_state["chamados"].pop(idx)
                salvar_chamados(st.session_state["chamados"])
                st.session_state["modo_dialog"] = "lista"
                st.rerun()  # rerun completo: atualiza a página toda
        with col_v:
            if st.button("← Voltar", use_container_width=True):
                st.session_state["modo_dialog"] = "lista"
                st.rerun(scope="fragment")


# ==========================================================
# PÁGINA PRINCIPAL
# ==========================================================
st.title("🤖 Automação TomTicket — Conciliação")
st.caption("Os chamados ficam salvos automaticamente: as alterações valem para os próximos meses.")

chamados = st.session_state["chamados"]
qtd_manha = sum(1 for c in chamados if c["Horário"] == "Manhã")
qtd_tarde = sum(1 for c in chamados if c["Horário"] == "Tarde")

m1, m2, m3 = st.columns(3)
m1.metric("📋 Total de chamados", len(chamados))
m2.metric("☀️ Manhã", qtd_manha)
m3.metric("🌙 Tarde", qtd_tarde)

st.markdown("")
if st.button("⚙️ Gerenciar chamados programados", type="primary", use_container_width=True):
    st.session_state["modo_dialog"] = "lista"
    dialog_gerenciar()

st.markdown("---")
st.subheader("🚀 Enviar chamados")
col1, col2 = st.columns(2)
with col1:
    if st.button(f"☀️ Rodar Manhã ({qtd_manha})", use_container_width=True):
        run_automation("Manhã")
with col2:
    if st.button(f"🌙 Rodar Tarde ({qtd_tarde})", use_container_width=True):
        run_automation("Tarde")

with st.expander("👁️ Ver lista completa (resumo)"):
    st.dataframe(
        pd.DataFrame(chamados, columns=["Atendente", "Nome", "Horário", "Mensagem", "Prazo"]),
        use_container_width=True,
        hide_index=True,
    )