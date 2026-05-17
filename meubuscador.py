from flask import Flask, render_template_string, request
import urllib.request
import urllib.parse
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
    <title>IA Search Pro - Futurista</title>
    <style>
        /* Fundo Dinâmico Espacial/Cyberpunk baseado na sua imagem */
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

        /* Rede Neural de Fundo (Simulando as linhas da imagem usando CSS) */
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

        /* Menu Superior Sóbrio (Igual ao do laptop) */
        .navbar {
            width: 100%;
            max-width: 1200px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            box-sizing: border-box;
        }
        .nav-links {
            display: flex;
            gap: 20px;
        }
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
        .nav-auth {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        .btn-login {
            color: #fff;
            text-decoration: none;
            font-size: 14px;
        }

        /* Container Principal Centralizado */
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
            margin-top: -40px; /* Sobe um pouco para centralizar melhor */
        }

        /* Animação de Entrada Fluida */
        @keyframes cyberGlow {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Barra de Busca Neon Estilo Holograma (IDÊNTICA À IMAGEM) */
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
            border-radius: 50px; /* Totalmente arredondada como a foto */
            outline: none; 
            box-sizing: border-box;
            backdrop-filter: blur(10px); /* Efeito Vidro Fosco */
            transition: all 0.3s ease;
            box-shadow: inset 0 0 15px rgba(0, 242, 254, 0.05);
        }

        /* Efeito de Foco com Brilho Neon Ciano Expandido */
        input:focus { 
            border-color: #00f2fe; 
            box-shadow: 0 0 25px rgba(0, 242, 254, 0.35), inset 0 0 10px rgba(0, 242, 254, 0.1);
        }

        /* Botão Lupa de Pesquisa dentro do Input */
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
        .search-btn:active { transform: scale(0.92); }

        /* Ícones de Atalhos Inferiores (Igual ao Computador/Celular da foto) */
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
            cursor: pointer;
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
            transform: translateY(-3px);
        }
        .shortcut-item:hover {
            color: #fff;
        }

        /* Card de Resultados em formato de Painel Holográfico */
        .result-card {
            width: 100%;
            background: rgba(10, 25, 36, 0.7); 
            padding: 30px; 
            border-radius: 20px; 
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(0, 242, 254, 0.05); 
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
            font-weight: 600; 
            border-bottom: 1px solid rgba(0, 242, 254, 0.1);
            padding-bottom: 12px;
            letter-spacing: 0.5px;
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
        .section-label {
            color: #5c7580;
            font-size: 11px;
            text-transform: uppercase;
            margin-bottom: 5px;
            font-weight: 600;
            letter-spacing: 1px;
        }
        .response-text { 
            font-size: 15px; 
            color: #c4c4cc; 
            line-height: 1.7; 
        }
        .links-container {
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.05);
        }
        .link-item a { 
            color: #00f2fe; 
            text-decoration: none; 
            font-weight: 500; 
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
        }
        .link-item a:hover { 
            color: #fff;
            text-shadow: 0 0 8px #00f2fe;
            transform: translateX(4px);
        }

        /* Responsividade para Celulares (Mobile Layout igual à imagem da direita) */
        @media (max-width: 600px) {
            body { padding: 15px; }
            .navbar { display: none; } /* Esconde o menu grande no celular */
            .main-container { margin-top: 40px; }
            h2 { font-size: 22px; }
            .shortcuts-container { gap: 15px; }
            .shortcut-icon { width: 44px; height: 44px; font-size: 16px; }
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
        <div class="nav-auth">
            <a href="#" class="btn-login">Login</a>
        </div>
    </header>

    <div class="main-container">
        
        <div class="search-wrapper">
            <form action="/" method="POST" class="search-form">
                <input type="text" name="query" placeholder="Pesquisa de Mercado | Digite sua busca..." value="{{ query }}" required>
                <button type="submit" class="search-btn">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                </button>
            </form>
        </div>

        <div class="shortcuts-container">
            <a href="https://duckduckgo.com" target="_blank" class="shortcut-item">
                <div class="shortcut-icon">🔍</div>
                <span>Populares</span>
            </a>
            <div class="shortcut-item">
                <div class="shortcut-icon">📊</div>
                <span>Categorias</span>
            </a>
            <div class="shortcut-item">
                <div class="shortcut-icon">⏳</div>
                <span>Histórico</span>
            </div>
        </div>

        {% if resposta_direta %}
        <div class="result-card">
            <div class="data-badge">{{ modo_busca }}</div>
            <h3 class="response-title">Central de Informações Estruturadas</h3>
            
            <div class="section-label" style="margin-top: 15px;">Dados Coletados:</div>
            <p class="response-text">{{ resposta_direta }}</p>
            
            {% if links_referencia %}
            <div class="links-container">
                <div class="section-label" style="margin-bottom: 10px;">Acessar Fontes Estendidas:</div>
                {% for link in links_referencia %}
                    <div class="link-item">
                        <a href="{{ link.href }}" target="_blank">➔ {{ link.title }}</a>
                    </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        {% endif %}

    </div>

</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    resposta_direta = ""
    links_referencia = []
    modo_busca = "Sistema de Busca Ativo"
    query = ""
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            try:
                termo_formatado = urllib.parse.quote(query)
                url = f"https://api.duckduckgo.com/?q={termo_formatado}&format=json&no_html=1&kl=br-pt"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, timeout=8) as response:
                    dados = json.loads(response.read().decode('utf-8'))
                    if dados.get("AbstractText"):
                        resposta_direta = dados.get("AbstractText")
                        if dados.get("AbstractURL"):
                            links_referencia.append({'title': 'Diretório Oficial de Dados', 'href': dados.get("AbstractURL")})
                    elif dados.get("RelatedTopics"):
                        for topico in dados["RelatedTopics"][:3]:
                            if "Text" in topico and not resposta_direta:
                                resposta_direta = topico["Text"]
                            if "FirstURL" in topico:
                                titulo_link = topico.get("Text", "Link Relacionado").split(" - ")[0][:60]
                                links_referencia.append({'title': titulo_link, 'href': topico["FirstURL"]})
            except Exception:
                pass
            if not resposta_direta:
                modo_busca = "Roteamento de Emergência"
                resposta_direta = f"Análise concluída para o termo: '{query}'. Para obter relatórios em tempo real e gráficos expandidos, utilize os canais integrados seguros abaixo."
                links_referencia = [
                    {'title': f"Explorar Base Gráfica para '{query}'", 'href': f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"},
                    {'title': f"Ver Histórico Enciclopédico de '{query}'", 'href': f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(query)}"}
                ]
    return render_template_string(HTML_TEMPLATE, resposta_direta=resposta_direta, links_referencia=links_referencia, modo_busca=modo_busca, query=query)

if __name__ == '__main__':
    app.run(debug=False)
