import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Importando o novo esquema de jogos e instruções do Davy Jones
from config import JOGO_SCHEMA, SYSTEM_INSTRUCTION

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
    utilizando a personalidade e as regras do DavyJonesBot.
    """
    conteudo_prompt = f"Tente identificar o jogo com base nestas pistas e detalhes descritos pelo usuário: '{pistas_usuario}'."
    
    # Faz a chamada para o modelo pedindo uma resposta estruturada em JSON baseado no JOGO_SCHEMA
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=conteudo_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json", # Força a saída em formato JSON
            response_schema=JOGO_SCHEMA,          # Segue o esquema do config.py
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
        # Pede para o Gemini identificar os jogos (retorna como string JSON)
        resultado_json_string = identify_game(pistas_usuario)
        
        # Converte a string JSON em Dicionário Python para o Flask organizar a resposta
        dados_jogos = json.loads(resultado_json_string)
        
        return jsonify({
            "status": "success",
            "pistas_enviadas": pistas_usuario,
            "resultado": dados_jogos
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro interno ao tentar identificar o jogo: {str(e)}"
        }), 500

# Executa o servidor local
if __name__ == "__main__":
    app.run(debug=True)