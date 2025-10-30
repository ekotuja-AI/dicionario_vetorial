# Script para Renomear o Projeto

## ⚠️ **IMPORTANTE: Execute FORA da pasta do projeto**

Este script deve ser executado na pasta pai do projeto (ex: `C:\Users\eduardok\dev\pessoal\`)

### No PowerShell:

```powershell
# 1. Navegue para a pasta pai
cd C:\Users\eduardok\dev\pessoal\

# 2. Renomeie a pasta
Rename-Item "meu_dicionario_vetorial" "dicionario_vetorial"

# 3. Entre na nova pasta
cd dicionario_vetorial
```

### No CMD:

```cmd
# 1. Navegue para a pasta pai
cd C:\Users\eduardok\dev\pessoal\

# 2. Renomeie a pasta
ren "meu_dicionario_vetorial" "dicionario_vetorial"

# 3. Entre na nova pasta
cd dicionario_vetorial
```

### Verificação:

Após renomear, verifique se tudo ainda funciona:

```powershell
# Teste rápido
python -c "from api import APIConfig; print(f'✅ {APIConfig.TITLE} - Projeto renomeado com sucesso!')"

# Teste Docker (opcional)
docker-compose up --build
```

## ✅ **Após Renomear**

O projeto terá a estrutura:

```
C:\Users\eduardok\dev\pessoal\dicionario_vetorial\
├── README.md
├── CHANGELOG.md  
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .gitignore
├── api/
└── services/
```

**Pronto!** Seu projeto agora se chama `dicionario_vetorial` 🎉