import os
import whisper
from pydub import AudioSegment
from bucket_minio import upload_file, download_file, check_obj_exist, get_all_chuck_list
import uuid

temp_dir = './temp_audio'


def upload_audio(audio_path,file_name):
    audio = AudioSegment.from_file(audio_path)
    temp_file_name = uuid.uuid4().hex
    output_path = os.path.join(temp_dir, f"{temp_file_name}.flac")

    audio.export(output_path, format="flac")

    upload_file(file_name + '/audio.flac', output_path, 'audio')

    if os.path.exists(output_path):
        os.remove(output_path)

    print("audio uploaded")


def upload_audio_chunk(folder_name):
    check_if_exist = check_obj_exist(folder_name + 'audio.flac')

    if not check_if_exist:
        print("Audio not found")
        return

    temp_file_name = uuid.uuid4().hex
    download_path = os.path.join(temp_dir, f"{temp_file_name}.flac")

    download_file(folder_name + 'audio.flac', download_path)

    audio = AudioSegment.from_file(download_path)

    audio_len = len(audio)

    chunk_size = 30 * 1000

    for i in range(0, audio_len, chunk_size):
        chunk = audio[i:i + chunk_size]

        output_file = os.path.join(temp_dir, f"chunk_{i // chunk_size}.flac")

        chunk.export(output_file, format="flac")

        upload_file(folder_name + 'chunk/' + f"chunk_{i // chunk_size}.flac", output_file, 'chunk-audio')

        if os.path.exists(output_file):
            os.remove(output_file)

    if os.path.exists(download_path):
        os.remove(download_path)

    print("chunk uploaded")


def transcribe_audio(folder_name) -> str:
    model = whisper.load_model("base")
    all_chunk = get_all_chuck_list(folder_name)

    subtitle = ''
    for chunk in all_chunk:
        temp_file_name = uuid.uuid4().hex
        download_path = os.path.join(temp_dir, f"{temp_file_name}.flac")
        download_file(chunk, download_path)

        audio = whisper.load_audio(download_path)
        audio = whisper.pad_or_trim(audio)

        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        options = whisper.DecodingOptions(fp16=False)
        result = whisper.decode(model, mel, options)
        subtitle += result.text + ' '
        if os.path.exists(download_path):
            os.remove(download_path)

    return subtitle
