#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
from selenium import webdriver
import time
####################################################################
# Utilizamos BeatifulSoap para obtener los datos
####################################################################
class DatosComplementariosProducto(object):
    """Clase para obtener datos complementarios del artículo (cantidad neta, ingredientes y análisis nutricional)"""

    def __init__(self, drv_webdriver, url):
        self.cantidad_neta = ''
        self.analisis_nutricional  = '' 
        self.ingredientes = ''  
        self.descripcion_error = ''
        self._webdriver = drv_webdriver
        self._url = url
        
    def obtener_datos_complementarios_producto(self):
        
        #Comprobamos si el webdriver está activo
        try:
            self._webdriver.window_handles
        #except selenium.common.exceptions.InvalidSessionIdException as e:
        except Exception as ex:
            print("El webdriver no está disponible en este momento.", ex)
            return(False)
        
        try:
            self._webdriver.get(self._url)
        except Exception as ex:
            self.descripcion_error = "No ha podido acceder a la URL del producto buscado. " + str(ex)
            print(self.descripcion_error)
            return(False)
        
        time.sleep(1)
        
        soup=BeautifulSoup(self._webdriver.page_source,"lxml")
        #mydivs = soup.findAll("div", {"class": ["col-sm-4"]})
        mydivs = soup.findAll("div", {"role": "contentinfo"})
        
        for elementoDiv in mydivs:
            clase=''.join(elementoDiv.get('class'))

            if (clase=='col-sm-4'):
                html_content = elementoDiv.prettify()
                html_content = html_content.replace("\r","")
                html_content = html_content.replace("\n","")
                #print(elementoDiv.get_text())
                sig_tag_ok = False
                for br in elementoDiv.findAll('br'):
                    next_s = br.nextSibling
                    texto = str(next_s).strip()
                    if sig_tag_ok:
                        #print("La cantidad buscada es:",texto)
                        self.cantidad_neta = texto
                        break
                    pos = texto.find("Cantidad neta")
                    #print(pos, next_s, "::::", texto)
                    if (pos != -1):
                        sig_tag_ok = True

                bloque_nutricional = False
                bloque_ingredientes = False
                for h2 in elementoDiv.findAll('h2'):
                    txth2 = h2.text
                    if (txth2.find('ANÁLISIS NUTRICIONAL') != -1):
                        bloque_nutricional = True
                    if (txth2.find('INGREDIENTES') != -1):
                        bloque_ingredientes = True

                if (bloque_nutricional):

                    texto=elementoDiv.get_text()
                    #print(texto)

                    #Borramos el texto ANALISIS NUTRICIONAL
                    texto=texto.replace("ANÁLISIS NUTRICIONAL","")
                    #localizamos los cambios de parrafo
                    pos=texto.find("\n")

                    texto_simp=texto[:pos]
                    #print(texto_simp)
                    #Ahora una vez que hemos detectado el corte, quitamos todos los saltos de línea.
                    texto_simp = texto_simp.replace("\r",". ")
                    texto_simp = texto_simp.replace("\n",". ")

                    #Localizamos "Energía" que es donde comienza la info nutricional
                    pos_energia=texto_simp.find("Energía")

                    #Localizamos "tamaño" o "cantidad" puesto que viene con estas dos nomenclaturas posibles
                    pos_tamanno=texto_simp.find("Tamaño")
                    if (pos_tamanno==-1):
                        pos_tamanno=texto_simp.find("Cantidad")

                    if (pos_tamanno != -1):
                        #Hemos localizado el texto "Tamaño"
                        if (pos_energia!=-1):
                            #Para los casos en que localice "Tamaño" y "Energía"(habitualmente primero info de tamaño y despues energía)
                            #Imprimimos como tamaño en texto entre la etiqueta "Tamaño" y "Energia"
                            #Imprimimos como análisis nutricional la info que comienza en etiqueta "Energía" hasta el final
                            #print ("->Tamaño: ",texto_simp[pos_tamanno:pos_energia])
                            txt_nutricional = texto_simp[pos_tamanno:pos_energia].strip()
                            if (len(txt_nutricional) > 0):
                                #Comprobar si acaba con punto
                                if (txt_nutricional[-1:] != '.'):
                                    txt_nutricional = txt_nutricional + '.'
                            txt_nutricional = txt_nutricional + ' ' + texto_simp[pos_energia:pos]
                            #print ("->Analisis nutricional: ",texto_simp[pos_tamanno:pos_energia] + '.' + texto_simp[pos_energia:pos])
                            #print("->Análisis nutricional:", txt_nutricional)
                            self.analisis_nutricional = txt_nutricional
                        else:
                            #Si localizamos "Tamaño" pero no "Energia", la info de tamaño es la que comienza en la etiqueta hasta el final.
                            #print ("->Analisis nutricional: ",texto_simp[pos_tamanno:pos])
                            self.analisis_nutricional = texto_simp[pos_tamanno:pos]

                    else:
                        #No hemos localizado el texto "Tamaño"
                        if (pos_energia!=-1):
                            #Si no localizamos "Tamaño" pero sí "Energía": La info nutricional comenzara en etiq "Energia" hasta el final
                            #print ("->Analisis nutricional: ",texto_simp[pos_energia:pos])
                            self.analisis_nutricional = texto_simp[pos_energia:pos]
                        else:
                            #Nos quedamos con todo el párrafo
                            #print (texto_simp)
                            self.analisis_nutricional = texto_simp

                #Bloque de ingredientes
                if (bloque_ingredientes):
                    #Localizamos "Ingredientes" y "consejos"
                    texto=elementoDiv.get_text()
                    #print(texto)
                    pos_ingredientes=texto.find("INGREDIENTES")
                    pos_consejos=texto.find("CONSEJOS")

                    #Quitamos todos los saltos de línea.
                    texto_simp = texto.replace("\r",". ")
                    texto_simp = texto_simp.replace("\n",". ")

                    if (pos_consejos!=-1):
                        #Si existe etiqueta "Consejos", los ingredientes irán desde etiq "Ingredientes" hasta "Consejos"
                        #print ("->Ingredientes: ",texto_simp[pos_ingredientes:pos_consejos].replace('INGREDIENTES',''))
                        self.ingredientes = texto_simp[pos_ingredientes:pos_consejos].replace('INGREDIENTES','')
                    else:
                        #Si no existe etiqueta "consejos" los ingredientes irán hasta el final del textto.
                        #print ("->Ingredientes: ",texto_simp[pos_ingredientes:].replace('INGREDIENTES',''))
                        self.ingredientes = texto_simp[pos_ingredientes:].replace('INGREDIENTES','')

        
        return(True)

