import PySimpleGUI as sg
import os.path
import cv2
import numpy as np


################ Importing Libraries #######################


def gui():
    # Limited File Types minimizing the error
    global resized_image, resized_gray_image
    file_types = [("JPEG (*.jpg)", "*.jpg"), ("BMP (*.bmp)", "*.bmp"), ("PPM (*.ppm)", "*.ppm"),
                  ("PNG (*.png)", "*.png"),
                  ("All files (*.*)", "*.*")]

    # Layout of the User Interface
    layout = [
        [sg.FileBrowse(file_types=file_types, key="-FILE-"),
         sg.Button('Load Image as GrayScale'), sg.Cancel('Exit')],
        [sg.InputText(size=(15, 15), key="-Iterations-", ), sg.T('Enter Iterations')],
        [sg.Button('Wavelet Transform'), ],
        [sg.Image(key="-INPUT IMAGE-"), sg.Image(key="-OUTPUT IMAGE-")]
    ]
    window = sg.Window('HW4_61047086s', layout)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        # Read Image
        elif event == 'Load Image as GrayScale':
            input_image_path = values['-FILE-']
            if os.path.exists(input_image_path):
                input_gray_image = cv2.imread(values["-FILE-"], 0)
                resized_gray_image = cv2.resize(input_gray_image, (512, 512), interpolation = cv2.INTER_CUBIC)
                input_imgbytes = cv2.imencode(".png", resized_gray_image)[1].tobytes()
                # Fetch the byte data from the in-memory file and Pass the data to the sg.Image object in the window.update() method
                window["-INPUT IMAGE-"].update(data=input_imgbytes)

        # Wavelet Transform
        elif event == 'Wavelet Transform':
            var_sigma = int(values['-Iterations-'])
            transformed_image = wavelet_transform(var_sigma, resized_gray_image)
            input_imgbytes = cv2.imencode(".png", transformed_image)[1].tobytes()
            window["-OUTPUT IMAGE-"].update(data=input_imgbytes)
            pass
    window.close()


def wavelet_transform(var_sigma, resized_gray_image):
    image = resized_gray_image
    scaling_function = var_sigma
    height, width = image.shape[:2]
    resultant_image = np.copy(image)

    if scaling_function == 0:
        return image
    else:
        for iterations in range(0, scaling_function):
            temp_image = HaarTransform(resultant_image[:height, :width])
            resultant_image[:height, :width] = temp_image[:height, :width]
            height = height // 2
            width = width // 2

    resultant_image = resultant_image.astype(np.uint8)
    return resultant_image

def HaarTransform(image):
    global wavelet_image
    result_img = np.copy(image).astype(np.float64)
    height, width = image.shape[:2]
    top_left = np.zeros((height,width),dtype=np.float64)
    top_right = np.zeros((height,width),dtype=np.float64)
    bottom_right = np.zeros((height,width),dtype=np.float64)
    bottom_left = np.zeros((height,width),dtype=np.float64)
    downsampling = 2
    for h_row in range(0,height//downsampling):
        for w_col in range(0,width//downsampling):

            # taking the pairs
            first_pair_pixel = result_img[0+2*h_row][0+2*w_col]
            second_pair_pixel = result_img[1+2*h_row][0+2*w_col]
            third_pair_pixel = result_img[0+2*h_row][1+2*w_col]
            fourth_pair_pixel = result_img[1+2*h_row][1+2*w_col]

            # According to page 16 pf ppt chapter 3.3 the Haar Algorithm
            Haar_algorithm_for_top_left = (first_pair_pixel+second_pair_pixel+third_pair_pixel+fourth_pair_pixel)//4
            Haar_algorithm_for_top_right = (first_pair_pixel-second_pair_pixel+third_pair_pixel-fourth_pair_pixel)//4
            Haar_algorithm_for_bottom_left = (first_pair_pixel+second_pair_pixel-third_pair_pixel-fourth_pair_pixel)//4
            Haar_algorithm_for_bottom_right = (first_pair_pixel-second_pair_pixel-third_pair_pixel+fourth_pair_pixel)//4

            # Separating the coefficient images on separate variable for further processing
            top_left[h_row,w_col] = Haar_algorithm_for_top_left
            top_right[h_row + width // downsampling, w_col] = Haar_algorithm_for_top_right
            bottom_left[h_row, w_col + height // downsampling] = Haar_algorithm_for_bottom_left
            bottom_right[h_row + width // downsampling, w_col + height // downsampling] = Haar_algorithm_for_bottom_right

    # Normalizing the images
    top_left = (np.abs(top_left)  / np.max(top_left))*255
    top_right = (np.abs(top_right) / np.max(top_right))*255
    bottom_left = (np.abs(bottom_left) / np.max(bottom_left))*255
    bottom_right = (np.abs(bottom_right) / np.max(bottom_right))*255

    # concatenating the image
    wavelet_image = top_left+top_right+bottom_left+bottom_right

    return wavelet_image


if __name__ == "__main__":
    gui()
