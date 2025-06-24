import os
import pdfplumber
from docx import Document
from typing import Optional
from smolagents import Tool
from gigasmol import GigaChatSmolModel


class ContractAnalyzerTool(Tool):
    """
    Инструмент анализа текста договора или описания услуги.
    Выявляет важные, скрытые или потенциально рискованные условия для потребителя.
    """
    name = "contract_analyzer"
    description = (
        "Анализирует текст финансового договора, страхового полиса или описания услуги "
        "и выделяет важные для клиента детали, потенциально рискованные или неочевидные условия."
    )

    inputs = {
        "text": {"type": "string", "description": "Текст договора или условий для анализа", "nullable": True},
        "file_path": {"type": "string", "description": "Путь к загруженному PDF или DOCX файлу", "nullable": True}
    }

    output_type = "string"

    def __init__(self, model: Optional[GigaChatSmolModel] = None):
        super().__init__()
        if model is None:
            raise ValueError("Необходимо передать модель GigaChat для ContractAnalyzerTool.")
        self.model = model

    def forward(self, text: Optional[str] = None, file_path: Optional[str] = None) -> str:
        if file_path:
            extracted_text = self._extract_text_from_file(file_path)
            if not extracted_text:
                raise ValueError("Не удалось извлечь текст из файла.")
        elif text:
            extracted_text = text
        else:
            raise ValueError("Необходимо либо указать текст, либо путь к файлу.")

        prompt = self._build_prompt(extracted_text)

        print(prompt)

        response = self.model(prompt)
        return response

    def _extract_text_from_file(self, file_path: str) -> str:
        if file_path.lower().endswith(".pdf"):
            try:
                with pdfplumber.open(file_path) as pdf:
                    return "\n".join(page.extract_text() or "" for page in pdf.pages if page.extract_text())
            except Exception as e:
                raise ValueError(f"Ошибка при чтении PDF: {e}")
        elif file_path.endswith(".docx"):
            try:
                doc = Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs])
            except Exception as e:
                raise ValueError(f"Ошибка при чтении DOCX: {e}")
        else:
            raise ValueError("Формат файла не поддерживается. Используйте PDF или DOCX.")

    def _build_prompt(self, document_text: str) -> str:
        return f"""
        Вы выступаете как консультант по финансовым услугам.
        
        Проанализируйте следующий текст договора или описания услуги. 
        Выделите все важные условия, на которые клиенту следует обратить внимание. 

        Предоставьте краткую, понятную сводку текста ниже и выделите потенциальные «опасные» места.

        Текст документа:
        {document_text[:6000]}
        """
