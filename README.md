# Clasificación de textos científicos en Esperanto

Práctica de Minería de Textos — CUNEF — Curso 2026/2027.

## Integrantes

- Álvaro Aguilar
- Rodrigo Calderón
- Ignacio Fernández

## Objetivo

Desarrollar un sistema de clasificación automática de textos científicos en Esperanto en tres categorías: Física, Química y Biología.

## Dataset

| Categoría | Párrafos originales | Párrafos definitivos |
|---|---:|---:|
| Física | 350 | 326 |
| Química | 350 | 350 |
| Biología | 350 | 329 |
| Total | 1050 | 1005 |

Formato CSV, separador punto y coma y codificación UTF-8.

## Metodología

1. Obtención automática de textos mediante la API de Wikipedia.
2. Limpieza y depuración del dataset.
3. Desarrollo de un modelo NLP propio basado en reglas lingüísticas.
4. Vectorización mediante TF-IDF.
5. Entrenamiento de Naive Bayes y Regresión Logística.
6. Evaluación mediante accuracy, F1 macro, matriz de confusión y validación cruzada.
7. Clasificación de páginas web mediante web scraping.

## Resultados

- 30 de 30 pruebas lingüísticas superadas.
- Accuracy media en validación cruzada de Naive Bayes: 91,42 %.
- Accuracy media en validación cruzada de Regresión Logística: 90,93 %.
- Tres de cuatro páginas web clasificadas según la categoría esperada.
- Comparación de la clasificación de páginas completas frente a párrafos individuales.

## Reproducibilidad

El cuaderno está diseñado para ejecutarse de forma autónoma en Google Colab, sin necesidad de GPU ni de subir archivos manualmente.

Se utiliza una semilla aleatoria fija de 42 y una copia integrada del dataset original para recuperarlo ante fallos de conexión con GitHub.

## Procedencia y licencia de los datos

Los textos proceden de Wikipedia en Esperanto (https://eo.wikipedia.org/), cuyos autores son sus colaboradores.

Los textos han sido modificados mediante procesos de selección, limpieza, etiquetado y depuración.

Licencia general de los textos reutilizados: Creative Commons Attribution-ShareAlike 4.0 International (https://creativecommons.org/licenses/by-sa/4.0/).

Queda pendiente recuperar la relación exacta de artículos originales para completar su atribución individual.
