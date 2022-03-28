import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from tomograph import Tomograph, make_result_image
from PIL import Image
import utilities
import time
import math


def make_sinogram(image, tomograph):
    sinogram = []
    while tomograph.progressAngle <= 360:
        sinogram.append(tomograph.scan(image, tomograph.radius * 2))
        tomograph.next_iteration()

    sinogram = utilities.normalize_sinogram(sinogram)
    io.imshow(np.array(sinogram, dtype=np.uint32), cmap='gray')
    io.show()

    return sinogram


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

        sinogram = np.zeros((math.ceil(360/step), detectors_number), dtype=np.uint32)
        fig = plt.figure(figsize=(40, 15))
        sinogram_plot = st.empty()

        for i in range(0, 360, step):
            tomograph.set_head_angle(i)
            sinogram_row = tomograph.scan(st.session_state.image, st.session_state.radius * 2)
            sinogram[int(i/step)] = sinogram_row



        print("Done")
        start = time.time()
        plt.imshow(sinogram, cmap='gray')
        # sinogram_plot.empty()
        sinogram_plot.pyplot(fig)
        end = time.time()
        print("Iteracja ", i, ": ", end-start)
        # fig, plot = plt.subplot(1, 1)

        # image = Image.fromarray(np.array(sinogram))
        # image = image.convert('RGB')
        # st.image(image, width=500)
        # make_result_image(sinogram, tomograph, st.session_state.radius)

    # image, radius = utilities.read_image("photos/CT_ScoutView.jpg")
    # image, radius = utilities.read_image("photos/Kropka.jpg")
    # image, radius = utilities.read_image("photos/Kwadraty2.jpg")
    # image, radius = utilities.read_image("photos/SADDLE_PE-large.JPG")
    # image, radius = utilities.read_image("photos/Shepp_logan.jpg")

    # io.imshow(image, cmap='gray')
    # io.show()
    # utilities.write_result(None)
