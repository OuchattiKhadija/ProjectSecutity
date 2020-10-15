from a5_2 import A5_2
from PIL import Image
import numpy as np
import base64
import io

#array 1D to 3D
def Array1dto3d(vector,shape):

    return np.asarray(vector).reshape(shape)

#convert array iamge to string binary
def listToString(s):
    # initialize an empty string
    str1 = ""
    #str(format(0, '08b'))
    # traverse in the string
    for ele in s:
        str1 += str(format(ele, '08b'))

        # return string
    return str1

#convert sting to list

def stringToList(strin):

    n=8 # split  8 bit  by  8 bit  to convert  binery to pixel 0 ---> 255
    newlist = [int(strin[i:i+n],2) for i in range(0, len(strin), n)]
        # return list
    return newlist

#encryption_image
def encryption_image(key,image):
    encryption =""

    key_n=len(image)//len(key)
    key_ =len(image)%len(key)
    key=(key*key_n)+key[:key_]

    for i in range(0,len(image)):
        if (image[i]==key[i]):
            encryption += '0'
        elif (image[i]!=key[i]):
            encryption += '1'

    return encryption



def main(key_,data_img):
    
    session_key = int(key_, 16)
    frame_counter = 0x21

    decoded_data = base64.b64decode(data_img)
    buf = io.BytesIO(decoded_data)
    img = Image.open(buf)

    try:
        a52 = A5_2(session_key, frame_counter)


    except ValueError as error:
        print('\nError: ' + str(error) + '\n')
        menu_actions['2']()

    #import image
    #img = Image.open('img.jpg').convert('RGB') #encry
    arr = np.array(img)

    # record the original shape
    shape = arr.shape


    # make a 1-dimensional view of arr
    flat_arr = arr.ravel()

    #convert  image pixel to binary 1010110....
    image_bit=listToString(list(flat_arr))

    #key stremm
    a,b = a52.get_key_stream()

    # chiffrement = key stremm  XOR message (image)
    image_encry=encryption_image(str(a)+str(b),image_bit)

    #iamge binary  to pixcels
    image_1D = stringToList(image_encry) # iamge 1D  #image_encry
    array = np.array(image_1D, dtype=np.uint8).reshape(shape)

    #covert  matrix of pixcels to image
    pil_img = Image.fromarray(array)
    #new_image.show()
    #new_image.save('decryption.jpg')
    buff = io.BytesIO()
    pil_img.save(buff,format="PNG")
    img_str = base64.b64encode(buff.getvalue())
    
    return ""+str(img_str,'utf-8')

