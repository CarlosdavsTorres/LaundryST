import os
import json
import openai
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime

# ==============================
# 1. Autenticação Google Sheets
# ==============================
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not credentials_json:
    raise ValueError("As credenciais do Google Sheets não foram encontradas nas variáveis de ambiente.")

credentials_dict = json.loads(credentials_json)
credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
gc = gspread.authorize(credentials)

# ID da planilha
SHEET_ID = "16cHqwWP3Yy1D4kln5_12vXferPvXwlEJvC79te_4OXw"
sheet = gc.open_by_key(SHEET_ID).sheet1

def save_to_google_sheets(user_message, bot_response):
    """Registra user_message (coluna A), bot_response (coluna B)
    e a data/hora (coluna C) na planilha do Google Sheets."""
    try:
        sheet.append_row([
            user_message,
            bot_response,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
    except Exception as e:
        # Se houver um erro ao salvar, mostra aviso mas não quebra a aplicação
        st.warning(f"Não foi possível salvar no Google Sheets: {e}")

# ======================
# 2. Autenticação OpenAI
# ======================
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("A chave da API OpenAI não foi encontrada nas variáveis de ambiente.")
openai.api_key = api_key

# =========================
# 3. Função de chamada OpenAI
# =========================
def ask_openai(messages):
    """Envia todo o histórico (messages) ao modelo gpt-3.5-turbo
    e retorna a resposta do assistant."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Erro ao chamar OpenAI: {e}"

# ======================
# 4. Início da aplicação
# ======================
st.title("Assistente Virtual da Lavandaria")

# Caso use Streamlit anterior ao 1.26 (sem suporte a st.chat_message),
# comente as duas funções "display_chat_messages" e "add_chat_message"
# e volte a usar o `for message in st.session_state.messages:` e `st.write(...)`.

def display_chat_messages(messages):
    """Exibe as mensagens do histórico com componentes de chat do Streamlit."""
    for msg in messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(msg["content"])
        else:
            # Mensagens de 'system' não costumam ser mostradas ao usuário
            pass

def add_chat_message(role, content):
    """Adiciona mensagem ao histórico na sessão e exibe imediatamente."""
    st.session_state.messages.append({"role": role, "content": content})

# Se não existir "messages" na sessão, cria com a primeira mensagem do assistant
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": """You are AssistantBot, an automated service that helps clients using our self-service laundry (called bloomest). 
You first greet the customer, then help with the questions, 
and then ask if they need any more help or would still like to contact a real person. 
Know that: The price for washing machines ranges from €4 for small machine to 5€ medium machine and 7,50€ large machine, depending on the size (if you have our membership card is only 3,50€, 4,50€ and 7€ respectively). 
The price for dryers is €2,50 for 20 minutes (if you have our membership card is only 2,20€). 
To use the machines, load the washing machine with your clothes, select program, pay in payment terminal and press start in the washing machine. 
The washing cycle usually takes between 30min to 1h, depending on the selected program (they may take longer than what machine says in the beginning, depending on amount of clothes). 
The operating hours are from 7 AM to 10 PM, every day of the week. 
You respond in a short, very conversational friendly style. 
The only other advantage of the membership card is seeing if machines are available in app. 
Specifically detail every advantage and price reduction of having the membership card if the client asks (there are no special discounts or points to accumulate to exchange for discounts). 
Respond in whichever language the client writes to you (for example, if the client says Ciao, reply in Italian, if they say Hi, reply in English, or if they say Hola, reply in Spanish). 
Begin everytime by saying: Olá, sou o assistente virtual da lavandaria do Campo Alegre! Em que posso ser útil?"""
        },
        {
            "role": "assistant",
            "content": "Olá, sou o assistente virtual da lavandaria do Campo Alegre! Em que posso ser útil?"
        }
    ]

# Exibe o histórico de conversa já existente
display_chat_messages(st.session_state.messages)

# Caixa de input para a pergunta do usuário
question = st.text_input("Sua Mensagem:", placeholder="Digite sua mensagem aqui...")

# Botão para enviar
if st.button("Enviar"):
    if question.strip():
        # Adiciona a mensagem do usuário ao histórico
        add_chat_message("user", question)

        # Chama a OpenAI com todo o histórico
        assistant_reply = ask_openai(st.session_state.messages)

        # Adiciona resposta do assistant ao histórico
        add_chat_message("assistant", assistant_reply)

        # Salva no Google Sheets (pergunta, resposta e data/hora)
        save_to_google_sheets(question, assistant_reply)

# Se quiser visualizar o histórico como texto simples (para debug):
# st.write(st.session_state.messages)
