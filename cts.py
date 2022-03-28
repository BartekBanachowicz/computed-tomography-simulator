import numpy as np
import streamlit as st
from PIL import Image

import utilities
from tomograph import Tomograph, make_result_image, make_sinogram

ALLOWED_IMAGE_FORMATS = {"jpeg", "png", "jpg", "dcm"}
DICOM_FORMAT = "dcm"


class Sliders:
    def __init__(self):
        self.detectors_number = st.sidebar.slider('Number of detectors', 0, 300, 180)
        self.detection_angle = st.sidebar.slider('Detection angle [degrees]', 0, 360, 120)
        self.step = st.sidebar.slider('Rotation per iteration [degrees]', 1, 30, 4)
        self.boundary = st.sidebar.slider('Boundary angle [degrees]', 0, 360, 360)


class InputFields:
    def __init__(self, container):
        self.patients_id = container.text_input("Patient's ID:", )
        self.patients_name = container.text_input("Patient's name and surname:")
        self.examination_date = container.date_input("Examination date:")


def handle_dicom_file(file):
    dicom = utilities.extract_dicom_data(file)
    st.session_state.image = dicom.image


def handle_upload():
    file = st.session_state.uploaded_file
    file_extension = st.session_state.uploaded_file.name.split(".")[1]
    if file_extension in ALLOWED_IMAGE_FORMATS:
        st.session_state['image'] = Image.open(st.session_state.uploaded_file)
    elif file_extension == DICOM_FORMAT:
        handle_dicom_file(file)
    else:
        print("Unexpected file format", file_extension)


def run_and_display(sinogram_container, tomograph_container):
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


def checkFileUploaded():
    if st.session_state.uploaded_file is not None:
        handle_upload()


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
    checkFileUploaded()

    mainContainer = st.container()
    inputColumn, previewColumn = mainContainer.columns(2)

    init_session_state(previewColumn)

    sliders = Sliders()
    inputs = InputFields(inputColumn)

    resultContainer = st.container()
    sinogram, tomograph = resultContainer.columns(2)

    if st.sidebar.button("Run") and st.session_state.image is not None:
        run_and_display(sinogram_container=sinogram, tomograph_container=tomograph)
