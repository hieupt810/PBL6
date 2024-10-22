FROM python:3.12.7-alpine

WORKDIR /fastapi

COPY . /fastapi/
RUN pip install --no-cache-dir --upgrade -r /fastapi/requirements.txt

EXPOSE 8000
CMD [ "fastapi", "run", "app/main.py", "--port", "8000"]
