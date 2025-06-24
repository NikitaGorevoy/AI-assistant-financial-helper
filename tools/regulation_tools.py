import os
import re
import pdfplumber
from docx import Document as DocxDocument
from difflib import get_close_matches
from typing import Optional, List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from smolagents import Tool
from gigasmol import GigaChatSmolModel


class RegulationSearchTool(Tool):
    name = "regulation_search"
    description = (
        "Ищет подходящие фрагменты нормативно-правовых актов (из .pdf/.txt/.docx) на основе запроса "
        "и, используя LLM, объясняет их понятным языком."
    )

    inputs = {
        "query": {
            "type": "string",
            "description": "Юридический или финансовый вопрос для поиска по нормативным текстам."
        }
    }

    output_type = "string"

    def __init__(self, model: GigaChatSmolModel, docs_path: str = "data/regulations"):
        super().__init__()
        self.model = model
        self.docs_path = docs_path
        self.text_chunks = self._load_chunks()

    def _load_chunks(self) -> List[Dict[str, str]]:
        print("[RegulationSearchTool] Загружаю документы...")

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = []

        for filename in os.listdir(self.docs_path):
            path = os.path.join(self.docs_path, filename)
            if not os.path.isfile(path):
                continue

            content = ""
            try:
                ext = filename.lower()
                if ext.endswith(".txt"):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                elif ext.endswith(".pdf"):
                    with pdfplumber.open(path) as pdf:
                        content = "\n".join(page.extract_text() or "" for page in pdf.pages)
                elif ext.endswith(".docx"):
                    doc = DocxDocument(path)
                    content = "\n".join([p.text for p in doc.paragraphs])
                else:
                    print(f"[!] Пропущен неподдерживаемый файл: {filename}")
                    continue
            except Exception as e:
                print(f"[!] Ошибка чтения {filename}: {e}")
                continue

            split = splitter.split_text(content)
            for chunk in split:
                clean = chunk.strip()
                if len(clean) >= 100:  # отсекаем бессмысленные короткие куски
                    chunks.append({"text": clean, "source": filename})

        print(f"✅ Загружено фрагментов: {len(chunks)}")
        return chunks

    def forward(self, query: str) -> str:
        print(f"🔎 Поиск по нормативке: '{query}'")
        texts = [ch["text"] for ch in self.text_chunks]
        matches = get_close_matches(query, texts, n=5, cutoff=0.2)

        # Собираем контекст
        if not matches:
            return "❌ Не удалось найти подходящие фрагменты по вашему запросу."

        contexts = []
        for match in matches:
            match_clean = match.strip().replace("\n", " ")
            source = next((ch["source"] for ch in self.text_chunks if ch["text"] == match), "неизвестный документ")
            contexts.append(f"[{source}]:\n{match_clean}")

        full_context = "\n\n".join(contexts)

        prompt = f"""
        Вы — консультант в области финансового и юридического права.

        Пользователь задал вопрос:
        "{query}"

        Найдены следующие фрагменты нормативно-правовых актов:

        {full_context}

        На основе приведённых фрагментов, дайте понятный ответ. Объясните суть требований и прав клиента, укажите источники.
        """

        response = self.model(prompt)

        if isinstance(response, dict) and "content" in response:
            return response["content"]

        if isinstance(response, str):
            return response.strip()

        raise TypeError("❌ Неверный тип ответа от модели: ожидается строка или {'content': ...}")
