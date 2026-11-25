"""Generación del dataset científico en Esperanto.

Extraído de los apartados 0 y 1.1–1.4 del cuaderno de la práctica.
Requiere pandas y requests. Ejecutar con: python generar_dataset.py
Wikipedia puede cambiar: el corpus generado no tiene por qué ser idéntico
al CSV original publicado. El cuaderno reproduce la depuración del original.
"""

import json
import random
import re
import time

import pandas as pd
import requests

SEMILLA = 42
random.seed(SEMILLA)

# ---------------- Parámetros del dataset ----------------
API = "https://eo.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "MT-CUNEF-PracticaEsperanto/1.0 (https://github.com/rodrigocalde/mineria-textos-esperanto; proyecto universitario)"}
ESPERA = 0.5                    # segundos entre peticiones (no sobrecargar el servidor)
REINTENTOS = 5                  # reintentos si Wikipedia responde 429 (demasiadas peticiones)

CATEGORIAS = {                  # clase del dataset -> categoría de Wikipedia en Esperanto
    "fisica": "Fiziko",
    "quimica": "Kemio",
    "biologia": "Biologio",
}
OBJETIVO_POR_CLASE = 350        # el enunciado recomienda más de 300
MAX_SUBCATEGORIAS = 25          # subcategorías exploradas por categoría
MAX_ARTICULOS_POR_CLASE = 400   # artículos que, como máximo, se descargan por clase
MAX_PARRAFOS_POR_ARTICULO = 8   # evita que un artículo largo domine una clase
MIN_CARACTERES = 100            # párrafos más cortos no aportan información
MIN_PALABRAS = 15

def consultar_api(params):
    """Hace una petición GET a la API de Wikipedia y devuelve el JSON, o None si falla.

    Si Wikipedia responde 429 (demasiadas peticiones), espera y lo vuelve a intentar,
    cada vez el doble de tiempo (2, 4, 8, 16... segundos).
    """
    params["format"] = "json"
    params["formatversion"] = 2
    for intento in range(REINTENTOS):
        try:
            respuesta = requests.get(API, params=params, headers=HEADERS, timeout=20)
            time.sleep(ESPERA)
            if respuesta.status_code == 200:
                return respuesta.json()
            if respuesta.status_code == 429:
                retry_after = respuesta.headers.get("Retry-After", "")
                espera = int(retry_after) if retry_after.isdigit() else 2 ** (intento + 1)
                print(f"  429: demasiadas peticiones, esperando {espera} s...")
                time.sleep(espera)
                continue
            print(f"  Aviso: código {respuesta.status_code}")
            return None
        except Exception as error:
            print(f"  Aviso: fallo en la petición ({type(error).__name__})")
            return None
    print("  Aviso: Wikipedia sigue limitando las peticiones, se omite esta consulta")
    return None

EXCLUIR = ["fizikist", "kemiist", "biologoj", "listo", "ŝablon", "vikipedi",
           "premi", "historio", "biografi", "personoj", "organizaĵ"]

def miembros_categoria(categoria):
    """Devuelve (artículos, subcategorías) de una categoría de Wikipedia."""
    datos = consultar_api({
        "action": "query", "list": "categorymembers",
        "cmtitle": "Kategorio:" + categoria,
        "cmtype": "page|subcat", "cmlimit": 500,
    })
    if datos is None:
        return [], []
    articulos, subcategorias = [], []
    for miembro in datos.get("query", {}).get("categorymembers", []):
        titulo = miembro["title"]
        if miembro["ns"] == 0:
            articulos.append(titulo)
        elif miembro["ns"] == 14:
            nombre = titulo.split(":", 1)[1]
            if not any(palabra in nombre.lower() for palabra in EXCLUIR):
                subcategorias.append(nombre)
    return articulos, subcategorias


def articulos_de_clase(categoria):
    """Artículos de la categoría principal y de sus subcategorías (hasta 2 niveles)."""
    articulos, subcategorias = miembros_categoria(categoria)
    for sub in subcategorias[:MAX_SUBCATEGORIAS]:
        nuevos, subsub = miembros_categoria(sub)
        articulos += nuevos
        if len(set(articulos)) < MAX_ARTICULOS_POR_CLASE:   # bajar un nivel solo si faltan artículos
            for sub2 in subsub[:3]:
                articulos += miembros_categoria(sub2)[0]
    return sorted(set(articulos))   # sin repetidos y en orden fijo (reproducible)

SECCIONES_FINALES = ["vidu ankaŭ", "referencoj", "eksteraj ligiloj", "notoj", "fontoj",
                     "literaturo", "bibliografio", "piednotoj"]

def descargar_texto(titulo):
    """Texto plano de un artículo de Wikipedia ('' si falla)."""
    datos = consultar_api({"action": "query", "prop": "extracts",
                           "explaintext": 1, "titles": titulo})
    if datos is None:
        return ""
    paginas = datos.get("query", {}).get("pages", [])
    return paginas[0].get("extract", "") if paginas else ""


def limpiar_parrafo(parrafo):
    parrafo = parrafo.replace(";", ",").replace("\xa0", " ")
    return " ".join(parrafo.split())          # quita espacios repetidos y saltos


def parrafo_valido(parrafo):
    if len(parrafo) < MIN_CARACTERES or len(parrafo.split()) < MIN_PALABRAS:
        return False
    if "\\" in parrafo or "{" in parrafo or "http" in parrafo:   # fórmulas LaTeX o enlaces
        return False
    return "." in parrafo                      # debe contener al menos una frase


def dividir_en_parrafos(texto):
    parrafos = []
    leyendo = True
    for linea in texto.split("\n"):
        if leyendo:
            linea = linea.strip()
            if linea.startswith("=="):
                if linea.strip("= ").lower() in SECCIONES_FINALES:
                    leyendo = False
            else:
                linea = limpiar_parrafo(linea)
                if parrafo_valido(linea):
                    parrafos.append(linea)
    return parrafos

def generar_dataset():
    # 1) Artículos de cada clase
    articulos = {}
    for clase, categoria in CATEGORIAS.items():
        articulos[clase] = articulos_de_clase(categoria)
        print(f"{clase}: {len(articulos[clase])} artículos encontrados")

    # 2) Descartar artículos que están en más de una clase
    todos = [t for lista in articulos.values() for t in lista]
    ambiguos = {t for t in todos if todos.count(t) > 1}
    print(f"Artículos ambiguos descartados: {len(ambiguos)}")

    # 3) Descargar y dividir en párrafos
    filas, vistos = [], set()
    for clase, lista in articulos.items():
        lista = [t for t in lista if t not in ambiguos]
        random.Random(SEMILLA).shuffle(lista)
        cuenta = 0
        for titulo in lista[:MAX_ARTICULOS_POR_CLASE]:
            if cuenta < OBJETIVO_POR_CLASE:
                parrafos = dividir_en_parrafos(descargar_texto(titulo))
                for parrafo in parrafos[:MAX_PARRAFOS_POR_ARTICULO]:
                    if parrafo not in vistos and cuenta < OBJETIVO_POR_CLASE:
                        vistos.add(parrafo)
                        filas.append({"text": parrafo, "class": clase, "articulo": titulo})
                        cuenta += 1
        print(f"  {clase}: {cuenta} párrafos")
    return pd.DataFrame(filas, columns=["text", "class", "articulo"])


if __name__ == "__main__":
    # Se generan archivos nuevos para no sobrescribir el corpus publicado.
    df = generar_dataset()
    recuento = df["class"].value_counts()
    print("\nDistribución del corpus generado:")
    print(recuento)

    if set(recuento.index) == set(CATEGORIAS) and recuento.min() > 300:
        df[["text", "class"]].to_csv(
            "dataset_ciencia_esperanto_generado.csv", sep=";",
            encoding="utf-8", index=False
        )
        # Conservamos el artículo de origen para futuras auditorías.
        df[["text", "class", "articulo"]].to_csv(
            "procedencia_generada.csv", sep=";", encoding="utf-8", index=False
        )
        print("Dataset nuevo y procedencia guardados correctamente.")
    else:
        print("Generación incompleta: no se guardan ni sustituyen los archivos publicados.")
