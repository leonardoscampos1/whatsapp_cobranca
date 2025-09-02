import pandas as pd
import requests
import re
import streamlit as st
import openpyxl as xl

# --- CONFIGURAÇÕES ---
URL_API = "https://whatsappcobranca-production.up.railway.app/message/sendText/enviomensagem"
API_KEY = "123456"  # substitua pela sua Global Key
NUMERO_REMETENTE = "5521980210457"  # número da instância registrado e ativo

st.title("📲 Envio de Mensagens de Cobrança")

arquivo = st.file_uploader("Selecione o arquivo Excel", type=["xlsx"])

if arquivo:
    # Lê o Excel sem índice
    df = pd.read_excel(arquivo, engine="openpyxl", dtype=str, index_col=None)
    st.write("Pré-visualização dos dados:")
    st.dataframe(df.head())

    if st.button("Enviar Mensagens"):
        for _, row in df.iterrows():
            cliente = row.get('CLIENTE', 'Cliente')
            
            # Tratamento de datas e valores
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

            # Tratamento do telefone
            numero_dest = str(row.get('TELEFONE', '')).strip()
            numero_dest = re.sub(r"\D", "", numero_dest)
            if not numero_dest.startswith("55"):
                numero_dest = "55" + numero_dest

            # Mensagem formatada
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
                "apikey": API_KEY,
                "Content-Type": "application/json"
            }

            # Envio da mensagem
            try:
                response = requests.post(URL_API, json=payload, headers=headers, timeout=10)

                # Tenta interpretar JSON
                try:
                    result = response.json()
                except ValueError:
                    st.error(f"⚠️ {cliente} ({numero_dest}): Resposta não é JSON. Retorno bruto: {response.text}")
                    continue

                # Checa status
                status = result.get("status", "").upper()
                if status == "PENDING":
                    st.success(f"✅ {cliente} ({numero_dest}): Mensagem enviada! (Status: pendente, confira no app)")
                elif status == "SENT":
                    st.success(f"✅ {cliente} ({numero_dest}): Mensagem enviada com sucesso!")
                else:
                    st.warning(f"⚠️ {cliente} ({numero_dest}): Retorno inesperado - {response.text}")

            except requests.exceptions.HTTPError as errh:
                st.error(f"❌ {cliente} ({numero_dest}): HTTP Error: {errh}")
            except requests.exceptions.ConnectionError as errc:
                st.error(f"❌ {cliente} ({numero_dest}): Connection Error: {errc}")
            except requests.exceptions.Timeout as errt:
                st.error(f"❌ {cliente} ({numero_dest}): Timeout Error: {errt}")
            except Exception as e:
                st.error(f"❌ {cliente} ({numero_dest}): Erro ao enviar - {e}")
