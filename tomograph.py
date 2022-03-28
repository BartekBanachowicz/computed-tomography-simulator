import math
import numpy as np
from PIL import Image
from skimage import draw
from skimage import io

import utilities


class Tomograph:
    def __init__(self, numOfDetectors, detectionAngle, stepAngle, radius):
        self.numOfDetectors = numOfDetectors  # D
        self.detectionAngle = detectionAngle  # Phi
        self.stepAngle = stepAngle  # alpha
        self.progressAngle = 0.0  # progress angle
        self.radius = radius - 1
        self.x = self.radius * math.cos(math.radians(self.progressAngle)) + self.radius - 1
        self.y = self.radius * math.sin(math.radians(self.progressAngle)) + self.radius - 1

    def set_head_angle(self, angle):
        self.progressAngle = angle
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
            scanResults.append(pixelsSum / len(pixels[0]))
        return scanResults

    def read_sinogram(self, sinogram, size):
        detectorsCoords = self.get_detectors_coords(size)
        resultPixels = []

        for i in range(self.numOfDetectors):
            pixels = draw.line_nd((math.floor(self.x), math.floor(self.y)),
                                  (math.floor(detectorsCoords[i][0]), math.floor(detectorsCoords[i][1])))
            resultPixels.append(pixels)

        iteration = int(self.progressAngle / self.stepAngle)
        print("Iteracja: ", iteration)
        resultValues = sinogram[iteration]

        return resultPixels, resultValues


def make_sinogram(image, tomograph, boundary):
    sinogram = []
    while tomograph.progressAngle < boundary:
        sinogram.append(tomograph.scan(image, tomograph.radius * 2))
        tomograph.next_iteration()

    sinogram = utilities.normalize_sinogram(sinogram)
    io.imshow(np.array(sinogram, dtype=np.uint32), cmap='gray')
    io.show()

    return sinogram


def make_result_image(sinogram, tomograph, radius, boundary):
    result_image = np.zeros((radius * 2, radius * 2), dtype=np.uint32)
    lines_per_pixel = np.zeros((radius * 2, radius * 2), dtype=np.uint32)
    tomograph.progressAngle = 0

    while tomograph.progressAngle < boundary:
        pixels, values = tomograph.read_sinogram(sinogram, radius * 2)
        for i in range(tomograph.numOfDetectors):
            for j in range(len(pixels[i][0])):
                result_image[pixels[i][0][j]][pixels[i][1][j]] += values[i]
                lines_per_pixel[pixels[i][0][j]][pixels[i][1][j]] += 1

        tomograph.next_iteration()

    # for i in range(radius*2):
    #     for j in range(radius*2):
    #         if lines_per_pixel[i][j] != 0:
    #             result_image[i][j] = result_image[i][j]/lines_per_pixel[i][j]

    result_image = utilities.normalize_image(result_image)

    return result_image
