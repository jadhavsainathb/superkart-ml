FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --default-timeout=100 \
    --retries 5 \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superKart_predictor_api"]