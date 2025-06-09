from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv

# Configurar navegador
opts = Options()
opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")
opts.add_argument("--disable-search-engine-choice-screen")
#opts.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

wait = WebDriverWait(driver, 10)

# Ir a la página inicial
driver.get('https://www.chedraui.com.mx/tecnologia/telefonia/smartphones')
sleep(5)

PAGINACION_MAX = 6
PAGINACION_ACTUAL = 1
productos = []

while PAGINACION_ACTUAL <= PAGINACION_MAX:
    print(f"\n[INFO] Página {PAGINACION_ACTUAL}")
    sleep(3)

    # Obtener todos los enlaces de productos
    enlaces = driver.find_elements(By.XPATH, '//a[contains(@class, "vtex-product-summary-2-x-clearLink")]')
    links_de_la_pagina = list(set([a.get_attribute("href") for a in enlaces if a.get_attribute("href")]))
    print(f"[INFO] {len(links_de_la_pagina)} productos encontrados")

    for link in links_de_la_pagina:
        try:
            driver.get(link)

            # Extraer título
            titulo_elemento = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//h1[contains(@class, "vtex-store-components-3-x-productName")]')
            ))
            titulo = titulo_elemento.text.strip()

            # Extraer precio
            try:
                precio_elemento = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//span[contains(@class, "productPriceSellingContainerQS")]')
                ))
                precio = precio_elemento.text.strip()
            except:
                precio = "Precio no disponible"

            print("Título:", titulo)
            print("Precio:", precio)

            productos.append({
                'titulo': titulo,
                'precio': precio
            })

            sleep(1)
            driver.back()
            sleep(2)

        except Exception as e:
            print("[ERROR] al procesar producto:", e)
            driver.back()
            continue

    # Ir a la siguiente página
    try:
        boton_siguiente = wait.until(EC.element_to_be_clickable(
            (By.XPATH, 'body > div.render-container.render-route-store-search-subcategory > div > div.vtex-store__template.bg-base > div > div:nth-child(7) > div > div > section > div.relative.justify-center.flex > div > div:nth-child(3) > section > div > div:nth-child(2) > div > div:nth-child(6) > div > div > section > a.chedrauimx-frontend-applications-4-x-perPageActive.pointer.white.bn.chedrauimx-frontend-applications-4-x-ButtonNext')
        ))
        boton_siguiente.click()
        PAGINACION_ACTUAL += 1
    except Exception as e:
        print("[INFO] No hay más páginas disponibles o botón no encontrado.")
        break

    sleep(4)

# Guardar en CSV
with open("productos.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["titulo", "precio"])
    writer.writeheader()
    writer.writerows(productos)

print(f"\nSe guardaron {len(productos)} productos en 'productos.csv'")
driver.quit()
