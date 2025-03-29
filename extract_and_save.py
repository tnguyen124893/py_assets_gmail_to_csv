import google.generativeai as genai
from PIL import Image
import os
import time
import logging
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def extract_text_and_numbers(image_path):
    try:
        # Load the image
        image = Image.open(image_path)
        
        # Resize the image to a smaller size (e.g., 800x800)
        image.thumbnail((800, 800))  # Maintain aspect ratio
        
        # Initialize Gemini Pro Vision model
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        # Prepare the prompt
        prompt = """Please analyze this financial report image and extract only the data from the first table.
        Return only the following columns in the output:
        
        - Ngày
        - Giá CCQ
        - SL CCQ sở hữu
        - Giá trị tài sản hiện tại
        - Tỷ lệ lãi lỗ trên vốn
        
        Please ensure the output is structured clearly with each column name in this format:
            Ngày, Giá CCQ, SL CCQ sở hữu, Giá trị tài sản hiện tại, Tỷ lệ lãi lỗ trên vốn
        For example:
            Ngày, Giá CCQ, SL CCQ sở hữu, Giá trị tài sản hiện tại, Tỷ lệ lãi lỗ trên vốn
            01/01/2022, 1000, 10, 10000, 5%
        Please return the output in a csv file and return only the data and nothing else."""
        
        # Generate response
        response = model.generate_content([prompt, image])
        
        # Clean the response to remove leading and trailing markdown
        cleaned_response = response.text.strip().replace("```csv\n", "").replace("```", "").strip()
        
        return cleaned_response  # Return the cleaned response
        
    except Exception as e:
        logging.error(f"An error occurred while processing {image_path}: {str(e)}")
        return None

def process_image_batch(image_paths: List[str], batch_size: int = 5) -> List[str]:
    """Process a batch of images with delay between requests."""
    batch_results = []
    
    for i, image_path in enumerate(image_paths):
        logging.info(f"Processing image {i+1}/{len(image_paths)}: {os.path.basename(image_path)}")
        extracted_info = extract_text_and_numbers(image_path)
        
        if extracted_info:
            batch_results.append(f"{extracted_info}\n")
        
        # Add delay between requests (2.5 seconds)
        if i < len(image_paths) - 1:  # Don't delay after the last image
            time.sleep(2.5)
    
    return batch_results

def main():
    # Specify the folder containing images
    folder_path = 'downloaded_images'
    
    # Get all image files
    image_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg')]
    total_images = len(image_files)
    logging.info(f"Found {total_images} images to process")
    
    # Process images in batches
    batch_size = 5
    all_extracted_info = []
    
    for i in range(0, total_images, batch_size):
        batch_files = image_files[i:i + batch_size]
        batch_paths = [os.path.join(folder_path, f) for f in batch_files]
        
        logging.info(f"\nProcessing batch {i//batch_size + 1}/{(total_images + batch_size - 1)//batch_size}")
        batch_results = process_image_batch(batch_paths, batch_size)
        all_extracted_info.extend(batch_results)
        
        # Add a longer delay between batches (5 seconds)
        if i + batch_size < total_images:
            logging.info("Waiting 5 seconds before next batch...")
            time.sleep(5)
    
    # Save all extracted text to a single TSV file
    with open('extracted_text.csv', 'w', encoding='utf-8') as file:
        file.writelines(all_extracted_info)
    logging.info("\nProcessing complete! Results saved to extracted_text.csv")

if __name__ == "__main__":
    main()