import cv2
import requests
import re

qrCode = cv2.QRCodeDetector() 
cap = cv2.VideoCapture(0)

# Variables Globales
cuadro = 100
doc = 0
frames_sin_qr = 0  # Contador de frames sin QR detectado
max_frames_sin_qr = 120  # Número de frames sin QR para considerar que desapareció

detected_url = None
search_result = None
processing = False
foundthis = "Elect"
dominio_valido = "https://registro.usac.edu.gt/generaCarne/"
url_procesada = False #Para controlar si la URL ya ha sido procesada

if not cap.isOpened():
  print("No se puede abrir la cámara")
  exit()

def searchthis(url, foundthis):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        matches = re.findall(foundthis, response.text, re.IGNORECASE)
        if matches:
            return True, f"Se encontró '{foundthis}'"
        else:
            return False, f"'{foundthis}' no encontrado"
    except Exception as e:
        return False, f"Error: {str(e)}"
    
def url_valida(url):
    return dominio_valido in url

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # 'Interfaz'
    cv2.putText(frame, 'Centre el QR del carne', (135, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.71, (255, 0, 0), 2)
    cv2.rectangle(frame, (cuadro, cuadro), (670 - cuadro, 470 - cuadro), (255, 0, 0), 2)

    qr_detectado = False
    url_actual = None

    if ret:
        ret_qr, decoded_info, points, _ = qrCode.detectAndDecodeMulti(frame)
        if ret_qr:
            for info, point in zip(decoded_info, points):
                if info and info.startswith("http"):
                    qr_detectado = True
                    url_actual = info
                    
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
    # Reiniciar estado si el QR desaparece
    if not qr_detectado:
        frames_sin_qr += 1
        if frames_sin_qr > max_frames_sin_qr:
            detected_url = None
            search_result = None
            url_procesada = False
            frames_sin_qr = 0  # Reinicia conteo de frames sin QR
    else:
        frames_sin_qr = 0
        # Actualizar URL si es diferente a la anterior
        if url_actual and url_actual != detected_url:
            detected_url = url_actual
            url_procesada = False
            print(f"Nuevo QR detectado: {detected_url}")

    # Procesar nuevo QR detectado
    if detected_url and url_valida(detected_url) and not url_procesada and not processing:
        processing = True
        found, message = searchthis(detected_url, foundthis)
        search_result = (found, message)
        print(message)
        url_procesada = True
        processing = False

    # Mostrar resultados en pantalla
    if detected_url and url_valida(detected_url):
        if not url_procesada:
            cv2.putText(frame, 'Procesando...', (135, 420), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        else:
            cv2.putText(frame, 'Usted pertenece a la USAC', (135, 420), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if search_result and search_result[0]:
                resultado = "Acceso Permitido, pertenece a EIME"
                color = (0, 255, 0)
            else:
                resultado = "Acceso DENEGADO, no pertenece a EIME"
                color = (0, 0, 255)
                
            cv2.putText(frame, resultado, (135, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow('Detector de codigos QR', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break 
    
cap.release()
cv2.destroyAllWindows()
