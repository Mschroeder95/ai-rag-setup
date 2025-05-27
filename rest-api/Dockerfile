FROM python:3.11-slim

# create & switch to working dir
WORKDIR /code

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY app/ ./app

ENV PYTHONPATH=/code/app

# tell Docker how to run FastAPI via Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
