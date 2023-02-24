from minio import Minio
from minio.error import S3Error


def setupClient() -> Minio:
    client = Minio(
        "bucket:9000",
        access_key="minio",
        secret_key="minio123",
        secure=False,
    )
    return client


def createBucketIfNotExist(client: Minio, bucket_name):
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)


def uploadFileToBucket(client: Minio, bucket_name, fileName, filePath, content_type):
    client.fput_object(
        bucket_name, fileName, filePath, content_type=content_type
    )


def downloadFileFormBucket(client: Minio, bucket_name, filePath, outputPath):
    client.fget_object(bucket_name, filePath, outputPath)


global_client = setupClient()
global_bucket_name = "audio-bucket"
createBucketIfNotExist(global_client, global_bucket_name)


def upload_file(to_path, fromPath, content_type):
    try:
        uploadFileToBucket(global_client, global_bucket_name, to_path, fromPath, content_type)
    except S3Error as exc:
        print("error occurred.", exc)


def download_file(file_path, output_path):
    try:
        downloadFileFormBucket(global_client, global_bucket_name, file_path, output_path)
    except S3Error as exc:
        print("error occurred.", exc)


def list_all_folders():
    array = []
    folders = global_client.list_objects(global_bucket_name)

    for obj in folders:
        if obj.is_dir:
            array.append(obj.object_name)

    return array


def get_all_chuck_list(folder_name):
    array = []
    prefix = folder_name + 'chunk/'
    chucks = global_client.list_objects(global_bucket_name, prefix=prefix, recursive=True)

    for obj in chucks:
        if not obj.is_dir:
            obj_stat = global_client.stat_object(global_bucket_name, obj.object_name)
            if obj_stat.content_type == 'chunk-audio':
                array.append(obj.object_name)

    return array


def check_obj_exist(path):
    objects = global_client.list_objects(global_bucket_name, prefix=path)
    for obj in objects:
        if not obj.is_dir:
            if obj.object_name == path:
                return True
    return False


def main():
    bucket_name = "audio-bucket"
    client = setupClient()
    createBucketIfNotExist(client, bucket_name)
    objects = check_obj_exist('folder-test/sample_audio.flac2')
    print(objects)
    # uploadFileToBucket(client, bucket_name, 'folder-test/chunk/audio3.flac', './sample_audio.flac', 'chunk-audio')


if __name__ == "__main__":
    main()
