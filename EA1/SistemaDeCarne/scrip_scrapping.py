import re
from colorama import Fore
import requests
import pandas as pd

website = "https://registro.usac.edu.gt/generaCarne/DatosEstudiante.php?rac=f449167db4e4f8fd1941e620fb682711"
resultado = requests.get(website)
resultado.encoding = 'utf-8'
content = resultado.text




patron = r"<p>([\s\S]*?)</p>"
datos = re.findall(patron, str(content)) 

#datos limpios
datos_limpios = [re.sub(r'<[^>]+>', '', d).strip() for d in datos]

# Ordenar datos de la siguiente forma [nombre, CUI, carné]
if len(datos_limpios) >= 3:
    nombre = datos_limpios[0]
    cui = datos_limpios[1]
    carne = datos_limpios[2]

df_acceso = {
"Nombre": nombre,
"CUI": cui,
"Carne": carne 
}

print(df_acceso)




