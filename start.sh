uv run --locked --no-sync scripts/ingest.py
uv run --locked --no-sync chainlit run src/demo_mlflow_agent_tracing/app.py --host 0.0.0.0 --port 8000