import openai
import streamlit as st
import os
import pandas as pd
from openpyxl import load_workbook

# Nome do ficheiro Excel para armazenar as conversas
EXCEL_FILE = "conversas_lavandaria.xlsx"

# Função para guardar conversas no Excel
def save_to_excel(user_message, bot_response, file):
    try:
        # Tenta carregar o ficheiro Excel existente
        workbook = load_workbook(file)
        sheet = workbook.active
        # Adiciona uma nova linha com a mensagem do usuário e a resposta do bot
        sheet.append([user_message, bot_response])
        workbook.save(file)
    except FileNotFoundError:
        # Cria um novo ficheiro se não existir
        df = pd.DataFrame([[user_message, bot_response]], columns=["Usuário", "Assistente"])
        df.to_excel(file, index=False, engine="openpyxl")

# Carrega as variáveis de ambiente, incluindo a chave de API
# load_dotenv()

# Configura a chave de API do OpenAI
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

# Define a função que interage com a API OpenAI usando o modelo gpt-3.5-turbo
def ask_openai(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are AssistantBot, an automated service that helps clients using our self-service laundry (called bloomest). \
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
                    Begin everytime by saying: Olá, sou o assistente virtual da lavandaria do Campo Alegre! Em que posso ser útil?""" },
                {"role": "user", "content": question}
            ],
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error: {e}"

# Configura o layout do Streamlit
st.title("Assistente Virtual da Lavandaria")

# Botão de download do Excel
if st.button("Descarregar Excel"):
    try:
        with open(EXCEL_FILE, "rb") as f:
            st.download_button(
                label="Descarregar Histórico (Excel)",
                data=f,
                file_name="conversas_lavandaria.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except FileNotFoundError:
        st.error("O ficheiro ainda não foi criado.")

# Botão de teste para criar o ficheiro Excel
if st.button("Criar Ficheiro Excel (Teste)"):
    save_to_excel("Teste Usuário", "Teste Assistente", EXCEL_FILE)
    st.success("Ficheiro Excel criado com sucesso!")


# Inicializa o log de conversa como uma lista vazia e adiciona a mensagem inicial do bot
if 'chat_log' not in st.session_state:
    st.session_state.chat_log = []
    st.session_state.chat_log.append("Assistente: Olá, sou o assistente virtual da lavandaria do Campo Alegre! Em que posso ser útil?")

# Caixa de entrada para a pergunta do usuário
question = st.text_input("Sua Mensagem:", placeholder="Digite sua mensagem aqui...")

# Botão para enviar a pergunta
if st.button("Enviar"):
    if question:
        # Adiciona a pergunta do usuário ao log
        st.session_state.chat_log.append(f"Você: {question}")
        
        # Obtém a resposta do bot e adiciona ao log
        answer = ask_openai(question)
        st.session_state.chat_log.append(f"Assistente: {answer}")
        
        # Salva a conversa no Excel
        save_to_excel(question, answer, EXCEL_FILE)

# Exibe o log de conversa
for message in st.session_state.chat_log:
    st.write(message)
