import pytesseract
from PIL import Image
import cv2
import numpy as np

def preprocess_image(image_path):
    # Read image using opencv
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        11, # Block size
        2  # C constant
    )
    
    # Denoise the image
    denoised = cv2.fastNlMeansDenoising(thresh)
    
    # Increase image size to improve OCR
    scale_factor = 2
    enlarged = cv2.resize(denoised, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    
    # Save preprocessed image
    cv2.imwrite("preprocessed_image.png", enlarged)
    
    return Image.open("preprocessed_image.png")

def extract_text_and_numbers(image_path):
    try:
        # Preprocess the image
        processed_image = preprocess_image(image_path)
        
        # Configure Tesseract parameters
        custom_config = r'--oem 3 --psm 6'
        
        # Extract text using Tesseract with Vietnamese language
        text = pytesseract.image_to_string(
            processed_image, 
            lang='vie',
            config=custom_config
        )
        
        print("Raw extracted text:")
        print(text)
        
        return text
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def main():
    # Specify your image path
    image_path = 'downloaded_images/image_20230212.jpg'
    
    # Extract text
    result = extract_text_and_numbers(image_path)

if __name__ == "__main__":
    main()