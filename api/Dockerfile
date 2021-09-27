FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
COPY ./app/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
ADD ./app /app
