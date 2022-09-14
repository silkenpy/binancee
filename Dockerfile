FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Install Poetry
#RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
#    cd /usr/local/bin && \
#    ln -s /opt/poetry/bin/poetry && \
#    poetry config virtualenvs.create false

# Copy using poetry.lock* in case it doesn't exist yet
#COPY ./pyproject.toml ./poetry.lock* ./app/
COPY requirements.txt .
RUN pip3 install -r requirements.txt

WORKDIR app
#RUN poetry install --no-root --no-dev

COPY ./ /app
EXPOSE 8000
USER root

CMD ["python3","/app/main.py"]
