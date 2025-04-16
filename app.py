import streamlit as st
import pandas as pd
import os
from io import BytesIO

ARQUIVO_ESTOQUE = 'estoque.csv'

def carregar_dados():
    if os.path.exists(ARQUIVO_ESTOQUE):
        return pd.read_csv(ARQUIVO_ESTOQUE)
    else:
        return pd.DataFrame(columns=["Item", "Quantidade", "Valor_Unitário", "Valor_Total"])

def salvar_dados(df):
    df.to_csv(ARQUIVO_ESTOQUE, index=False)

def registrar_entrada(df):
    st.subheader("📥 Entrada de Itens")
    item = st.text_input("Nome do item")
    quantidade = st.number_input("Quantidade", min_value=1, step=1)
    valor_unitario = st.number_input("Valor unitário (R$)", min_value=0.0, format="%.2f")

    if st.button("Registrar Entrada"):
        valor_total = quantidade * valor_unitario
        if item in df["Item"].values:
            df.loc[df["Item"] == item, "Quantidade"] += quantidade
            df.loc[df["Item"] == item, "Valor_Unitário"] = valor_unitario
            df.loc[df["Item"] == item, "Valor_Total"] = df["Quantidade"] * df["Valor_Unitário"]
        else:
            df = pd.concat([df, pd.DataFrame([[item, quantidade, valor_unitario, valor_total]],
                                             columns=df.columns)], ignore_index=True)
        salvar_dados(df)
        st.success(f"{quantidade} unidades de '{item}' registradas com sucesso.")
    return df

def registrar_saida(df):
    st.subheader("📤 Saída de Itens")
    itens = df["Item"].tolist()
    if not itens:
        st.warning("Nenhum item cadastrado.")
        return df

    item = st.selectbox("Selecione o item", itens)
    quantidade = st.number_input("Quantidade a retirar", min_value=1, step=1)

    if st.button("Registrar Saída"):
        estoque_atual = df.loc[df["Item"] == item, "Quantidade"].values[0]
        if quantidade > estoque_atual:
            st.error(f"Estoque insuficiente. Disponível: {estoque_atual}")
        else:
            df.loc[df["Item"] == item, "Quantidade"] -= quantidade
            df.loc[df["Item"] == item, "Valor_Total"] = df["Quantidade"] * df["Valor_Unitário"]
            salvar_dados(df)
            st.success(f"{quantidade} unidades de '{item}' retiradas com sucesso.")
    return df

def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Estoque')
    output.seek(0)
    return output

def exibir_relatorio(df):
    st.subheader("📊 Relatório de Saldo")
    if df.empty:
        st.info("Nenhum item cadastrado ainda.")
    else:
        st.dataframe(df)
        excel_data = gerar_excel(df)
        st.download_button(
            label="⬇️ Baixar Relatório em Excel",
            data=excel_data,
            file_name="relatorio_estoque.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def main():
    st.title("📦 Sistema de Estoque Logístico")
    menu = st.sidebar.radio("Menu", ["Registrar Entrada", "Registrar Saída", "Relatório de Saldo"])
    df = carregar_dados()

    if menu == "Registrar Entrada":
        df = registrar_entrada(df)
    elif menu == "Registrar Saída":
        df = registrar_saida(df)
    elif menu == "Relatório de Saldo":
        exibir_relatorio(df)

if __name__ == "__main__":
    main()
