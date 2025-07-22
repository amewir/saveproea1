import cv2
import requests
import re  # Para búsqueda de patrones

qrCode = cv2.QRCodeDetector() 
cap = cv2.VideoCapture(0)

# Variables Globales
cuadro = 100
detected_url = None
search_result = None
processing = False
SEARCH_TERM = "Electr"  # Término específico a buscar

if not cap.isOpened():
    print("No se puede abrir la cámara")
    exit()

def search_in_webpage(url, search_term):
    """Busca un término específico en el contenido de una página web"""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        # Buscar coincidencias (insensible a mayúsculas/minúsculas)
        matches = re.findall(search_term, response.text, re.IGNORECASE)
        
        if matches:
            # Encontramos el término
            return True, f"Se encontró '{search_term}' ({len(matches)} veces)"
        else:
            # El término no está presente
            return False, f"'{search_term}' no encontrado"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

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
        cv2.putText(frame, 'Presione ESPACIO para buscar', (50, 480), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f'Buscar: "{SEARCH_TERM}"', (50, 510), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Mostrar resultados de búsqueda
    if search_result:
        color = (0, 255, 0) if search_result[0] else (0, 0, 255)
        cv2.putText(frame, search_result[1], (50, 550), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    if ret:
        ret_qr, decoded_info, points, _ = qrCode.detectAndDecodeMulti(frame)
        if ret_qr and not processing:
            for info, point in zip(decoded_info, points):
                if info and info.startswith('http'):
                    # Actualizar solo si es una nueva URL
                    if detected_url != info:
                        detected_url = info
                        search_result = None
                        print(f"URL detectada: {info}")
                    
                    # Resaltar QR
                    frame = cv2.polylines(frame, [point.astype(int)], 
                                        True, (0, 255, 0), 8)
                    break
    else:
        print("Error en el fotograma")
        break

    cv2.imshow('Buscador QR: ' + SEARCH_TERM, frame)
    
    key = cv2.waitKey(1)
    
    # Tecla ESPACIO para buscar el término
    if key == 32 and detected_url and not processing:  # 32 = SPACE
        processing = True
        search_result = (False, "Buscando...")
        print(f"\nBuscando '{SEARCH_TERM}' en: {detected_url}")
        
        # Realizar búsqueda
        found, message = search_in_webpage(detected_url, SEARCH_TERM)
        search_result = (found, message)
        print(message)
        
        processing = False
    
    # Tecla C para cancelar
    if key == ord('c') or key == ord('C'):
        detected_url = None
        search_result = None
    
    # Tecla Q para salir
    if key & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()