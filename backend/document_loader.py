import fitz

from docx import Document


def load_pdf(path):

    pdf = fitz.open(path)

    text = []

    for page in pdf:
        text.append(page.get_text())

    return "\n".join(text)


def load_docx(path):

    doc = Document(path)

    return "\n".join([
        p.text
        for p in doc.paragraphs
    ])


def load_document(path):

    if path.endswith(".pdf"):
        return load_pdf(path)

    if path.endswith(".docx"):
        return load_docx(path)

    raise Exception("Unsupported file")