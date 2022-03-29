import datetime

import imageio
import numpy as np
import pydicom
from pydicom import dcmread, Dataset, FileDataset
from PIL import Image


class Patient:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class DicomWrapper:
    def __init__(self, input_file):
        ds = dcmread(input_file)
        self.originalDicom = ds
        self.image = self._extract_dicom_image(ds)

        self.patient = Patient(None, None)
        if "PatientID" in ds:
            self.patient.id = ds.PatientID
        if "PatientName" in ds:
            self.patient.name = ds.PatientName

        if "StudyDate" in ds:
            date = ds.StudyDate
            self.study_date = datetime.date(int(date[0:4]), int(date[4:6]), int(date[6:]))
        else:
            self.study_date = None

        if "ImageComments" in ds:
            self.image_comments = ds.ImageComments
        else:
            self.image_comments = None

    def _extract_dicom_image(self, dicom_data):
        print("extracting dicom image")
        pixels = dicom_data.pixel_array
        return (pixels - pixels.min()) / (pixels.max() - pixels.min())


def createNewMetadata():
    m = Dataset()
    m.MediaStorageSOPClassUID = pydicom._storage_sopclass_uids.CTImageStorage
    m.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    m.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
    return m


def createNewDicom(image_shape):
    metadata = createNewMetadata()

    ds = FileDataset(None, {}, preamble=b"\0" * 128)
    set_required_params(ds, image_shape, metadata)

    return ds


def set_required_params(ds, image_shape, metadata):
    ds.file_meta = metadata
    ds.is_little_endian = True
    ds.is_implicit_VR = True
    ds.SOPClassUID = pydicom._storage_sopclass_uids.CTImageStorage
    ds.SOPInstanceUID = metadata.MediaStorageSOPInstanceUID
    ds.Modality = "CT"
    ds.SeriesInstanceUID = pydicom.uid.generate_uid()
    ds.StudyInstanceUID = pydicom.uid.generate_uid()
    ds.FrameOfReferenceUID = pydicom.uid.generate_uid()
    ds.BitsStored = 16
    ds.BitsAllocated = 16
    ds.SamplesPerPixel = 1
    ds.HighBit = 15
    ds.ImagesInAcquisition = 1
    ds.InstanceNumber = 1
    ds.SmallestImagePixelValue = b'\\x00\\x00'
    ds.LargestImagePixelValue = b'\\xff\\xff'

    ds.Columns, ds.Rows = image_shape
    print(image_shape)
    ds.ImageType = r"ORIGINAL\PRIMARY\AXIAL"
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 0
    pydicom.dataset.validate_file_meta(ds.file_meta, enforce_standard=True)


def getFormattedDate(date):
    return str(date.year) + fill_zeros(date.month) + str(date.day)


def fill_zeros(date):
    x = str(date)
    if len(x) == 1:
        return "0" + x
    else:
        return x


def convert(inputImage):
    inputImage.save("test123.jpg")
    return imageio.imread("test123.jpg", pilmode="L")


# todo?

def saveDicom(inputFields, inputImage, dicomWrapper=None):
    image = convert(inputImage)
    if image.dtype != np.uint16:
        image = image.astype(np.uint16)

    print("Saving dicom")
    if dicomWrapper is None:
        print("No input dicom found, creating new")
        dicom = createNewDicom(image.shape)
    else:
        print("Input dicom found, importing data")
        dicom = dicomWrapper.originalDicom
        set_required_params(dicom, image.shape, createNewMetadata())

    dicom.PixelData = image.tostring()
    dicom.PatientName = inputFields.patient_name
    dicom.PatientID = inputFields.patient_id
    dicom.StudyDate = getFormattedDate(inputFields.examination_date)
    dicom.ImageComments = inputFields.image_comments

    dicom.save_as("test.dcm", write_like_original=False)


def saveModifiedDicom(inputFields, dicomWrapper):
    print("Saving dicom")
    print("Input dicom found, importing data")
    dicom = dicomWrapper.originalDicom

    dicom.PatientName = inputFields.patient_name
    dicom.PatientID = inputFields.patient_id
    dicom.StudyDate = getFormattedDate(inputFields.examination_date)
    dicom.ImageComments = inputFields.image_comments

    dicom.save_as("test.dcm", write_like_original=False)
