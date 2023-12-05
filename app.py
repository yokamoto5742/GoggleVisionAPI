import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account
import os
import json

MAX_FILE_SIZE = 204800 * 1024  # 200MB in kilobytes
SUPPORTED_TYPES = ["png", "jpg"]


def transcribe_image(file):
    if file is None:
        return None

    # Heroku環境かどうかを判断
    if 'HEROKU' in os.environ:
        # Heroku環境の場合
        credentials_json = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
        credentials = service_account.Credentials.from_service_account_info(credentials_json)
    else:
        # ローカル環境の場合
        credentials = service_account.Credentials.from_service_account_file(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])

    client = vision.ImageAnnotatorClient(credentials=credentials)

    # File loading
    content = file.read()
    image = vision.Image(content=content)

    # OCR execution
    response = client.document_text_detection(image=image)
    return response.full_text_annotation.text


def main():
    st.title("画像ファイルのOCRツール")

    uploaded_image_file = st.file_uploader("画像をアップロードしてください", type=SUPPORTED_TYPES)

    if uploaded_image_file and uploaded_image_file.size <= MAX_FILE_SIZE:
        transcription_message = st.empty()
        transcription_message.subheader("OCR処理中…")

        transcript = transcribe_image(uploaded_image_file)
        transcription_message.empty()

        if transcript:
            st.subheader("出力結果")
            st.text_area("OCR文章", transcript, height=500)
            st.download_button("ダウンロード", transcript.encode("utf-8"), "transcription.txt", "text/plain")
    elif uploaded_image_file:
        st.error("ファイルサイズが大きすぎます。200MB以下のファイルをアップロードしてください。")


if __name__ == "__main__":
    main()
