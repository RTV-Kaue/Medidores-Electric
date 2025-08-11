# exportar_dataclip_para_drive.py
# requirements: requests google-api-python-client google-auth google-auth-httplib2
import os, gzip, requests
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CSV_URL = os.environ["DATA_CLIP_CSV_URL"]
DRIVE_FOLDER_ID = os.environ["GDRIVE_FOLDER_ID"]
SA_JSON = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]

resp = requests.get(CSV_URL, timeout=60)
resp.raise_for_status()

hoje = datetime.now().strftime("%Y%m%d")
fname = f"leituras_{hoje}.csv.gz"
tmp_path = f"/tmp/{fname}"

with gzip.open(tmp_path, "wt", encoding="utf-8", newline="") as f:
    f.write(resp.text)

key_path = "/tmp/sa.json"
with open(key_path, "w", encoding="utf-8") as f:
    f.write(SA_JSON)

creds = service_account.Credentials.from_service_account_file(
    key_path, scopes=["https://www.googleapis.com/auth/drive.file"]
)
service = build("drive", "v3", credentials=creds)

file_metadata = {"name": fname, "parents": [DRIVE_FOLDER_ID]}
media = MediaFileUpload(tmp_path, mimetype="application/gzip", resumable=True)
uploaded = service.files().create(body=file_metadata, media_body=media, fields="id,name").execute()
print(f"Enviado para Drive: {uploaded['name']}")
