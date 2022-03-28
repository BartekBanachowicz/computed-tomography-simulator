import numpy as np
import streamlit as st
from PIL import Image

import DicomUtils
import utilities
from tomograph import Tomograph, make_result_image, make_sinogram

ALLOWED_IMAGE_FORMATS = {"jpeg", "png", "jpg"}
DICOM_FORMAT = "dcm"


def existing(key):
    if key not in st.session_state:
        return False
    else:
        return True


class Sliders:
    def __init__(self):
        self.detectors_number = st.sidebar.slider('Number of detectors', 0, 300, 180, key="detectors")
        self.detection_angle = st.sidebar.slider('Detection angle [degrees]', 0, 360, 120, key="angle")
        self.step = st.sidebar.slider('Rotation per iteration [degrees]', 1, 30, 4, key="step")
        self.boundary = st.sidebar.slider('Boundary angle [degrees]', 0, 360, 360, key="boundary")


class InputFields:
    def __init__(self, container, dicom=None):
        if dicom is not None:
            self.patient_id = container.text_input("Patient's ID:", value=dicom.patient.id)
            self.patient_name = container.text_input("Patient's name and surname:", value=dicom.patient.name)
            self.examination_date = container.date_input("Examination date:", value=dicom.study_date)
        else:
            self.patient_id = container.text_input("Patient's ID:")
            self.patient_name = container.text_input("Patient's name and surname:")
            self.examination_date = container.date_input("Examination date:")


def handle_dicom_file(file, inputFieldsContainer):
    dicom = DicomUtils.Dicom(file)
    st.session_state.dicom = dicom
    st.session_state.image = dicom.image
    InputFields(inputFieldsContainer, dicom)


def handle_image_file(inputFieldsContainer):
    st.session_state.image = Image.open(st.session_state.uploaded_file)
    InputFields(inputFieldsContainer)


def handle_upload(inputFieldsContainer):
    if st.session_state.uploaded_file is not None:
        file = st.session_state.uploaded_file
        file_extension = st.session_state.uploaded_file.name.split(".")[1]
        if file_extension in ALLOWED_IMAGE_FORMATS:
            handle_image_file(inputFieldsContainer)
        elif file_extension == DICOM_FORMAT:
            handle_dicom_file(file, inputFieldsContainer)
        else:
            print("Unexpected file format", file_extension)


def run_and_display(sinogram_container, tomograph_container, sliders):
    image_array, st.session_state['radius'] = utilities.read_image(st.session_state.image)

    tomograph = Tomograph(sliders.detectors_number, sliders.detection_angle, sliders.step, st.session_state.radius)
    sinogram = make_sinogram(image_array, tomograph, sliders.boundary)

    sinogram_image = Image.fromarray(np.array(sinogram))
    sinogram_image = sinogram_image.convert('RGB')

    sinogram_container.image(sinogram_image, width=350)

    tomograph_image = make_result_image(sinogram, tomograph, st.session_state.radius, sliders.boundary)
    tomograph_image = Image.fromarray(tomograph_image)
    tomograph_image = tomograph_image.convert('RGB')

    tomograph_container.image(tomograph_image, width=350, clamp=True)


def init_session_state(previewContainer):
    if 'image' not in st.session_state:
        st.session_state.image = None
    if 'radius' not in st.session_state:
        st.session_state.radius = None

    if st.session_state.image is not None:
        previewContainer.text("Imported image")
        previewContainer.image(st.session_state.image)


if __name__ == '__main__':
    st.title('Computed Tomography Simulator')
    st.sidebar.header("Control panel")

    st.session_state.uploaded_file = st.sidebar.file_uploader("Upload your file")

    mainContainer = st.container()
    inputColumn, previewColumn = mainContainer.columns(2)
    init_session_state(previewColumn)
    sliders = Sliders()

    handle_upload(inputColumn)

    resultContainer = st.container()
    sinogram, tomograph = resultContainer.columns(2)

    dataToSave = False
    if st.sidebar.button("Run") and st.session_state.image is not None:
        run_and_display(sinogram_container=sinogram, tomograph_container=tomograph, sliders=sliders)
        dataToSave = True

    if dataToSave and st.sidebar.button("Export DICOM"):
        DicomUtils.saveDicom(st.session_state.dicom)
