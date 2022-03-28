import datetime

import numpy as np
import pydicom
from pydicom import dcmread, Dataset, FileDataset
from skimage import img_as_ubyte
from skimage.exposure import rescale_intensity


class Patient:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class DicomWrapper:
    def __init__(self, input_file):
        ds = dcmread(input_file)
        self.originalDicom = ds
        self.image = self._extract_dicom_image(ds)
        self.patient = Patient(ds.PatientID, ds.PatientName)
        date = ds.StudyDate
        self.study_date = datetime.date(int(date[0:4]), int(date[4:6]), int(date[6:]))

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
    ds.file_meta = metadata
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    ds.SOPClassUID = pydicom._storage_sopclass_uids.CTImageStorage
    ds.SOPInstanceUID = metadata.MediaStorageSOPInstanceUID

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

    ds.Rows, ds.Columns = image_shape

    ds.ImageType = r"ORIGINAL\PRIMARY\AXIAL"

    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 0

    pydicom.dataset.validate_file_meta(ds.file_meta, enforce_standard=True)

    return ds


def saveDicom(inputFields, inputImage, dicomWrapper=None):
    image = img_as_ubyte(rescale_intensity(np.array(inputImage), out_range=(0.0, 1.0)))
    print("Saving dicom")
    if dicomWrapper is None:
        print("No input dicom found, creating new")
        dicom = createNewDicom(image.shape)
    else:
        dicom = dicomWrapper.originalDicom
        dicom.PixelData = image.tobytes()
        dicom.PatientName = inputFields.patient_name
        dicom.PatientID = inputFields.patient_id
        dicom.StudyDate = str(inputFields.examination_date.year) + str(inputFields.examination_date.month) + str(
            inputFields.examination_date.day)
        dicom.file_meta = createNewMetadata()

    dicom.save_as("test.dcm", write_like_original=False)
