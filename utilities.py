import math

import numpy as np
import pydicom._storage_sopclass_uids
from pydicom.pixel_data_handlers.pillow_handler import *
from skimage.color import rgb2gray


def normalize_oy(y, size):
    return size - y


def maksimum(tab):
    local_maks = -10000.0
    for i in range(len(tab)):
        for j in range(len(tab[i])):
            if tab[i][j] > local_maks:
                local_maks = tab[i][j]
    return local_maks

def minimum(tab):
    local_min = 10000.0
    for i in range(len(tab)):
        for j in range(len(tab[i])):
            if tab[i][j] < local_min:
                local_min = tab[i][j]
    return local_min


def normalize_sinogram(sinogram):
    # maxVal = max(max(sinogram))
    maxVal = maksimum(sinogram)
    factor = 255.0 / maxVal
    for i in range(len(sinogram)):
        for j in range(len(sinogram[i])):
            temp = sinogram[i][j] * factor

            if temp > 255:
                print(temp)

            sinogram[i][j] = temp

    # for i in range(len(sinogram)):
    #     for j in range(len(sinogram[i])):
    #         if sinogram[i][j] > 255:
    #             print("Ping")

    return sinogram


# def normalize(sinogram):
#     max = 1
#     min = 100
#     for z in range(len(sinogram)):
#         for i in sinogram[z]:
#             if i > max:
#                 max = i
#             if i < min and i != 0:
#                 min = i
#     for z in range(len(sinogram)):
#         for i in range(len(sinogram[z])):
#             sinogram[z][i] = (sinogram[z][i] - min) / max
#     print(max)
#     return sinogram


def normalize_image(image):
    maxVal = maksimum(image)
    factor = 255.0 / maxVal
    for i in range(len(image)):
        for j in range(len(image[0])):
            image[i][j] = image[i][j] * factor

    for i in range(len(image)):
        for j in range(len(image[i])):
            if image[i][j] > 255:
                print("Ping")

    print("Global min: ", minimum(image))
    print("Global max: ", maksimum(image))

    return image


def resize_image(image, size):
    background = Image.new('L', (size, size), 'black')

    if len(image.shape) > 2:
        image = rgb2gray(image)

    if np.max(image) <= 1.0:
        image = np.uint8(image * 255)

    image = Image.fromarray(image)
    position = (math.floor(size / 2 - image.width / 2), math.floor(size / 2 - image.height / 2))
    background.paste(image, position)
    image = np.array(background)
    # print(image.shape)

    return image


def read_image(image):
    image = np.asarray(image)
    h, w = (image.shape[0], image.shape[1])
    radius = math.ceil(math.sqrt(w ** 2 + h ** 2) / 2)
    print("H: ", h, " W: ", w, " Radius: ", radius)
    image = resize_image(image, radius * 2)

    return image, radius






