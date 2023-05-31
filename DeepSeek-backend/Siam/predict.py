import numpy as np
from PIL import Image

from Siam.siamese import Siamese


def siamese_cmp(img1_path, img2_path):
    model = Siamese()
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)
    probability = model.detect_image(img1, img2)
    # print(probability)
    return probability

# if __name__ == "__main__":
#     model = Siamese()
#
#     while True:
#         image_1 = input('Input image_1 filename:')
#         try:
#             image_1 = Image.open(image_1)
#         except:
#             print('Image_1 Open Error! Try again!')
#             continue
#
#         image_2 = input('Input image_2 filename:')
#         try:
#             image_2 = Image.open(image_2)
#         except:
#             print('Image_2 Open Error! Try again!')
#             continue
#         probability = model.detect_image(image_1,image_2)
#         print(probability)
