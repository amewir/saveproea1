import cv2
import requests
import re

qrCode = cv2.QRCodeDetector() 
cap = cv2.VideoCapture(0)

#Variables Globales
cuadro = 100 #define el tamaño del cuadro para el documento
doc = 0

detected_url = None
search_result = None
processing = False
foundthis = "Elect"   #Término esencial a buscar
url_procesada = False #Para controlar si la URL ya ha sido procesada
dominio_valido = "https://registro.usac.edu.gt/generaCarne/"

if not cap.isOpened():
  print("No se puede abrir la cámara")
  exit()
  

def searchthis(url, foundthis):
    #Buscar un término especifico en el contenido del carne del usuario
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        #Buscar coincidencias, sin importar mayúsculas o minúsculas
        matches = re.findall(foundthis, response.text, re.IGNORECASE)
        if matches:
            #Encontramos el término
            return True, f"Se encontró '{foundthis}'"
            #Añadir función para habilitar el acceso a la puerta de acceso al labortorio
            

        else:
            #El término no está presente
            
            #añadir función para denegar el acceso a la puerta de acceso al laboratorio
            return False, f"'{foundthis}' no encontrado"
        
    except Exception as e:
        return False, f"Error: {str(e)}"
    
def url_valida(url):
    #Verifica si la URL es valida y pertenece a la institución
    return dominio_valido in url

while True:
    
    ret, frame = cap.read()

    if not ret:
        continue

     # 'Interfaz'
    cv2.putText(frame, 'Centre el QR del carne', (135, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.71, (255, 0, 0), 2)
    cv2.rectangle(frame, (cuadro, cuadro), (670 - cuadro, 470 - cuadro), (255, 0, 0), 2)




    if ret:
        ret_qr, decoded_info, points, _ = qrCode.detectAndDecodeMulti(frame)
        if ret_qr and not processing:
            for info, point in zip(decoded_info, points):
                if info and info.startswith("http"):

                    if url_valida(info):
                        if detected_url != info:
                            detected_url = info
                            rl_procesada = False # Reiniciar para volver a escanear
                            print(f"URL detectada: {detected_url}")

                    # Dibujar el QR detectado
                    frame = cv2.polylines(frame, [point.astype(int)], True, (0, 255, 0), 8)
                    break

                    color = (0, 255, 0)
                    print(info)
                else:
                    frame = cv2.polylines(frame, [point.astype(int)], True, (0, 0, 255), 8)
                    cv2.putText(frame, 'URL no valida', (int(point[0][0]), int(point[0][1]) - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                   
# Realizar búsqueda solo si tenemos una URL válida no procesada
    if detected_url and url_valida(detected_url) and not url_procesada and not processing:
        processing = True
        found, message = searchthis(detected_url, foundthis)
        search_result = (found, message)  # Almacenar el resultado
        print(message)
        url_procesada = True  # Marcar como procesada
        processing = False

    # Mostrar mensajes en pantalla
    if detected_url:
        if url_valida(detected_url):
            if not url_procesada:
                # Mostrar mensaje mientras se procesa
                cv2.putText(frame, 'Procesando...', (135, 420), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            else:
                # Mostrar resultado después de procesar
                cv2.putText(frame, 'Usted pertenece a la USAC', (135, 420), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Mostrar acceso permitido/denegado basado en el resultado real
                if search_result and search_result[0]:
                    resultado = "Acceso Permitido, pertenece a EIME"
                    color = (0, 255, 0)
                else:
                    resultado = "Acceso DENEGADO, no pertenece a EIME"
                    color = (0, 0, 255)
                    
                cv2.putText(frame, resultado, (135, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow('Detector de codigos QR', frame)
    
      # Tecla Q para salir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break 
    
cap.release()
cv2.destroyAllWindows()