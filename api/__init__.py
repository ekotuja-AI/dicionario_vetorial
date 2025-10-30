"""
Pacote API do Dicionário Vetorial

Este pacote contém todos os módulos relacionados à API REST:
- dicionarioAPI.py: Endpoints e configuração da API
- models.py: Modelos Pydantic para validação de dados
- config.py: Configurações centralizadas da aplicação
"""

__version__ = "1.0.0"
__author__ = "Eduardo Kotujansky"

# Exportar classes principais para facilitar importação
from .models import (
    PalavraRequest,
    BuscaRequest,
    BuscaResult,
    BuscaResponse,
    StatusResponse,
    EstatisticasResponse,
    AdicionarResponse
)
from .config import APIConfig

__all__ = [
    "PalavraRequest",
    "BuscaRequest", 
    "BuscaResult",
    "BuscaResponse",
    "StatusResponse",
    "EstatisticasResponse",
    "AdicionarResponse",
    "APIConfig"
]