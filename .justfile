default_version := `uv version --short`
project_name := "demo_mlflow_agent_tracing"

_default:
    @ just --list --unsorted --justfile {{ justfile() }}

# Runs recipes for MR approval
pre-mr: format lint test

# Formats code
[group("Dev")]
format:
    uv run ruff check --select I --fix src tests 
    uv run ruff format src tests 

# Lints code
[group("Dev")]
lint *options:
    uv run ruff check src tests  {{ options }}

# Tests code
[group("Dev")]
test *options:
    uv run pytest -s tests/ {{ options }}

# Increments the code version
[group("Dev")]
bump type:
    uv run bump2version --current-version={{ default_version }} {{ type }}
    uv lock

# Builds the image
[group("Dev")]
build-image tag="latest":
    podman build -t {{ project_name }}:latest -f Containerfile .

# Runs the container
[group("Testing")]
test-container: (build-image "latest")
    - podman run \
        --rm \
        --name {{ project_name }} \
        -p 8000:8000 \
        -v ./.env:/opt/app-root/src/.env \
        -it {{ project_name }}:latest 

