import math

import numpy as np
from PIL import Image
from pydicom import Dataset
from skimage import io, draw
from skimage.color import rgb2gray


def normalize_oy(y, size):
    return size - y


class Tomograph:
    def __init__(self, numOfDetectors, detectionAngle, stepAngle, radius):
        self.numOfDetectors = numOfDetectors  # D
        self.detectionAngle = detectionAngle  # Phi
        self.stepAngle = stepAngle  # alpha
        self.progressAngle = 0.0  # progress angle
        self.x = radius * math.cos(math.radians(0))
        self.y = radius * math.sin(math.radians(0))
        self.radius = radius-1

    def next_iteration(self):
        self.progressAngle = self.progressAngle + self.stepAngle
        self.x = radius * math.cos(math.radians(self.progressAngle))
        self.y = radius * math.sin(math.radians(self.progressAngle))

    def get_detectors_coords(self, size):
        detectors_coords = []
        for i in range(self.numOfDetectors):
            x = math.floor(self.radius * math.cos(math.radians(self.progressAngle) + math.pi - math.radians(self.detectionAngle / 2) +  i * math.radians(self.detectionAngle) / (self.numOfDetectors - 1))) + math.floor(size/2)
            y = math.floor(self.radius * math.sin(math.radians(self.progressAngle) + math.pi - math.radians(self.detectionAngle / 2) +  i * math.radians(self.detectionAngle) / (self.numOfDetectors - 1))) + math.floor(size/2)
            detectors_coords.append((x, normalize_oy(y, size)))

        print(detectors_coords)
        return detectors_coords

    def scan(self, image, size):
        detectorsCoords = self.get_detectors_coords(size)
        scanResults = []
        for i in range(self.numOfDetectors):
            pixels = draw.line_nd((self.x, self.y), (detectorsCoords[i][0], detectorsCoords[i][1]), endpoint=True)
            pixelsSum = 0
            for j in range(len(pixels)):
                pixelsSum = pixelsSum + image[pixels[j][0]][pixels[j][1]]
                image[pixels[j][0]][pixels[j][1]] = 255.0
            scanResults.append(pixelsSum / len(pixels))
            #image[pixels[0]][pixels[1]] = 255.0

        # print(scanResults)

        return scanResults


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
    image = io.imread(path)
    h, w = (image.shape[0], image.shape[1])
    print(h, w)
    radius = math.floor(math.sqrt(w ** 2 + h ** 2) / 2)
    image = resize_image(image, radius * 2)

    return image, radius


def write_result(result):
    meta = Dataset()
    print(meta)


def process_image(image, radius):
    tomograph = Tomograph(2, 30, 30, radius)
    sinogram = []
    while tomograph.progressAngle <= 360:
        sinogram.append(tomograph.scan(image, radius * 2))
        tomograph.next_iteration()

    io.imshow(image, cmap='gray')
    io.show()
    # sinogram = tomograph.scan(image, radius * 2)
    # print(sinogram)
    # io.imshow(np.array(sinogram, dtype=np.uint8), cmap='gray')
    # io.show()


if __name__ == '__main__':
    # image, radius = read_image("photos/CT_ScoutView.jpg")
    image, radius = read_image("photos/Kropka.jpg")
    # image, radius = read_image("photos/Kwadraty2.jpg")
    # image, radius = read_image("photos/SADDLE_PE-large.JPG")

    process_image(image, radius)

    # io.imshow(image, cmap='gray')
    # io.show()
    write_result(None)
