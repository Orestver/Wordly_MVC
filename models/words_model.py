from pdfminer.high_level import extract_text
from docx import Document
import re, os, random
import json

class WordsModel():
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

        self.supported_extensions = {'.pdf', '.docx', '.json', '.txt'}

    def clean_text(self, text: str) -> str:
        """Метод для очищення тексту від дужок та обробки слешів."""
        # 1. Видаляємо дужки та їхній вміст
        text = re.sub(r"\(.*?\)", "", text)
        
        # 2. Обробляємо слеші: "здавати / брати в оренду" -> "здавати в оренду, брати в оренду"
        def slash_replacer(match):
            word1 = match.group(1)
            word2 = match.group(2)
            suffix = match.group(3)
            if suffix:
                return f"{word1} {suffix}, {word2} {suffix}"
            else:
                return f"{word1}, {word2}"

        text = re.sub(r"(\S+)\s*/\s*(\S+)(?:\s+(.+))?", slash_replacer, text)
        
        # 3. Прибираємо зайві пробіли
        text = re.sub(r"\s+", " ", text)
        
        return text.strip()

    def parse_line(self, line: str) -> tuple[str, str] | tuple[None, None]:
        line = line.strip()
        if not line:
            return None, None
        
        line = re.sub(r"^\d+[\.\)]?\s*", "", line)
        line = line.replace("–", "-").replace("—", "-")

        # шукаємо останній дефіс, який відокремлює англійське слово від перекладу
        if "-" not in line:
            return None, None

        parts = line.rsplit("-", 1)
        if len(parts) != 2:
            return None, None

        eng, ukr = parts
        
        eng = self.clean_text(eng).lower()
        ukr = self.clean_text(ukr)

        return eng, ukr

    def load_words_from_file(self, filename: str) -> dict:
        """Універсальний метод: отримує шлях, повертає словник"""
        words_dict = {}
        ext = os.path.splitext(filename)[1].lower()

        if ext not in self.supported_extensions:
            return {}

        lines = []
        try:
            if ext == ".pdf":
                text = extract_text(filename)
                lines = text.splitlines()
            elif ext == ".docx":
                doc = Document(filename)
                lines = [p.text for p in doc.paragraphs if p.text.strip()]
            elif ext == ".json":
                with open(filename, "r", encoding="utf-8") as f:
                    return json.load(f)
            elif ext == ".txt":
                with open(filename, "r", encoding="utf-8") as f:
                    lines = f.read().splitlines()
            else:
                raise ValueError(f"Формат {ext} не підтримується")

            # Загальна логіка обробки для pdf, docx, txt
            for line in lines:
                if not line.strip(): 
                    continue # Пропускаємо порожні рядки
                
                eng, ukr = self.parse_line(line)
                if eng and ukr:
                    words_dict[eng] = ukr

        except Exception as e:
            raise Exception(f"Помилка при читанні {ext}: {e}")

        return words_dict
    
    # Читає конкретний JSON-словник за іменем
    def load_pack_data(self, pack_name: str):
        file_path = os.path.join(self.storage_dir, f"{pack_name}.json")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    # Зберігає або оновлює JSON файл словника 
    def save_pack(self, words_dict: dict, filename: str):
        path = os.path.join(self.storage_dir, f"{filename}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(words_dict, f, ensure_ascii=False, indent=4)

    # Повертає список назв усіх .json файлів у папці словників
    def get_available_packs(self) -> list[str]:
        if not os.path.exists(self.storage_dir):
            return []
        return [f.replace(".json", "") for f in os.listdir(self.storage_dir) if f.endswith(".json")]
    
    # Повертає випадкові пари для режиму 'Відповідність'
    def get_quiz_pairs(self, pack_name: str, count: int = 4):
        file_path = os.path.join(self.storage_dir, f"{pack_name}.json")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            keys = random.sample(list(data.keys()), min(count, len(data)))
            return {k: data[k].split(",")[0].strip() for k in keys}
        except Exception:
            return {}
        
    # Видаляє конкретний JSON файл за іменем
    def delete_pack(self, filename: str):
        path = os.path.join(self.storage_dir, f"{filename}.json")
        if os.path.exists(path):
            os.remove(path)
