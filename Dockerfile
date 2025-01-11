FROM python:3.13-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=1.8.5
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock ./

# Install dependencies (no virtual environment)
RUN poetry config virtualenvs.create false
RUN poetry install --only=main --no-root

# Stage 2: Final stage
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy only installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY . .

# Set the default command
CMD ["python", "src/run.py"]
