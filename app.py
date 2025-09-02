import pandas as pd
import requests
import re
import streamlit as st
import openpyxl as xl
# --- Configurações ---
url = r"https://whatsappcobranca-production.up.railway.app//message/sendText/enviomensagem"
api_key = "123456"
numero_remetente = "5521980210457"  # sua instância

st.title("📲 Envio de Mensagens de Cobrança")

arquivo = st.file_uploader("Selecione o arquivo Excel", type=["xlsx"])

if arquivo:
    #não trazer o ind
    df = pd.read_excel(arquivo, engine="openpyxl", dtype=str, index_col=None)

    st.write("Pré-visualização dos dados:")
    st.dataframe(df.head())

    if st.button("Enviar Mensagens"):
        for _, row in df.iterrows():
            cliente = row.get('CLIENTE', 'Cliente')
            emissao = pd.to_datetime(row.get('EMISSÃO')).strftime('%d/%m/%Y')
            nf = row.get('NF', '')
            valor = f"R$ {float(row.get('VALOR', 0)):.2f}".replace('.', ',')
            vencimento = pd.to_datetime(row.get('VENCIMENTO')).strftime('%d/%m/%Y')
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
                "number": numero_dest,  # <--- Corrigido: envia para o número do cliente
                "textMessage": {"text": mensagem}
            }

            headers = {
                "apikey": api_key,
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(url, json=payload, headers=headers)
                result = response.json()

                status = result.get("status", "").upper()

                if status == "PENDING":
                    st.success(f"✅ {cliente}: Mensagem enviada! (Status: pendente, confira no app)")
                elif status == "SENT":
                    st.success(f"✅ {cliente}: Mensagem enviada com sucesso!")
                else:
                    st.warning(f"⚠️ {cliente}: Retorno inesperado - {response.text}")

            except Exception as e:
                st.error(f"❌ {cliente}: Erro ao enviar - {e}")


