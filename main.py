#!/usr/bin/env python

import argparse
import os
import dotenv
import httplib2
from apiclient.discovery import build
from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaFileUpload
import json

dotenv.load_dotenv()


class GooglePlayPublisher:
    def __init__(self, service_account_email, key_file):
        self.service_account_email = service_account_email
        self.key_file = key_file
        self.scopes = ['https://www.googleapis.com/auth/androidpublisher']
        self.service = self.authenticate()

    def authenticate(self):
        credentials = ServiceAccountCredentials.from_p12_keyfile(
            self.service_account_email, self.key_file, scopes=self.scopes)
        http = httplib2.Http()
        http = credentials.authorize(http)
        return build('androidpublisher', 'v3', http=http)

    def list_bundles(self, package_name):
        try:
            edit_request = self.service.edits().insert(body={}, packageName=package_name)
            result = edit_request.execute()
            edit_id = result['id']

            apks_result = self.service.edits().bundles().list(
                editId=edit_id, packageName=package_name).execute()

            for apk in apks_result.get('bundles', []):
                print('versionCode: ', apk['versionCode'])
        except client.AccessTokenRefreshError:
            print('The credentials have been revoked or expired. Please re-run the application to re-authorize.')

    def upload_aab(self, package_name, aab_file, track, release_notes):
        try:
            edit_request = self.service.edits().insert(body={}, packageName=package_name)
            result = edit_request.execute()
            edit_id = result['id']

            media = MediaFileUpload(aab_file, mimetype='application/octet-stream', resumable=True)
            upload_request = self.service.edits().bundles().upload(
                editId=edit_id, packageName=package_name, media_body=media)
            upload_result = upload_request.execute()
            print(f"Uploaded AAB versionCode: {upload_result['versionCode']}")

            track_body = {
                "track": track,
                "releases": [{
                    "versionCodes": [str(upload_result['versionCode'])],
                    "status": "completed",
                    "releaseNotes": release_notes
                }]
            }
            self.service.edits().tracks().update(
                editId=edit_id, packageName=package_name, track=track, body=track_body).execute()

            self.service.edits().commit(editId=edit_id, packageName=package_name).execute()
            print(f"AAB uploaded and released to {track} track successfully.")
        except client.AccessTokenRefreshError:
            print('The credentials have been revoked or expired. Please re-run the application to re-authorize.')


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('package_name', help='The package name. Example: com.android.sample')
    argparser.add_argument('--aab', help='Path to the AAB file', required=False)
    argparser.add_argument('--track', help='Track to upload the AAB file to (internal, alpha, beta, production)',
                           required=False)
    argparser.add_argument('--release-notes', help='JSON string with release notes, e.g. {"en-US": "Bug fixes."}', required=False)
    args = argparser.parse_args()

    service_account_email = os.getenv("SERVICE_ACCOUNT_EMAIL")
    key_file = 'key.p12'

    publisher = GooglePlayPublisher(service_account_email, key_file)

    if args.aab:
        release_notes = []
        if args.release_notes:
            try:
                notes_dict = json.loads(args.release_notes)
                release_notes = [{"language": lang, "text": text} for lang, text in notes_dict.items()]
            except json.JSONDecodeError:
                print("Invalid release notes format. Please provide a valid JSON string.")
                return
        publisher.upload_aab(args.package_name, args.aab, args.track, release_notes)
    else:
        publisher.list_bundles(args.package_name)


if __name__ == '__main__':
    main()
