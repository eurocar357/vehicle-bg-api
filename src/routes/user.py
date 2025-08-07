from flask import Blueprint

user_bp = Blueprint(\'user\', __name__)

# Exemplo de rota, pode ser expandido conforme necessário
@user_bp.route(\'/test\')
def test_user_route():
    return \'User route test successful\'
