import pandas as pd
import numpy as np
from datetime import datetime

# Carregar o CSV original
df = pd.read_csv("csv/desaparecidos_integrado_limpo.csv")
coluna_data_fato = 'data do fato ocorrido_x'

def calcular_dias_desaparecido(data_str):
    try:
        # Converte com suporte a timezone
        data_evento = pd.to_datetime(data_str, utc=True, errors='coerce')
        if pd.isnull(data_evento):
            return None
        hoje = pd.Timestamp(datetime.now(), tz="UTC")
        return (hoje - data_evento).days
    except Exception as e:
        return None

# Função para extrair faixa etária da idade
def extrair_faixa_etaria(idade_str):
    try:
        idade = int(str(idade_str).split()[0])
        if idade < 12:
            return '0-11'
        elif idade < 18:
            return '12-17'
        elif idade < 30:
            return '18-29'
        elif idade < 45:
            return '30-44'
        elif idade < 60:
            return '45-59'
        else:
            return '60+'
    except:
        return 'Não informado'

# Cópia da base original
df_anon = df.copy()

# Gerar ID numérico
df_anon['id'] = np.arange(1, len(df_anon) + 1)

# Calcular faixa etária
df_anon['faixa_etaria'] = df_anon['idade'].apply(extrair_faixa_etaria)

# Selecionar colunas não identificáveis
df_publica = df_anon[[
    'id',
    'faixa_etaria',
    'sexo',
    'uf nascimento',
    'municipio nascimento',
    'bairro',
    'cor dos olhos',
    'cabelo',
    'estava acompanhada',
    'estado civil',
    'nome da cidade onde ocorreu o fato',
    'data do fato ocorrido_x',
    'encontrado'
]].rename(columns={
    'uf nascimento': 'estado',
    'municipio nascimento': 'cidade',
    'cor dos olhos': 'cor_olhos',
    'cabelo': 'tipo_cabelo',
    'estava acompanhada': 'estava_acompanhada',
    'estado civil': 'estado_civil',
    'nome da cidade onde ocorreu o fato':'cidade_desaparecimento',
    'data do fato ocorrido_x':'data_ocorrido_desaparecimento'

})

# Criar campo fictício de tempo desaparecido (já que não temos data)
df_anon['tempo_desaparecido_dias'] = df_anon[coluna_data_fato].apply(calcular_dias_desaparecido)
df_publica['tempo_desaparecido_dias'] = df_anon['tempo_desaparecido_dias']


# Reordenar colunas
df_publica = df_publica[[
    'id', 'faixa_etaria', 'sexo', 'estado', 'cidade', 'bairro',
    'tempo_desaparecido_dias', 'cor_olhos', 'tipo_cabelo',
    'estava_acompanhada', 'estado_civil', 'cidade_desaparecimento', 'data_ocorrido_desaparecimento',
    'encontrado'
]]
df_publica['cidade_desaparecimento'] = df_publica['cidade_desaparecimento'].fillna('Desconhecido')
df_publica['tempo_desaparecido_dias'] = df_publica['tempo_desaparecido_dias'].fillna(-1)
df_publica['data_ocorrido_desaparecimento'] = df_publica['data_ocorrido_desaparecimento'].fillna('Desconhecido')

# Salvar como CSV anonimizado
df_publica.to_csv("base_publica_desaparecidos.csv", index=False)

print("Arquivo 'base_publica_desaparecidos.csv' gerado com sucesso!")
