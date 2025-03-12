# Usa uma imagem leve do Python
FROM python:3.9-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia apenas as dependências primeiro (melhora o cache do Docker)
COPY requirements.txt ./

# Instala as dependências do Locust
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos para o container
COPY . .

# Define a porta do Locust para expor no container
EXPOSE 8089  

# Define o comando de inicialização do Locust
CMD ["locust", "-f", "locustfile.py", "--host=http://api.local"]
