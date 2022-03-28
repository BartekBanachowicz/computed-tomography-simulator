import datetime

from pydicom import dcmread


class Patient:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Dicom:

    def fromFile(self, patient, date, image):
        self.patient = patient
        self.study_date = datetime.date(int(date[0:4]), int(date[4:6]), int(date[6:]))
        self.image = image

    def __init__(self, input_file):
        ds = dcmread(input_file)
        self.image = self._extract_dicom_image(ds)
        self.patient = Patient(ds.PatientID, ds.PatientName)
        date = ds.StudyDate
        self.study_date = datetime.date(int(date[0:4]), int(date[4:6]), int(date[6:]))

    def _extract_dicom_image(self, dicom_data):
        print("extracting dicom image")
        pixels = dicom_data.pixel_array
        return (pixels - pixels.min()) / (pixels.max() - pixels.min())
