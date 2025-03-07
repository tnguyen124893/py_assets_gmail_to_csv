import os
import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

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
        query = 'subject:"Báo cáo NAV quỹ VDF" from:hainh2304@gmail.com has:attachment'
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No messages found.')
            return

        # Create a folder to store the downloaded images
        folder_path = 'downloaded_images'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            send_date = None
            for header in msg['payload']['headers']:
                if header['name'] == 'Date':
                    send_date = header['value']
                    break
            if send_date:
                send_date = datetime.strptime(send_date, '%a, %d %b %Y %H:%M:%S %z').strftime('%Y%m%d')

            for part in msg['payload']['parts']:
                if part['filename']:
                    if 'data' in part['body']:
                        data = part['body']['data']
                    else:
                        att_id = part['body']['attachmentId']
                        att = service.users().messages().attachments().get(userId='me', messageId=message['id'], id=att_id).execute()
                        data = att['data']
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))

                    # Generate a unique filename based on the send date
                    filename = f'image_{send_date}.jpg'
                    path = os.path.join(folder_path, filename)

                    # Ensure the filename is unique by appending a counter if necessary
                    counter = 1
                    while os.path.exists(path):
                        filename = f'image_{send_date}_{counter}.jpg'
                        path = os.path.join(folder_path, filename)
                        counter += 1

                    with open(path, 'wb') as f:
                        f.write(file_data)
                    print(f'Attachment {path} downloaded.')

    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()