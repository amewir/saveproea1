import cv2

qrCode = cv2.QRCodeDetector() 
cap = cv2.VideoCapture(0)

#Variables Globales
cuadro = 100 #define el tamaño del cuadro para el documento
doc = 0

if not cap.isOpened():
  print("No se puede abrir la cámara")
  exit()
  
while True:
    
    ret, frame = cap.read()

     # 'Interfaz'
    cv2.putText(frame, 'Centre el QR del carne', (120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.71, (0, 255, 0), 2)
    cv2.rectangle(frame, (cuadro, cuadro), (620 - cuadro, 500 - cuadro), (0, 255, 0), 2)


    if ret:
        ret_qr, decoded_info, points, _ = qrCode.detectAndDecodeMulti(frame)
        if ret_qr:
            for info, point in zip(decoded_info, points):
                if info:
                    color = (0, 255, 0)
                    print(info)
                else:
                    color = (0, 0, 255)
                frame = cv2.polylines(frame, [point.astype(int)], True, color, 8)
    else:
        print("No se puede recibir el fotograma (¿final de la transmisión?). Saliendo ...")
        break

    cv2.imshow('Detector de codigos QR', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()