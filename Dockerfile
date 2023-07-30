FROM python:3.10.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
RUN pip install --upgrade pip
COPY . /code/
COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/
RUN mkdir -p /vol/web/media
RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user
RUN chown -R django-user:django-user /vol/
RUN chmod -R 755 /vol/web/
USER django-user