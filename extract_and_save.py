import google.generativeai as genai
from PIL import Image
import os

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
        
        Please ensure the output is structured clearly with each column name followed by its corresponding value, in this format: column_name| value
        Please return the output in a csv file and return only the data and nothing else."""
        
        # Generate response
        response = model.generate_content([prompt, image])
        
        # Clean the response to remove leading and trailing markdown
        cleaned_response = response.text.strip().replace("```csv\n", "").replace("```", "").strip()
        
        return cleaned_response  # Return the cleaned response
        
    except Exception as e:
        print(f"An error occurred while processing {image_path}: {str(e)}")
        return None

def main():
    # Specify the folder containing images
    folder_path = 'downloaded_images'
    
    # List to hold all extracted information
    all_extracted_info = []

    # Loop over every image in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.jpg'):  # Check for image file extensions
            image_path = os.path.join(folder_path, filename)
            # Extract text using Gemini
            extracted_info = extract_text_and_numbers(image_path)

            # Append the extracted information to the list
            if extracted_info:
                all_extracted_info.append(f"{extracted_info}\n")  # Add a newline for CSV formatting

    # Save all extracted text to a single CSV file
    with open('extracted_text.csv', 'w', encoding='utf-8') as file:
        file.writelines(all_extracted_info)  # Write all extracted information at once

if __name__ == "__main__":
    main()