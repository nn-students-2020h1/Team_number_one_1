import img.frame as frame
import numpy as np
import cv2
from io import BytesIO

IMG_DIR = 'img/'
# Main image (on which the transformed image will be placed).
template = cv2.imread(IMG_DIR + 'template.jpg', cv2.IMREAD_COLOR)
# Mask for the main image.
mask = cv2.imread(IMG_DIR + 'mask.jpg', cv2.IMREAD_GRAYSCALE)

def generate_image(input_bytes):
    # Convert given bytes to cv2 object.
    uploaded = cv2.imdecode(np.frombuffer(input_bytes, np.uint8), cv2.IMREAD_COLOR)
    
    # Shape of given image.
    h1, w1, _ = uploaded.shape
    # Shape of main image.
    h2, w2, _ = template.shape

    # The points on the main image that the received image will be transformed to.
    # Declared in the frame module.
    expected_points = np.array(frame.points, dtype=np.float64)
    # The frame of the received image.
    original_points = np.array([[0, 0], [w1, 0], [0, h1], [w1, h1]], dtype=np.float64)
    
    # Calculate coefficients and apply Homography Transformation.
    hg, _ = cv2.findHomography(original_points, expected_points, cv2.RANSAC, 5.0)
    transformed = cv2.warpPerspective(uploaded, hg, (w2, h2))

    mask_inv = cv2.bitwise_not(mask)
    transformed = cv2.bitwise_and(transformed, transformed, mask=mask_inv)
    result = cv2.bitwise_and(template, template, mask=mask)
    result = cv2.bitwise_or(result, transformed)

    _, byte_image = cv2.imencode(".jpg", result)
    iobuff = BytesIO(byte_image)

    return iobuff
