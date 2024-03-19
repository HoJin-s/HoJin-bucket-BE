FROM python:3.9

COPY . /fastapi
WORKDIR /fastapi

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
RUN pip install gunicorn

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]