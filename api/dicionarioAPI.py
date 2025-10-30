import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi import status as http_status
from fastapi.responses import JSONResponse
import uvicorn

import sys
sys.path.append('.')
from services.dicionarioService import dicionario_service
from api.models import (
    PalavraRequest,
    BuscaRequest,
    BuscaResult,
    BuscaResponse,
    StatusResponse,
    EstatisticasResponse,
    AdicionarResponse
)
from api.config import APIConfig

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Iniciando API do dicionário vetorial...")
    dicionario_service.inicializar()
    print("✅ API iniciada com sucesso!")
    yield
    # Shutdown
    print("🛑 Encerrando API...")

# Configuração detalhada da aplicação FastAPI
app = FastAPI(
    **APIConfig.get_fastapi_config(),
    lifespan=lifespan
)

@app.get(
    "/",
    tags=["Sistema"],
    summary="Informações da API",
    description="Endpoint raiz que retorna informações básicas sobre a API e seus endpoints disponíveis",
    response_description="Informações básicas da API"
)
async def root():
    """
    ## Endpoint Raiz
    
    Retorna informações básicas sobre a API, incluindo:
    * Nome e versão da API
    * Lista de endpoints principais
    * Links para documentação
    
    **Não requer parâmetros**
    """
    return {
        "message": "Dicionário Vetorial API", 
        "version": "1.0.0",
        "description": "API para busca semântica usando embeddings",
        "endpoints": {
            "buscar": "/buscar - Busca semântica de palavras",
            "adicionar": "/adicionar - Adiciona nova palavra",
            "status": "/status - Status dos serviços",
            "estatisticas": "/estatisticas - Estatísticas da coleção"
        },
        "documentacao": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get(
    "/status",
    tags=["Sistema"],
    summary="Status do Sistema",
    description="Verifica a saúde e status de todos os componentes do sistema",
    response_model=StatusResponse,
    responses={
        200: {
            "description": "Status obtido com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "qdrant_conectado": True,
                        "colecoes": 1,
                        "modelo_carregado": True,
                        "inicializado": True
                    }
                }
            }
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "erro": "Conexão com Qdrant falhou",
                        "qdrant_conectado": False,
                        "modelo_carregado": True,
                        "inicializado": False
                    }
                }
            }
        }
    }
)
async def status():
    """
    ## Verificação de Status
    
    Verifica o status de todos os componentes:
    * **Qdrant**: Conexão com banco vetorial
    * **Modelo**: SentenceTransformer carregado
    * **Inicialização**: Serviço completamente inicializado
    
    **Útil para:**
    * Health checks
    * Monitoramento
    * Troubleshooting
    """
    return dicionario_service.verificar_status()

@app.get(
    "/estatisticas",
    tags=["Sistema"],
    summary="Estatísticas da Coleção",
    description="Obtém métricas e estatísticas detalhadas da coleção de palavras",
    response_model=EstatisticasResponse,
    responses={
        200: {
            "description": "Estatísticas obtidas com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "nome_colecao": "dicionario_pt",
                        "total_palavras": 12,
                        "dimensoes_vetor": 384,
                        "distancia": "Cosine"
                    }
                }
            }
        },
        500: {"description": "Erro ao obter estatísticas"}
    }
)
async def estatisticas():
    """
    ## Estatísticas da Coleção
    
    Retorna informações detalhadas sobre a coleção:
    * **Nome da coleção** no Qdrant
    * **Total de palavras** armazenadas
    * **Dimensões do vetor** de embedding
    * **Métrica de distância** utilizada
    
    **Útil para:**
    * Monitoramento de crescimento
    * Análise de performance
    * Configuração de sistemas
    """
    try:
        return dicionario_service.obter_estatisticas()
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )

@app.post(
    "/buscar",
    tags=["Busca"],
    summary="Busca Semântica",
    description="Realiza busca semântica no dicionário usando embeddings para encontrar palavras similares",
    response_model=BuscaResponse,
    responses={
        200: {
            "description": "Busca realizada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "query": "local onde alguém vive",
                        "resultados": [
                            {
                                "palavra": ["casa", "local onde alguém mora"],
                                "score": 0.8945
                            },
                            {
                                "palavra": ["moradia", "local onde alguém mora, casa, residência"],
                                "score": 0.8723
                            },
                            {
                                "palavra": ["lar", "local onde alguém mora"],
                                "score": 0.8456
                            }
                        ]
                    }
                }
            }
        },
        422: {"description": "Erro de validação nos dados de entrada"},
        500: {"description": "Erro interno do servidor"}
    }
)
async def buscar_palavras(request: BuscaRequest):
    """
    ## Busca Semântica de Palavras
    
    Utiliza embeddings de linguagem para encontrar palavras semanticamente similares.
    
    **Como funciona:**
    1. Converte sua query em vetor de embedding
    2. Busca vetores similares na base Qdrant
    3. Retorna palavras ordenadas por similaridade
    
    **Parâmetros:**
    * **query**: Texto para buscar (ex: "animal de estimação")
    * **limit**: Máximo de resultados (1-50, padrão: 10)
    
    **Score:** Valor entre 0-1, onde 1 = match perfeito
    
    **Exemplos de queries:**
    * "sentimento de alegria" → felicidade, contentamento
    * "fruta doce" → banana, melão, abacaxi
    * "lugar para morar" → casa, lar, moradia
    """
    try:
        resultados_raw = dicionario_service.buscar_palavras(request.query, request.limit)
        
        # Formatar resultados
        resultados = [
            BuscaResult(palavra=palavra, score=score)
            for palavra, score in resultados_raw
        ]
        
        return BuscaResponse(query=request.query, resultados=resultados)
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na busca: {str(e)}"
        )

@app.post(
    "/adicionar",
    tags=["Gestão"],
    summary="Adicionar Palavra",
    description="Adiciona uma nova palavra e sua definição ao dicionário vetorial",
    response_model=AdicionarResponse,
    status_code=http_status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Palavra adicionada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Palavra adicionada com sucesso",
                        "palavra": "cachorro",
                        "definicao": "animal doméstico quadrúpede da família dos canídeos",
                        "id": 13
                    }
                }
            }
        },
        400: {"description": "Dados inválidos fornecidos"},
        422: {"description": "Erro de validação nos dados de entrada"},
        500: {"description": "Erro interno do servidor"}
    }
)
async def adicionar_palavra(request: PalavraRequest):
    """
    ## Adicionar Nova Palavra
    
    Expande o dicionário adicionando uma nova palavra com sua definição.
    
    **Processo:**
    1. Valida os dados de entrada
    2. Gera embedding da definição
    3. Armazena no banco vetorial Qdrant
    4. Retorna confirmação com ID único
    
    **Regras:**
    * Palavra: 1-100 caracteres
    * Definição: 1-500 caracteres
    * Cada palavra recebe um ID único
    
    **Dicas para boas definições:**
    * Seja específico e claro
    * Use linguagem simples
    * Inclua contexto quando necessário
    * Evite circularidade (definir palavra usando ela mesma)
    
    **Exemplos:**
    * ❌ "carro: é um carro"
    * ✅ "carro: veículo automotor de quatro rodas"
    """
    try:
        resultado = dicionario_service.adicionar_palavra(request.palavra, request.definicao)
        return resultado
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar palavra: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "dicionarioAPI:app", 
        host=APIConfig.HOST, 
        port=APIConfig.PORT, 
        reload=APIConfig.RELOAD
    )