import PySimpleGUI as sg
import os.path
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

################ Importing Libraries #######################


def gui(graph_count):
    # Limited File Types minimizing the error
    global resized_image,figure_canvas
    file_types = [("JPEG (*.jpg)", "*.jpg"), ("BMP (*.bmp)", "*.bmp"), ("PPM (*.ppm)", "*.ppm"),  ("PNG (*.png)", "*.png"),
                  ("All files (*.*)", "*.*")]

    # Layout of the User Interface
    layout = [
        [sg.FileBrowse(file_types=file_types, key="-FILE-"),
         sg.Button('Load Image as GrayScale'),
         sg.Button('Histogram'),
         sg.Cancel('Exit')],
        [sg.Image(key="-INPUT IMAGE-"),sg.Canvas(key="-HISTOGRAM-")]
    ]
    window = sg.Window('HW2_61047086s', layout)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED,'Exit'):
            break

        # Read Image
        elif event == 'Load Image as GrayScale':
            input_image_path = values['-FILE-']
            if os.path.exists(input_image_path):
                input_image = cv2.imread(values["-FILE-"])
                # Calling Grayscale Function
                gray_image = grayscale_conversion(input_image)
                resized_image = cv2.resize(gray_image,(500,500))
                input_imgbytes = cv2.imencode(".png", resized_image)[1].tobytes()
                # Fetch the byte data from the in-memory file and Pass the data to the sg.Image object in the window.update() method
                window["-INPUT IMAGE-"].update(data=input_imgbytes)

        # Load Histogram
        elif event == 'Histogram':
            # For first graph
            if graph_count == 0:
                # Create Histogram
                fig,histogram_axis = create_histogram(resized_image)
                # Show Histogram
                figure_canvas = show_histogram(window["-HISTOGRAM-"].TKCanvas, fig)
                graph_count += 1
            else:
                # Delete previous plot and canvas
                delete_histogram(figure_canvas)
                fig, histogram_axis = create_histogram(resized_image)
                figure_canvas = show_histogram(window["-HISTOGRAM-"].TKCanvas, fig)
    window.close()

def show_histogram(canvas, figure):
    # Creating a new canvas using Tkinter integrated matplotlib and plotting the figure on windows
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

def create_histogram(resized_image):
    # Create the histogram of image in array format
    Image_Height = resized_image.shape[0]
    Image_Width = resized_image.shape[1]
    image_histogram = np.zeros([256], np.int32)
    for h_pixel in range(0, Image_Height):
        for w_pixel in range(0, Image_Width):
            image_histogram[resized_image[h_pixel, w_pixel]] += 1
    # Creating histogram
    fig, histogram_axis = plt.subplots(1, 1, figsize=(5, 5))
    histogram_axis.plot(image_histogram)
    return fig, histogram_axis

def grayscale_conversion(input_image):
    # Convert to grayscale
    gray_image = np.full(input_image.shape, 0, dtype=np.uint8)
    for h_pixel in range(input_image.shape[0]):
        for w_pixel in range((input_image.shape[1])):
            # Find the average of the BGR pixel values
            gray_image[h_pixel, w_pixel] = sum(input_image[h_pixel, w_pixel]) * 0.33
    return gray_image

def delete_histogram(figure):
    # Deleting the previous Histogram
    figure.get_tk_widget().forget()
    plt.close('all')


if __name__=="__main__":
    gui(graph_count = 0)