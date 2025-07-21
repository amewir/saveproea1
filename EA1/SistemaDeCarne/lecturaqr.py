import cv2
import pyqrcode
import png
from pyqrcode import QRCode
from pyzbar.pyzbar import decode
import numpy as np


#Captura para QR
cap = cv2.VideoCapture(1)

#Ciclo para capturar QR
while True:

    ret, frame = cap.read()
    #aca leimos el frame

    #Leeremos el QR
    for codes in decode(frame):
        

        info = codes.data.decode('utf-8')

        tipo = info[0:2]
        tipo = int(tipo)