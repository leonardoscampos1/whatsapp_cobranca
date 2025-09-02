import pandas as pd
import requests
import re
import streamlit as st
import openpyxl as xl

# --- Configurações ---
url = "https://whatsappcobranca-production.up.railway.app//message/sendText/enviomensagem"
api_key = "123456"
numero_remetente = "5521980210457"  # sua instância

st.title("📲 Envio de Mensagens de Cobrança")

arquivo = st.file_uploader("Selecione o arquivo Excel", type=["xlsx"])

if arquivo:
    # Não trazer o índice
    df = pd.read_excel(arquivo, engine="openpyxl", dtype=str, index_col=None)

    st.write("Pré-visualização dos dados:")
    st.dataframe(df.head())

    if st.button("Enviar Mensagens"):
        for _, row in df.iterrows():
            cliente = row.get('CLIENTE', 'Cliente')
            try:
                emissao = pd.to_datetime(row.get('EMISSÃO')).strftime('%d/%m/%Y')
            except:
                emissao = "N/A"
            nf = row.get('NF', '')
            try:
                valor = f"R$ {float(row.get('VALOR', 0)):.2f}".replace('.', ',')
            except:
                valor = "R$ 0,00"
            try:
                vencimento = pd.to_datetime(row.get('VENCIMENTO')).strftime('%d/%m/%Y')
            except:
                vencimento = "N/A"
            vendedor = row.get('VENDEDOR', '')
            obs = row.get('OBS', '')
            filial = row.get('FILIAL', '')

            numero_dest = str(row.get('TELEFONE', '')).strip()
            numero_dest = re.sub(r"\D", "", numero_dest)
            if not numero_dest.startswith("55"):
                numero_dest = "55" + numero_dest

            mensagem = (
                f"Olá {cliente}*.\n"
                f"Segue nota *{nf}* de *{valor}* com vencimento em *{vencimento}*.\n"
                f"Emitida em *{emissao}*.\n"
                f"Seu vendedor é *{vendedor}*.\n"
                f"Observação: *{obs}*, filial: *{filial}*"
            )

            payload = {
                "number": numero_dest,
                "textMessage": {"text": mensagem}
            }

            headers = {
                "apikey": api_key,
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                try:
                    data = response.json()
                    st.success(f"✅ {cliente} {numero_dest}: Mensagem enviada com sucesso")
                except ValueError:
                    st.warning(f"⚠️ {cliente} {numero_dest}: Resposta não é JSON. Retorno: {response.text}")
            except requests.exceptions.HTTPError as errh:
                st.error(f"❌ {cliente} {numero_dest}: HTTP Error: {errh}")
            except requests.exceptions.ConnectionError as errc:
                st.error(f"❌ {cliente} {numero_dest}: Connection Error: {errc}")
            except requests.exceptions.Timeout as errt:
                st.error(f"❌ {cliente} {numero_dest}: Timeout Error: {errt}")

