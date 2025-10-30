"""
Modelos Pydantic para a API do Dicionário Vetorial

Este módulo contém todas as classes de dados utilizadas pela API,
incluindo modelos de request, response e validação de dados.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class PalavraRequest(BaseModel):
    """Modelo para requisição de adição de nova palavra"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "palavra": "cachorro",
                "definicao": "animal doméstico quadrúpede da família dos canídeos"
            }
        }
    )
    
    palavra: str = Field(
        ...,
        description="A palavra a ser adicionada ao dicionário",
        min_length=1,
        max_length=100,
        example="cachorro"
    )
    definicao: str = Field(
        ...,
        description="Definição ou significado da palavra",
        min_length=1,
        max_length=500,
        example="animal doméstico quadrúpede da família dos canídeos"
    )


class BuscaRequest(BaseModel):
    """Modelo para requisição de busca semântica"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "local onde alguém vive",
                "limit": 5
            }
        }
    )
    
    query: str = Field(
        ...,
        description="Texto para busca semântica no dicionário",
        min_length=1,
        max_length=200,
        example="local onde alguém vive"
    )
    limit: Optional[int] = Field(
        default=10,
        description="Número máximo de resultados a retornar",
        ge=1,
        le=50,
        example=5
    )


class BuscaResult(BaseModel):
    """Modelo para resultado individual de busca"""
    palavra: tuple = Field(
        ...,
        description="Tupla contendo a palavra e sua definição",
        example=["casa", "local onde alguém mora"]
    )
    score: float = Field(
        ...,
        description="Score de similaridade semântica (0-1, maior é melhor)",
        ge=0.0,
        le=1.0,
        example=0.8945
    )


class BuscaResponse(BaseModel):
    """Modelo para resposta completa de busca"""
    model_config = ConfigDict(
        json_schema_extra={
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
                    }
                ]
            }
        }
    )
    
    query: str = Field(..., description="Query original da busca")
    resultados: List[BuscaResult] = Field(
        ...,
        description="Lista de resultados ordenados por relevância"
    )


class StatusResponse(BaseModel):
    """Modelo para resposta de status do sistema"""
    status: str = Field(..., description="Status geral do sistema", example="ok")
    qdrant_conectado: bool = Field(..., description="Se a conexão com Qdrant está ativa")
    colecoes: int = Field(..., description="Número de coleções no Qdrant")
    modelo_carregado: bool = Field(..., description="Se o modelo SentenceTransformer está carregado")
    inicializado: bool = Field(..., description="Se o serviço foi completamente inicializado")


class EstatisticasResponse(BaseModel):
    """Modelo para resposta de estatísticas da coleção"""
    nome_colecao: str = Field(..., description="Nome da coleção no Qdrant")
    total_palavras: int = Field(..., description="Número total de palavras no dicionário")
    dimensoes_vetor: int = Field(..., description="Dimensões dos vetores de embedding")
    distancia: str = Field(..., description="Métrica de distância utilizada")


class AdicionarResponse(BaseModel):
    """Modelo para resposta de adição de palavra"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Palavra adicionada com sucesso",
                "palavra": "cachorro",
                "definicao": "animal doméstico quadrúpede da família dos canídeos",
                "id": 13
            }
        }
    )
    
    message: str = Field(..., description="Mensagem de confirmação")
    palavra: str = Field(..., description="Palavra que foi adicionada")
    definicao: str = Field(..., description="Definição que foi adicionada")
    id: int = Field(..., description="ID único da palavra na coleção")