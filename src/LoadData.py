import os
import docx2txt
from PyPDF2 import PdfReader

def extract_text_from_txt(filepath):
    with open(filepath, "r") as f:
        return f.read()

def extract_text_from_pdf(filepath):
    reader = PdfReader(filepath)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def extract_text_from_docx(filepath):
    return docx2txt.process(filepath)

def load_documents(folderpath = "data/docs"):
    docs = {}
    for filename in os.listdir(folderpath):
        filepath = os.path.join(folderpath, filename)
        ext = filename.split(".")[-1].lower()
        if ext == "txt":
            text = extract_text_from_txt(filepath)
        elif ext == "pdf":
            text = extract_text_from_pdf(filepath)
        elif ext == "docx":
            text = extract_text_from_docx(filepath)
        else:
            continue
        if text:
            docs[filename] = text.strip()
            print(f" Loaded {filename} ({len(text)} characters)")
    return docs









# import os
# import fitz
# import docx

# def extract_text_from_txt(filepath: str) -> str:
#     with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
#         return file.read()

# def extract_text_from_pdf(filepath: str) -> str:
#     text = ""
#     with fitz.open(filepath) as pdf:
#         for page in pdf:
#             text += page.get_text("text")
#     return text

# def extract_text_from_docx(filepath: str) -> str:
#     doc = docx.Document(filepath)
#     text = "\n".join([para.text for para in doc.paragraphs])
#     return text

# def clean_text(text: str) -> str:
#     text = text.replace("\n", " ").replace("\r", " ")
#     text = " ".join(text.split())
#     return text.strip()

# def load_documents_from_directory(folder_path: str) -> dict:
#     supported_extensions = (".txt", ".pdf", ".docx")
#     documents = {}

#     for filename in os.listdir(folder_path):
#         filepath = os.path.join(folder_path, filename)

#         if not os.path.isfile(filepath) or not filename.lower().endswith(supported_extensions):
#             continue

#         try:
#             if filename.lower().endswith(".txt"):
#                 raw_text = extract_text_from_txt(filepath)
#             elif filename.lower().endswith(".pdf"):
#                 raw_text = extract_text_from_pdf(filepath)
#             elif filename.lower().endswith(".docx"):
#                 raw_text = extract_text_from_docx(filepath)
#             else:
#                 continue

#             cleaned_text = clean_text(raw_text)
#             documents[filename] = cleaned_text
#             print(f" Loaded {filename} ({len(cleaned_text)} characters)")
        
#         except Exception as e:
#             print(f" Error loading {filename}: {e}")
    
#     return documents

# if __name__ == "__main__":
#     folder_path = "data/docs"
#     docs = load_documents_from_directory(folder_path)
#     for name, text in docs.items():
#         print(f"\n {name}:\n{text[:100]}...\n")