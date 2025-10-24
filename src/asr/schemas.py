from pydantic import BaseModel


class MinIOEnc(BaseModel):
    minio_access_key: str
    minio_secret_key: str


class ASRPayload(BaseModel):
    input_minio_cred: MinIOEnc
    input_minio_endpoint: str
    input_bucket_name: str
    input_object_path: str

    output_minio_cred: MinIOEnc | None = None
    output_minio_endpoint: str | None = None
    output_bucket_name: str | None = None
    output_object_path: str | None = None

    language: str | None = None
    temperature: float | None = None
    prompt: str | None = None


class MappingDataSchema(BaseModel):
    type: str
    segment_index: int | None = None
    start: float | None = None
    end: float | None = None
