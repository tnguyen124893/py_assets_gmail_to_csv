IL-Jerry: My asset manager sends me reports of my financial asset value to my gmail address. The reports are images attached to the emails. I want to extract the data from the images and save them in a csv file for analysis.

GitHub Copilot: To achieve this, you can follow these steps:

1. **Access Gmail and download attachments**: Use the Gmail API to access your emails and download the image attachments.
2. **Extract text from images**: Use an OCR (Optical Character Recognition) library like Tesseract to extract text from the images.
3. **Parse the extracted text**: Process the extracted text to get the relevant data.
4. **Save data to CSV**: Use the `csv` module in Python to save the parsed data into a CSV file.

Here's a sample implementation in Python:

1. **Install necessary libraries**:
   ```sh
   pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
   pip install pytesseract pillow
   ```

2. **Set up Gmail API**: Follow the [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python) to enable the API and get your `credentials.json` file.

3. **Download attachments from Gmail**:
   ```python
   # filepath: download_attachments.py
   import os.path
   import base64
   import pytesseract
   from PIL import Image
   from google.oauth2.credentials import Credentials
   from googleapiclient.discovery import build
   from googleapiclient.errors import HttpError
   import csv

   SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

   def main():
       creds = None
       if os.path.exists('token.json'):
           creds = Credentials.from_authorized_user_file('token.json', SCOPES)
       if not creds or not creds.valid:
           if creds and creds.expired and creds.refresh_token:
               creds.refresh(Request())
           else:
               flow = InstalledAppFlow.from_client_secrets_file(
                   'credentials.json', SCOPES)
               creds = flow.run_local_server(port=0)
           with open('token.json', 'w') as token:
               token.write(creds.to_json())

       try:
           service = build('gmail', 'v1', credentials=creds)
           results = service.users().messages().list(userId='me', q='has:attachment').execute()
           messages = results.get('messages', [])

           if not messages:
               print('No messages found.')
               return

           for message in messages:
               msg = service.users().messages().get(userId='me', id=message['id']).execute()
               for part in msg['payload']['parts']:
                   if part['filename']:
                       if 'data' in part['body']:
                           data = part['body']['data']
                       else:
                           att_id = part['body']['attachmentId']
                           att = service.users().messages().attachments().get(userId='me', messageId=message['id'], id=att_id).execute()
                           data = att['data']
                       file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                       path = part['filename']

                       with open(path, 'wb') as f:
                           f.write(file_data)
                       print(f'Attachment {path} downloaded.')

       except HttpError as error:
           print(f'An error occurred: {error}')

   if __name__ == '__main__':
       main()
   ```

4. **Extract text from images and save to CSV**:
   ```python
   # filepath: extract_and_save.py
   import pytesseract
   from PIL import Image
   import csv
   import os

   def extract_text_from_image(image_path):
       image = Image.open(image_path)
       text = pytesseract.image_to_string(image)
       return text

   def parse_text(text):
       # Implement your parsing logic here
       # For example, split by lines and extract relevant data
       lines = text.split('\n')
       data = []
       for line in lines:
           if line.strip():
               data.append(line.strip().split())
       return data

   def save_to_csv(data, csv_path):
       with open(csv_path, mode='w', newline='') as file:
           writer = csv.writer(file)
           writer.writerows(data)

   def main():
       image_folder = '.'  # Folder where images are saved
       csv_path = 'output.csv'
       all_data = []

       for filename in os.listdir(image_folder):
           if filename.endswith('.png') or filename.endswith('.jpg'):
               image_path = os.path.join(image_folder, filename)
               text = extract_text_from_image(image_path)
               data = parse_text(text)
               all_data.extend(data)

       save_to_csv(all_data, csv_path)
       print(f'Data saved to {csv_path}')

   if __name__ == '__main__':
       main()
   ```

Run `download_attachments.py` to download the image attachments from your Gmail. Then run `extract_and_save.py` to extract the text from the images and save the data to a CSV file.

Make sure to adjust the parsing logic in `parse_text` function according to the format of your financial reports.

Similar code found with 3 license types

IL-Jerry: How do I set up Tesseract?

GitHub Copilot: To set up Tesseract on your Mac, follow these steps:

1. **Install Tesseract**:
   You can install Tesseract using Homebrew. If you don't have Homebrew installed, you can install it by following the instructions on [Homebrew's website](https://brew.sh/).

   Once Homebrew is installed, open your terminal and run:
   ```sh
   brew install tesseract
   ```

2. **Verify the installation**:
   After the installation is complete, you can verify that Tesseract is installed correctly by running:
   ```sh
   tesseract --version
   ```

   You should see the version information for Tesseract.

3. **Install the Python wrapper for Tesseract**:
   If you haven't already, install the `pytesseract` library using pip:
   ```sh
   pip install pytesseract
   ```

4. **Configure Tesseract in your Python script**:
   In your Python script, you need to specify the path to the Tesseract executable if it's not in your PATH. By default, Homebrew installs Tesseract in `/usr/local/bin/tesseract`. You can set the path in your script like this:
   ```python
   import pytesseract

   # Set the tesseract executable path
   pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
   ```

Here's an example of how to integrate this into your existing script:

```python
import pytesseract
from PIL import Image
import csv
import os

# Set the tesseract executable path
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def parse_text(text):
    # Implement your parsing logic here
    # For example, split by lines and extract relevant data
    lines = text.split('\n')
    data = []
    for line in lines:
        if line.strip():
            data.append(line.strip().split())
    return data

def save_to_csv(data, csv_path):
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def main():
    image_folder = '.'  # Folder where images are saved
    csv_path = 'output.csv'
    all_data = []

    for filename in os.listdir(image_folder):
        if filename.endswith('.png') or filename.endswith('.jpg'):
            image_path = os.path.join(image_folder, filename)
            text = extract_text_from_image(image_path)
            data = parse_text(text)
            all_data.extend(data)

    save_to_csv(all_data, csv_path)
    print(f'Data saved to {csv_path}')

if __name__ == '__main__':
    main()
```

With these steps, you should have Tesseract set up and ready to use in your Python script for extracting text from images.
