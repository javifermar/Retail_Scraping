#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
from datetime import datetime
import sys

class AccesoGadisline(object):
    """Clase para acceder a la página de categorías y productos"""
    def __init__(self, drv_webdriver, url):
        self._webdriver = drv_webdriver
        self._url = url
        self.descripcion_error = '' # Descripción de error
        self.contenido_robots = ''  # Contenido del robots.txt
        self.url_menu = ''          # La URL que obtiene de acceso al menú (donde están las categorías)
        
    def obtener_contenido_robots(self):
        print(self._webdriver)
        #Comprobamos si el webdriver está activo
        
        try:
            self._webdriver.window_handles
        
        #except selenium.common.exceptions.InvalidSessionIdException as e:
        except Exception as ex:
            print("El webdriver no está disponible en este momento.", ex)
            return(False)
        
        urlrobots = self._url + '/robots.txt'
        self._webdriver.get(urlrobots)
        
        self._webdriver.get(urlrobots)
        try:
            robots_txt = self._webdriver.find_element_by_xpath("//body")
            self.contenido_robots = robots_txt.text

            return(self.contenido_robots)
        except Exception as ex:
            self.descripcion_error = "Error al intentar obtener el texto de 'robots.txt'" + ex
            #print("Error al intentar obtener el texto de 'robots.txt'", ex)
            return(self.descripcion_error)
    
    ###############################################################################################
    #
    ###############################################################################################
    def acceso_inicial(self):
        #Abrimos la URL deseada, en nuestro caso gadisline.com
        self._webdriver.get(self._url)

        # La página tiene un botón de aceptar las cookies, que vamos a simular que aceptamos para que desaparezca de ahí
        try:
            botonAceptar = self._webdriver.find_element_by_id('removecookie')
            botonAceptar.click()
        except:
            pass

        
        try:
            #Vamos a simular que escribimos directamente en la caja del código postal.
            #Aunque realmente esto no va a llegar a funcionar, ya que es necesario pasar por el 
            # desplegable de códigos postales.
            #En este caso simulamos que introducimos el valor de 15001 para la caja del código postal.
            cajaCP = self._webdriver.find_element_by_class_name("select2-selection__placeholder")
            self._webdriver.execute_script('arguments[0].innerHTML = "15001";', cajaCP)
        except:
            pass
        
        try:
            #Simulamos que vamos a introducir el código postal
            elementoSeleccionCP = self._webdriver.find_element_by_id('cl_postal_code')
            elementoSeleccionCP = self._webdriver.find_element_by_id('cl_postal_code')
            elementoSeleccionCP.send_keys ("")
            elementoSeleccionCP.send_keys(Keys.RETURN)

            #Para poder seleccionar el valor dentro del combobox, creamos un Select del propio combo, que luego nos 
            #permite usar el método "select_by_value". En este caso escogemos el código postal 15002
            valorCP = Select(self._webdriver.find_element_by_id('cl_postal_code'))
            valorCP.select_by_value("15002")

            #Una vez seleccionado el código postal, tenemos que simular la pulsación del botón naranja "CONTINUAR >"
            botonContinuar = self._webdriver.find_element_by_class_name('btn.principal_btn.btn_new_client.ladda-button')                                                                       .click()

            print("Entrando en la página de Gadisline donde se encuentran los precios...")
        except:
            pass
        # Vamos a controlar que aparezca en la siguiente página el objeto del menú que es el que queremos localizar
        # Entonces en lugar de hacer un sleep sin más, intentamos controlar la página hasta que aparezca el contenido 
        # buscado

        # Marcamos el tiempo de inicio
        tInicio = datetime.now()
        tiempo_pausa = 1
        while True:
            #Comprobar si existe un elemento concreto, que es el menú de la siguiente página
            try:
                self._webdriver.find_element_by_xpath("//div[@class='acc-menu col-xs-10 col-sm-10 labels']")
                print("¡¡ Elemento de menú encontrado !! --> Estamos ya en la página de las categorías de productos")
                break
            except Exception as e:
                print("Por ahora no damos encontrado el elemento del menú de categorías buscado. Devuelve el error:",str(e))

            # Hacemos una pausa
            time.sleep(tiempo_pausa)

            # Comprobamos cuanto tiempo llevamos en este bucle. Si supera los 10 segundos, abortamos el script    
            tActual = datetime.now()

            if ((tActual - tInicio).total_seconds() > 10):
                print ("Paramos la ejecución del programa")
                sys.exit(0)


        #En este momento estamos en la página donde está el menú de las categorías de productos
        time.sleep(1)
        self.url_menu = self._webdriver.current_url
        return(True)
        
        

