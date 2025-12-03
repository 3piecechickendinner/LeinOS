# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM python:3.11-slim

RUN pip install --no-cache-dir uv==0.8.13

WORKDIR /code

# Copy dependency files
COPY ./pyproject.toml ./README.md ./uv.lock* ./

# Copy all application code
COPY ./agents ./agents
COPY ./api ./api
COPY ./core ./core
COPY ./shared_tools ./shared_tools
COPY ./.env.example ./.env.example

# Install dependencies
RUN uv sync --frozen

# Build arguments for versioning
ARG COMMIT_SHA=""
ENV COMMIT_SHA=${COMMIT_SHA}

ARG AGENT_VERSION=0.0.0
ENV AGENT_VERSION=${AGENT_VERSION}

# Environment variables for production
ENV GOOGLE_PROJECT_ID=${GOOGLE_CLOUD_PROJECT}
ENV GOOGLE_CLOUD_LOCATION=us-central1
ENV GOOGLE_GENAI_USE_VERTEXAI=True

EXPOSE 8080

# Use our existing FastAPI application
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
