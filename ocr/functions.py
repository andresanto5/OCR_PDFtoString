import cv2
from PIL import Image
import pytesseract
from langdetect import detect
import os
from pdf2image import convert_from_path
import numpy as np

class ImageTextExtractor:
    def pdf_to_images(self, input_file):
        """
        Converte um arquivo PDF em uma lista de imagens.
        
        :param input_file: O caminho para o arquivo PDF de entrada.
        :type input_file: str
        :return: Uma lista de imagens.
        :rtype: list
        """
        try:
            images = convert_from_path(input_file, dpi=300)
            return images
        except Exception as e:
            print(f"Erro na conversão de PDF para imagens: {e}")
            return []

    def image_processing(self, image):
        """
        Realiza o pré-processamento de uma imagem.

        :param image: A imagem de entrada.
        :type image: PIL.Image
        :return: A imagem pré-processada em escala de cinza.
        :rtype: numpy.ndarray
        """
        try:
            # Converte a imagem para escala de cinza
            gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
            bigger = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            blur = cv2.GaussianBlur(gray, (3, 3), 1)
            thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            return thresh
        except Exception as e:
            print(f"Erro no pré-processamento da imagem: {e}")
            return None

    def extract_text(self, processed_image, min_confidence=40):
        """
        Extrai texto de uma imagem processada.

        :param processed_image: A imagem processada.
        :type processed_image: numpy.ndarray
        :param min_confidence: A confiança mínima das palavras a serem extraídas.
        :type min_confidence: int
        :return: O texto extraído e verificado.
        :rtype: str
        """
        try:
            # Extraia o texto da imagem processada
            text = pytesseract.image_to_string(Image.fromarray(processed_image), lang='por', config='--oem 1 --psm 3')

            # Realiza a verificação do idioma
            if self.is_portuguese_brazilian(text):
                # Realiza a verificação da confiança das palavras
                min_conf_words = self.min_conf(processed_image, min_confidence)
                verified_text = ' '.join(min_conf_words)

                return verified_text
            else:
                print("O texto extraído não é compatível com o idioma Português Brasileiro.")
                return ""
        except Exception as e:
            print(f"Erro na extração de texto da imagem: {e}")
            return ""

    def is_portuguese_brazilian(self, text):
        """
        Verifica se o texto está no idioma Português Brasileiro.

        :param text: O texto a ser verificado.
        :type text: str
        :return: True se o texto estiver em Português Brasileiro, False caso contrário.
        :rtype: bool
        """
        try:
            lang = detect(text)
            return lang == 'pt'
        except Exception as e:
            print(f"Erro ao detectar idioma: {e}")
            return False

    def min_conf(self, processed_image, min_confidence=40):
        """
        Filtra palavras com base na confiança das palavras.

        :param processed_image: A imagem processada.
        :type processed_image: numpy.ndarray
        :param min_confidence: A confiança mínima das palavras a serem mantidas.
        :type min_confidence: int
        :return: Lista de palavras com confiança igual ou superior a min_confidence.
        :rtype: list
        """
        confidences = pytesseract.image_to_data(Image.fromarray(processed_image), output_type=pytesseract.Output.DICT, lang='por')
        min_conf_words = [word for i, word in enumerate(confidences['text']) if int(confidences['conf'][i]) >= min_confidence]
        return min_conf_words

    def save_text_to_file(self, text, output_path):
        """
        Salva o texto extraído em um arquivo de texto.

        :param text: O texto a ser salvo.
        :type text: str
        :param output_path: O caminho para o arquivo de saída.
        :type output_path: str
        """
        try:
            # Salva o texto extraído em um arquivo de texto
            with open(output_path, 'w', encoding='utf-8') as arquivo:
                arquivo.write(text)
        except Exception as e:
            print(f"Erro ao salvar o texto em um arquivo: {e}")

    def run(self, pdf_file, output_path):
        """
        Executa o processo completo de extração de texto a partir de um arquivo PDF.

        :param pdf_file: O caminho para o arquivo PDF de entrada.
        :type pdf_file: str
        :param output_path: O caminho para o arquivo de saída do texto extraído.
        :type output_path: str
        """
        # Converte o PDF em imagens
        pdf_images = self.pdf_to_images(pdf_file)

        if not pdf_images:
            print("Erro ao converter PDF para imagens.")
            return

        # Inicializa o texto extraído
        extracted_text = ''

        # Processa cada imagem e extrai o texto
        for image in pdf_images:
            # Realiza o pré-processamento da imagem
            processed_image = self.image_processing(image)

            if processed_image is not None:
                # Extraia e verifique o texto
                verified_text = self.extract_text(processed_image)

                # Adicione o texto verificado ao resultado
                if verified_text:
                    extracted_text += verified_text + '\n'

        # Verifica se o texto foi extraído e salva em um arquivo
        if extracted_text:
            self.save_text_to_file(extracted_text, output_path)
            print(f"Texto extraído e salvo em '{output_path}'")
        else:
            print("Nenhum texto extraído ou erro durante o processo.")