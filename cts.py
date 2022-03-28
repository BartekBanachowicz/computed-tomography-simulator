import numpy as np
import streamlit as st
from PIL import Image

import utilities
from tomograph import Tomograph, make_result_image, make_sinogram

ALLOWED_IMAGE_FORMATS = {"jpeg", "png", "jpg", "dcm"},
DICOM_FORMAT = "dcm"


class Sliders:
    def __init__(self):
        self.detectors_number = st.sidebar.slider('Number of detectors', 0, 300, 180)
        self.detection_angle = st.sidebar.slider('Detection angle [degrees]', 0, 360, 120)
        self.step = st.sidebar.slider('Rotation per iteration [degrees]', 1, 30, 4)
        self.boundary = st.sidebar.slider('Boundary angle [degrees]', 0, 360, 360)


def handle_dicom_file(st, file):
    dicom = utilities.extract_dicom_data(file)
    st.session_state.image = dicom.image


if __name__ == '__main__':
    st.title('Computed Tomography Simulator')
    st.sidebar.header("Control panel")

    if 'image' not in st.session_state:
        st.session_state['image'] = None
    if 'radius' not in st.session_state:
        st.session_state['radius'] = None

    st.session_state['uploaded_file'] = st.sidebar.file_uploader("Upload your file")
    if st.session_state.uploaded_file is not None:
        file = st.session_state.uploaded_file
        file_extension = st.session_state.uploaded_file.name.split(".")[1]

        if file_extension in ALLOWED_IMAGE_FORMATS:
            st.session_state['image'] = Image.open(st.session_state.uploaded_file)
        elif file_extension == DICOM_FORMAT:
            handle_dicom_file(st, file)
        else:
            print("Unexpected file format {}", file_extension)

    container1 = st.container()
    col1, col2 = container1.columns(2)

    sliders = Sliders()


    patients_id = col1.text_input("Patient's ID:", )
    patients_name = col1.text_input("Patient's name and surname:")
    examination_date = col1.date_input("Examination date:")

    if st.session_state.image is not None:
        col2.text("Imported image")
        col2.image(st.session_state.image)

    container2 = st.container()
    col21, col22 = container2.columns(2)

    if st.sidebar.button("Run") and st.session_state.image is not None:
        image_array, st.session_state['radius'] = utilities.read_image(st.session_state.image)

        tomograph = Tomograph(sliders.detectors_number, sliders.detection_angle, sliders.step, st.session_state.radius)
        sinogram = make_sinogram(image_array, tomograph, sliders.boundary)

        sinogram_to_display = Image.fromarray(np.array(sinogram))
        sinogram_to_display = sinogram_to_display.convert('RGB')
        col21.image(sinogram_to_display, width=350)

        result_image = make_result_image(sinogram, tomograph, st.session_state.radius, boundary)
        result_image = Image.fromarray(result_image)
        result_image = result_image.convert('RGB')
        col22.image(result_image, width=350, clamp=True)
