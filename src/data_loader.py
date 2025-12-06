from pathlib import Path
from typing import List, Any
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from langchain_community.document_loaders import JSONLoader
from bs4 import BeautifulSoup
from langchain_core.documents import Document

def load_all_documents(data_dir: str) -> List[Any]:
    """
    Load all supported files from the data directory and convert to LangChain document structure.
    Supported: PDF, TXT, CSV, Excel, Word, JSON
    """
    # Use project root data folder
    data_path = Path(data_dir).resolve()
    print(f"[DEBUG] Data path: {data_path}")
    documents = []


    # PDF files
    pdf_files = list(data_path.glob('*.pdf'))
    print(f"[DEBUG] Found {len(pdf_files)} PDF files: {[str(f) for f in pdf_files]}")
    for pdf_file in pdf_files:
        print(f"[DEBUG] Loading PDF: {pdf_file}")
        try:
            loader = PyPDFLoader(str(pdf_file))
            pages = loader.load_and_split()
            for page_no, page in enumerate(pages, start=1):
                page.metadata["source"] = pdf_file.name
                page.metadata["page"] = page_no
                documents.append(page)
            print(f"[DEBUG] Loaded {len(pages)} PDF pages from {pdf_file}")
        except Exception as e:
            print(f"[ERROR] Failed to load PDF {pdf_file}: {e}")


    # TXT files
    txt_files = list(data_path.glob('*.txt'))
    print(f"[DEBUG] Found {len(txt_files)} TXT files: {[str(f) for f in txt_files]}")
    for txt_file in txt_files:
        print(f"[DEBUG] Loading TXT: {txt_file}")
        try:
            loader = TextLoader(str(txt_file))
            results = loader.load()
            for r in results:
                r.metadata["source"] = txt_file.name
                r.metadata["page"] = 1
                documents.append(r)
            print(f"[DEBUG] Loaded {len(results)} TXT docs from {txt_file}")
        except Exception as e:
            print(f"[ERROR] Failed to load TXT {txt_file}: {e}")

    # HTML files (efficient loader: extract visible text only)
    html_files = list(data_path.glob('*.html'))
    print(f"[DEBUG] Found {len(html_files)} HTML files: {[str(f) for f in html_files]}")
    for html_file in html_files:
        print(f"[DEBUG] Loading HTML: {html_file}")
        try:
            with open(html_file, encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f, "html.parser")
                # Remove script and style elements
                for tag in soup(["script", "style", "noscript"]):
                    tag.decompose()
                text = soup.get_text(separator="\n", strip=True)
                # Remove excessive blank lines
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                clean_text = "\n".join(lines)
                doc = Document(page_content=clean_text, metadata={"source": html_file.name, "page": 1})
                documents.append(doc)
            print(f"[DEBUG] Loaded HTML text from {html_file}")
        except Exception as e:
            print(f"[ERROR] Failed to load HTML {html_file}: {e}")

    # CSV files
    csv_files = list(data_path.glob('*.csv'))
    print(f"[DEBUG] Found {len(csv_files)} CSV files: {[str(f) for f in csv_files]}")
    for csv_file in csv_files:
        print(f"[DEBUG] Loading CSV: {csv_file}")
        try:
            loader = CSVLoader(str(csv_file))
            results = loader.load()
            for r in results:
                r.metadata["source"] = csv_file.name
                r.metadata["page"] = 1
                documents.append(r)
            print(f"[DEBUG] Loaded {len(results)} CSV docs from {csv_file}")
        except Exception as e:
            print(f"[ERROR] Failed to load CSV {csv_file}: {e}")

    # Excel files
    xlsx_files = list(data_path.glob('*.xlsx'))
    print(f"[DEBUG] Found {len(xlsx_files)} Excel files: {[str(f) for f in xlsx_files]}")
    for xlsx_file in xlsx_files:
        print(f"[DEBUG] Loading Excel: {xlsx_file}")
        try:
            loader = UnstructuredExcelLoader(str(xlsx_file))
            results = loader.load()
            for r in results:
                r.metadata["source"] = xlsx_file.name
                r.metadata["page"] = 1
                documents.append(r)
            print(f"[DEBUG] Loaded {len(results)} Excel docs from {xlsx_file}")
        except Exception as e:
            print(f"[ERROR] Failed to load Excel {xlsx_file}: {e}")

    # Word files
    docx_files = list(data_path.glob('*.docx'))
    print(f"[DEBUG] Found {len(docx_files)} Word files: {[str(f) for f in docx_files]}")
    for docx_file in docx_files:
        print(f"[DEBUG] Loading Word: {docx_file}")
        try:
            loader = Docx2txtLoader(str(docx_file))
            results = loader.load()
            for r in results:
                r.metadata["source"] = docx_file.name
                r.metadata["page"] = 1
                documents.append(r)
            print(f"[DEBUG] Loaded {len(results)} Word docs from {docx_file}")
        except Exception as e:
            print(f"[ERROR] Failed to load Word {docx_file}: {e}")

    # JSON files
    json_files = list(data_path.glob('*.json'))
    print(f"[DEBUG] Found {len(json_files)} JSON files: {[str(f) for f in json_files]}")
    for json_file in json_files:
        print(f"[DEBUG] Loading JSON: {json_file}")
        try:
            loader = JSONLoader(str(json_file))
            results = loader.load()
            for r in results:
                r.metadata["source"] = json_file.name
                r.metadata["page"] = 1
                documents.append(r)
            print(f"[DEBUG] Loaded {len(results)} JSON docs from {json_file}")
        except Exception as e:
            print(f"[ERROR] Failed to load JSON {json_file}: {e}")

    print(f"[DEBUG] Total loaded documents: {len(documents)}")
    return documents    

# Example usage
# if __name__ == "__main__":
#     docs = load_all_documents("data")
#     print(f"Loaded {len(docs)} documents.")
#     print("Example document:", docs[0] if docs else None)