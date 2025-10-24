import os
from collections import defaultdict

from docling.document_converter import DocumentConverter
from docling_core.types.doc import PictureItem

from src.normal_document.config import normal_document_settings


class NormalDocumentService:
    def __init__(self, task_id, pages: list[int] = None):
        self.doc_convertor = DocumentConverter(
            allowed_formats=normal_document_settings.allowed_formats,
            format_options=normal_document_settings.format_options,
        )
        self.converted = None
        self.page_by_page_md = {}
        self.task_id = task_id
        self.pic_dir = os.path.join("pictures", str(self.task_id))
        os.makedirs(self.pic_dir, exist_ok=True)
        self.pics = defaultdict(list)
        self.pages = pages

    def convert(self, input_file) -> None:
        self.converted = self.doc_convertor.convert(input_file)

    @property
    def total_pages(self) -> int:
        return self.converted.document.num_pages()

    def get_pages_to_process(self) -> list[int]:
        if self.pages is not None:
            return self.pages
        return list(range(1, self.total_pages + 1))

    def extract_page_by_page_md(self) -> None:
        for page_no in self.get_pages_to_process():
            self.page_by_page_md[page_no] = self.converted.document.export_to_markdown(
                page_no=page_no
            )

    def extract_pictures(self) -> None:
        for page_no in self.get_pages_to_process():
            picture_counter = 0
            for element, _ in self.converted.document.iterate_items(page_no=page_no):
                if isinstance(element, PictureItem):
                    picture_counter += 1
                    element_image_filename = os.path.join(
                        self.pic_dir, f"page-{page_no}-picture-{picture_counter}.png"
                    )
                    with open(element_image_filename, "wb") as fp:
                        element.get_image(self.converted.document).save(fp, "PNG")
                    self.pics[page_no].append(element_image_filename)

    def cleanup(self):
        os.rmdir(self.pic_dir)
