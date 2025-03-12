# Usa uma imagem leve do Python
FROM python:3.9-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia e instala dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Define variáveis de ambiente para integração com o nginx-proxy
ENV VIRTUAL_HOST=api.local
ENV VIRTUAL_PORT=8000

# Comando para rodar a API
CMD ["uvicorn", "routes:app", "--host", "0.0.0.0", "--port", "8000"]
