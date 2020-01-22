FROM python:3.8-alpine
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
RUN mkdir /code
WORKDIR /code

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8080

CMD bash -c "gunicorn --workers=3 dispatcher.py:app -b 0.0.0.0:8080"