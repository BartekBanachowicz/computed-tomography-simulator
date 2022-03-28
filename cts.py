import numpy as np
import matplotlib as mt
import streamlit as st
from tomograph import Tomograph, make_sinogram, make_result_image
from PIL import Image
import utilities

if __name__ == '__main__':

    if 'image' not in st.session_state:
        st.session_state['image'] = None
    if 'radius' not in st.session_state:
        st.session_state['radius'] = None

    st.title('Computed Tomography Simulator')

    filename = st.sidebar.text_input("File name")
    if len(filename) > 0:
        st.session_state.image, st.session_state.radius = utilities.read_image(filename)

    detectors_number = st.sidebar.slider('Number of detectors', 0, 300, 180)
    detection_angle = st.sidebar.slider('Detection angle [degrees]', 0, 360, 120)
    step = st.sidebar.slider('Rotation per iteration [degrees]', 1, 30, 4)

    if st.sidebar.button("Run") and st.session_state.image is not None and st.session_state.radius is not None:
        tomograph = Tomograph(detectors_number, detection_angle, step, st.session_state.radius)
        sinogram = make_sinogram(st.session_state.image, tomograph)
        image = Image.fromarray(np.array(sinogram))
        image = image.convert('RGB')
        st.image(image)
        make_result_image(sinogram, tomograph, st.session_state.radius)

    # image, radius = utilities.read_image("photos/CT_ScoutView.jpg")
    # image, radius = utilities.read_image("photos/Kropka.jpg")
    # image, radius = utilities.read_image("photos/Kwadraty2.jpg")
    # image, radius = utilities.read_image("photos/SADDLE_PE-large.JPG")
    # image, radius = utilities.read_image("photos/Shepp_logan.jpg")

    # io.imshow(image, cmap='gray')
    # io.show()
    # utilities.write_result(None)
