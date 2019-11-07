# Retail_Scraping
Este proyecto realiza una extracción limitada de información de la web gadisline.com. Se extraen precios, información nutricional e  ingredientes para una categoria seleccionada por el usuario.

En una primera fase se escanea toda la estructura de productos ofertados y permite seleccionar una categoría en la que profundizar y obtener información más detallada. Esto es, nos permite descargar todos los productos de la categoría seleccionada detallando su precio, precio unitario, cantidad neta, la url de acceso y la url que obtiene su imagen. También se obtiene la información nutricional del producto y sus ingredientes.
Finalmente se ha desarrollado un histórico de precios, donde se almacenarán los precios descargados de la categoría seleccionada con la fecha actual, permitiendo actualizaciones diarias.

Las librerías necesarias son las siguientes:

Para proceder a su ejecución :
python Retail_Scraping.py

Como resultado se obtienen 5 datasets con la siguiente estructura. Ver wiki para más información.
	

