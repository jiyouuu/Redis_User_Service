# CMD ["uvicorn", "main:app", "--host","0.0.0.0", "--port","8001","--reload"]

FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

COPY ./app .

CMD ["/wait-for-it.sh", "user_db:3306", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
