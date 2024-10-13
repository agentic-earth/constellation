import fitz

def read_pdf(pdf_path):
    pdf = fitz.open(pdf_path)
    text = ""
    for page_num in range(pdf.page_count):
        page = pdf.load_page(page_num)
        text += page.get_text()
    return text

if __name__ == "__main__":
    pdf_path = "/Users/justinxiao/Downloads/coursecode/CSCI2340/constellation-backend/api/backend/app/features/agent/scraped_papers/70 years of machine learning in geoscience in review.pdf"
    pdf_text = read_pdf(pdf_path)
    print(pdf_text)