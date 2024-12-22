import openai
import streamlit as st
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Configuração do Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not credentials_json:
    raise ValueError("As credenciais do Google Sheets não foram encontradas nas variáveis de ambiente.")

credentials_dict = json.loads(credentials_json)
credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
gc = gspread.authorize(credentials)

# ID e folha do Google Sheets
SHEET_ID = "16cHqwWP3Yy1D4kln5_12vXferPvXwlEJvC79te_4OXw"
spreadsheet = gc.open_by_key(SHEET_ID)
sheet = spreadsheet.worksheet("Folha1")

# Função para salvar perguntas, respostas e data/hora
def save_to_google_sheets(user_message, bot_response):
    try:
        # Formata a data e hora no formato 'dd/mm/yyyy HH:MM:SS'
        time_string = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        # Adiciona os dados à folha
        new_row = [user_message, bot_response, time_string]
        sheet.append_row(new_row)
    except Exception as e:
        st.error(f"Erro ao salvar no Google Sheets: {e}")

# Configuração do OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("A chave da API OpenAI não foi encontrada nas variáveis de ambiente.")
openai.api_key = api_key

# Função para interação com o ChatGPT
def ask_openai(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """Você é um assistente virtual amigável que ajuda clientes da lavandaria self-service Bloomest."""},
                {"role": "user", "content": question}
            ],
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Erro: {e}"

# Configuração do Streamlit
st.title("Assistente Virtual da Lavandaria")

# Inicializa o log de conversa
if 'chat_log' not in st.session_state:
    st.session_state.chat_log = []
    st.session_state.chat_log.append("Assistente: Olá, sou o assistente virtual da lavandaria do Campo Alegre! Em que posso ajudar?")

# Entrada do usuário
question = st.text_input("Sua Mensagem:", placeholder="Digite sua mensagem aqui...", key="user_input")

# Botão para enviar
if st.button("Enviar"):
    if question:
        # Adiciona a mensagem ao log
        st.session_state.chat_log.append(f"Você: {question}")
        # Obtém a resposta do OpenAI
        answer = ask_openai(question)
        st.session_state.chat_log.append(f"Assistente: {answer}")
        # Salva a conversa no Google Sheets
        save_to_google_sheets(question, answer)

# Exibe o log de conversa
for message in st.session_state.chat_log:
    st.write(message)
