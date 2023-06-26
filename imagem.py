import cv2
from PIL import Image
import numpy as np


# Carrega a imagem
image1 = cv2.imread('img/alcicleia.jpeg')

# Converte para escala de cinza
img = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)

# Limiar da imagem e aplicação do filtro Gaussiano
ret, limiar = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)
blur = cv2.GaussianBlur(limiar, (5, 5), 0)


# Aplicação do filtro de mediana
m, n = blur.shape
img_new1 = np.zeros([m, n])
for i in range(1, m-1):
    for j in range(1, n-1):
        temp = [blur[i-1, j-1],
                blur[i-1, j],
                blur[i-1, j + 1],
                blur[i, j-1],
                blur[i, j],
                blur[i, j + 1],
                blur[i + 1, j-1],
                blur[i + 1, j],
                blur[i + 1, j + 1]]
        temp = sorted(temp)
        img_new1[i, j] = temp[4]
img_new1 = img_new1.astype(np.uint8)

# Mostra a imagem
cv2.imshow('Limiar', img_new1)

# Salva a imagem
cv2.imwrite('img/assinaturaTratada.bmp', img_new1)

if cv2.waitKey(0) & 0xff == 27:
    cv2.destroyAllWindows()
