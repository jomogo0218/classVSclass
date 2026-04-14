import pypdf
import json

def test_encoding(pdf_path):
    reader = pypdf.PdfReader(pdf_path)
    text = reader.pages[0].extract_text()
    try:
        # Some PDFs use specific encodings that extract_text tries to handle, 
        # but let's see if we can re-encode/decode?
        # Usually, pypdf handles it, but maybe the font mapping is weird.
        print("Raw text snippet:")
        print(text[:500])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_encoding("d:/classVSclass/114-2班級課表(0309起實施).pdf")
