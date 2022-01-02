import PySimpleGUI as sg
import os.path
import cv2
import numpy as np
# Limited File Types minimizing the error
file_types = [("JPEG (*.jpg)", "*.jpg"),("BMP (*.bmp)", "*.bmp"),("PPM (*.ppm)", "*.ppm"),
              ("All files (*.*)", "*.*")]
# Layout of the User Interface
layout = [
    [sg.FileBrowse(file_types = file_types, key="-FILE-"),
    sg.Button('Load Image'),
    sg.Button("Save"), sg.Cancel('Exit')],

    [sg.Image(key="-INPUT IMAGE-"),sg.Image(key="-OUTPUT IMAGE-")]

]

window = sg.Window('HW1_61047086s', layout)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED,'Exit'):
        break
    # Read Image
    elif event == 'Load Image':
        input_image_path = values['-FILE-']
        if os.path.exists(input_image_path):
            input_image = cv2.imread(values["-FILE-"])
            input_resized_image = cv2.resize(input_image,(300,300))
            input_imgbytes = cv2.imencode(".png", input_resized_image)[1].tobytes()
            # Fetch the byte data from the in-memory file and Pass the data to the sg.Image object in the window.update() method
            window["-INPUT IMAGE-"].update(data=input_imgbytes)
            output_image = np.full(input_resized_image.shape,0,dtype=np.uint8)
            # Dimension Values of input image
            height = input_resized_image.shape[0]
            width = input_resized_image.shape[1]
            # iterating over each pixel and writing to a new file
            for h_pixel in range(height):
                for w_pixel in range(width):
                    # Copying pixel value from input image to output image
                    output_image[h_pixel, w_pixel] = input_resized_image[h_pixel, w_pixel]
            output_imgbytes = cv2.imencode(".png", output_image)[1].tobytes()
            window["-OUTPUT IMAGE-"].update(data=output_imgbytes)
    # Write Image
    elif event == 'Save':
        # Load Image Path
        input_image_path = values["-FILE-"]
        if os.path.exists(input_image_path):
            # Save Image Path
            write_image_path = sg.popup_get_file('', save_as=True,file_types=file_types, default_path=input_image_path)
            # Read Image
            input_image= cv2.imread(input_image_path)
            # Write Image
            write_image = np.full(input_image.shape, 0, dtype=np.uint8)
            # Dimension Values of input image
            height = input_image.shape[0]
            width = input_image.shape[1]
            # iterating over each pixel and writing to a new file
            for h_pixel in range(height):
                for w_pixel in range(width):
                    # Copying pixel value from input image to output image
                    write_image[h_pixel, w_pixel] = input_image[h_pixel, w_pixel]
            cv2.imwrite(write_image_path,write_image)
            
            sg.popup_quick_message('Image save complete', background_color='red', text_color='white', font='Any 16')
        else:
            sg.popup_quick_message('Error Please Check Path', background_color='red', text_color='white', font='Any 16')


window.close()
