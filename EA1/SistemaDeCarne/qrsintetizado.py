import cv2
import requests
import re
import time
import os
import csv
from datetime import datetime
import psycopg2
from bs4 import BeautifulSoup
import pandas as pd

qrCode = cv2.QRCodeDetector() 
cap = cv2.VideoCapture(0)

# Variables Globales
cuadro = 100
detected_url = None
foundthis = "Electr"    
dominio_valido = "https://registro.usac.edu.gt/generaCarne/"
ultimo_resultado = None
ultimo_color = None
ultimo_mensaje = None
tiempo_mensaje = 0
duracion_mensaje = 5  # Duración del mensaje en segundos

estado_laboratorio = {}
ultimo_carne_procesado = None
tiempo_ultimo_escaneo = 0

conn = psycopg2.connect(
    database = "db_ea1proyecto",
    user = "postgres",  
    password = "whatsapp",
    host = "localhost",
    port = "5432")
cur = conn.cursor()


if not cap.isOpened():
  print("No se puede abrir la cámara")
  exit()

#Crear archivo CSV si no existe
if not os.path.exists('accesos_permitidos.csv'):
    with open('accesos_permitidos.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Entrada', 'Nombre', 'Carne', 'CUI', 'Estado', 'Salida'])

def searchthis(url, foundthis):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return bool(re.search(foundthis, response.text, re.IGNORECASE))
    except:
        return False
    
def url_valida(url):
    return dominio_valido in url

def extraer_datos(url):
    try:
        response = requests.get(url)
        content = response.text
        patron = r"<p>([\s\S]*?)</p>"
        datos = re.findall(patron, content)
        datos_limpios = [re.sub(r'<[^>]+>', '', d).strip() for d in datos]
        
        if len(datos_limpios) >= 3:
            return {
                "Nombre": datos_limpios[0],
                "CUI": datos_limpios[1],
                "Carne": datos_limpios[2]
            }
        return None
    except:
        return None

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Interfaz
    cv2.putText(frame, 'Centre el QR del carne', (135, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.71, (255, 0, 0), 2)
    cv2.rectangle(frame, (cuadro, cuadro), (670 - cuadro, 470 - cuadro), (255, 0, 0), 2)

    # Detectar QR
    ret_qr, decoded_info, points, _ = qrCode.detectAndDecodeMulti(frame)
    qr_detectado = False
    url_actual = None

    if ret_qr:
        for info, point in zip(decoded_info, points):
            if info and info.startswith("http"):
                qr_detectado = True
                url_actual = info
                
                if url_valida(info):
                    # Dibujar contorno verde para QR válido
                    frame = cv2.polylines(frame, [point.astype(int)], True, (0, 255, 0), 8)
                    cv2.putText(frame, 'URL VALIDA', (int(point[0][0]), int(point[0][1]) - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Procesar nuevo QR detectado
                    if detected_url != info or ((ultimo_carne_procesado and tiempo_actual - tiempo_ultimo_escaneo > 20)):
                        detected_url = info
                        pertenece = searchthis(info, foundthis)
                        
                        if pertenece:
                            ultimo_resultado = "Acceso Permitido, pertenece a EIME"
                            ultimo_color = (0, 255, 0)
                            datos = extraer_datos(info)
                            if datos:
                                carne = datos['Carne']
                                if carne in estado_laboratorio:
                                    if estado_laboratorio[carne]:  # Si ya está dentro
                                        accion = "SALIDA"
                                        estado_laboratorio[carne] = False
                                        color_accion = (0, 0, 255)  # Rojo para salida
                                    else:  # Si está fuera
                                        accion = "ENTRADA"
                                        estado_laboratorio[carne] = True
                                        color_accion = (0, 255, 0)  # Verde para entrada
                                else:
                                    # Primera vez que se escanea (registrar entrada)
                                    accion = "ENTRADA"
                                    estado_laboratorio[carne] = True
                                    color_accion = (0, 255, 0)
                                
                                # Actualizar mensajes
                                ultimo_resultado = f"Acceso {accion}"
                                ultimo_color = color_accion
                                ultimo_mensaje = f"{datos['Nombre']} | {datos['Carne']} | {accion}"
                                ultimo_carne_procesado = carne
                                tiempo_ultimo_escaneo = tiempo_actual
                                
                                

                            # Guardar en CSV
                            with open('accesos_permitidos.csv', 'a', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                
                                # Registrar entrada
                                if accion == "ENTRADA":
                                    hora_entrada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    writer.writerow([
                                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        datos['Nombre'],
                                        datos['Carne'],
                                        datos['CUI'],
                                        'Permitido',
                                        ''
                                    ])
                                # Registrar salida
                                elif accion == "SALIDA":
                                    
                                    writer.writerow([
                                    hora_entrada,
                                    datos['Nombre'],
                                    datos['Carne'],
                                    datos['CUI'],
                                    'Permitido',
                                #salida
                                datetime.now().strftime('%Y-%m-%d %H:%M:%S') if accion == "SALIDA" else ''

                            ])
                        else:
                            ultimo_resultado = "Acceso DENEGADO, no pertenece a EIME"
                            ultimo_color = (0, 0, 255)
                            ultimo_mensaje = None
                        
                        tiempo_mensaje = time.time()
                        print(ultimo_resultado)
                else:
                    # Dibujar contorno rojo para URL inválida
                    frame = cv2.polylines(frame, [point.astype(int)], True, (0, 0, 255), 8)
                    cv2.putText(frame, 'URL no valida', (int(point[0][0]), int(point[0][1]) - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Mostrar mensajes si no han expirado
    tiempo_actual = time.time()
    if tiempo_actual - tiempo_mensaje < duracion_mensaje and ultimo_resultado:
        # Mostrar resultado principal
        cv2.putText(frame, ultimo_resultado, (135, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, ultimo_color, 2)
        
        # Mostrar datos personales si existen
        if ultimo_mensaje:
            cv2.putText(frame, ultimo_mensaje, (135, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Indicar que pertenece a la USAC
        cv2.putText(frame, 'Usted pertenece a la USAC', (135, 420), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    elif qr_detectado and url_valida(url_actual):
        # Mostrar mensaje de procesamiento si el QR es nuevo
        cv2.putText(frame, 'Procesando...', (135, 420), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow('Detector de codigos QR', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break 

df = pd.read_csv('accesos_permitidos.csv', encoding='utf-8')

for index, row in df.iterrows():
        insert_query = """
        INSERT INTO accesos_permitidos (entrada, nombre, carne, cui, estado, salida)
        VALUES (%s, %s, %s, %s, %s, %s);"""
        values = list(row)
        
        try:
            cur.execute(insert_query, values)
            conn.commit()
        except Exception as e:
            print(f"Error al insertar fila {index + 1}: {e}")
            conn.rollback()
conn.commit()
conn.close() 

cap.release()
cv2.destroyAllWindows()