#!/usr/bin/env python
# coding: utf-8

# In[7]:


from selenium import webdriver
import time
import pandas as pd
import numpy as np
from AccesoGadisline import AccesoGadisline
from Categoria import Categoria
from Producto import Producto


print('Iniciando Scraper')
driver = webdriver.Chrome(executable_path=r'C:\Chromedriver\chromedriver.exe')
###################################################### 
### Obtener en user-agent
######################################################
agent = driver.execute_script("return navigator.userAgent")
print("=====================================================================================================")
print("El user-agent utilizado es:\n",agent,sep='')
print("=====================================================================================================")
time.sleep(1.5)
######################################################
##### Aceder a la página de gadisline.com
######################################################
objAccGadis = AccesoGadisline(driver, 'http://gadisline.com')
######################################################
#### Mostramos el contenido del fichero robots.txt
######################################################
print(objAccGadis.obtener_contenido_robots())
time.sleep(1.5)
######################################################
#### Intentamos ahora superar la primera traba para acceder al menú de categorías
######################################################
urlmenu = ''
if objAccGadis.acceso_inicial():
    urlmenu = objAccGadis.url_menu
    print("URL Menú de Categorías de Productos:", urlmenu)
else:
    print("Sin acceso a la página principal (Menú de Categorías de Productos)")

######################################################
#### Definimos el directorio de datos y los ficheros
######################################################
directorio_datos = "Datos/"
directorio_imagenes = "Imagenes/"
f_categorias_csv = 'categorias.csv'
f_prod_csv = 'productos.csv'
f_hstprec_csv = 'historico_precios.csv'
f_ingredientes_csv = 'ingredientes.csv'
f_nutricional_csv = 'a_nutricional.csv'

######################################################
#### Vamos a buscar las diferentes categorías de productos
######################################################
categorias = Categoria(driver, urlmenu, directorio_datos, f_categorias_csv)
df_cat = categorias.obtener_categorias_web()
#Guardamos las categorías leídas
categorias.grabar_categorias()


# In[13]:


import sys
del sys.modules['Producto']
del sys.modules['DatosComplementariosProducto']

from Producto import Producto


# In[19]:


######################################################
# Selector de categorías para escrapear
######################################################
nivel = 1
condN1 = df_cat['N1']>0
condN2 = True
condN3 = True
condN1_old = df_cat['N1']>0
condN2_old = True
condN3_old = True
buscarProductos = False
catNivel1 = ''
catNivel2 = ''
catNivel3 = ''

while True:
    campoN = 'N' + str(nivel)
    campoNivel = 'Nivel' + str(nivel)
    df_grupo=pd.DataFrame(df_cat[condN1 & condN2 & condN3].groupby([campoN, campoNivel]).size().rename('Total Páginas'))
    print(df_grupo)
    if (nivel == 1):
        valor = input('Selecciona una categoría {}. Escriba SALIR si lo desea: '.format(campoN))
    else:
        valor = input('Selecciona una categoría {}. Puede poner 0 para TODAS. Escriba SALIR si lo desea: '.format(campoN))
    
    if valor.isdigit():
        try:
            if (nivel==1):
                v1 = int(valor)
                if (v1 == 0): 
                    continue
                else:
                    condN1_old = condN1
                    condN1 = (df_cat[campoN]==v1)    
            elif (nivel==2):
                v2 = int(valor)
                if (v2 == 0):
                    buscarProductos = True
                else:
                    condN2_old = condN2
                    condN2 = (df_cat[campoN]==v2)               
            elif (nivel==3):
                v3 = int(valor)
                if (v3 == 0):
                    buscarProductos = True
                else:
                    condN3_old = condN3
                    condN3 = (df_cat[campoN]==v3)
            else:
                inicializa_parametros_selector_categorias()
                continue
                
            num_pags=df_cat[condN1 & condN2 & condN3].shape[0]
            #print(nivel, 'Paginas', num_pags)
            if (num_pags > 0):
                if (nivel==1):
                    if (v1 > 0):
                        catNivel1 = str(df_cat[condN1 & condN2 & condN3][campoNivel].unique()[0])
                    else:
                        catNivel1 = ''
                    condN1_old = condN1
                    nivel += 1
                elif (nivel==2):
                    if (v2 > 0):
                        catNivel2 = str(df_cat[condN1 & condN2 & condN3][campoNivel].unique()[0])
                    else:
                        catNivel2 = ''
                    condN2_old = condN2
                    nivel += 1
                elif (nivel==3):
                    if (v3 > 0):
                        catNivel3 = str(df_cat[condN1 & condN2 & condN3][campoNivel].unique()[0])
                    else:
                        catNivel3 = ''
                    condN3_old = condN3
                    buscarProductos = True  
                else:
                    pass
            else:
                condN1 = condN1_old
                condN2 = condN2_old
                condN3 = condN3_old
            
            if (buscarProductos):
                #Rutina de búsqueda de productos
                print("==================================================================")
                print('Productos N1{} N2{} N3{}: '.format(catNivel1, catNivel2, catNivel3))
                print("==================================================================")
                productos = Producto(drv_webdriver=driver, ruta_datos=directorio_datos,                                     ruta_imagenes=directorio_imagenes,                                     f_prod_csv=f_prod_csv, f_histprecios_csv=f_hstprec_csv,                                     f_ingredientes=f_ingredientes_csv, f_nutricional=f_nutricional_csv)
                print (productos.obtener_productos_web(df_categorias_buscar=categorias.df_cat_csv,                                       genera_historico_precios=True,                                       N1=catNivel1,N2=catNivel2,N3=catNivel3))
                #Grabamos la actualizacion de categorías
                categorias.grabar_categorias(omitir_carga_csv=True)
                
                #Grabamos los datos de productos obtenidos
                productos.grabar_productos()
                
                #Obtenemos los datos complementarios de los productos que acabamos de buscar
                productos.obtener_datos_complementarios_productos()
                
                
                #Volvemos a empezar inicializando las variables
                nivel = 1
                condN1 = df_cat['N1']>0
                condN2 = True
                condN3 = True
                condN1_old = df_cat['N1']>0
                condN2_old = True
                codnN3_old = True
                buscarProductos = False
                catNivel1 = ''
                catNivel2 = ''
                catNivel3 = ''
            else:
                pass
        except ValueError:
            pass
    else:
        if (valor.upper() == 'SALIR'):
            break


# In[18]:


catNivel1 = df_cat[df_cat['N1']==6]['Nivel1'].unique()

