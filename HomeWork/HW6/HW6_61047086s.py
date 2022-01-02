import PySimpleGUI as sg
import os.path
import cv2
import numpy as np
# Limited File Types minimizing the error
file_types = [("JPEG (*.jpg)", "*.jpg"),("BMP (*.bmp)", "*.bmp"),("PPM (*.ppm)", "*.ppm"),("PNG (*.png)", "*.png"),
              ("All files (*.*)", "*.*")]
# Layout of the User Interface
layout = [
    [sg.FileBrowse(file_types = file_types, key="-FILE-"),sg.Button('Load Image')],
    [sg.Button("Save"), sg.Cancel('Exit')],
    [sg.InputText(size=(15, 15),key="-Kernel Size-",),sg.T('Enter Kernel')],
    [sg.Button('Image Smoothing'), sg.Button("Edge Detection")],
    [sg.Image(key="-INPUT IMAGE-"),sg.Image(key="-OUTPUT IMAGE-")]

]

window = sg.Window('HW6_61047086s', layout)


def gaussian_blur(input_resized_image,input_kernel_size):
    kernel = input_kernel_size * input_kernel_size
    convolved_image = np.copy(input_resized_image)
    temp = np.pad(input_resized_image, input_kernel_size // 2, mode='constant')
    height, width = temp.shape
    for h_row in range(0, height - input_kernel_size + 1):
        for w_col in range(0, width - input_kernel_size + 1):
            convolved_image[h_row][w_col] = int((np.sum(temp[h_row: h_row + input_kernel_size, w_col: w_col + input_kernel_size])) / kernel)
    return convolved_image
def canny_edge_detection(gaussian_image):
    sobel_image,gradient_direction = sobel_edge(gaussian_image)
    non_max_suppressed_image = non_max_suppression(sobel_image,gradient_direction)
    hysterisis_thresholded_image = hysteresis_threshold(non_max_suppressed_image)

    return hysterisis_thresholded_image
def hysteresis_threshold(nms_img):
    # Find strong and weak threshold
    highThreshold = nms_img.max()*0.09
    lowThreshold = highThreshold*0.05
    res = np.zeros((nms_img.shape[0], nms_img.shape[1]), dtype=np.int32)
    weak = np.int32(75)
    strong = np.int32(255)

    strong_row, strong_col = np.where(nms_img >= highThreshold)
    weak_row, weak_col = np.where((nms_img <= highThreshold) & (nms_img >= lowThreshold))
    res[strong_row, strong_col] = strong
    res[weak_row, weak_col] = weak

    # Hysterisis- Joining the weak and strong pixel edges

    for h_row in range(1, nms_img.shape[0] - 1):
        for w_col in range(1, nms_img.shape[1] - 1):
            if (nms_img[h_row, w_col] == weak):
                if ((nms_img[h_row + 1, w_col - 1] == strong) or (nms_img[h_row + 1, w_col] == strong) or (nms_img[h_row + 1, w_col + 1] == strong)
                        or (nms_img[h_row, w_col - 1] == strong) or (nms_img[h_row, w_col + 1] == strong)
                        or (nms_img[h_row - 1, w_col - 1] == strong) or (nms_img[h_row - 1, w_col] == strong) or (
                                nms_img[h_row - 1, w_col + 1] == strong)):
                    nms_img[h_row, w_col] = strong
                else:
                    nms_img[h_row, w_col] = 0
    return nms_img
def non_max_suppression(sobel_image, theta):
    # Removing Redundant and Duplicate Edges
    gradient_magnitude = sobel_image
    gradient_direction = theta
    image_row, image_col = gradient_magnitude.shape
    suppressed_image = np.zeros(gradient_magnitude.shape)
    PI = 180
    for h_row in range(1, image_row - 1):
        for w_col in range(1, image_col - 1):
            direction = gradient_direction[h_row, w_col]
            # Starting Clockwise
            if (0 <= direction < PI / 8) or (15 * PI / 8 <= direction <= 2 * PI):
                before_pixel = gradient_magnitude[h_row, w_col - 1]
                after_pixel = gradient_magnitude[h_row, w_col + 1]
            elif (PI / 8 <= direction < 3 * PI / 8) or (9 * PI / 8 <= direction < 11 * PI / 8):
                before_pixel = gradient_magnitude[h_row + 1, w_col - 1]
                after_pixel = gradient_magnitude[h_row - 1, w_col + 1]

            elif (3 * PI / 8 <= direction < 5 * PI / 8) or (11 * PI / 8 <= direction < 13 * PI / 8):
                before_pixel = gradient_magnitude[h_row - 1, w_col]
                after_pixel = gradient_magnitude[h_row + 1, w_col]

            else:
                before_pixel = gradient_magnitude[h_row - 1, w_col - 1]
                after_pixel = gradient_magnitude[h_row + 1, w_col + 1]

            if gradient_magnitude[h_row, w_col] >= before_pixel and gradient_magnitude[h_row, w_col] >= after_pixel:
                suppressed_image[h_row, w_col] = gradient_magnitude[h_row, w_col]
    return suppressed_image
def sobel_edge(c_image):
    SobelImage = np.copy(c_image)
    theta = np.copy(c_image)
    # Horizontal kernel
    k1 = np.array([
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ])
    # Vertical Kernel
    k2 = np.array([
        [-1, -2, -1],
        [0, 0, 0],
        [1, 2, 1]
    ])
    # Avoid Index Out of Control
    index_control = np.zeros((c_image.shape[0] - 2, c_image.shape[1] - 2), dtype='int32')
    for h_row in range(index_control.shape[0]):
        for w_col in range(index_control.shape[1]):
            # calculate Gx and Gy of Sobel
            p1 = convolution(c_image[h_row:h_row + 3, w_col:w_col + 3], k1)
            p2 = convolution(c_image[h_row:h_row + 3, w_col:w_col + 3], k2)
            # Calculate Gradient Magnitude
            SobelImage[h_row,w_col] = np.sqrt(p1 ** 2 + p2 ** 2)
            theta[h_row,w_col] = np.arctan2(p1, p2)
    gradient_direction = theta * 180. / np.pi
    gradient_direction[gradient_direction < 0] += 180
    return SobelImage,gradient_direction
def convolution(img, kernel):
    row_a, col_a = img.shape
    rb, col_b = kernel.shape
    res = 0
    for h_row in range(row_a):
        for w_col in range(col_a):
            if 0 <= row_a - h_row - 1 < rb and 0 <= col_a - w_col - 1 < col_b:
                res += img[h_row, w_col] * kernel[row_a - h_row - 1, col_a - w_col - 1]
    return res
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED,'Exit'):
        break
    # Read Image
    elif event == 'Load Image':
        input_image_path = values['-FILE-']
        if os.path.exists(input_image_path):
            input_image = cv2.imread(values["-FILE-"],0)
            input_resized_image = cv2.resize(input_image,(500,500))
            input_imgbytes = cv2.imencode(".png", input_resized_image)[1].tobytes()
            # Fetch the byte data from the in-memory file and Pass the data to the sg.Image object in the window.update() method
            window["-INPUT IMAGE-"].update(data=input_imgbytes)
    # Write Image
    elif event == 'Save':
        # Load Image Path
        input_image_path = values["-FILE-"]
        if os.path.exists(input_image_path):
            # Save Image Path
            write_image_path = sg.popup_get_file('', save_as=True,file_types=file_types, default_path=input_image_path)
            # need to add code here
            
            sg.popup_quick_message('Image save complete', background_color='red', text_color='white', font='Any 16')
        else:
            sg.popup_quick_message('Error Please Check Path', background_color='red', text_color='white', font='Any 16')

    elif event == 'Image Smoothing':
        input_kernel_size = values['-Kernel Size-']
        if input_kernel_size.isdigit():
            convolved_image = gaussian_blur(input_resized_image,int(input_kernel_size))
            input_imgbytes = cv2.imencode(".png", convolved_image)[1].tobytes()
            # Fetch the byte data from the in-memory file and Pass the data to the sg.Image object in the window.update() method
            window["-OUTPUT IMAGE-"].update(data=input_imgbytes)
        else:
            sg.popup_quick_message('Wrong Kernel', background_color='red', text_color='white', font='Any 16')

    elif event == 'Edge Detection':
        input_kernel_size = values['-Kernel Size-']
        if input_kernel_size.isdigit():
            gaussian_image = gaussian_blur(input_resized_image,int(input_kernel_size))
            canny_image = canny_edge_detection(gaussian_image)
            input_imgbytes = cv2.imencode(".png", canny_image)[1].tobytes()
            # Fetch the byte data from the in-memory file and Pass the data to the sg.Image object in the window.update() method
            window["-OUTPUT IMAGE-"].update(data=input_imgbytes)
        else:
            sg.popup_quick_message('Wrong Kernel', background_color='red', text_color='white', font='Any 16')

window.close()