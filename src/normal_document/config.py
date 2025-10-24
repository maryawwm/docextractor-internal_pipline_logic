from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import (
    PdfFormatOption,
    WordFormatOption,
)
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from pydantic import BaseModel, ConfigDict


class NormalDocumentConverterConfig(BaseModel):
    allowed_formats: list[InputFormat]
    format_options: dict[InputFormat, object]

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


normal_document_settings = NormalDocumentConverterConfig(
    allowed_formats=[InputFormat.PDF, InputFormat.DOCX],
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=StandardPdfPipeline,
            backend=PyPdfiumDocumentBackend,
            pipeline_options=PdfPipelineOptions(
                images_scale=1.0,
                generate_picture_images=True,
            ),
        ),
        InputFormat.DOCX: WordFormatOption(
            pipeline_cls=SimplePipeline,
        ),
    },
)
