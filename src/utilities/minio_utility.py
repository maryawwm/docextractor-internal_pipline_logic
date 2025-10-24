from minio import Minio


class MinioUtility:
    def __init__(self, endpoint, access_key, secret_key, secure):
        self.client = Minio(
            endpoint, access_key=access_key, secret_key=secret_key, secure=secure
        )

    def download_file(self, bucket_name, file_key, file_path):
        self.client.fget_object(
            bucket_name=bucket_name, object_name=file_key, file_path=file_path
        )
        return file_path

    def upload_file(self, bucket_name, file_key, file_path):
        self.client.fput_object(
            bucket_name=bucket_name, object_name=file_key, file_path=file_path
        )
        return file_key
