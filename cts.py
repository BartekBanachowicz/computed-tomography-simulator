import math

import numpy
import numpy as np
import pydicom
from PIL import Image
from pydicom import Dataset

from skimage.color import rgb2gray
from skimage import io


class Tomograph:
    def __init__(self, numOfDetectors, detectionAngle, stepAngle):
        self.numOfDetectors = numOfDetectors  # D
        self.detectionAngle = detectionAngle  # Phi
        self.stepAngle = stepAngle  # alpha
        self.progressAngle = 0.0  # progress angle

    def next_iteration(self):
        self.progressAngle = self.progressAngle + self.stepAngle


def resize_image(image, size):
    background = Image.new('L', (size, size), 'black')

    if len(image.shape) > 2:
        image = rgb2gray(image)

    if np.max(image) <= 1.0:
        image = np.uint8(image*255)

    #image = Image.fromarray(np.uint8(image*255), mode="L")
    image = Image.fromarray(image)
    #print(np.max(image.))
    #image.show()

    #img = Image.open(i)
    #img_with_border = ImageOps.expand(img,border=300,fill='black')
    #background = rgb2gray(background)
    position = (math.floor(size / 2 - image.width / 2), math.floor(size / 2 - image.height/2))
    background.paste(image, position)
    #image.paste(background, position)
    background.show()
    #background.to

    return numpy.array(background)


def read_image(path):
    image = io.imread(path)
    h, w = (image.shape[0], image.shape[1])
    print(h, w)
    radius = math.ceil(math.sqrt(w ** 2 + h ** 2) / 2)
    image = resize_image(image, radius * 2 + 10)

    return image, radius


def write_result(result):
    meta = Dataset()
    print(meta)


def make_sinogram(emitterAngle):
    pass


def processing_image():
    pass


if __name__ == '__main__':
    #image, radius = read_image("photos/CT_ScoutView.jpg")
    image, radius = read_image("photos/Kropka.jpg")
    #image, radius = read_image("photos/Kwadraty2.jpg")
    #image, radius = read_image("photos/SADDLE_PE-large.JPG")

    #io.imshow(image)
    #io.show()
    write_result(None)
