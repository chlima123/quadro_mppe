import pandas as pd
import streamlit as st

BASES_DADOS = {
    "1a Entrancia": "https://portal.mppe.mp.br/documents/d/guest/quadro-geral-membros-mppe-oficial-1-entrancia?download=true",
    "2a Entrancia": "https://portal.mppe.mp.br/documents/d/guest/quadro-geral-membros-mppe-oficial-2-entrancia?download=true",
    "3a Entrancia": "https://portal.mppe.mp.br/documents/d/guest/quadro-geral-membros-mppe-oficial-3-entrancia?download=true",
    "2a Instancia": "https://portal.mppe.mp.br/documents/d/guest/quadro-geral-membros-mppe-oficial-2-instancia-1?download=true",
}
COLUNAS_FILTRO = ["Circunscricao", "Municipio", "Atuacao", "Atribuicao"]
COLUNAS_SAIDA = ["Circunscricao", "Municipio", "Cargo", "Atribuicao", "Atuacao", "Promotor de Justica"]
MAPEAMENTO = {
    "Circunscricao": "Circunscricao",
    "Municipio": "Municipio",
    "Cargo": "Cargo",
    "Atuacao": "Atuacao",
    "Atribuicao": "Atribuicao",
    "Promotor de Justica": "Promotor de Justica",
}


def normalizar_coluna(nome: str) -> str:
    trocas = str.maketrans(
        {
            "á": "a", "à": "a", "â": "a", "ã": "a",
            "é": "e", "ê": "e",
            "í": "i",
            "ó": "o", "ô": "o", "õ": "o",
            "ú": "u",
            "ç": "c",
            "Á": "A", "À": "A", "Â": "A", "Ã": "A",
            "É": "E", "Ê": "E",
            "Í": "I",
            "Ó": "O", "Ô": "O", "Õ": "O",
            "Ú": "U",
            "Ç": "C",
        }
    )
    texto = " ".join(nome.replace("\n", " ").split()).translate(trocas)
    return texto


@st.cache_data(show_spinner=False)
def carregar_dados(url: str) -> pd.DataFrame:
    df = pd.read_excel(url, sheet_name="Quadro Geral")
    df.columns = [normalizar_coluna(col) for col in df.columns]

    for col in COLUNAS_SAIDA:
        if col not in df.columns:
            df[col] = ""

    # Corrige celulas vazias comuns em planilhas com linhas mescladas.
    for col in ["Circunscricao", "Municipio", "Atribuicao", "Atuacao"]:
        if col in df.columns:
            df[col] = df[col].ffill()

    return df


st.set_page_config(page_title="Consulta Quadro Geral MPPE", layout="wide")
st.title("Consulta Eletronica - Quadro Geral MPPE")

base_escolhida = st.selectbox("Quadro", list(BASES_DADOS.keys()))
data_url = BASES_DADOS[base_escolhida]
st.caption(f"Fonte: {base_escolhida}")

try:
    dados = carregar_dados(data_url)
except Exception as exc:
    st.error(f"Nao foi possivel carregar os dados da planilha oficial. Detalhe: {exc}")
    st.stop()

st.subheader("1) Escolha o criterio")
criterios_disponiveis = [c for c in COLUNAS_FILTRO if c in dados.columns]
if not criterios_disponiveis:
    st.warning("Nenhum criterio de consulta disponivel nesta base.")
    st.stop()

criterio = st.radio(
    "Criterio de consulta",
    options=criterios_disponiveis,
    horizontal=True,
)

st.subheader("2) Escolha o valor")
valores = (
    dados[criterio]
    .dropna()
    .astype(str)
    .str.strip()
)
valores = sorted([v for v in valores.unique().tolist() if v and v != "-"])

if not valores:
    st.warning("Nao ha valores disponiveis para o criterio selecionado.")
    st.stop()

valor = st.selectbox(f"Valor de {criterio}", options=valores)

resultado = dados[dados[criterio].astype(str).str.strip() == valor][COLUNAS_SAIDA].copy()
resultado = resultado.rename(columns=MAPEAMENTO)

st.subheader("3) Resultado")
st.caption(f"Registros encontrados: {len(resultado)}")
st.dataframe(resultado, use_container_width=True, hide_index=True)
