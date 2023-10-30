from functions import ImageTextExtractor

if __name__ == "__main__":
    extractor = ImageTextExtractor()
    pdf_file = 'ocr/Input/mensagem.pdf'
    output_path = 'ocr/Output/OCR.txt'
    extractor.run(pdf_file, output_path)
