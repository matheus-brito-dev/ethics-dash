import pandas as pd

desaparecidos = pd.read_csv("csv/desaparecidos.csv", dtype="str")
encontrados = pd.read_csv("csv/encontrados.csv", dtype="str")




def padronizar_campos(desaparecidos, encontrados):
    for df in [desaparecidos, encontrados]:
        df.columns = df.columns.str.strip().str.lower()
        df["cpf"] = df["cpf"].astype(str).str.strip()
        df["cpf"] = df["cpf"].str.replace(r"\D", "", regex=True)
        df["cpf"] = df["cpf"].replace(["", "nan"], pd.NA)
    # Remove duplicatas por CPF após limpeza
    encontrados = encontrados.drop_duplicates(subset="cpf", keep="first")
    return desaparecidos, encontrados

def converter_datas(encontrados):
    encontrados["data do fato ocorrido"] = pd.to_datetime(encontrados["data do fato ocorrido"], errors='coerce')
    encontrados["data momento registro pessoa encontrada"] = pd.to_datetime(
        encontrados["data momento registro pessoa encontrada"], errors='coerce'
    )
    return encontrados

def preencher_campos_nulo(encontrados):
    encontrados["pessoa foi encontrada"] = encontrados["pessoa foi encontrada"].fillna("Não")
    encontrados["encontrado"] = encontrados["pessoa foi encontrada"].str.lower().eq("sim").astype(int)
    return encontrados

def juntar_dfs(desaparecidos, encontrados):
    dados_integrados = pd.merge(
        desaparecidos,
        encontrados[
            ["cpf", "data do fato ocorrido", "data momento registro pessoa encontrada",
             "pessoa foi encontrada", "descricao como foi encontrado", "encontrado"]
        ],
        on="cpf",
        how="left"
    )

    dados_integrados["pessoa foi encontrada"] = dados_integrados["pessoa foi encontrada"].fillna("Não")
    dados_integrados["encontrado"] = dados_integrados["encontrado"].fillna(0).astype(int)

    dados_integrados = dados_integrados.drop_duplicates(subset="cpf")

    dados_integrados.to_csv("desaparecidos_integrado_limpo.csv", index=False)
    return dados_integrados

# Executar o pipeline ETL
# desaparecidos, encontrados = padronizar_campos(desaparecidos, encontrados)
# encontrados = converter_datas(encontrados)
# encontrados = preencher_campos_nulo(encontrados)
# dados_integrados = juntar_dfs(desaparecidos, encontrados)
