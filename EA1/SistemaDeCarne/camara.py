import cv2
import requests
from bs4 import BeautifulSoup

qrCode = cv2.QRCodeDetector() 
cap = cv2.VideoCapture(0)

# Variables Globales
cuadro = 100
detected_url = None  # Almacena la URL detectada
web_content = None   # Almacenará el contenido web
processing = False   # Controla si estamos procesando una URL

if not cap.isOpened():
    print("No se puede abrir la cámara")
    exit()

def obtener_contenido(url):
    """Obtiene contenido la pagina de Registro y Estadistica"""
    try:
        #Comprobar conexion o si la URL es valida y existe
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        #Realizar un parsing de la pagina web para obtener la informacion pertinente.as
        soup = BeautifulSoup(response.text, 'html.parser')

        
        title = soup.title.string if soup.title else "Sin título"
        paragraphs = [p.get_text() for p in soup.find_all('p)')]
        contenido = "\n".join(paragraphs[:3])


        return f"Título: {title}\nContenido:\n{contenido}"
    
    except Exception as e:
        return f"Error al obtener contenido: {str(e)}"

while True:
    ret, frame = cap.read()

    # Interfaz
    cv2.putText(frame, 'Centre el QR del carne', (120, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.71, (0, 255, 0), 2)
    cv2.rectangle(frame, (cuadro, cuadro), 
                 (620 - cuadro, 500 - cuadro), (0, 255, 0), 2)
    
    # Mostrar instrucciones
    if detected_url:
        cv2.putText(frame, f'URL: {detected_url[:30]}...', (50, 450), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, 'Presione ESPACIO para ver contenido', (50, 480), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, 'Presione C para cancelar', (50, 510), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Mostrar contenido web si está disponible
    if web_content:
        cv2.putText(frame, web_content, (50, 550), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

    if ret:
        ret_qr, decoded_info, points, _ = qrCode.detectAndDecodeMulti(frame)
        if ret_qr and not processing:  # Solo detectar si no estamos procesando
            for info, point in zip(decoded_info, points):
                if info and info.startswith('http'):
                    # Solo actualizar si es una nueva URL
                    if detected_url != info:
                        detected_url = info
                        web_content = None
                        print(f"URL detectada: {info}")
                    
                    # Resaltar QR
                    frame = cv2.polylines(frame, [point.astype(int)], 
                                        True, (0, 255, 0), 8)
                    break
    else:
        print("Error en el fotograma")
        break

    cv2.imshow('Detector de codigos QR', frame)
    
    key = cv2.waitKey(1)
    
    # Tecla ESPACIO para procesar la URL
    if key == 32 and detected_url and not processing:  # 32 = SPACE
        processing = True
        web_content = "Procesando contenido..."
        print(f"\nObteniendo contenido de: {detected_url}")
        # Obtener contenido en segundo plano (podría ser con hilos en una app real)
        web_content = obtener_contenido(detected_url)
        print(web_content)
        print("-" * 50)
        processing = False
    
    # Tecla C para cancelar
    if key == ord('c') or key == ord('C'):
        detected_url = None
        web_content = None
    
    # Tecla Q para salir
    if key & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()