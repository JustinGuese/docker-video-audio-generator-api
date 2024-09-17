FROM python:3.11-slim
RUN apt update && apt install -y ffmpeg
RUN pip install poetry && poetry config virtualenvs.create false
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --only root
COPY ./src/ /app/
CMD ["uvicorn", "api:app", "--host", "0.0.0.0"]