import requests
from bs4 import BeautifulSoup
import json
import os

# URL objetivo
URL = "https://es.wiktionary.org/wiki/Especial:Todas/%C3%89"

# Ruta del archivo de salida
OUTPUT_FILE = "Output_data/wikcionario_el_chido.json"


def obtener_html(url):
    """
    Envía una solicitud GET a la URL y devuelve el contenido HTML.
    """
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        return respuesta.text
    else:
        raise Exception(f"Error al acceder a la página: {respuesta.status_code}")


def parsear_palabras_y_significados(html):
    """
    Parsea el contenido HTML usando BeautifulSoup y extrae palabras con sus significados.
    Solo incluye palabras que comienzan con 'É'.
    """
    soup = BeautifulSoup(html, "html.parser")
    resultado = []

    # Buscar el contenedor principal de las palabras
    contenedor = soup.find("div", class_="mw-allpages-body")

    if not contenedor:
        raise Exception("No se encontró el contenedor principal de palabras")

    # Cada palabra está en un <li>
    elementos = contenedor.find_all("li")

    for li in elementos:
        enlace = li.find("a")
        if enlace:
            palabra = enlace.text.strip()

            # Filtro: solo palabras que empiezan con "É"
            if palabra.startswith("É"):
                link_palabra = "https://es.wiktionary.org" + enlace["href"]

                # Obtener la definición
                definicion = obtener_definicion(link_palabra)

                resultado.append({
                    "palabra": palabra,
                    "significado": definicion
                })

    return resultado


def obtener_definicion(url_palabra):
    """
    Accede a la página individual de una palabra y extrae la primera definición en <dd>.
    """
    try:
        html = obtener_html(url_palabra)
        soup = BeautifulSoup(html, "html.parser")

        definicion = soup.find("dd")
        if definicion:
            return definicion.text.strip()
        else:
            return "Definición no encontrada"

    except Exception as e:
        return f"Error al obtener definición: {e}"


def guardar_json(data, archivo):
    """
    Guarda los datos en formato JSON. Evita duplicados basados en la palabra.
    """
    existentes = []

    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            existentes = json.load(f)

    palabras_existentes = set(item["palabra"] for item in existentes)
    nuevos_unicos = [item for item in data if item["palabra"] not in palabras_existentes]

    total = existentes + nuevos_unicos

    # Asegurar carpeta de salida
    os.makedirs(os.path.dirname(archivo), exist_ok=True)

    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(total, f, indent=2, ensure_ascii=False)


def main():
    print("Obteniendo HTML de Wikcionario...")
    html = obtener_html(URL)

    print("Extrayendo palabras que comienzan con É...")
    datos = parsear_palabras_y_significados(html)

    print(f"Total extraído: {len(datos)}")
    guardar_json(datos, OUTPUT_FILE)
    print(f"Datos guardados en: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
