import openai
import streamlit as st
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Configurar autenticação do Google Sheets usando variáveis de ambiente
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not credentials_json:
    raise ValueError("As credenciais do Google Sheets não foram encontradas nas variáveis de ambiente.")

credentials_dict = json.loads(credentials_json)
credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
gc = gspread.authorize(credentials)

# ID da tua folha de cálculo do Google Sheets
SHEET_ID = "16cHqwWP3Yy1D4kln5_12vXferPvXwlEJvC79te_4OXw"  # Substituir pelo ID correto
spreadsheet = gc.open_by_key(SHEET_ID)
sheet = spreadsheet.worksheet("Folha1")  # Acessa a folha chamada "Folha1"

# Função para guardar perguntas, respostas e data/hora da pergunta
def save_to_google_sheets(user_message, bot_response):
    try:
        # Formata a data e hora no formato 'dd/mm/aaaa HH:MM:SS'
        time_string = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        # Adiciona a linha na planilha com as colunas A (pergunta), B (resposta) e C (data/hora)
        new_row = [user_message, bot_response, time_string]
        sheet.insert_row(new_row, index=2)  # Adiciona na segunda linha para evitar sobreposição de cabeçalhos
    except Exception as e:
        st.error(f"Erro ao salvar no Google Sheets: {e}")

# Configura a chave de API do OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("A chave da API OpenAI não foi encontrada nas variáveis de ambiente.")
openai.api_key = api_key

# Define a função que interage com a API OpenAI usando o modelo gpt-3.5-turbo
def ask_openai(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """Você é um assistente virtual amigável que ajuda clientes de uma lavandaria self-service chamada Bloomest. Responda em tom curto, educado e objetivo."""},
                {"role": "user", "content": question}
            ],
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Erro: {e}"

# Configura o layout do Streamlit
st.title("Assistente Virtual da Lavandaria")

# Inicializa o log de conversa como uma lista vazia e adiciona a mensagem inicial do bot
if 'chat_log' not in st.session_state:
    st.session_state.chat_log = []
    st.session_state.chat_log.append("Assistente: Olá, sou o assistente virtual da lavandaria do Campo Alegre! Em que posso ajudar?")

# Caixa de entrada para a pergunta do usuário
question = st.text_input("Sua Mensagem:", placeholder="Digite sua mensagem aqui...", key="user_input")

# Botão para enviar a pergunta
if st.button("Enviar"):
    if question:
        # Adiciona a pergunta do usuário ao log
        st.session_state.chat_log.append(f"Você: {question}")

        # Obtém a resposta do bot e adiciona ao log
        answer = ask_openai(question)
        st.session_state.chat_log.append(f"Assistente: {answer}")

        # Salva a conversa no Google Sheets (pergunta, resposta e hora/dia)
        save_to_google_sheets(question, answer)

# Exibe o log de conversa
for message in st.session_state.chat_log:
    st.write(message)
