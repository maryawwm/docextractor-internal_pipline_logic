from pydantic import BaseModel


class MinIOEnc(BaseModel):
    minio_access_key: str
    minio_secret_key: str


class ProcessPayload(BaseModel):
    input_minio_cred: MinIOEnc
    input_minio_endpoint: str
    input_bucket_name: str
    input_object_path: str
    pages: list[int] | None = None
    extract_images: int = 0 | 1
    output_minio_cred: MinIOEnc | None = None
    output_minio_endpoint: str | None = None
    output_bucket_name: str | None = None
    output_object_path: str | None = None


class MappingDataSchema(BaseModel):
    type: str
    page_number: int
    pic_number: int | None = None
