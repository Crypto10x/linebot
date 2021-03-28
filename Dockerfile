FROM python:3.7.9
WORKDIR /app
RUN pip install --upgrade pip
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . .
CMD gunicorn -b 0.0.0.0:$PORT app:app
