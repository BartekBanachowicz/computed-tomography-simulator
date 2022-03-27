from PIL import Image
import numpy as np
import math
from skimage.io import imread, imshow
from skimage.color import rgb2gray
from pydicom import Dataset


def normalize_oy(y, size):
    return size - y


def normalize_sinogram(sinogram):
    maxVal = max(max(sinogram))
    factor = 255.0 / maxVal
    for i in range(len(sinogram)):
        for j in range(len(sinogram[0])):
            sinogram[i][j] = sinogram[i][j] * factor
    return sinogram


def normalize_image(image):
    maxVal = np.max(image)
    factor = 255.0 / maxVal
    for i in range(len(image)):
        for j in range(len(image[0])):
            image[i][j] = image[i][j] * factor
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


def read_image(path):
    image = imread(path)
    h, w = (image.shape[0], image.shape[1])
    radius = math.ceil(math.sqrt(w ** 2 + h ** 2) / 2)
    print("H: ", h, " W: ", w, " Radius: ", radius)
    image = resize_image(image, radius * 2)

    return image, radius


def write_result(result):
    meta = Dataset()
    print(meta)
