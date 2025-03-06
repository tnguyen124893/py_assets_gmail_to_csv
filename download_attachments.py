import os.path
import base64
from urllib.request import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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