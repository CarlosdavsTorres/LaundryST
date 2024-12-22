import openai
import streamlit as st
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. Ler as credenciais do ambiente
credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not credentials_json:
    raise ValueError("As credenciais do Google Sheets não foram encontradas nas variáveis de ambiente.")

# 2. Converter o JSON em dict
credentials_dict = json.loads(credentials_json)

# 3. Criar credenciais para o Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
gc = gspread.authorize(credentials)

# 4. Aceder à folha de cálculo pelo ID
SHEET_ID = "16cHqwWP3Yy1D4kln5_12vXferPvXwlEJvC79te_4OXw"  # Substituir com o ID correto
sheet = gc.open_by_key(SHEET_ID).sheet1  # Abre a primeira folha

# 5. Função para salvar Pergunta, Resposta e Data/Hora
def save_to_google_sheets(user_message, bot_response):
    time_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    sheet.append_row([user_message, bot_response, time_string], value_input_option='USER_ENTERED')

# 6. Configurar a API Key do OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("A chave da API OpenAI não foi encontrada nas variáveis de ambiente.")
openai.api_key = api_key

# 7. Função que envia pergunta para o modelo gpt-3.5-turbo
def ask_openai(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are AssistantBot, an automated service that helps clients using our self-service laundry (called bloomest). \
You first greet the customer, then help with the questions, \
and then ask if they need any more help or would still like to contact a real person. \
Know that: The price for washing machines ranges from €4 for small machine to 5€ medium machine and 7,50€ large machine, depending on the size (if you have our membership card is only 3,50€, 4,50€ and 7€ respectively). \
The price for dryers is €2,50 for 20 minutes (if you have our membership card is only 2,20€). \
To use the machines, load the washing machine with your clothes, select program, pay in payment terminal and press start in the washing machine. \
The washing cycle usually takes between 30min to 1h, depending on the selected program (they may take longer than what machine says in the beginning, depending on amount of clothes). \
The operating hours are from 7 AM to 10 PM, every day of the week. \
You respond in a short, very conversational friendly style. \
The only other advantage of the membership card is seeing if machines are available in app. \
Specifically detail every advantage and price reduction of having the membership card if the client asks (there are no special discounts or points to accumulate to exchange for discounts). \
Respond in whichever language the client writes to you (for example, if the client says Ciao, reply in Italian, if they say Hi, reply in English, or if they say Hola, reply in Spanish). \
Begin everytime by saying: Olá, sou o assistente virtual da lavandaria do Campo Alegre! Em que posso ser útil?"""
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error: {e}"

# 8. Layout do Streamlit
st.title("Assistente Virtual da Lavandaria")

# 9. Inicializa o log de conversa (se não existir)
if 'chat_log' not in st.session_state:
    st.session_state.chat_log = []
    # Mensagem inicial do bot
    st.session_state.chat_log.append(
        "Assistente: Olá, sou o assistente virtual da lavandaria do Campo Alegre! Em que posso ser útil?"
    )

# 10. Caixa de entrada de texto
question = st.text_input("Sua Mensagem:", placeholder="Digite sua mensagem aqui...", key="user_input")

# 11. Botão para enviar pergunta
if st.button("Enviar"):
    if question:
        # Adiciona a pergunta do usuário ao log
        st.session_state.chat_log.append(f"Você: {question}")

        # Obtém resposta do modelo
        answer = ask_openai(question)
        st.session_state.chat_log.append(f"Assistente: {answer}")

        # Salvar no Google Sheets
        save_to_google_sheets(question, answer)

# 12. Exibir o log de conversa
for message in st.session_state.chat_log:
    st.write(message)
