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

SHEET_ID = "16cHqwWP3Yy1D4kln5_12vXferPvXwlEJvC79te_4OXw"
sheet = gc.open_by_key(SHEET_ID).sheet1

def save_to_google_sheets(user_message, bot_response):
    """
    Salva a pergunta, a resposta e o timestamp na planilha (colunas A, B e C).
    """
    sheet.append_row([
        user_message,
        bot_response,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

# Configuração da chave da API OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("A chave da API OpenAI não foi encontrada nas variáveis de ambiente.")
openai.api_key = api_key

# Função para interagir com a API OpenAI
def ask_openai(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=300,
            temperature=0.4
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error: {e}"

# Configuração do layout do Streamlit
st.title("Assistente Virtual da Lavandaria")

# Inicializa o histórico de mensagens no session_state
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """You are AssistantBot, an automated service that helps clients using our self-service laundry (called bloomest). \
        You first greet the customer, then help with the questions, \
        and then ask if they need any more help or would still like to contact a real person. \
        Know that: The price for washing machines ranges from €4 for small machine to 5€ medium machine and 7,50€ large machine, depending on the size (if you have our membership card is only 3,50€, 4,50€ and 7€ respectively). \
        The price for dryers is €2,50 for 20 minutes (if you have our membership card is only 2,20€). \
        To use the machines, load the washing machine with your clothes, select program, pay in payment terminal and press start in the washing machine. \
        The washing cycle usually takes between 30min to 1h, depending on the selected program (they may take longer than what machine says in the beginning, depending on amount of clothes). \
        The operating hours are from 7 AM to 10 PM, every day of the week. \
        Respond in a short, very conversational friendly style. \
        The membership card also gives you access to the app, which is used to book a machine, receive vouchers, see machine occupancy. \
        Specifically detail every advantage and price reduction of having the membership card if the client asks. \
        Respond in whichever language the client writes to you."""}
    ]

# Função para processar a mensagem do usuário
def process_message(user_input):
    """
    Processa a mensagem do usuário e gera uma resposta, mantendo memória curta.
    """
    # Adiciona a mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Mantém apenas as últimas 6 mensagens no histórico para memória curta
    memory = st.session_state.messages[-6:]

    # Obtém a resposta do OpenAI
    bot_response = ask_openai(memory)

    # Adiciona a resposta ao histórico
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # Salva no Google Sheets
    save_to_google_sheets(user_input, bot_response)

# Interface principal
with st.form(key="user_input_form"):
    user_input = st.text_input("Sua Mensagem:", placeholder="Digite sua mensagem aqui")
    submitted = st.form_submit_button("Enviar")

# Processa a mensagem quando o formulário é enviado
if submitted and user_input:
    process_message(user_input)

# Exibe o histórico de conversa
for msg in st.session_state.messages:
    role = "Você" if msg["role"] == "user" else "Assistente"
    st.write(f"{role}: {msg['content']}")
