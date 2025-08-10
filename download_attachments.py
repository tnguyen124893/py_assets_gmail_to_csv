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



class GmailClient:
    def __init__(self, scopes, token_path='token.json', creds_path='credentials.json'):
        self.scopes = scopes
        self.token_path = token_path
        self.creds_path = creds_path
        self.creds = self._get_gmail_credentials()
        self.service = self._build_service()

    def _get_gmail_credentials(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds_path, self.scopes)
                creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        return creds

    def _build_service(self):
        try:
            service = build('gmail', 'v1', credentials=self.creds)
            return service
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def get_messages(self, query):
        try:
            if self.service is None:
                raise Exception("Gmail service initialization failed")
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            if not messages:
                print('No messages found.')
            return messages
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
        except Exception as error:
            print(f'Service error: {error}')
            return []

    def get_message(self, msg_id):
        if self.service is None:
            raise Exception("Gmail service initialization failed")
        try:
            return self.service.users().messages().get(userId='me', messageId=msg_id).execute()
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    def get_attachment(self, msg_id, att_id):
        if self.service is None:
            raise Exception("Gmail service initialization failed")
        return self.service.users().messages().attachments().get(userId='me', messageId=msg_id, id=att_id).execute()






def main():
    gmail_client = GmailClient(SCOPES)
    query = 'subject:"Báo cáo NAV quỹ VDF" from:hainh2304@gmail.com has:attachment'
    messages = gmail_client.get_messages(query)

    folder_path = 'downloaded_images'
    if not os.path.exists(folder_path) and messages:
        os.makedirs(folder_path)

    for message in messages:
        msg = gmail_client.get_message(message['id'])
        if msg is None:
            print(f"Could not fetch message {message['id']}")
            continue
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
                    att = gmail_client.get_attachment(message['id'], att_id)
                    data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))

                filename = f'image_{send_date}.jpg'
                path = os.path.join(folder_path, filename)

                counter = 1
                while os.path.exists(path):
                    filename = f'image_{send_date}_{counter}.jpg'
                    path = os.path.join(folder_path, filename)
                    counter += 1

                with open(path, 'wb') as f:
                    f.write(file_data)
                print(f'Attachment {path} downloaded.')


if __name__ == '__main__':
    main()