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
    <title>Buscador Inteligente</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            background-color: #121214; 
            color: #e1e1e6; 
            padding: 40px; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            margin: 0;
            -webkit-font-smoothing: antialiased;
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .box { 
            background: #1d1d22; 
            padding: 35px; 
            border-radius: 12px; 
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); 
            border: 1px solid #29292e;
            width: 100%; 
            max-width: 680px; 
            margin-bottom: 25px; 
            animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
        }
        .result-card {
            border-left: 3px solid #a8a8b3;
            animation-delay: 0.1s;
        }
        h2 { 
            color: #ffffff; 
            margin-top: 0; 
            text-align: center; 
            font-size: 26px;
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        .search-form { 
            display: flex; 
            gap: 12px; 
            margin-top: 25px; 
        }
        input { 
            flex: 1; 
            padding: 14px 18px; 
            font-size: 16px; 
            background: #121214;
            border: 1px solid #29292e; 
            color: #ffffff;
            border-radius: 8px; 
            outline: none; 
            transition: border-color 0.25s ease, box-shadow 0.25s ease;
        }
        input:focus { 
            border-color: #4da6ff; 
            box-shadow: 0 0 0 3px rgba(77, 166, 255, 0.15);
        }
        button { 
            padding: 14px 28px; 
            font-size: 16px; 
            background: #29292e; 
            color: #ffffff; 
            border: 1px solid #323238; 
            border-radius: 8px; 
            cursor: pointer; 
            font-weight: 500; 
            transition: background 0.2s ease, border-color 0.2s ease, transform 0.1s ease;
        }
        button:hover { 
            background: #323238;
            border-color: #4da6ff;
        }
        button:active { transform: scale(0.97); }
        .response-title { 
            color: #ffffff; 
            font-size: 20px; 
            margin-top: 0; 
            margin-bottom: 20px; 
            font-weight: 600; 
            border-bottom: 1px solid #29292e;
            padding-bottom: 12px;
        }
        .data-badge {
            display: inline-block;
            background: #29292e;
            color: #c4c4cc;
            padding: 5px 12px;
            border-radius: 4px;
            font-size: 13px;
            margin-bottom: 15px;
            border: 1px solid #323238;
        }
        .section-label {
            color: #8d8d99;
            font-size: 11px;
            text-transform: uppercase;
            margin-bottom: 6px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .response-text { 
            font-size: 15px; 
            color: #c4c4cc; 
            line-height: 1.6; 
            margin-bottom: 25px;
        }
        .links-container {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #29292e;
        }
        .link-item { margin-bottom: 10px; }
        .link-item a { 
            color: #4da6ff; 
            text-decoration: none; 
            font-weight: 500; 
            font-size: 15px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: color 0.2s ease, transform 0.2s ease;
        }
        .link-item a:hover { 
            color: #80bfff;
            transform: translateX(3px);
        }
    </style>
</head>
<body>
    <div class="box">
        <h2>Buscador Inteligente</h2>
        <form action="/" method="POST" class="search-form">
            <input type="text" name="query" placeholder="O que você deseja pesquisar hoje?" value="{{ query }}" required>
            <button type="submit">Pesquisar</button>
        </form>
    </div>
    {% if resposta_direta %}
    <div class="box result-card">
        <h3 class="response-title">Resultado da Busca</h3>
        <div class="section-label">Fonte de dados:</div>
        <div class="data-badge">{{ modo_busca }}</div>
        <div class="section-label" style="margin-top: 15px;">Informações encontradas:</div>
        <p class="response-text">{{ resposta_direta }}</p>
        {% if links_referencia %}
        <div class="links-container">
            <div class="section-label" style="margin-bottom: 10px;">Links e referências úteis:</div>
            {% for link in links_referencia %}
                <div class="link-item">
                    <a href="{{ link.href }}" target="_blank">🡪 {{ link.title }}</a>
                </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    resposta_direta = ""
    links_referencia = []
    modo_busca = "Base de Dados Web"
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
                            links_referencia.append({'title': 'Artigo de Referência Principal', 'href': dados.get("AbstractURL")})
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
                modo_busca = "Direcionamento Alternativo"
                resposta_direta = f"Exibindo centrais de consulta rápidas para o termo solicitado: '{query}'."
                links_referencia = [
                    {'title': f"Buscar resultados para '{query}' na Web", 'href': f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"},
                    {'title': f"Ver verbete '{query}' na Enciclopédia Aberta", 'href': f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(query)}"}
                ]
    return render_template_string(HTML_TEMPLATE, resposta_direta=resposta_direta, links_referencia=links_referencia, modo_busca=modo_busca, query=query)

if __name__ == '__main__':
    app.run(debug=False)
