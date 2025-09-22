from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv
import os
import base64
import requests
from selenium.webdriver.chrome.options import Options

driver = webdriver.Chrome()
dados = []

# Cria pasta para salvar imagens
os.makedirs('imagens', exist_ok=True)

import re
import mimetypes
import base64

def salvar_imagem_base64(img_src, nome_base, i):
    try:
        match = re.match(r'data:(image/[^;]+);base64,(.*)', img_src)
        if not match:
            print(f"[ERRO] Formato de imagem inválido no card {i}")
            return "Erro ao extrair base64"

        mime_type = match.group(1)
        base64_data = match.group(2).replace('\n', '').replace('\r', '').replace(' ', '')
        missing_padding = len(base64_data) % 4
        if missing_padding:
            base64_data += '=' * (4 - missing_padding)

        ext = mimetypes.guess_extension(mime_type) or '.jpg'
        nome_arquivo = f"imagens/{nome_base}_{i}{ext}"

        with open(nome_arquivo, 'wb') as f:
            f.write(base64.b64decode(base64_data))

        return nome_arquivo
    except Exception as e:
        print(f"[ERRO] ao salvar imagem base64 do card {i}: {e}")
        return "Erro ao salvar imagem"


try:
    url_desap = 'https://desaparecidos.codata.pb.gov.br/desaparecidos/'
    url_enco = 'https://desaparecidos.codata.pb.gov.br/encontrados'
    options = Options()
    options.add_argument('--headless')  # Executa sem interface gráfica
    options.add_argument('--no-sandbox')  # (Linux, evita erros)

    driver = webdriver.Chrome(options=options)
    driver.get(url_enco)
    time.sleep(30)  # Espera inicial

    cards = driver.find_elements(By.CSS_SELECTOR, 'div.column.is-one-third.custom-card')

    for i, card in enumerate(cards, 1):
        texto = card.text.strip()
        detalhes_extraidos = {}

        # Captura o link da página de detalhes
        try:
            link_element = card.find_element(By.CSS_SELECTOR, 'a.title.is-6')
            href = link_element.get_attribute('href')
        except:
            href = 'Link não encontrado'

        if href != 'Link não encontrado':
            # Abre nova aba
            driver.execute_script("window.open(arguments[0]);", href)
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(5)

            # 🔽 Coleta imagem dentro da página individual
            # try:
            #     img_element = driver.find_element(By.CSS_SELECTOR, 'figure.image img')
            #     img_src = img_element.get_attribute('src')
            #
            #     if img_src:
            #         if img_src.startswith('data:image'):  # imagem embutida em base64
            #             # separa o prefixo 'data:image/jpeg;base64,' do conteúdo
            #             base64_data = img_src.split(',')[1]
            #             base64_data = base64_data.replace('\n', '').replace('\r', '').replace(' ', '')
            #             missing_padding = len(base64_data) % 4
            #             print(f"[DEBUG] Salvando imagem do card {i}")
            #             print(f"[DEBUG] Base64 começa com: {img_src[:30]}")
            #             print(f"[DEBUG] Tamanho base64: {len(base64_data)}")
            #             if missing_padding:
            #                 base64_data += '=' * (4 - missing_padding)
            #             nome_arquivo = f"imagens/pessoa_{i}.jpg"
            #             with open(nome_arquivo, 'wb') as f:
            #                 f.write(base64.b64decode(base64_data))
            #             detalhes_extraidos["imagem_local"] = nome_arquivo
            #         elif "no-picture" not in img_src:  # imagem externa comum
            #             response = requests.get(img_src, stream=True)
            #             if response.status_code == 200:
            #                 nome_arquivo = f"imagens/pessoa_{i}.jpg"
            #                 with open(nome_arquivo, 'wb') as f:
            #                     for chunk in response.iter_content(1024):
            #                         f.write(chunk)
            #                 detalhes_extraidos["imagem_local"] = nome_arquivo
            #             else:
            #                 detalhes_extraidos["imagem_local"] = "Erro ao baixar imagem"
            #         else:
            #             detalhes_extraidos["imagem_local"] = "Sem imagem"
            #     else:
            #         detalhes_extraidos["imagem_local"] = "Sem imagem"
            #
            # except Exception as e:
            #     print(f"Erro ao baixar imagem do card {i}: {e}")
            #     detalhes_extraidos["imagem_local"] = "Erro ao extrair imagem"

            # 🔽 Extrai detalhes da pessoa
            try:
                colunas = driver.find_elements(By.CSS_SELECTOR, 'div.column')
                for col in colunas:
                    try:
                        card_content = col.find_element(By.CSS_SELECTOR, 'div.card-content')
                        tabela = card_content.find_element(By.TAG_NAME, 'table')
                        linhas = tabela.find_elements(By.TAG_NAME, 'tr')

                        for linha in linhas:
                            colunas = linha.find_elements(By.TAG_NAME, 'td')
                            if len(colunas) == 2:
                                chave = colunas[0].text.strip().lower()
                                valor = colunas[1].text.strip()
                                detalhes_extraidos[chave] = valor
                    except:
                        continue
            except Exception as e:
                print('Erro ao extrair os detalhes:', e)

            # Fecha aba e volta
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)

        # Cria dicionário final
        registro = {
            "nome_data_card": texto,
            "link_detalhes": href
        }
        registro.update(detalhes_extraidos)
        dados.append(registro)

finally:
    driver.quit()

# Coleta todos os campos únicos
campos = set()
for d in dados:
    campos.update(d.keys())

# Salva em CSV
with open('csv/encontrados.csv', mode='w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(campos))
    writer.writeheader()
    writer.writerows(dados)

print("✅ Dados e imagens salvos com sucesso!")
