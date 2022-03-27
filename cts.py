import streamlit as st
from tomograph import Tomograph, make_sinogram, make_result_image
import utilities

if __name__ == '__main__':
    st.title('Computed Tomography Simulator')

    # image, radius = utilities.read_image("photos/CT_ScoutView.jpg")
    # image, radius = utilities.read_image("photos/Kropka.jpg")
    image, radius = utilities.read_image("photos/Kwadraty2.jpg")
    # image, radius = utilities.read_image("photos/SADDLE_PE-large.JPG")
    # image, radius = utilities.read_image("photos/Shepp_logan.jpg")

    data_load_state = st.text('Data have been loaded successfully')

    tomograph = Tomograph(180, 120, 4, radius)
    sinogram = make_sinogram(image, tomograph)

    make_result_image(sinogram, tomograph, radius)
    # io.imshow(image, cmap='gray')
    # io.show()
    # utilities.write_result(None)
