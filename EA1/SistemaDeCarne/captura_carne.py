#LIBRERIAS

import cv2
import pytesseract
import re

#VARIABLE EN EL PROYECTO

cuadro = 100 #define el tamaño del cuadro para el documento 
doc = 0 

cap = cv2.VideoCapture(0)
cap.set(3,1280) #Ancho
cap.set(4,720) #Alto

def texto (imagen):
    global doc
    
    #Direccion de tesseract
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

    #Escala de grises
    escala = 2.0
    imagen = cv2.resize(imagen, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    #INVERTIR COLORES PARA LETRAS BLANCAS
    invertido = cv2.bitwise_not(gris)

    #FILTRO clahe
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    contraste = clahe.apply(invertido)

    #gaussian
    suavizado = cv2.GaussianBlur(contraste, (5,5), 0)

    # Umbral adaptativo
    umbral = cv2.adaptiveThreshold(
        suavizado, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        31, 10
    )


    #Configurar OCR
    config = "--psm 1"
    text = pytesseract.image_to_string(umbral, config=config)
    print(text)
    
while True:
    #Lectura de Captura 

    ret, frame = cap.read()

     # 'Interfaz'
    cv2.putText(frame, 'Ubique el documento de identificacion', (120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.71, (0, 255, 0), 2)
    cv2.rectangle(frame, (cuadro, cuadro), (620 - cuadro, 500 - cuadro), (0, 255, 0), 2)

    #Opciones
    if doc == 0:
            cv2.putText(frame,'Presiona "i" para capturar el documento',(120, 150-cuadro), cv2.FONT_HERSHEY_SIMPLEX, 0.71, (0,255,0),2)
 
# Leemos el teclado
    t = cv2.waitKey(5)
    cv2.imshow('ID INTELIGENTE', frame)

    #Escape
    if t == 27:
        break
    #Captura del documento con la letra i de identificar 
    elif t == 105 or t == 73:  # 'i' or 'I'
         texto(frame)

cap.release()
cv2.destroyAllWindows()

