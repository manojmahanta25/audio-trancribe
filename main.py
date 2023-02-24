import os
import uuid
from audio_util import upload_audio, upload_audio_chunk, transcribe_audio
from bucket_minio import list_all_folders, upload_file

directory = "./audio"
temp_dir = './temp_audio'


def get_all_not_transcribe_audio_paths():
    fileList = []
    files = os.listdir(directory)

    folderExist = list_all_folders()

    for file in files:
        file_name, file_extension = os.path.splitext(os.path.basename(file))
        if not file_name + '/' in folderExist:
            fileList.append(os.path.join(directory, file))

    print(fileList)
    return fileList


def upload_subtitle(folder_name, subtitle):
    temp_file_name = uuid.uuid4().hex
    file_path = os.path.join(temp_dir, f"{temp_file_name}.txt")

    with open(file_path, "w") as f:
        f.write(subtitle)
        f.close()

    upload_file(folder_name + 'transcribe.txt', file_path, 'transcribe-text')

    if os.path.exists(file_path):
        os.remove(file_path)

    print("transcription uploaded")


def process():
    audio_paths = get_all_not_transcribe_audio_paths()

    for audio_path in audio_paths:
        file_name, file_extension = os.path.splitext(os.path.basename(audio_path))
        upload_audio(audio_path, file_name)
        upload_audio_chunk(file_name + '/')
        subtitle = transcribe_audio(file_name + '/')
        upload_subtitle(file_name + '/', subtitle)


def main():
    process()


if __name__ == "__main__":
    main()
