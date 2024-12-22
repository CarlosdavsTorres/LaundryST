import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def main():
    # 1) Carregar variáveis de ambiente
    credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not credentials_json:
        raise ValueError("As credenciais do Google Sheets não foram encontradas nas variáveis de ambiente.")

    credentials_dict = json.loads(credentials_json)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
    gc = gspread.authorize(credentials)

    # 2) Abrir a planilha
    sheet_id = "16cHqwWP3Yy1D4kln5_12vXferPvXwlEJvC79te_4OXw"  # Substituir caso necessário
    sheet = gc.open_by_key(sheet_id).sheet1

    # 3) Preparar dados
    user_message = "Teste Pergunta"
    bot_response = "Teste Resposta"
    time_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # 4) Usar append_row
    sheet.append_row([user_message, bot_response, time_string])

    print("Linha adicionada com sucesso. Verifica a terceira coluna no Google Sheets.")

if __name__ == "__main__":
    main()
