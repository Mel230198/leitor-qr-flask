from flask import Flask, render_template, request
import cv2
from pyzbar.pyzbar import decode
import os
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = []
    if request.method == 'POST':
        arquivo = request.files['imagem']
        if arquivo and allowed_file(arquivo.filename):
            nome_seguro = secure_filename(arquivo.filename)
            caminho = os.path.join(UPLOAD_FOLDER, nome_seguro)
            arquivo.save(caminho)

            imagens = []

            if caminho.lower().endswith('.pdf'):
                try:
                    imagens_pdf = convert_from_path(caminho, dpi=300)
                    imagens = imagens_pdf
                except Exception as e:
                    resultado.append(f"Erro ao converter PDF: {str(e)}")
                    return render_template('index.html', resultado=resultado)
            else:
                img = cv2.imread(caminho)
                if img is not None:
                    imagens = [img]
                else:
                    resultado.append("Erro ao ler a imagem JPG/PNG.")
                    return render_template('index.html', resultado=resultado)

            encontrou_qrcode = False
            for img in imagens:
                if not isinstance(img, np.ndarray):
                    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

                qrcodes = decode(img)
                if qrcodes:
                    encontrou_qrcode = True
                    for qr in qrcodes:
                        dados = qr.data.decode('utf-8')
                        resultado.append(f"QR Code encontrado: {dados}")

            if not encontrou_qrcode:
                resultado.append("Nenhum QR Code encontrado.")

        else:
            resultado.append("Arquivo não permitido. Por favor, envie um PDF, JPG, JPEG ou PNG.")

    return render_template('index.html', resultado=resultado)

if __name__ == '__main__':
    app.run(debug=True)
