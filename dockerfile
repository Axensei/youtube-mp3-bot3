# Usa Python 3.13 slim come base
FROM python:3.13-slim

# Aggiorna i pacchetti e installa ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Imposta la cartella di lavoro
WORKDIR /app

# Copia requirements.txt e installa dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il resto del progetto
COPY . .

# Comando per avviare il bot
CMD ["python", "bot.py"]
