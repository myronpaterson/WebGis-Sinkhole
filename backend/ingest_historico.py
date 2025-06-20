import os
import psycopg2
from dotenv import load_dotenv
import sys

# --- PASSO 1: CARREGAR E VERIFICAR A URL ---
print("--- INICIANDO TENTATIVA FINAL DE INSERÇÃO ---")
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERRO CRÍTICO: A variável DATABASE_URL não foi lida. Verifique o arquivo .env e salve-o.")
    sys.exit() # Interrompe o script se a URL não for lida

# Imprime o endereço do servidor de forma segura (sem a senha) para confirmação
safe_url_part = DATABASE_URL.split('@')[-1]
print(f"✅ SUCESSO: A URL foi lida. O script tentará se conectar a: ...@{safe_url_part}")


# --- PASSO 2: DADOS A SEREM INSERIDOS (código original) ---
medicoes_historicas = [
    {
        "id_relatorio": "MEDIÇÃO 112", "data_medicao": "2025-05-27", "responsavel": "Aline Lago Guimarães",
        "area": 3666.20, "perimetro": 259.65, "diametro_maior": 118.07, "diametro_menor": 52.75,
        "geometria_wkt": "POLYGON((-38.756469 -13.012653, -38.755775 -13.011919, -38.756325 -13.012006, -38.756469 -13.012653))"
    },
    {
        "id_relatorio": "MEDIÇÃO 111", "data_medicao": "2025-04-28", "responsavel": "Aline Lago Guimarães",
        "area": 3663.70, "perimetro": 259.63, "diametro_maior": 117.76, "diametro_menor": 52.75,
        "geometria_wkt": "POLYGON((-38.756469 -13.012653, -38.755775 -13.011919, -38.756325 -13.012006, -38.756469 -13.012653))"
    },
    {
        "id_relatorio": "MEDIÇÃO 110", "data_medicao": "2025-03-25", "responsavel": "Aline Lago Guimarães",
        "area": 3663.70, "perimetro": 259.63, "diametro_maior": 117.76, "diametro_menor": 52.75,
        "geometria_wkt": "POLYGON((-38.756469 -13.012653, -38.755775 -13.011919, -38.756325 -13.012006, -38.756469 -13.012653))"
    }
]

# --- PASSO 3: CONEXÃO E INSERÇÃO (código original) ---
conn = None
try:
    print("\nIniciando conexão com o banco de dados...")
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ SUCESSO: Conexão estabelecida!")
    
    with conn.cursor() as cur:
        print("Iniciando a inserção de dados...")
        for medicao in medicoes_historicas:
            cur.execute(
                "INSERT INTO medicoes (data_medicao, id_relatorio, nome_responsavel) VALUES (%s, %s, %s) RETURNING id;",
                (medicao["data_medicao"], medicao["id_relatorio"], medicao["responsavel"])
            )
            medicao_id = cur.fetchone()[0]
            print(f" -> Inserido em 'medicoes': {medicao['id_relatorio']}")
            
            cur.execute(
                "INSERT INTO dados_sinkhole (medicao_id, area_m2, perimetro_m, diametro_externo_maior_m, diametro_externo_menor_m, geometria) VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326));",
                (medicao_id, medicao["area"], medicao["perimetro"], medicao["diametro_maior"], medicao["diametro_menor"], medicao["geometria_wkt"])
            )
            print(f"  -> Inserido em 'dados_sinkhole' para a medição ID {medicao_id}")
    
    conn.commit()
    print("\n✅ SUCESSO FINAL: Todos os dados foram inseridos e salvos no banco!")

except Exception as e:
    if conn:
        conn.rollback()
    print("\n❌ FALHA: Ocorreu um erro durante a operação com o banco de dados.")
    print(f"   -> DETALHES DO ERRO: {e}")

finally:
    if conn:
        conn.close()
        print("\nConexão com o banco de dados fechada.")