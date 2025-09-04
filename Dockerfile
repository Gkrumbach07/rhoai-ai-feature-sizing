FROM llamaindex/llama-deploy:main

# Copy the application code
COPY src/ /app/code/src/
COPY deployment.yml /app/code/
COPY pyproject.toml /app/code/

WORKDIR /app/code

# Set environment variables for LlamaDeploy
ENV LLAMA_DEPLOY_APISERVER_RC_PATH=/app/code
ENV LLAMA_DEPLOY_APISERVER_HOST=0.0.0.0
ENV LLAMA_DEPLOY_APISERVER_PORT=8000

# OpenShift compatibility
EXPOSE 8000

# For OpenShift internal communication
ENV LLAMA_DEPLOY_API_SERVER_URL="http://127.0.0.1:8000"
