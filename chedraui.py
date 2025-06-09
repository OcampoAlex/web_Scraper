

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import csv

# Definimos el User Agent en Selenium utilizando la clase Options
opts = Options()
opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")
opts.add_argument("--disable-search-engine-choice-screen")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

# URL inicial
driver.get('https://www.chedraui.com.mx/tecnologia/telefonia/smartphones')

# Esperar a que cargue para que pueda cargar el DOM de la pagina y se puedan seleccionar los elementos de html
sleep(3) 

# Configuración de paginación
PAGINACION_MAX = 6
PAGINACION_ACTUAL = 1

# Lista para almacenar los productos
productos = []

# Lógica de scraping por páginas
while PAGINACION_MAX >= PAGINACION_ACTUAL:

    print(f"\n[INFO] Página {PAGINACION_ACTUAL}")

    # Obtener todos los enlaces de productos en la página
    links_productos = driver.find_elements(By.XPATH, '/html/body/div[2]/div/div[1]/div/div[3]/div/div/section/div[2]/div/div[3]/section/div/div[2]/div/div[5]/div/div/div[1]')
    links_de_la_pagina = [a.get_attribute("href") for a in links_productos]

    # Visitar cada producto y extraer datos
    for link in links_de_la_pagina:
        sleep(2)
        try:
            driver.get(link)
            titulo = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/div/div/div[3]/div/div[1]/div/section/div/div/div/div[2]/div/div/div[2]/div/div[2]/h1/span[2]').text
            precio = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/div/div/div[3]/div/div[1]/div/section/div/div/div/div[2]/div/div/div[3]/div/div[1]/div/div/div/div/div[2]/section/div/section/div[1]/div[1]/span/span').text
            precio = precio.replace('\n', '').replace('\t', '')
            print("Título:", titulo)
            print("Precio:", precio)

            # Guardar datos en lista
            productos.append({
                'titulo': titulo,
                'precio': precio
            })

            driver.back()
        except Exception as e:
            print("Error al procesar producto:", e)
            driver.back()

    # Intentar ir a la siguiente página
    try:
        siguiente = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/div[4]/div/div/section/div[2]/div/div[3]/section/div/div[2]/div/div[6]/div/div/section/a[2]')
        siguiente.click()
    except:
        print("[INFO] No hay más páginas disponibles.")
        break

    PAGINACION_ACTUAL += 1
    sleep(2)

# Guardar en CSV
nombre_archivo = 'productos.csv'
with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['titulo', 'precio'])
    writer.writeheader()
    writer.writerows(productos)

print(f"Se guardaron {len(productos)} productos en '{nombre_archivo}'.")

# Cerrar navegador
driver.quit()
