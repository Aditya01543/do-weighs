from pathlib import Path
import PyPDF2

path = Path('Requirements.pdf')
reader = PyPDF2.PdfReader(path)
for i, page in enumerate(reader.pages, start=1):
    print('--- PAGE %d ---' % i)
    text = page.extract_text() or ''
    print(text)
    print()