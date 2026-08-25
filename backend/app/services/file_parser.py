"""File parsing utilities for extracting raw text from PDF, DOCX, and TXT files."""
import io
import fitz  # PyMuPDF
import docx


def parse_file(filename: str, content: bytes) -> str:
    """Parses a file based on its extension and returns raw text.
    
    Supported: .txt, .pdf, .docx
    """
    ext = filename.split('.')[-1].lower()
    
    if ext == 'txt':
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            raise ValueError("UTF-8 decoding failed for straight text file.")
            
    elif ext == 'pdf':
        text = []
        try:
            # open PDF from bytes
            doc = fitz.open(stream=content, filetype="pdf")
            for page in doc:
                text.append(page.get_text())
            doc.close()
            return "\n".join(text)
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
            
    elif ext == 'docx':
        try:
            # open DOCX from bytes
            f = io.BytesIO(content)
            doc = docx.Document(f)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {str(e)}")
            
    else:
        raise ValueError(f"Unsupported file format: .{ext}")
