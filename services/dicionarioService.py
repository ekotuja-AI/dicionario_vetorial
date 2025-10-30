import os
import time
from typing import List, Tuple

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models


class DicionarioService:
    """Serviço responsável por toda a lógica de negócio do dicionário vetorial"""
    
    def __init__(self):
        self.client = None
        self.model = None
        self.collection_name = "dicionario_pt"
        self._initialized = False
    
    def inicializar(self):
        """Inicializa conexão com Qdrant e carrega modelo"""
        if self._initialized:
            return
            
        print("🚀 Inicializando serviço de dicionário vetorial...")
        self._conectar_qdrant()
        self._carregar_modelo()
        self._inicializar_colecao()
        self._initialized = True
        print("✅ Serviço inicializado com sucesso!")
    
    def _conectar_qdrant(self):
        """Estabelece conexão com Qdrant"""
        host = os.getenv("QDRANT_HOST", "localhost")
        port = int(os.getenv("QDRANT_PORT", "6333"))
        
        # Aguarda Qdrant estar disponível
        max_retries = 30
        for attempt in range(max_retries):
            try:
                self.client = QdrantClient(host=host, port=port)
                # Testa a conexão
                self.client.get_collections()
                print(f"✅ Conectado ao Qdrant em {host}:{port}")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⏳ Aguardando Qdrant... Tentativa {attempt + 1}/{max_retries}")
                    time.sleep(2)
                else:
                    raise Exception(f"❌ Erro ao conectar com Qdrant após {max_retries} tentativas: {e}")
    
    def _carregar_modelo(self):
        """Carrega modelo SentenceTransformer"""
        print("📚 Carregando modelo SentenceTransformer...")
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("✅ Modelo carregado com sucesso")
    
    def _inicializar_colecao(self):
        """Cria coleção e insere dados iniciais se necessário"""
        try:
            # Verifica se coleção existe
            collections = self.client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)
            
            if not collection_exists:
                print("🔧 Criando coleção e inserindo dados iniciais...")
                self._criar_colecao_com_dados_iniciais()
            else:
                print("✅ Coleção já existe, usando dados existentes")
                
        except Exception as e:
            print(f"❌ Erro ao inicializar coleção: {e}")
            raise
    
    def _criar_colecao_com_dados_iniciais(self):
        """Cria coleção e insere dados iniciais"""
        # Palavras exemplo
        palavras = [
            ("banana", "fruta tropical amarela rica em potássio"),
            ("abacaxi", "fruta tropical com casca áspera e sabor agridoce"),
            ("lar", "local onde alguém mora"),
            ("casa", "local onde alguém mora"),
            ("moradia", "local onde alguém mora, casa, residência"),
            ("felicidade", "sentimento positivo de alegria e contentamento"),
            ("tristeza", "sentimento negativo de melancolia e infelicidade"),
            ("amizade", "relação afetiva entre pessoas baseada em confiança e carinho"),
            ("melão", "fruta tropical de casca verde e polpa doce"),
            ("ciúmes", "sentimento de insegurança e possessividade em relação a algo ou alguém"),
            ("Jacarta", "capital da Indonésia"),
            ("Brasília", "capital do Brasil"),
        ]
        
        # Gerar embeddings
        vetores = self.model.encode([desc for _, desc in palavras])
        
        # Criar coleção
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(size=vetores.shape[1], distance=models.Distance.COSINE)
        )
        
        # Inserir dados
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(id=i, vector=vetores[i].tolist(), payload={"palavra": palavras[i]})
                for i in range(len(palavras))
            ]
        )
        
        print(f"✅ Inseridas {len(palavras)} palavras no banco vetorial")
    
    def verificar_status(self) -> dict:
        """Verifica status da conexão com Qdrant e modelo"""
        try:
            collections = self.client.get_collections() if self.client else None
            return {
                "status": "ok",
                "qdrant_conectado": self.client is not None,
                "colecoes": len(collections.collections) if collections else 0,
                "modelo_carregado": self.model is not None,
                "inicializado": self._initialized
            }
        except Exception as e:
            return {
                "status": "error",
                "erro": str(e),
                "qdrant_conectado": False,
                "modelo_carregado": self.model is not None,
                "inicializado": self._initialized
            }
    
    def buscar_palavras(self, query: str, limit: int = 10) -> List[Tuple[Tuple[str, str], float]]:
        """Busca palavras semanticamente similares à query"""
        if not self._initialized:
            raise Exception("Serviço não foi inicializado")
        
        # Gerar embedding da query
        query_vector = self.model.encode([query])[0].tolist()
        
        # Buscar no Qdrant
        result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        # Formatar resultados
        return [(r.payload['palavra'], r.score) for r in result]
    
    def adicionar_palavra(self, palavra: str, definicao: str) -> dict:
        """Adiciona uma nova palavra ao dicionário"""
        if not self._initialized:
            raise Exception("Serviço não foi inicializado")
        
        # Gerar embedding da definição
        embedding = self.model.encode([definicao])[0].tolist()
        
        # Buscar próximo ID disponível
        novo_id = self._obter_proximo_id()
        
        # Inserir nova palavra
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=novo_id, 
                    vector=embedding, 
                    payload={"palavra": (palavra, definicao)}
                )
            ]
        )
        
        return {
            "message": "Palavra adicionada com sucesso",
            "palavra": palavra,
            "definicao": definicao,
            "id": novo_id
        }
    
    def _obter_proximo_id(self) -> int:
        """Obtém o próximo ID disponível para inserção"""
        # Busca por todos os pontos para encontrar o maior ID
        scroll_result = self.client.scroll(
            collection_name=self.collection_name,
            limit=10000  # Ajuste conforme necessário
        )
        
        max_id = 0
        if scroll_result[0]:  # Se há pontos na coleção
            max_id = max(point.id for point in scroll_result[0])
        
        return max_id + 1
    
    def obter_estatisticas(self) -> dict:
        """Obtém estatísticas da coleção"""
        if not self._initialized:
            raise Exception("Serviço não foi inicializado")
        
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "nome_colecao": self.collection_name,
                "total_palavras": collection_info.points_count,
                "dimensoes_vetor": collection_info.config.params.vectors.size,
                "distancia": collection_info.config.params.vectors.distance.value
            }
        except Exception as e:
            return {"erro": f"Erro ao obter estatísticas: {str(e)}"}


# Instância global do serviço
dicionario_service = DicionarioService()