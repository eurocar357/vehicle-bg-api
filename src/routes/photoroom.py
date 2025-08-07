import os
import requests
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile
import uuid
from PIL import Image
import io

photoroom_bp = Blueprint(\'photoroom\', __name__)

# Chave da API PhotoRoom
PHOTOROOM_API_KEY = \"sandbox_sk_pr_default_94d4ff84f881c6d399b6216ee237e5c09044da7a\"
PHOTOROOM_API_URL = \"https://image-api.photoroom.com/v2/edit\"

# Prompt para o fundo do estúdio fotográfico
STUDIO_PROMPT = \"Create a background that is a photography studio, with smooth white walls, a uniform background without pillars, curtains, etc. Smooth floor in light gray, minimalist environment, soft lighting, modernity\"

# Configurações de upload
UPLOAD_FOLDER = \'/tmp/uploads\'
PROCESSED_FOLDER = \'/tmp/processed\'
ALLOWED_EXTENSIONS = {\'png\', \'jpg\', \'jpeg\', \'gif\', \'bmp\', \'webp\'}

# Criar diretórios se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True )
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return \'.\' in filename and \
           filename.rsplit(\'\.\', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image_with_photoroom(image_path):
    \"\"\"
    Processa uma imagem usando a API PhotoRoom para gerar um fundo de estúdio
    \"\"\"
    try:
        with open(image_path, \'rb\') as image_file:
            files = {
                \'image_file\': image_file
            }
            data = {
                \'size\': \'full\',
                \'format\': \'png\',
                \'background_prompt\': STUDIO_PROMPT
            }
            headers = {
                \'X-Api-Key\': PHOTOROOM_API_KEY
            }
            response = requests.post(PHOTOROOM_API_URL, headers=headers, files=files, data=data)
            response.raise_for_status()  # Levanta um erro para códigos de status HTTP ruins (4xx ou 5xx)

            # Salvar a imagem processada
            processed_filename = f\"processed_{uuid.uuid4()}.png\"
            processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
            with open(processed_path, \'wb\') as f:
                f.write(response.content)
            return processed_filename
    except requests.exceptions.RequestException as e:
        print(f\"Erro na requisição PhotoRoom: {e}\")
        if hasattr(e, \'response\') and e.response is not None:
            print(f\"Resposta da API: {e.response.text}\")
        return None
    except Exception as e:
        print(f\"Erro inesperado no processamento: {e}\")
        return None

@photoroom_bp.route(\'/upload\', methods=[\'POST\'])
def upload_image():
    \"\"\"
    Endpoint para upload de imagens e processamento com PhotoRoom
    \"\"\"
    if \'image\' not in request.files:
        return jsonify({\'error\': \'Nenhuma imagem fornecida\'}), 400

    files = request.files.getlist(\'image\')
    processed_results = []

    for file in files:
        if file.filename == \'\':
            processed_results.append({\'original_filename\': \'N/A\', \'success\': False, \'message\': \'Nome de arquivo vazio\'}) # Adicionado para tratar arquivos vazios
            continue

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f\"{uuid.uuid4()}_{filename}\"
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(filepath)

            processed_filename = process_image_with_photoroom(filepath)
            
            if processed_filename:
                processed_results.append({
                    \'original_filename\': filename,
                    \'processed_filename\': processed_filename,
                    \'success\': True,
                    \'preview_url\': f\'/api/photoroom/preview/{processed_filename}\\n
                    \'download_url\': f\'/api/photoroom/download/{processed_filename}\'
                })
            else:
                processed_results.append({\'original_filename\': filename, \'success\': False, \'message\': \'Falha no processamento da imagem com PhotoRoom\'}) # Adicionado para falha no processamento
        else:
            processed_results.append({\'original_filename\': file.filename, \'success\': False, \'message\': \'Tipo de arquivo não permitido ou arquivo inválido\'}) # Adicionado para tipo de arquivo não permitido

    return jsonify(processed_results), 200

@photoroom_bp.route(\'/download/<filename>\')
def download_file(filename):
    \"\"\"
    Endpoint para download de imagens processadas
    \"\"\"
    try:
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({\'error\': \'Arquivo não encontrado\'}), 404
    except Exception as e:
        return jsonify({\'error\': f\'Erro ao baixar arquivo: {str(e)}\'}), 500

@photoroom_bp.route(\'/preview/<filename>\')
def preview_file(filename):
    \"\"\"
    Endpoint para visualizar imagens processadas
    \"\"\"
    try:
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({\'error\': \'Arquivo não encontrado\'}), 404
    except Exception as e:
        return jsonify({\'error\': f\'Erro ao visualizar arquivo: {str(e)}\'}), 500

@photoroom_bp.route(\'/status\')
def status():
    \"\"\"
    Endpoint para verificar status da API
    \"\"\"
    return jsonify({
        \'status\': \'online\',
        \'api_key_configured\': bool(PHOTOROOM_API_KEY),
        \'upload_folder\': UPLOAD_FOLDER,
        \'processed_folder\': PROCESSED_FOLDER
    })

