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
url_pag_menu = driver.current_url
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
time.sleep(2)



#Un aspecto importante es poder ver que user-agent estamos utilizando y ver si es adecuado el cambio
#Realmente al usar el chromedriver estamos simulando como que una persona está usando un navegador Chrome visitando páginas
agent = driver.execute_script("return navigator.userAgent")
print("=====================================================================================================")
print("El user-agent utilizado es:\n",agent,sep='')
print("=====================================================================================================")




# Recorrer el arbol de todas las categorías/subcategorías (3 niveles) de productos
# Hemos visto que podemos navegar por el menú de categorías simulando un click de en el menú
# Pero hemos visto que en la página donde está el menú podemos obtener todo el árbol completo.

# Para ello volvemos a la página del menú
driver.back()
if (driver.current_url != url_pag_menu):
    driver.get(url_pag_menu)


#Vamos a crear un pandas DataFrame donde vamos a obtenemos una estructura de 3 niveles, con las categorías de los productos
#Cada nivel L3 contiene una URL que nos lleva a la página donde se encuentran los productos de esa categoría.
#Por ejemplo una categoría es la siguiente:
#  Nivel1 = Lácteos
#    Nivel2 = Yogures
#      Nivel3 = Yogur con frutas 
#         Una vez llegamos a este Nivel3, obtenemos una URL 
#         (concretamente https://www.gadisline.com/listado-de-productos/?idListProd=131317) que contiene los productos
#         asociados con ese nivel

elementos_tabla = 0
N1 = 0
N2 = 0
N3 = 0
txtN1 = ''
txtN2 = ''
txtN3 = ''

df = pd.DataFrame(columns=['N1','N2','N3','Nivel1','Nivel2','Nivel3', 'URL', 'NumArticulos','UltActualizacion'])


# Marcamos el tiempo de inicio
tInicio = datetime.now()

#Accedemos al menú, a través del elemento padre:
#  - Podemos hacerlo con: driver.find_element_by_class_name("acc-menu.col-xs-10.col-sm-10.labels")
#  - Podemos hacerlo con: driver.find_element_by_xpath("//div[@class='acc-menu col-xs-10 col-sm-10 labels']")

#parentElement = driver.find_element_by_class_name("acc-menu.col-xs-10.col-sm-10.labels")
#parentElement = driver.find_element_by_class_name("menu_category_container")
elementoPadreMenu = driver.find_element_by_xpath("//div[@class='acc-menu col-xs-10 col-sm-10 labels']")

#Una vez localizado el elemento padre del menú, buscamos los tag "div" que cuelgan de él
elementList_div = elementoPadreMenu.find_elements_by_tag_name("div")

#Recorremos los elementos "div" que cuelgan del MenúPadre
for elemento_div in elementList_div:
    clase_div = elemento_div.get_attribute('class')
    
    #Nos interesan los elementos div cuya clase "col-xs-12 category-wrapper"
    if (clase_div == 'col-xs-12 category-wrapper'):
        #Si solo quiero un nivel
        #elementList_a = elemento_div.find_element_by_tag_name("a")
        #print (elementList_a.get_attribute('text'))
        
        #Una vez encontrado cada elemento "div" de clase = "col-xs-12 category-wrapper" buscamos 
        #los tag <a> ya que en ellos se encuentran los diferentes niveles (del 1 al 3)
        
        elementList_a = elemento_div.find_elements_by_tag_name("a")
        for elemento_a in elementList_a:
            #El nivel se obtiene leyendo el atributo "data-ga_action" de los tags encontrados
            nivel = elemento_a.get_attribute('data-ga_action')
            url_link = ''
            if (nivel == 'nivel 1'):
                print('(L1) +--->', end='')
                texto = elemento_a.get_attribute('text')
                txtN1 = texto
                N1 += 1
            elif (nivel == 'nivel 2'):
                print('   (L2) +--->', end='')
                texto = elemento_a.get_attribute('text')
                txtN2 = texto
                N2 += 1
            elif (nivel == 'nivel 3'):
                # En el nivel 3 aparte del texto que obtenemos en los otros niveles, tenemos un link a esa categoría
                print('      (L3) +--->', end='')
                texto = elemento_a.get_attribute('aria-label')
                txtN3 = texto
                url_link = elemento_a.get_attribute('href')
                texto = texto + ' [ ' + url_link + ' ]'
                N3 += 1
                df.loc[elementos_tabla] = N1,N2,N3,txtN1,txtN2,txtN3,url_link,0,                                           datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                elementos_tabla += 1
            else:
                print('----------')
            print (texto)
            
# Marcamos el tiempo de fin
tFin = datetime.now()

texto = 'Hemos invertido {:4.2f} segundos en obtener {:d} categorías (de 3 niveles)' .format((tFin-tInicio).total_seconds(), df.shape[0])
print(texto)


