# Retail_Scraping
Este proyecto realiza una extracción limitada de información de la web gadisline.com. Se extraen precios, información nutricional e  ingredientes para una categoria seleccionada por el usuario.

En una primera fase se escanea toda la estructura de productos ofertados y permite seleccionar una categoría en la que profundizar y obtener información más detallada. Esto es, nos permite descargar todos los productos de la categoría seleccionada detallando su precio, precio unitario, cantidad neta, la url de acceso y la url que obtiene su imagen. También se obtiene la información nutricional del producto y sus ingredientes.
Finalmente se ha desarrollado un histórico de precios, donde se almacenarán los precios descargados de la categoría seleccionada con la fecha actual, permitiendo actualizaciones diarias.

**Las librerías necesarias son las siguientes:

from selenium import webdriver

import time

import pandas as pd

import numpy as np

from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import Select

from datetime import datetime

import sys

from datetime import datetime

import os

from pathlib import Path

from bs4 import BeautifulSoup

from pathlib import Path

import requests

from urllib.request import Request, urlopen

**Para proceder a su ejecución :
 - Es preciso para la correcta ejecución de este proyecto, localizar el archivo chromedriver.exe que se puede encontrar en la carpeta Chromedriver de este proyecto en la ruta local
c:\Chromedriver

 - Verificar que se tienen instaladas las librerías indicadas anteriormente.
 
 - Ejecutar python Retail_Scraping.py

NOTA: Se recomienda inicialmente la ejecución sobre una categoría con un número moderado de elementos. Por ejemplo, Panadería.

![menu]Chromedriver/(Chromedriver/pantallazo menu.PNG)

**Como resultado se obtienen 5 datasets con la siguiente estructura. Ver wiki para más información.
	

