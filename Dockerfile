FROM python:3.10.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
RUN pip install --upgrade pip
COPY . /code/
COPY requirements.txt /code/
RUN pip install -r requirements.txt