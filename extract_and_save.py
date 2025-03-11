import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np


def preprocess_image(image_path):
    # Read image using opencv
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply histogram equalization
    equalized = cv2.equalizeHist(gray)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        equalized, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 
        11, # Block size
        2  # C constant
    )
    
    # Apply morphological operations to remove noise
    kernel = np.ones((1, 1), np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Denoise the image
    denoised = cv2.fastNlMeansDenoising(morph, h=30)
    
    # Increase image size to improve OCR
    scale_factor = 2
    enlarged = cv2.resize(denoised, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    
    # Convert to PIL Image for further enhancement
    pil_image = Image.fromarray(enlarged)
    
    # Enhance the image
    enhancer = ImageEnhance.Contrast(pil_image)
    enhanced_image = enhancer.enhance(2)
    enhanced_image = enhanced_image.filter(ImageFilter.SHARPEN)
    
    # Save preprocessed image
    enhanced_image.save("preprocessed_image.png")
    
    return enhanced_image

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
        
        # Split the text into lines and return the third line
        lines = text.split('\n')
        if len(lines) >= 3:
            return print(lines[2])
        else:
            return "The third line does not exist."
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def main():
    # Specify your image path
    image_path = 'downloaded_images/image_20250311.jpg'
    
    # Extract text
    result = extract_text_and_numbers(image_path)

if __name__ == "__main__":
    main()