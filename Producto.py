#!/usr/bin/env python
# coding: utf-8

# In[14]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
import pandas as pd
import numpy as np
import os
from pathlib import Path
from DatosComplementariosProducto import DatosComplementariosProducto 

class Producto(object):
    """Clase para los de productos"""
    def __init__(self, drv_webdriver, directorio_datos, f_prod_csv, f_histprecios_csv, f_ingredientes, f_nutricional):
        self._webdriver = drv_webdriver
        self._directorio_datos = directorio_datos
        self._fich_prod_csv = f_prod_csv
        self._fich_hstprec_csv = f_histprecios_csv
        self._fich_ingredientes_csv = f_ingredientes
        self._fich_nutricional_csv = f_nutricional
        self.descripcion_error = ''
        self._df_prod_vacio = pd.DataFrame(columns=['Id','Nombre','PVP', 'PVP_Unidad_Medida', 'Cantidad_Neta',                                                    'URL_Producto', 'URL_Imagen', 'UltActualizacion'])
        self.df_prod_web = (self._df_prod_vacio).copy()
        self.df_prod_csv = (self._df_prod_vacio).copy()
        
        self._df_hist_prec_vacio = pd.DataFrame(columns=['Id', 'DiaCaptura', 'PVP', 'PVP_Unidad_Medida',                                                         'UltActualizacion'])
        self.df_hist_prec = (self._df_hist_prec_vacio).copy()
        
        self._df_ingredientes_vacio = pd.DataFrame(columns=['Id', 'Ingredientes', 'UltActualizacion'])
        self.df_ingredientes = (self._df_ingredientes_vacio).copy()
        
        self._df_nutricional_vacio = pd.DataFrame(columns=['Id', 'AnalisisNutricional', 'UltActualizacion'])
        self.df_nutricional = (self._df_nutricional_vacio).copy
    #####################################################################################
    # Método: "obtener_productos_web"
    # Se le pueden pasar los 3 niveles de categorías (N1, N2 y N3)
    # Se le indica también si ir generando el historico de precios
    #####################################################################################
    def obtener_productos_web(self, df_categorias_buscar, genera_historico_precios=True, N1='', N2='', N3=''):
        
        #Comprobamos si el webdriver está activo
        try:
            self._webdriver.window_handles
        
        #except selenium.common.exceptions.InvalidSessionIdException as e:
        except Exception as ex:
            self.descripcion_error = "El webdriver no está disponible en este momento. " + str(ex)
            print(self.descripcion_error)
            return(False)
        
        if (genera_historico_precios):
            self._recuperar_fichero_historico_precios()

        self.df_prod_web = (self._df_prod_vacio).copy()
        #######################################################################
        # Aplicar los filtros de categorias N1, N2 y N3
        #######################################################################
        condN1 = True
        condN2 = True
        condN3 = True
        if (N1):
            condN1 = df_categorias_buscar['Nivel1']==N1
        if (N2):
            condN2 = df_categorias_buscar['Nivel2']==N2
        if (N3):
            condN3 = df_categorias_buscar['Nivel3']==N3
        
        indices = df_categorias_buscar[condN1 & condN2 & condN3].index
        
        for i in indices:
            #Obtenemos la URL donde están los productos de la categoría 'actual'
            url_categoria = df_categorias_buscar.loc[i, 'URL']
            print (df_categorias_buscar.loc[i, 'Nivel1'], df_categorias_buscar.loc[i, 'Nivel2'],                    df_categorias_buscar.loc[i, 'Nivel3'], url_categoria,sep='->')
            if self.acceder_url_categoria(url_categoria):
                print("Accediendo a {} ...".format(url_categoria))
                productos = self._obtener_datos_productos_categoria(self.df_prod_web, genera_historico_precios)
                #Actualizamos en el catálogo de categorías el nº de artículos
                df_categorias_buscar.loc[i, 'NumArticulos'] = productos
                df_categorias_buscar.loc[i, 'UltActualizacion'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                print("Encontrados {} artículos es esa categoría".format(productos))
                time.sleep(1.5)
        return(True)
    
    #####################################################################################
    # Método: "obtener_datos_complementarios_productos"
    #  De los productos leidos (df_prod_web) intentar obtener los datos complementarios
    #####################################################################################
    def obtener_datos_complementarios_productos(self):
        
        #Comprobamos si el webdriver está activo
        try:
            self._webdriver.window_handles
        
        #except selenium.common.exceptions.InvalidSessionIdException as e:
        except Exception as ex:
            self.descripcion_error = "El webdriver no está disponible en este momento. " + str(ex)
            print(self.descripcion_error)
            return(False)

        self.df_prod_web = self.df_prod_web.astype({'Id':'int'})
        self.df_prod_csv = self.df_prod_csv.astype({'Id':'int'})
        
        
        self._recuperar_fichero_ingredientes()
        self._recuperar_fichero_nutricional()
        
        
        hubo_cantidad_neta = False
        hubo_ingredientes = False
        hubo_nutricional = False
        
        ing_filasnuevas=0 
        ing_filaseditadas=0
        nut_filasnuevas=0 
        nut_filaseditadas=0
        #Al mezclar, nos quedamos con el indices 
        filas_productos = pd.merge(self.df_prod_web, self.df_prod_csv, on=['Id'], how='inner', left_index=True).index
        for i in (filas_productos):
            #Obtenemos la URL donde están los productos de la categoría 'actual'
            url_producto = self.df_prod_csv.loc[i, 'URL_Producto']
            datoscomp = DatosComplementariosProducto(self._webdriver, url_producto)
            print("Obteniendo datos del artículo: {}...".format(self.df_prod_csv.loc[i, 'Nombre']))
            if datoscomp.obtener_datos_complementarios_producto():
                #print(self.df_prod_csv.loc[i, 'Nombre'],"Cantidad neta:",datoscomp.cantidad_neta)
                #print("Ingredientes:",datoscomp.ingredientes)
                #print("Análisis Nutricional:",datoscomp.analisis_nutricional)
                valor_id = self.df_prod_csv.loc[i, 'Id']
                cantidad_neta = datoscomp.cantidad_neta.strip()
                ingredientes = datoscomp.ingredientes.strip()
                nutricional = datoscomp.analisis_nutricional.strip()
                
                fecha_hora_act = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                
                if (cantidad_neta):
                    hubo_cantidad_neta = True
                    self.df_prod_csv.loc[i, 'Cantidad_Neta'] = cantidad_neta
                    self.df_prod_csv.loc[i, 'UltActualizacion'] = fecha_hora_act
                if (ingredientes):
                    hubo_ingredientes = True
                    #Comprobar si existe en el fichero ingredientes (coincidencia Id)
                    fila = (self.df_ingredientes).loc[(self.df_ingredientes['Id']==valor_id)].index
                    if (fila.empty):
                        fila = (self.df_ingredientes).shape[0]
                        (self.df_ingredientes).loc[fila]= valor_id,ingredientes,fecha_hora_act
                        ing_filasnuevas += 1
                    else:
                        (self.df_ingredientes).loc[fila,'Ingredientes'] = ingredientes
                        (self.df_ingredientes).loc[fila,'UltActualizacion'] = fecha_hora_act
                        ing_filaseditadas += 1
                if (nutricional):
                    hubo_nutricional = True
                    #Comprobar si existe en el fichero nutricional (coincidencia Id)
                    fila = (self.df_nutricional).loc[(self.df_nutricional['Id']==valor_id)].index
                    if (fila.empty):
                        fila = (self.df_nutricional).shape[0]
                        (self.df_nutricional).loc[fila]= valor_id,nutricional,fecha_hora_act
                        nut_filasnuevas += 1
                    else:
                        (self.df_nutricional).loc[fila,'AnalisisNutricional'] = ingredientes
                        (self.df_nutricional).loc[fila,'UltActualizacion'] = fecha_hora_act
                        nut_filaseditadas += 1
        
                time.sleep(1.5)
        
        if (hubo_cantidad_neta):
            # Guardar dataframe de productos porque se actualizaron 'Cantidad_Neta'
            self.grabar_productos(omitir_carga_csv=True, graba_historico_precios=False)
        if (hubo_ingredientes):
            # Guardar dataframe de ingredientes
            fich_ingredientes = self._obtener_fichero_ingredientes()
            self.df_ingredientes.to_csv(fich_ingredientes, index = None, header=True, sep=';', encoding='utf-8')
            print("Fichero de ingredientes de productos. Filas Nuevas %d. Filas Editadas %d" %                   (ing_filasnuevas, ing_filaseditadas))
        if (hubo_nutricional):
            # Guardar dataframe de análisis nutricional
            fich_nutricional = self._obtener_fichero_nutricional()
            self.df_nutricional.to_csv(fich_nutricional, index = None, header=True, sep=';', encoding='utf-8')
            print("Fichero de análisis nutricional de productos. Filas Nuevas %d. Filas Editadas %d" %                   (nut_filasnuevas, nut_filaseditadas))
        return(True)
    #####################################################################################
    # Método: "acceder_url_categoria"
    # Dada una URL (de categoría)
    #   - Acceder a esa URL
    #   - Hacer scroll-down hasta que la página deje de crecer
    #####################################################################################
    def acceder_url_categoria(self, url_categoria):
        #Comprobamos si el webdriver está activo
        try:
            self._webdriver.window_handles
        
        #except selenium.common.exceptions.InvalidSessionIdException as e:
        except Exception as ex:
            self.descripcion_error = "El webdriver no está disponible en este momento. " + str(ex)
            print(self.descripcion_error)
            return(False)
        
        try:
            self._webdriver.get(url_categoria)
        except Exception as ex:
            self.descripcion_error = "No ha podido acceder a la URL de la categoría buscada. " + str(ex)
            print(self.descripcion_error)
            return(False)
        
        #Para cada URL cargada, vamos a hacer scroll hasta abajo de todo, para que se carguen todos los productos
        tiempo_pausa_scroll = 1.5

        # Get scroll height
        ultimo_height = self._webdriver.execute_script("return document.body.scrollHeight")

        while True:
            # Hacemos scroll hacia abajo
            self._webdriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Esperamos para que se cargue la página
            time.sleep(tiempo_pausa_scroll)

            scroll = self._webdriver.find_element_by_tag_name('body').send_keys(Keys.END)

            # Esperamos para que se cargue la página
            time.sleep(tiempo_pausa_scroll)

            # Volvemos a calcular la altura de la página después de haber ejecutado el scroll
            # Si ha cambiado, continuamos, sino hemos acabado de hacer scroll
            nuevo_height = self._webdriver.execute_script("return document.body.scrollHeight")
            if nuevo_height == ultimo_height:
                break
            ultimo_height = nuevo_height
            
        return(True)
    
    #####################################################################################
    # Método: "_obtener_datos_productos_categoria"
    # Estando ya posicionado en la página de los productos de la categoría buscada
    #   - Recorrer todos los elementos 'product_container' y obtener los datos
    #####################################################################################
    def _obtener_datos_productos_categoria(self, df_prod_read, genera_historico_precios):
        #En este punto podemos leer la página de los productos
        elementos = self._webdriver.find_elements_by_xpath("//div[@class='product_container']")
        #elementos = row_ul.find_elements_by_xpath("//li[@class='col-sm-3 grid_view ']")
        #elementos = row_ul.find_elements_by_xpath("//a[@class='gtmProductClick']")
        filas = df_prod_read.shape[0]
        productos = 0;
        for row_div in elementos:
            #En cada <div role="article" id="product_5410076" class="product_container">
            # Buscamos la descripcion del artículo, el precio, el link del artículo, el precio por unidad de medida

            cell_img = row_div.find_element_by_xpath(".//img[@class='img-responsive product_img opacity_hover']")
            cell_name= row_div.find_element_by_xpath(".//a[@class='gtmProductClick']")
            cell_price = row_div.find_element_by_xpath(".//p[@class='product_price']")
            cell_price_measure = row_div.find_element_by_xpath(".//p[@class='product_unity_price']")

            url_imagen = cell_img.get_attribute('src')
            valor_id = int(cell_name.get_attribute('id'))
            nombre = cell_name.get_attribute('text')
            url_producto = cell_name.get_attribute('href')
            pvp = cell_price.get_attribute('innerText')
            pvp_unidad_medida = cell_price_measure.get_attribute('innerText')
            dia_captura = datetime.now().strftime("%d/%m/%Y")
            fecha_hora_act = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            #print (productos, valor_id, nombre, pvp, pvp_unidad_medida, url_producto, url_imagen)
            print (productos, valor_id, nombre, pvp, pvp_unidad_medida)
            df_prod_read.loc[filas] = valor_id,nombre,pvp,pvp_unidad_medida,0,url_producto,url_imagen,fecha_hora_act
            if (genera_historico_precios):
                #Comprobar si existe en el histórico de precios (coincidencia Id y DiaCaptura)
                filahist = (self.df_hist_prec).loc[(self.df_hist_prec['Id']==valor_id) &                                                    (self.df_hist_prec['DiaCaptura']==dia_captura)].index
                if (filahist.empty):
                    filahist = (self.df_hist_prec).shape[0]
                    (self.df_hist_prec).loc[filahist]= valor_id,dia_captura,pvp,pvp_unidad_medida,fecha_hora_act
                else:
                    (self.df_hist_prec).loc[filahist,'PVP'] = pvp
                    (self.df_hist_prec).loc[filahist,'PVP_Unidad_Medida'] = pvp_unidad_medida
                    (self.df_hist_prec).loc[filahist,'UltActualizacion'] = fecha_hora_act
            
            productos += 1
            filas += 1
            
        return(productos)
    #####################################################################################
    # Obtener el nombre del fichero histórico de precios
    #####################################################################################
    def _obtener_fichero_historico_precios(self):
        fich_histprecios = Path(self._directorio_datos + self._fich_hstprec_csv)
        return(fich_histprecios)
    #####################################################################################
    # Obtener el nombre del fichero de ingredientes
    #####################################################################################
    def _obtener_fichero_ingredientes(self):
        fich_ingredientes = Path(self._directorio_datos + self._fich_ingredientes_csv)
        return(fich_ingredientes)
    #####################################################################################
    # Obtener el nombre del fichero de analisis nutricional
    #####################################################################################
    def _obtener_fichero_nutricional(self):
        fich_nutricional = Path(self._directorio_datos + self._fich_nutricional_csv)
        return(fich_nutricional)
    #####################################################################################
    # Leer el fichero histórico de precios (cargarlo en self.df_hist_prec)
    #####################################################################################
    def _recuperar_fichero_historico_precios(self):
        fich_histprecios = self._obtener_fichero_historico_precios()
        
        #Comprobamos el directorio de datos, y si no existe lo creamos
        if not os.path.exists(self._directorio_datos):
            os.makedirs(self._directorio_datos)
            
        if fich_histprecios.is_file():
            self.df_hist_prec = pd.read_csv(fich_histprecios, header=0, sep=';', encoding='utf-8')
            print("Recuperado el dataframe guardado de histórico de precios. El nº registros es:",                  self.df_hist_prec.shape[0])
        else:
            print("Aún no existe un dataframe guardado con toda la información de los de productos.")
            self.df_hist_prec = (self._df_hist_prec_vacio).copy()
        
        return(True)
    #####################################################################################
    # Leer el fichero de ingredientes (cargarlo en self.df_ingredientes)
    #####################################################################################
    def _recuperar_fichero_ingredientes(self):
        fich_ingredientes = self._obtener_fichero_ingredientes()
        
        #Comprobamos el directorio de datos, y si no existe lo creamos
        if not os.path.exists(self._directorio_datos):
            os.makedirs(self._directorio_datos)
            
        if fich_ingredientes.is_file():
            self.df_ingredientes = pd.read_csv(fich_ingredientes, header=0, sep=';', encoding='utf-8')
            print("Recuperado el dataframe guardado de ingredientes de productos. El nº registros es:",                  self.df_ingredientes.shape[0])
        else:
            print("Aún no existe un dataframe guardado con toda la información de los ingredientes de productos.")
            self.df_ingredientes = (self._df_ingredientes_vacio).copy()
        
        self.df_ingredientes = self.df_ingredientes.astype({'Id':'int'})
        return(True)
    #####################################################################################
    # Leer el fichero de análisis nutricional (cargarlo en self.df_hist_prec)
    #####################################################################################
    def _recuperar_fichero_nutricional(self):
        fich_nutricional = self._obtener_fichero_nutricional()
        
        #Comprobamos el directorio de datos, y si no existe lo creamos
        if not os.path.exists(self._directorio_datos):
            os.makedirs(self._directorio_datos)
            
        if fich_nutricional.is_file():
            self.df_nutricional = pd.read_csv(fich_nutricional, header=0, sep=';', encoding='utf-8')
            print("Recuperado el dataframe guardado de análisis nutricional de productos. El nº registros es:",                  self.df_nutricional.shape[0])
        else:
            print("Aún no existe un dataframe guardado con toda la información de análisis nutricional de productos.")
            self.df_nutricional = (self._df_nutricional_vacio).copy()
            
        self.df_nutricional = self.df_nutricional.astype({'Id':'int'})
        return(True)
    #####################################################################################
    # Método: "_obtener_datos_productos_categoria"
    # Estando ya posicionado en la página de los productos de la categoría buscada
    #   - Recorrer todos los elementos 'product_container' y obtener los datos
    #####################################################################################
    def grabar_productos(self, omitir_carga_csv=False, graba_historico_precios=True):
        
        #Comprobamos el directorio de datos, y si no existe lo creamos
        if not os.path.exists(self._directorio_datos):
            os.makedirs(self._directorio_datos)

        fich_productos = Path(self._directorio_datos + self._fich_prod_csv)
     
        
        if not(omitir_carga_csv):
            if fich_productos.is_file():
                self.df_prod_csv = pd.read_csv(fich_productos, header=0, sep=';', encoding='utf-8') 
                print("Recuperado el dataframe guardado de productos. El nº de productos es:", self.df_prod_csv.shape[0])
            else:
                print("Aún no existe un dataframe guardado con toda la información de los de productos.")
                self.df_cat_csv = (self._df_prod_vacio).copy()
            
             # Mezclamos los dataframes (añadir al dataframe csv los nuevos datos obtenidos web)
            self.df_prod_csv = self._mezclar_dataframe_web_csv(self.df_prod_web, self.df_prod_csv)
        else:
            # Esta parte es cuando tenemos ya el dataframe del CSV cargado en memoria
            # y no lo queremos recargar
            pass
        
        #Guardamos el nuevo dataframe actualizado de categorías
        self.df_prod_csv.to_csv (fich_productos, index = None, header=True, sep=';', encoding='utf-8')
        
        if (graba_historico_precios):
            fich_histprecios = self._obtener_fichero_historico_precios()
            self.df_hist_prec.to_csv(fich_histprecios, index = None, header=True, sep=';', encoding='utf-8')
        
        return(True)
    #####################################################################################
    # Método: "_mezclar_dataframe_web_csv"
    # Mezclar los datos de producto leídos con lo que ya estaba guardado en el CSV
    #####################################################################################
    def _mezclar_dataframe_web_csv(self, df_web, df_csv):
        # Vamos a cruzar los 2 dataset (el leído de la web y el del CSV por 'Id', lo ponemos como int)
        df_csv = df_csv.astype({'Id':'int'})
        df_web = df_web.astype({'Id':'int'})

        #Editar las filas que sí existen, es decir que ya estaban en el DataFrame
        #Al mezclar, las columnas coincidentes que no son la "clave" llevan el sufijo "_x" y "_y"
        merge_df = pd.merge(df_web, df_csv, on=['Id'], how='inner', left_index=True)
        print("Artículos a actualizar:",merge_df.shape[0])
        #Mantenemos los índices de 'df_csv' que son los que hay que actualizar
        for fila in merge_df.index:
            #Actualizar los valores
            df_csv.loc[fila,'Nombre'] = merge_df.loc[fila,'Nombre_x']
            df_csv.loc[fila,'PVP'] = merge_df.loc[fila,'PVP_x']
            df_csv.loc[fila,'PVP_Unidad_Medida'] = merge_df.loc[fila,'PVP_Unidad_Medida_x']
            df_csv.loc[fila,'Cantidad_Neta'] = merge_df.loc[fila,'Cantidad_Neta_x']
            df_csv.loc[fila,'URL_Producto'] = merge_df.loc[fila,'URL_Producto_x']
            df_csv.loc[fila,'URL_Imagen'] = merge_df.loc[fila,'URL_Imagen_x']
            df_csv.loc[fila,'UltActualizacion'] = merge_df.loc[fila,'UltActualizacion_x']

        #Ahora vamos a buscar nuevos elementos
        #Al mezclar, las columnas coincidentes que no son la "clave" llevan el sufijo "_x" y "_y"
        merge_df = pd.merge(df_web, df_csv, on=['Id'], how='left')

        #Nos quedamos con las columnas de "df_web" que no existen en el "df_prod"
        columnas = ['Id','Nombre_x','PVP_x','PVP_Unidad_Medida_x','Cantidad_Neta_x',                    'URL_Producto_x','URL_Imagen_x', 'UltActualizacion_x']
        df_nuevosprod = merge_df.loc[merge_df['Nombre_y'].isnull(), columnas]
        print("Nuevos artículos:",df_nuevosprod.shape[0])

        if (df_nuevosprod.shape[0] > 0):
            #Renombramos las columnas
            columnas = ['Id','Nombre','PVP','PVP_Unidad_Medida','Cantidad_Neta',                        'URL_Producto','URL_Imagen','UltActualizacion']
            df_nuevosprod.columns = columnas
            df_nuevosprod.head(10)

            #Finalmente concatenamos los dataframes
            df_csv = pd.concat([df_csv, df_nuevosprod], axis = 0)

        df_csv = df_csv.reset_index(drop=True)
        
        #Ya hemos terminado con los dataframes "merge_df" y "df_nuevascat"
        lst_delete = [merge_df, df_nuevosprod]
        del lst_delete
        
        return(df_csv)
        

