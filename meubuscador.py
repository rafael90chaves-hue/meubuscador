from flask import Flask, render_template_string, request
import os
import urllib.request
import json

app = Flask(__name__)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IA Search Pro - Cérebro Ativo</title>
    <style>
        body { 
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
            background: radial-gradient(circle at 50% 30%, #0c1a24 0%, #050b10 70%, #020406 100%);
            color: #e1e1e6; 
            min-height: 100vh;
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            margin: 0;
            padding: 0;
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
        }
        body::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                radial-gradient(rgba(0, 242, 254, 0.05) 2px, transparent 4px),
                linear-gradient(rgba(0, 242, 254, 0.02) 1px, transparent 1px);
            background-size: 40px 40px, 80px 80px;
            z-index: -1;
            opacity: 0.8;
        }
        .navbar {
            width: 100%;
            max-width: 1200px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            box-sizing: border-box;
        }
        .nav-links { display: flex; gap: 20px; }
        .nav-links a {
            color: #8fa0a6;
            text-decoration: none;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: color 0.3s;
        }
        .nav-links a:hover, .nav-links a.active {
            color: #00f2fe;
            text-shadow: 0 0 8px rgba(0, 242, 254, 0.6);
        }
        .main-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            width: 100%;
            max-width: 750px;
            padding: 20px;
            box-sizing: border-box;
            margin-top: -40px;
        }
        @keyframes cyberGlow {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .search-wrapper {
            width: 100%;
            position: relative;
            animation: cyberGlow 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
        }
        .search-form { 
            position: relative;
            display: flex; 
            align-items: center;
            width: 100%;
        }
        input { 
            width: 100%; 
            padding: 18px 60px 18px 25px; 
            font-size: 16px; 
            background: rgba(10, 25, 36, 0.6);
            border: 2px solid rgba(0, 242, 254, 0.3); 
            color: #ffffff;
            border-radius: 50px; 
            outline: none; 
            box-sizing: border-box;
            backdrop-filter: blur(10px); 
            transition: all 0.3s ease;
            box-shadow: inset 0 0 15px rgba(0, 242, 254, 0.05);
        }
        input:focus { 
            border-color: #00f2fe; 
            box-shadow: 0 0 25px rgba(0, 242, 254, 0.35), inset 0 0 10px rgba(0, 242, 254, 0.1);
        }
        .search-btn { 
            position: absolute;
            right: 8px;
            background: #102a3a;
            border: 1px solid rgba(0, 242, 254, 0.5);
            color: #00f2fe;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.2);
        }
        .search-btn:hover {
            background: #00f2fe;
            color: #050b10;
            box-shadow: 0 0 15px #00f2fe;
        }
        .shortcuts-container {
            display: flex;
            gap: 30px;
            margin-top: 35px;
            animation: cyberGlow 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
            animation-delay: 0.2s;
        }
        .shortcut-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            text-decoration: none;
            color: #8fa0a6;
            font-size: 12px;
            transition: all 0.3s ease;
        }
        .shortcut-icon {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(255,255,255,0.03);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: #c4c4cc;
            transition: all 0.3s ease;
        }
        .shortcut-item:hover .shortcut-icon {
            border-color: #00f2fe;
            color: #00f2fe;
            background: rgba(0, 242, 254, 0.05);
            box-shadow: 0 0 15px rgba(0, 242, 254, 0.2);
        }
        .result-card {
            width: 100%;
            background: rgba(10, 25, 36, 0.7); 
            padding: 30px; 
            border-radius: 20px; 
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); 
            border: 1px solid rgba(0, 242, 254, 0.2);
            margin-top: 30px;
            box-sizing: border-box;
            backdrop-filter: blur(12px);
            animation: cyberGlow 0.6s ease both;
        }
        .response-title { 
            color: #ffffff; 
            font-size: 18px; 
            margin-top: 0; 
            border-bottom: 1px solid rgba(0, 242, 254, 0.1);
            padding-bottom: 12px;
        }
        .data-badge {
            display: inline-block;
            background: rgba(0, 242, 254, 0.1);
            color: #00f2fe;
            padding: 4px 12px;
            border-radius: 30px;
            font-size: 11px;
            text-transform: uppercase;
            font-weight: bold;
            border: 1px solid rgba(0, 242, 254, 0.3);
            margin-bottom: 15px;
        }
        .response-text { 
            font-size: 15px; 
            color: #c4c4cc; 
            line-height: 1.7; 
            white-space: pre-line;
        }
        @media (max-width: 600px) {
            .navbar { display: none; }
            .shortcuts-container { gap: 15px; }
        }
    </style>
</head>
<body>

    <header class="navbar">
        <div class="nav-links">
            <a href="#" class="active">Campanha</a>
            <a href="#">Conteúdo</a>
            <a href="#">Recursos</a>
            <a href="#">Estatísticas</a>
        </div>
    </header>

    <div class="main-container">
        <div class="search-wrapper">
            <form action="/" method="POST" class="search-form">
                <input type="text" name="query" placeholder="Faça uma pergunta para a Inteligência Artificial..." value="{{ query }}" required>
                <button type="submit" class="search-btn">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                </button>
            </form>
        </div>

        <div class="shortcuts-container">
            <div class="shortcut-item">
                <div class="shortcut-icon">🤖</div>
                <span>IA Ativa</span>
            </div>
            <div class="shortcut-item">
                <div class="shortcut-icon">⚡</div>
                <span>Ultra Rápido</span>
            </div>
            <div class="shortcut-item">
                <div class="shortcut-icon">✨</div>
                <span>Original</span>
            </div>
        </div>

        {% if resposta_direta %}
        <div class="result-card">
            <div class="data-badge">Modelo Cognitivo Ativo</div>
            <h3 class="response-title">Resposta da Inteligência Artificial</h3>
            <p class="response-text">{{ resposta_direta }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    resposta_direta = ""
    query = ""
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            raw_key = os.environ.get("GEMINI_API_KEY", "")
            # Remove qualquer espaço ou quebra de linha acidental da chave
            api_key = raw_key.strip()
            
            if not api_key:
                resposta_direta = "Erro: A variável GEMINI_API_KEY está vazia ou não foi configurada no Render."
            else:
                try:
                    # Endpoint v1beta simplificado para requisições brutas diretas
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                    
                    body = {
                        "contents": [{
                            "parts": [{
                                "text": str(query)
                            }]
                        }]
                    }
                    
                    data = json.dumps(body).encode('utf-8')
                    
                    req = urllib.request.Request(
                        url, 
                        data=data, 
                        headers={'Content-Type': 'application/json'},
                        method='POST'
                    )
                    
                    with urllib.request.urlopen(req, timeout=15) as response:
                        resultado = json.loads(response.read().decode('utf-8'))
                        resposta_direta = resultado['candidates'][0]['content']['parts'][0]['text']
                except urllib.error.HTTPError as http_err:
                    # Se der erro do Google, captura o motivo exato enviado por eles
                    try:
                        erro_corpo = http_err.read().decode('utf-8')
                        detalhes = json.loads(erro_corpo)
                        msg_google = detalhes['error']['message']
                        resposta_direta = f"O Google recusou a conexão (Erro {http_err.code}): {msg_google}. Verifique se sua chave da API está correta e ativa."
                    except:
                        resposta_direta = f"Erro HTTP {http_err.code}. Verifique sua chave de API no painel do Render."
                except Exception as e:
                    resposta_direta = f"Ocorreu um erro de rede: {str(e)}"

    return render_template_string(HTML_TEMPLATE, resposta_direta=resposta_direta, query=query)

if __name__ == '__main__':
    app.run(debug=False)
