#!/usr/bin/env python
# coding: utf-8

# In[5]:


from selenium import webdriver
import time
from datetime import datetime
import pandas as pd
import numpy as np
import os
from pathlib import Path

class Categoria(object):
    """Clase para las categorías de productos"""
    def __init__(self, drv_webdriver, url, directorio_datos, fichero_csv):
        self._webdriver = drv_webdriver
        self._url = url
        self._directorio_datos = directorio_datos
        self._fichero_csv = fichero_csv
        self.descripcion_error = ''
        self._df_cat_vacio = pd.DataFrame(columns=['Nivel1','Nivel2','Nivel3',                                                 'URL', 'NumArticulos','UltActualizacion'])
        self.df_cat_web = pd.DataFrame(columns=['N1','N2','N3','Nivel1','Nivel2','Nivel3',                                                 'URL', 'NumArticulos','UltActualizacion'])
        self.df_cat_csv = pd.DataFrame(columns=['Nivel1','Nivel2','Nivel3',                                                 'URL', 'NumArticulos','UltActualizacion'])
        
    def obtener_categorias_web(self):
        
        #Comprobamos si el webdriver está activo
        try:
            self._webdriver.window_handles
        
        #except selenium.common.exceptions.InvalidSessionIdException as e:
        except Exception as ex:
            self.descripcion_error = "El webdriver no está disponible en este momento. " + str(ex)
            print(self.descripcion_error)
            return(self.df_cat_web)
        
        if (self._webdriver.current_url != self._url):
            #Ir a la página de menú de categorías de productos
            try:
                self._webdriver.get(self._url)
            except Exception as ex:
                self.descripcion_error = "Error al intentar acceder a la página del menú de categorías de productos" +                                          str(ex)
                print(self.descripcion_error)
                return(self.df_cat_web)
        
        try:
            elementos_tabla = 0
            N1 = 0
            N2 = 0
            N3 = 0
            txtN1 = ''
            txtN2 = ''
            txtN3 = ''
            
            # Marcamos el tiempo de inicio
            tInicio = datetime.now()

            #Accedemos al menú, a través del elemento padre:
            #  - Podemos hacerlo con: driver.find_element_by_class_name("acc-menu.col-xs-10.col-sm-10.labels")
            #  - Podemos hacerlo con: driver.find_element_by_xpath("//div[@class='acc-menu col-xs-10 col-sm-10 labels']")

            #parentElement = driver.find_element_by_class_name("acc-menu.col-xs-10.col-sm-10.labels")
            #parentElement = driver.find_element_by_class_name("menu_category_container")
            elementoPadreMenu = self._webdriver.find_element_by_xpath("//div[@class='acc-menu col-xs-10 col-sm-10 labels']")

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
                            self.df_cat_web.loc[elementos_tabla] = N1,N2,N3,txtN1,txtN2,txtN3,url_link,0,                                                                    datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            elementos_tabla += 1
                        else:
                            print('----------')
                        print (texto)

            # Marcamos el tiempo de fin
            tFin = datetime.now()

            texto = 'Hemos invertido {:4.2f} segundos en obtener {:d} categorías (de 3 niveles)'             .format((tFin-tInicio).total_seconds(), self.df_cat_web.shape[0])
            print(texto)
            
        except Exception as ex:
            self.descripcion_error = "Error obteniendo las categorías de productos" + str(ex)
            print(self.descripcion_error)
            
        
        return(self.df_cat_web)
    
    def grabar_categorias(self, omitir_carga_csv=False):
        #print(df)
        #print(type(df))
        
         #Comprobamos el directorio de datos, y si no existe lo creamos
        if not os.path.exists(self._directorio_datos):
            os.makedirs(self._directorio_datos)

        fich_categorias = Path(self._directorio_datos + self._fichero_csv) 
        
        if not(omitir_carga_csv):
            if fich_categorias.is_file(): 
                self.df_cat_csv = pd.read_csv(fich_categorias, header=0, sep=';', encoding='utf-8') 
                print("Recuperado el dataframe guardado, el nº de categorías N1-N2-N3 es:", self.df_cat_csv.shape[0])
            else:
                print("Aún no existe un dataframe guardado con toda la información de las categorías de productos.")
                self.df_cat_csv = self._df_cat_vacio
        else:
            # Esta parte es cuando tenemos ya el dataframe del CSV cargado en memoria
            # y no lo queremos recargar
            pass
            
        # Mezclamos los dataframes (añadir al dataframe csv los nuevos datos obtenidos web)
        self.df_cat_csv = self._mezclar_dataframe_web_csv(self.df_cat_web, self.df_cat_csv)
        
        #Guardamos el nuevo dataframe actualizado de categorías
        self.df_cat_csv.to_csv (fich_categorias, index = None, header=True, sep=';', encoding='utf-8')  
        
    def _mezclar_dataframe_web_csv(self, df_web, df_csv):
        #Si hemos leído de la web la estructura de productos, la vamos a comparar con el dataframe 
        #que acabamos de cargar, para ver si hay categorías nuevas, o si alguna ha cambiado la URL

        #Al mezclar, las columnas coincidentes que no son la "clave" llevan el sufijo "_x" y "_y"
        merge_df = pd.merge(df_web, df_csv, on=['Nivel1','Nivel2','Nivel3'], how='left')

        #Nos quedamos con las columnas de "df_web" que no existen en el "df_"
        columnas = ['Nivel1','Nivel2','Nivel3','URL_x','NumArticulos_x','UltActualizacion_x']
        df_nuevascat = merge_df.loc[merge_df['NumArticulos_y'].isnull(), columnas]
        print("Nuevas categorias:",df_nuevascat.shape[0])
        #Renombramos las columnas
        columnas = ['Nivel1','Nivel2','Nivel3','URL','NumArticulos','UltActualizacion']
        df_nuevascat.columns = columnas
        #df_nuevascat.head(10)

        #Para los que ya existían vamos a comprobar si han cambiado las URL, en ese caso las actualizamos
        #Al mezclar, las columnas coincidentes que no son la "clave" llevan el sufijo "_x" y "_y"
        merge_df = pd.merge(df_web, df_csv, on=['Nivel1','Nivel2','Nivel3'], how='inner', left_index=True)
        #Mantenemos los índices de 'df_cat' que son los que hay que actualizar
        filas_act_URL = merge_df[merge_df.URL_x != merge_df.URL_y].index
        merge_df.head(10)
        print("Categorías que han cambiado de URL:", filas_act_URL.shape[0])
        for fila in filas_act_URL:
            #Cambiar la URL de df_cat por la nueva
            #print(df_csv.loc[fila, 'URL'], merge_df.loc[fila,'URL_x'])
            df_csv.loc[fila, 'URL'] = merge_df.loc[fila,'URL_x']
            df_csv.loc[fila, 'UltActualizacion'] = merge_df.loc[fila,'UltActualizacion_x']
        
        #Finalmente concatenamos los dataframes
        df_csv = pd.concat([df_csv, df_nuevascat], axis = 0, sort=False)
        df_csv = df_csv.reset_index(drop=True)
        
        #Ya hemos terminado con los dataframes "merge_df" y "df_nuevascat"
        lst_delete = [merge_df, df_nuevascat]
        del lst_delete
        
        return(df_csv)
        

