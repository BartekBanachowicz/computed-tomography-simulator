import math
import numpy as np
from PIL import Image
from skimage import draw
from skimage import io

import utilities
from bresenham import line


class Tomograph:
    def __init__(self, numOfDetectors, detectionAngle, stepAngle, radius):
        self.numOfDetectors = numOfDetectors  # D
        self.detectionAngle = detectionAngle  # Phi
        self.stepAngle = stepAngle  # alpha
        self.progressAngle = 0.0  # progress angle
        self.radius = radius - 1
        self.x = self.radius * math.cos(math.radians(self.progressAngle)) + self.radius - 1
        self.y = self.radius * math.sin(math.radians(self.progressAngle)) + self.radius - 1

    def next_iteration(self):
        self.progressAngle = self.progressAngle + self.stepAngle
        self.x = math.floor(self.radius * math.cos(math.radians(self.progressAngle)) + self.radius) - 1
        self.y = math.floor(self.radius * math.sin(math.radians(self.progressAngle)) + self.radius) - 1

    def get_detectors_coords(self, size):
        detectors_coords = []
        for i in range(self.numOfDetectors):
            x = math.floor(self.radius * math.cos(
                math.radians(self.progressAngle) + math.pi - math.radians(self.detectionAngle / 2) + i * math.radians(
                    self.detectionAngle) / (self.numOfDetectors - 1))) + math.floor(size / 2)
            y = math.floor(self.radius * math.sin(
                math.radians(self.progressAngle) + math.pi - math.radians(self.detectionAngle / 2) + i * math.radians(
                    self.detectionAngle) / (self.numOfDetectors - 1))) + math.floor(size / 2)
            detectors_coords.append((x, y))

        return detectors_coords

    def scan(self, image, size):
        detectorsCoords = self.get_detectors_coords(size)
        scanResults = []
        for i in range(self.numOfDetectors):
            pixels = draw.line_nd((self.x, self.y), (detectorsCoords[i][0], detectorsCoords[i][1]))
            pixelsSum = sum(image[pixels])

            # TODO - test sum instead of avg
            scanResults.append(pixelsSum / len(pixels[0]))
            # scanResults.append(pixelsSum)
        return scanResults

    def read_sinogram(self, sinogram, size):
        detectorsCoords = self.get_detectors_coords(size)
        resultPixels = []

        for i in range(self.numOfDetectors):
            # TODO - Use draw.line_nd instead of bresenham.line
            #  P.S. It impacts on most nested 'for' loop in make_result_image

            pixels = draw.line_nd((math.floor(self.x), math.floor(self.y)),
                                  (math.floor(detectorsCoords[i][0]), math.floor(detectorsCoords[i][1])))

            # pixels = line(math.floor(self.x), math.floor(self.y), math.floor(detectorsCoords[i][0]),
            #               math.floor(detectorsCoords[i][1]))
            resultPixels.append(pixels)

        iteration = int(self.progressAngle / self.stepAngle)
        print("Iteracja: ", iteration)
        resultValues = sinogram[iteration]

        return resultPixels, resultValues


def make_sinogram(image, tomograph):
    sinogram = []
    while tomograph.progressAngle <= 360:
        sinogram.append(tomograph.scan(image, tomograph.radius * 2))
        tomograph.next_iteration()

    # print(sinogram)
    sinogram = utilities.normalize_sinogram(sinogram)
    # sinogram = utilities.normalize(sinogram)
    # for i in range(len(sinogram)):
    #     for j in range(len(sinogram[i])):
    #         if sinogram[i][j] > 255:
    #             print("Ping")
    io.imshow(np.array(sinogram, dtype=np.uint32), cmap='gray')
    io.show()

    # image = Image.fromarray(np.array(sinogram))
    # image.show()

    return sinogram


def make_result_image(sinogram, tomograph, radius):
    result_image = np.zeros((radius * 2, radius * 2), dtype=np.uint32)
    lines_per_pixel = np.zeros((radius * 2, radius * 2), dtype=np.uint32)
    tomograph.progressAngle = 0

    while tomograph.progressAngle <= 360:
        pixels, values = tomograph.read_sinogram(sinogram, radius * 2)
        for i in range(tomograph.numOfDetectors):
            # TODO - It needs to be changed if read_sinogram changed

            # for j in range(len(pixels[i])):
            #     result_value = result_image[pixels[i][j][0]][pixels[i][j][1]] + values[i]
            #     result_image[pixels[i][j][0]][pixels[i][j][1]] = result_value
            #     if result_value >= 255.0:
            #         result_image[pixels[i][j][0]][pixels[i][j][1]] = 255
            #     else:
            #         result_image[pixels[i][j][0]][pixels[i][j][1]] = result_value

            for j in range(len(pixels[i][0])):
                result_image[pixels[i][0][j]][pixels[i][1][j]] += values[i]
                lines_per_pixel[pixels[i][0][j]][pixels[i][1][j]] += 1

        tomograph.next_iteration()

    result_image = utilities.normalize_image(result_image)
    print(np.min(result_image))
    print(np.max(result_image))

    io.imshow(result_image, cmap='gray')
    io.show()

    image = Image.fromarray(result_image)
    image.show()
