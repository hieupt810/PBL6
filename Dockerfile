FROM python:3.12.7-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /fastapi
COPY . /fastapi/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /fastapi/requirements.txt

EXPOSE 8000
CMD [ "fastapi", "run", "app/main.py", "--port", "8000"]
