import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Importando apenas as instruções do Davy Jones do config.py
from config import SYSTEM_INSTRUCTION

# Carrega as variáveis de ambiente e inicia o Gemini
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Inicializa o Flask
app = Flask(__name__)
CORS(app)

def identify_game(pistas_usuario):
    """
    Envia a descrição/pistas do usuário para o Gemini descobrir qual é o jogo,
    retornando uma resposta puramente em texto na voz do DavyJonesBot.
    """
    conteudo_prompt = f"Tente identificar o jogo com base nestas pistas e detalhes descritos pelo usuário: '{pistas_usuario}'."
    
    # Faz a chamada para o modelo pedindo uma resposta simples em texto livre
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=conteudo_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            # Removemos o response_mime_type e o response_schema para aceitar texto livre
        )
    )
    return response.text

@app.route("/")
def root():
    return jsonify({
        "status": "success",
        "message": "DavyJonesBot - API Identificadora de Jogos funcionando!",
        "version": "1.0"
    }), 200

@app.route("/identify", methods=["POST"])
def identify():
    data = request.get_json()
    
    # Validação 1: O JSON foi enviado com o campo esperado?
    if not data or "pistas" not in data:
        return jsonify({
            "status": "error",
            "message": "Por favor, envie um objeto JSON contendo a chave 'pistas' com a descrição do jogo."
        }), 400
        
    pistas_usuario = data.get("pistas", "").strip()
    
    # Validação 2: O usuário enviou um texto com tamanho mínimo aceitável para análise?
    if not isinstance(pistas_usuario, str) or len(pistas_usuario) < 10:
        return jsonify({
            "status": "error",
            "message": "Por favor, forneça uma descrição um pouco mais detalhada (mínimo de 10 caracteres)."
        }), 400
    
    try:
        # Pede para o Gemini identificar os jogos (retorna como string de texto puro)
        resultado_texto = identify_game(pistas_usuario)
        
        return jsonify({
            "status": "success",
            "pistas_enviadas": pistas_usuario,
            "resultado": resultado_texto # Retorna o texto formatado da IA diretamente
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro interno ao tentar identificar o jogo: {str(e)}"
        }), 500

# Executa o servidor local
if __name__ == "__main__":
    app.run(debug=True)