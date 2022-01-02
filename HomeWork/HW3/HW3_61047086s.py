import PySimpleGUI as sg
import os.path
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import math
from numpy import random
################ Importing Libraries #######################


def gui(graph_count):
    # Limited File Types minimizing the error
    global resized_image,figure_canvas
    file_types = [("JPEG (*.jpg)", "*.jpg"), ("BMP (*.bmp)", "*.bmp"), ("PPM (*.ppm)", "*.ppm"),  ("PNG (*.png)", "*.png"),
                  ("All files (*.*)", "*.*")]

    # Layout of the User Interface
    layout = [
        [sg.FileBrowse(file_types=file_types, key="-FILE-"),
         sg.Button('Load Image Grayscaled'),sg.Cancel('Exit')],
        [sg.InputText(size=(15, 15),key="-VARIANCE-",),sg.T('Enter Variance')],
        [sg.Button('Apply Gaussian Noise'),sg.Button('Histogram of Gaussian Image')],
        [sg.Image(key="-INPUT IMAGE-"),sg.Image(key="-OUTPUT IMAGE-"),sg.Canvas(key="-HISTOGRAM-")]
    ]
    window = sg.Window('HW3_61047086s', layout)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED,'Exit'):
            break

        # Read Image
        elif event == 'Load Image Grayscaled':
            input_image_path = values['-FILE-']
            if os.path.exists(input_image_path):
                gray_image = cv2.imread(values["-FILE-"],0)
                resized_image = cv2.resize(gray_image,(500,500))
                input_imgbytes = cv2.imencode(".png", resized_image)[1].tobytes()
                # Fetch the byte data from the in-memory file and Pass the data to the sg.Image object in the window.update() method
                window["-INPUT IMAGE-"].update(data=input_imgbytes)

        # Load Image Applying Gaussian Noise
        elif event == 'Apply Gaussian Noise':
            var_sigma = values['-VARIANCE-']
            Noisy_image,noise_record = Gaussian_Noise(var_sigma,resized_image)
            input_imgbytes = cv2.imencode(".png", Noisy_image)[1].tobytes()
            # Fetch the byte data from the in-memory file and Pass the data to the sg.Image object in the window.update() method
            window["-OUTPUT IMAGE-"].update(data=input_imgbytes)

        # Load Histogram
        elif event == 'Histogram of Gaussian Image':
            if graph_count == 0:
                fig,histogram_axis = create_histogram(noise_record)
                figure_canvas = show_histogram(window["-HISTOGRAM-"].TKCanvas, fig)
                graph_count += 1
            else:
                delete_histogram(figure_canvas)
                fig, histogram_axis = create_histogram(noise_record)
                figure_canvas = show_histogram(window["-HISTOGRAM-"].TKCanvas, fig)
    window.close()


def show_histogram(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


def create_histogram(resized_image):
    Image_Height = resized_image.shape[0]
    Image_Width = resized_image.shape[1]
    image_histogram = np.zeros([256])
    for h_pixel in range(0, Image_Height):
        for w_pixel in range(0, Image_Width):
            image_histogram[int(round(resized_image[h_pixel,w_pixel]))] += 1

    # Creating histogram
    fig, histogram_axis = plt.subplots(1, 1, figsize=(5, 5))
    histogram_axis.plot(image_histogram)
    return fig, histogram_axis


def Gaussian_Noise(var_sigma,resized_image):
    gaussian_image = np.full(resized_image.shape, 0, dtype=np.float32)
    new_image = np.full(resized_image.shape, 0, dtype=np.float32)
    noise_record = np.empty(resized_image.shape, dtype=np.float32)
    sd_sigma = float(var_sigma)

    for h_pixel in range(resized_image.shape[0]):
        for w_pixel in range(resized_image.shape[1] - 1):
            r = random.rand(1)
            var_phi = random.rand(1)
            z1, z2 = box_mueller_transform(sd_sigma,r, var_phi)
            gaussian_image[h_pixel, w_pixel] = resized_image[h_pixel, w_pixel] + z1
            gaussian_image[h_pixel, w_pixel + 1] = resized_image[h_pixel, w_pixel + 1] + z2
            noise_record[h_pixel, w_pixel] = z1
            noise_record[h_pixel, w_pixel + 1] = z2
            # Step 5 setting the new image I
            if gaussian_image[h_pixel, w_pixel] < 0:
                new_image[h_pixel, w_pixel] = 0
            elif gaussian_image[h_pixel, w_pixel] > 254:
                new_image[h_pixel, w_pixel] = 254
            else:
                new_image[h_pixel, w_pixel] = gaussian_image[h_pixel, w_pixel]
            # Step 5 setting the new image II
            if gaussian_image[h_pixel, w_pixel + 1] < 0:
                new_image[h_pixel, w_pixel + 1] = 0
            elif gaussian_image[h_pixel, w_pixel + 1] > 254:
                new_image[h_pixel, w_pixel + 1] = 254
            else:
                new_image[h_pixel, w_pixel + 1] = gaussian_image[h_pixel, w_pixel + 1]
    return new_image,noise_record

def box_mueller_transform(sd_sigma,r, var_phi):
    z1 = sd_sigma * math.cos(2 * math.pi * var_phi) * np.sqrt(-2 * np.log(r))
    z2 = sd_sigma * math.sin(2 * math.pi * var_phi) * np.sqrt(-2 * np.log(r))
    return z1, z2


def delete_histogram(figure):
    figure.get_tk_widget().forget()
    plt.close('all')


if __name__=="__main__":
    gui(graph_count = 0)