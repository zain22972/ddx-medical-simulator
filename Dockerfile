FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" pydantic requests gradio
COPY src/ ./src/
ENV PYTHONPATH=/app/src
ENV DDX_TASK_ID=1
ENV HOST=0.0.0.0
ENV PORT=7860
EXPOSE 7860
CMD ["uvicorn", "envs.ddx_env.server.app:app", "--host", "0.0.0.0", "--port", "7860"]
