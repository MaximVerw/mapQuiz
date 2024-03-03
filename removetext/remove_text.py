import cv2
import keras_ocr
import numpy as np
import math
from PIL import Image


class TextRemover:
    def __init__(self):
        self.pipeline = keras_ocr.pipeline.Pipeline()
        #self.inpainter = Inpainter()

    def make_blackish_white_within_mask(self,img, mask, threshold=50):
        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to identify blackish colors
        _, blackish_mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)

        # Combine the mask and the blackish mask, final mask disabled for now
        final_mask = cv2.bitwise_or(mask, blackish_mask)

        # Apply the final mask to make blackish colors white within the mask
        img[final_mask != 0] = [200, 200, 200]  # Make blackish colors greywhite

        # blur
        blurred_img = img.copy()
        kernel_size = (15, 15)  # Adjust kernel size as needed
        blur_amount = 1  # Adjust blur amount as needed
        img[final_mask != 0] = cv2.GaussianBlur(blurred_img[final_mask != 0], kernel_size, blur_amount)
        return img, final_mask
    def compute_grad(self, image_gray, mode: str) -> np.ndarray:
        """
        Function to compute the gradients magnitude of the image
        set mode to "double" if you want to apply it two times
        """
        # Compute the gradients using the Sobel operator
        dx = cv2.Sobel(image_gray, cv2.CV_64F, 1, 0, ksize=3)
        dy = cv2.Sobel(image_gray, cv2.CV_64F, 0, 1, ksize=3)

        # Compute the magnitude and direction of the gradients
        mag = np.sqrt(dx ** 2 + dy ** 2)

        if mode == "double":
            # Compute the gradients using the Sobel operator
            dx = cv2.Sobel(mag, cv2.CV_64F, 1, 0, ksize=3)
            dy = cv2.Sobel(mag, cv2.CV_64F, 0, 1, ksize=3)

            # Compute the magnitude and direction of the gradients
            magmag = np.sqrt(dx ** 2 + dy ** 2)
            return (magmag / magmag.max() * 255).astype(np.uint8)

        return (mag / mag.max() * 255).astype(np.uint8)


    def detect_draw(self, pipeline, image_gray, viz):
        img = cv2.cvtColor(image_gray, cv2.COLOR_GRAY2RGB)
        # read image from the an image path (a jpg/png file or an image url)
        # Prediction_groups is a list of (word, box) tuples
        b = pipeline.recognize([img])
        if viz:
            keras_ocr.tools.drawAnnotations(image=img, predictions=b[0])

        x_min = int(min([b[0][i][1][:, 0].min() for i in range(len(b[0]))]))
        x_max = int(max([b[0][i][1][:, 0].max() for i in range(len(b[0]))]))

        y_min = int(min([b[0][i][1][:, 1].min() for i in range(len(b[0]))]))
        y_max = int(max([b[0][i][1][:, 1].max() for i in range(len(b[0]))]))
        return (x_min, y_min, x_max, y_max)


    def remove(self, image_gray, bb, offset):
        # Create a mask of the same size as the image
        mask = np.ones_like(image_gray) * 255

        # Draw a white rectangle on the mask within the bounding box
        cv2.rectangle(mask, (bb[0] - offset, bb[1] - offset), (bb[2] + offset, bb[3] + offset), (0, 0, 0), -1)

        # Apply the mask to the original image
        masked_image = cv2.bitwise_and(image_gray, mask)

        return masked_image
    def main(self, pipeline, image_gray, offset):
        mag = self.compute_grad(image_gray,"single")
        bb = self.detect_draw(pipeline, mag, viz=True)
        masked_image = self.remove(image_gray, bb, offset)
        return masked_image


    def midpoint(self, x1, y1, x2, y2):
        x_mid = int((x1 + x2) / 2)
        y_mid = int((y1 + y2) / 2)
        return (x_mid, y_mid)

    def inpaint_text(self, img_path, pipeline):
        # read image
        img = keras_ocr.tools.read(img_path)
        # generate (word, box) tuples
        prediction_groups = pipeline.recognize([img])
        mask = np.zeros(img.shape[:2], dtype='uint8')
        for box in prediction_groups[0]:
            x0, y0 = box[1][0]
            x1, y1 = box[1][1]
            x2, y2 = box[1][2]
            x3, y3 = box[1][3]

            x_mid0, y_mid0 = self.midpoint(x1, y1, x2, y2)
            x_mid1, y_mi1 = self.midpoint(x0, y0, x3, y3)
            x_mid2, y_mid2 = self.midpoint(x0, y0, x1, y1)
            x_mid3, y_mid3 = self.midpoint(x2, y2, x3, y3)

            thickness1 = int((math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))/1.5)
            thickness2 = int((math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2))/1.5)

            if thickness1<thickness2:
                cv2.line(mask, (x_mid0, y_mid0), (x_mid1, y_mi1), 255, thickness1)
            else:
                cv2.line(mask, (x_mid2, y_mid2), (x_mid3, y_mid3), 255, thickness2)

            # Apply Gaussian blur to the regions defined by the mask
            img, mask = self.make_blackish_white_within_mask(img, mask,120)

        inpainted_img = cv2.inpaint(img, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
        # self.inpainter.inPaintImage(img, mask)
        return Image.fromarray(inpainted_img.astype('uint8'))

    def process_image(self, PATH):
        img = self.inpaint_text(PATH, self.pipeline)
        outputPath = PATH.replace("-base.jpg","") + "-blurred.jpg"
        img.save(outputPath, format='JPEG')
        return outputPath
