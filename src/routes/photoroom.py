{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import os\
import requests\
from flask import Blueprint, request, jsonify, send_file\
from werkzeug.utils import secure_filename\
import tempfile\
import uuid\
from PIL import Image\
import io\
\
photoroom_bp = Blueprint(\\'photoroom\\', __name__)\
\
# Chave da API PhotoRoom\
PHOTOROOM_API_KEY = \\"sandbox_sk_pr_default_94d4ff84f881c6d399b6216ee237e5c09044da7a\\"\
PHOTOROOM_API_URL = \\"https://image-api.photoroom.com/v2/edit\\"\
\
# Prompt para o fundo do est\'fadio fotogr\'e1fico\
STUDIO_PROMPT = \\"Create a background that is a photography studio, with smooth white walls, a uniform background without pillars, curtains, etc. Smooth floor in light gray, minimalist environment, soft lighting, modernity\\"\
\
# Configura\'e7\'f5es de upload\
UPLOAD_FOLDER = \\'/tmp/uploads\\'\
PROCESSED_FOLDER = \\'/tmp/processed\\'\
ALLOWED_EXTENSIONS = \{\\'png\\', \\'jpg\\', \\'jpeg\\', \\'gif\\', \\'bmp\\', \\'webp\\'\}\
\
# Criar diret\'f3rios se n\'e3o existirem\
os.makedirs(UPLOAD_FOLDER, exist_ok=True )\
os.makedirs(PROCESSED_FOLDER, exist_ok=True)\
\
def allowed_file(filename):\
    return \\'.\\' in filename and \\\
           filename.rsplit(\\'\\.\\', 1)[1].lower() in ALLOWED_EXTENSIONS\
\
def process_image_with_photoroom(image_path):\
    \\"\\"\\"\
    Processa uma imagem usando a API PhotoRoom para gerar um fundo de est\'fadio\
    \\"\\"\\"\
    try:\
        with open(image_path, \\'rb\\') as image_file:\
            files = \{\
                \\'imageFile\\': image_file\
            \}\
            \
            data = \{\
                \\'referenceBox\\': \\'originalImage\\',\
                \\'background.prompt\\': STUDIO_PROMPT,\
                \\'pr-ai-background-model-version\\': \\'background-studio-beta-2025-03-17\\'\
            \}\
            \
            headers = \{\
                \\'x-api-key\\': PHOTOROOM_API_KEY\
            \}\
            \
            response = requests.post(\
                PHOTOROOM_API_URL,\
                files=files,\
                data=data,\
                headers=headers\
            )\
            \
            if response.status_code == 200:\
                return response.content\
            else:\
                print(f\\"Erro na API PhotoRoom: \{response.status_code\} - \{response.text\}\\")\
                return None\
                \
    except Exception as e:\
        print(f\\"Erro ao processar imagem: \{str(e)\}\\")\
        return None\
\
@photoroom_bp.route(\\'/upload\\', methods=[\\'POST\\'])\
def upload_files():\
    \\"\\"\\"\
    Endpoint para upload de m\'faltiplas imagens\
    \\"\\"\\"\
    try:\
        if \\'files\\' not in request.files:\
            return jsonify(\{\\'error\\': \\'Nenhum arquivo enviado\\'\}), 400\
        \
        files = request.files.getlist(\\'files\\')\
        \
        if not files or all(file.filename == \\'\\' for file in files):\
            return jsonify(\{\\'error\\': \\'Nenhum arquivo selecionado\\'\}), 400\
        \
        processed_files = []\
        \
        for file in files:\
            if file and allowed_file(file.filename):\
                # Gerar nome \'fanico para o arquivo\
                filename = secure_filename(file.filename)\
                unique_filename = f\\"\{uuid.uuid4()\}_\{filename\}\\"\
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)\
                \
                # Salvar arquivo original\
                file.save(file_path)\
                \
                # Processar com PhotoRoom\
                processed_image_data = process_image_with_photoroom(file_path)\
                \
                if processed_image_data:\
                    # Salvar imagem processada\
                    processed_filename = f\\"processed_\{unique_filename\}\\"\
                    processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)\
                    \
                    with open(processed_path, \\'wb\\') as f:\
                        f.write(processed_image_data)\
                    \
                    processed_files.append(\{\
                        \\'original_filename\\': filename,\
                        \\'processed_filename\\': processed_filename,\
                        \\'status\\': \\'success\\'\
                    \})\
                else:\
                    processed_files.append(\{\
                        \\'original_filename\\': filename,\
                        \\'status\\': \\'error\\',\
                        \\'message\\': \\'Falha ao processar com PhotoRoom\\'\
                    \})\
                \
                # Limpar arquivo original\
                os.remove(file_path)\
            else:\
                processed_files.append(\{\
                    \\'original_filename\\': file.filename,\
                    \\'status\\': \\'error\\',\
                    \\'message\\': \\'Tipo de arquivo n\'e3o permitido\\'\
                \})\
        \
        return jsonify(\{\
            \\'message\\': \\'Upload processado com sucesso\\',\
            \\'files\\': processed_files\
        \}), 200\
        \
    except Exception as e:\
        return jsonify(\{\\'error\\': f\\'Erro interno do servidor: \{str(e)\}\\'\}), 500\
\
@photoroom_bp.route(\\'/download/<filename>\\')\
def download_file(filename):\
    \\"\\"\\"\
    Endpoint para download de imagens processadas\
    \\"\\"\\"\
    try:\
        file_path = os.path.join(PROCESSED_FOLDER, filename)\
        if os.path.exists(file_path):\
            return send_file(file_path, as_attachment=True)\
        else:\
            return jsonify(\{\\'error\\': \\'Arquivo n\'e3o encontrado\\'\}), 404\
    except Exception as e:\
        return jsonify(\{\\'error\\': f\\'Erro ao baixar arquivo: \{str(e)\}\\'\}), 500\
\
@photoroom_bp.route(\\'/preview/<filename>\\')\
def preview_file(filename):\
    \\"\\"\\"\
    Endpoint para visualizar imagens processadas\
    \\"\\"\\"\
    try:\
        file_path = os.path.join(PROCESSED_FOLDER, filename)\
        if os.path.exists(file_path):\
            return send_file(file_path)\
        else:\
            return jsonify(\{\\'error\\': \\'Arquivo n\'e3o encontrado\\'\}), 404\
    except Exception as e:\
        return jsonify(\{\\'error\\': f\\'Erro ao visualizar arquivo: \{str(e)\}\\'\}), 500\
\
@photoroom_bp.route(\\'/status\\')\
def status():\
    \\"\\"\\"\
    Endpoint para verificar status da API\
    \\"\\"\\"\
    return jsonify(\{\
        \\'status\\': \\'online\\',\
        \\'api_key_configured\\': bool(PHOTOROOM_API_KEY),\
        \\'upload_folder\\': UPLOAD_FOLDER,\
        \\'processed_folder\\': PROCESSED_FOLDER\
    \})\
\
}