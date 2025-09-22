import pandas as pd


base_final = pd.read_csv("csv/base_publica_desaparecidos.csv", dtype="str")


# Percentual de campos nulos por coluna
percentuais_nulos = base_final.isna().mean().sort_values(ascending=False) * 100
print(percentuais_nulos)

# Contar CPFs faltando
#print("CPFs faltando:", base_final["cpf"].isna().sum())
