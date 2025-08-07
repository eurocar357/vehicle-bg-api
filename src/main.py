{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import os\
import sys\
# DON\\'T CHANGE THIS !!!\
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))\
\
from flask import Flask, send_from_directory\
from flask_cors import CORS\
from src.models.user import db\
from src.routes.user import user_bp\
from src.routes.photoroom import photoroom_bp\
\
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), \\'static\\'))\
app.config[\\'SECRET_KEY\\'] = \\'asdf#FGSgvasgf$5$WGT\\'\
\
# Configurar CORS para permitir requisi\'e7\'f5es do frontend\
CORS(app)\
\
app.register_blueprint(user_bp, url_prefix=\\'/api\\')\
app.register_blueprint(photoroom_bp, url_prefix=\\'/api/photoroom\\')\
\
# uncomment if you need to use database\
app.config[\\'SQLALCHEMY_DATABASE_URI\\'] = f\\"sqlite:///\{os.path.join(os.path.dirname(__file__), \\'database\\', \\'app.db\\')\}\\"\
app.config[\\'SQLALCHEMY_TRACK_MODIFICATIONS\\'] = False\
db.init_app(app)\
with app.app_context():\
    db.create_all()\
\
@app.route(\\'/\\', defaults=\{\\'path\\': \\'\\'\}) \
@app.route(\\'/<path:path>\\')\
def serve(path):\
    static_folder_path = app.static_folder\
    if static_folder_path is None:\
            return \\"Static folder not configured\\", 404\
\
    if path != \\"\\" and os.path.exists(os.path.join(static_folder_path, path)):\
        return send_from_directory(static_folder_path, path)\
    else:\
        index_path = os.path.join(static_folder_path, \\'index.html\\')\
        if os.path.exists(index_path):\
            return send_from_directory(static_folder_path, \\'index.html\\')\
        else:\
            return \\"index.html not found\\", 404\
\
\
if __name__ == \\'__main__\\':\
    app.run(host=\\'0.0.0.0\\', port=5000, debug=True)\
}