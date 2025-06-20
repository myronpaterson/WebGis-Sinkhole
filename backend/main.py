import os
import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Carrega as variáveis de ambiente do arquivo .env (nossa DATABASE_URL)
load_dotenv()

# Cria a instância principal da nossa aplicação API
app = FastAPI()

# --- Configuração do CORS (MUITO IMPORTANTE) ---
# Por segurança, os navegadores bloqueiam um site (ex: localhost:3000)
# de fazer requisições para um servidor em um endereço diferente (ex: localhost:8000).
# O CORS é a configuração que cria uma "ponte de permissão" entre eles.
# Aqui, estamos dizendo para o nosso backend: "Qualquer pedido vindo de localhost:3000 é confiável".
origins = [
    "http://localhost:3000", # Endereço padrão onde aplicações React rodam em desenvolvimento
     "http://localhost:5173", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permitimos todos os métodos (GET, POST, etc.)
    allow_headers=["*"], # Permitimos todos os cabeçalhos
)

def conectar_db():
    """Função para conectar ao banco de dados."""
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# --- Endpoints da API (O "menu" de pedidos que nosso garçom atende) ---

@app.get("/")
def raiz():
    """Este é o endpoint raiz. É como o "olá" do nosso garçom.
    Ótimo para um teste rápido para ver se a API está no ar.
    """
    return {"mensagem": "Bem-vindo à API de Monitoramento do Sinkhole!"}


@app.get("/medicoes")
def obter_medicoes():
    """
    Este é o nosso endpoint principal. Quando chamado, ele busca todas as
    medições do banco de dados e as retorna em formato JSON.
    """
    conn = conectar_db()
    if not conn:
        return {"erro": "Não foi possível conectar ao banco de dados"}

    medicoes_formatadas = []
    try:
        with conn.cursor() as cur:
            # Este é o comando SQL. Observe duas coisas importantes:
            # 1. JOIN: Estamos juntando as tabelas 'medicoes' e 'dados_sinkhole' para pegar dados de ambas.
            # 2. ST_AsGeoJSON: Esta é a função MÁGICA do PostGIS. Ela converte o formato de geometria
            #    complexo do banco em um texto simples no padrão GeoJSON, que é o que os
            #    mapas na web (Leaflet, Mapbox) entendem.
            cur.execute("""
                SELECT
                    m.id,
                    m.id_relatorio,
                    m.data_medicao,
                    d.area_m2,
                    d.perimetro_m,
                    d.diametro_externo_maior_m,
                    d.diametro_externo_menor_m,
                    ST_AsGeoJSON(d.geometria) as geometria_geojson
                FROM
                    medicoes m
                JOIN
                    dados_sinkhole d ON m.id = d.medicao_id
                ORDER BY
                    m.data_medicao DESC;
            """)
            
            resultados = cur.fetchall()
            nomes_colunas = [desc[0] for desc in cur.description]
            
            for resultado in resultados:
                medicoes_formatadas.append(dict(zip(nomes_colunas, resultado)))

    except Exception as e:
        return {"erro": f"Erro ao buscar dados: {e}"}
    finally:
        if conn:
            conn.close()

    return medicoes_formatadas