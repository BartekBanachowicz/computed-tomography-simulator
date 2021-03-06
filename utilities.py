import datetime
import math

import numpy as np
import pydicom._storage_sopclass_uids
from pydicom import dcmread
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
    maxVal = maksimum(sinogram)
    factor = 255.0 / maxVal
    for i in range(len(sinogram)):
        for j in range(len(sinogram[i])):
            temp = sinogram[i][j] * factor
            sinogram[i][j] = temp

    return sinogram


def normalize_image(image):
    maxVal = maksimum(image)
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

    return image


def read_image(image):
    image = np.asarray(image)
    h, w = (image.shape[0], image.shape[1])
    radius = math.ceil(math.sqrt(w ** 2 + h ** 2) / 2)
    print("H: ", h, " W: ", w, " Radius: ", radius)
    image = resize_image(image, radius * 2)

    return image, radius


def write_result(image, patient, filename):
    meta = Dataset()
    meta.MediaStorageSOPClassUID = pydicom._storage_sopclass_uids.CTImageStorage
    meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

    ds = FileDataset(None, {}, preamble=b"\0" * 128)
    ds.file_meta = meta

    ds.is_little_endian = True
    ds.is_implicit_VR = False

    ds.SOPClassUID = pydicom._storage_sopclass_uids.CTImageStorage
    ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID

    ds.PatientName = patient["Name"]
    ds.PatientID = patient["ID"]
    ds.ImageComments = patient["Comments"]

    ds.Modality = "CT"
    ds.SeriesInstanceUID = pydicom.uid.generate_uid()
    ds.StudyInstanceUID = pydicom.uid.generate_uid()
    ds.FrameOfReferenceUID = pydicom.uid.generate_uid()

    ds.BitsStored = 8
    ds.BitsAllocated = 8
    ds.SamplesPerPixel = 1
    ds.HighBit = 7

    ds.ImagesInAcquisition = 1
    ds.InstanceNumber = 1

    ds.Rows, ds.Columns = image.shape

    ds.ImageType = r"ORIGINAL\PRIMARY\AXIAL"

    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 0

    pydicom.dataset.validate_file_meta(ds.file_meta, enforce_standard=True)

    ds.PixelData = image.tobytes()

    ds.save_as(filename, write_like_original=False)


class Patient:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Dicom:
    def __init__(self, patient, date, image):
        self.patient = patient
        self.study_date = datetime.date(int(date[0:4]), int(date[4:6]), int(date[6:]))
        self.image = image


def extract_dicom_data(input_file):
    ds = dcmread(input_file)
    print(ds.PatientID)
    image = extract_dicom_image(ds)
    patient = Patient(ds.PatientID, ds.PatientName)
    dicom = Dicom(patient, ds.StudyDate, image)
    return dicom


def extract_dicom_image(dicom_data):
    print("extracting dicom image")
    pixels = dicom_data.pixel_array
    return (pixels - pixels.min()) / (pixels.max() - pixels.min())
