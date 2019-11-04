#!/usr/bin/env python
# coding: utf-8


import zipfile
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
import sys
from pathlib import Path
import pandas as pd
from selenium.webdriver.support.ui import Select

print('Iniciando Scraper')
driver = webdriver.Chrome(executable_path=r'C:\Chromedriver\chromedriver.exe')
#Antes de nada vamos a listar el fichero "robots.txt"
driver.get('http://gadisline.com/robots.txt')
robots_txt = driver.find_element_by_xpath("//body")
print("==================================================")
print("=        CONTENIDO DEL FICHERO ROBOTS.TXT        =")
print("==================================================")
print(robots_txt.text)
print("==================================================")
#Abrimos la URL deseada, en nuestro caso gadisline.com
driver.get('http://gadisline.com')

# La página tiene un botón de aceptar las cookies, que vamos a simular que aceptamos para que desaparezca de ahí
try:
    botonAceptar = driver.find_element_by_id('removecookie')
    botonAceptar.click()
except:
    pass


#Vamos a simular que escribimos directamente en la caja del código postal.
#Aunque realmente esto no va a llegar a funcionar, ya que es necesario pasar por el desplegable de códigos postales.
#En este caso simulamos que introducimos el valor de 15001 para la caja del código postal.
cajaCP = driver.find_element_by_class_name("select2-selection__placeholder")
driver.execute_script('arguments[0].innerHTML = "15001";', cajaCP)


#Simulamos que vamos a introducir el código postal
elementoSeleccionCP = driver.find_element_by_id('cl_postal_code')
elementoSeleccionCP = driver.find_element_by_id('cl_postal_code')
elementoSeleccionCP.send_keys ("")
elementoSeleccionCP.send_keys(Keys.RETURN)

#Para poder seleccionar el valor dentro del combobox, creamos un Select del propio combo, que luego nos 
#permite usar el método "select_by_value". En este caso escogemos el código postal 15002
valorCP = Select(driver.find_element_by_id('cl_postal_code'))
valorCP.select_by_value("15002")

#Una vez seleccionado el código postal, tenemos que simular la pulsación del botón naranja "CONTINUAR >"
botonContinuar = driver.find_element_by_class_name('btn.principal_btn.btn_new_client.ladda-button').click()

print("Entrando en la página de Gadisline donde se encuentran los precios...")

#Temporizamos 3 segundos para dar tiempo a cargar la siguiente página
time.sleep(3)


#Ahora hay un menú por categorías de productos al que podemos pinchar para acceder a los productos
#ultramarinos
a=driver.find_element_by_xpath("//a[@id='a-11']")
driver.execute_script("arguments[0].click();", a)
#azucar/edulcorantes
a=driver.find_element_by_xpath("//a[@id='level2_0']")
driver.execute_script("arguments[0].click();", a)
#azucar
a=driver.find_element_by_xpath("//a[@id='child-111010']")
driver.execute_script("arguments[0].click();", a)
#producto
#a=driver.find_element_by_xpath("//a[@id='5410079']")
#driver.execute_script("arguments[0].click();", a)

# Hemos sido capaces de pichar en:
#  - Ultramarinos
#    - Azúcar / edulcorantes
#      - Azúcar
# Y en este momento estamos ya en una página con una serie de artículos

print("La nueva dirección URL donde nos encontramos es:",driver.current_url)






