FROM python:3.9-buster

WORKDIR /peru
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "app/app.py"]
