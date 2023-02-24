FROM python:3.10

RUN apt-get update && apt-get install -y ffmpeg

RUN pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu


WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]