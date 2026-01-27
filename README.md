# Demo Mlflow Agent Tracing

## Introduction

## Getting Started

### Prerequisites

In order to work on this project, the following tools *must* be installed:

- [`uv`](https://docs.astral.sh/uv/)
- [`just`](https://just.systems/man/en/)
- [`oc`](https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html) (**optional**)

### Initial Steps
To begin working on this project:

1. Clone the repository to your local system via `git clone`
1. Change directory to the project `cd demo_mlflow_agent_tracing`
1. Install the project dependencies `uv sync --all-groups`
1. Run `just` to see available recipes

### Layout

The simplified directory structure is as follows:

```
├── demo_mlflow_agent_tracing
│   ├── main.py
│   └── __init__.py
├── tests/
├── sql
│   └── sample.sql
├── docs/
├── notebooks/
├── webapp
│   ├── intro.py
│   ├── static
│   │   ├── images/
│   │   └── markdown/
│   └── pages
│       └── app.py
└── oc-templates/
    ├── base/
    └── overlays/
```

- [demo_mlflow_agent_tracing](./src/demo_mlflow_agent_tracing) contains the main application code.
- [notebooks](./notebooks) should contain any notebooks you are experimenting with and/or wish to commit
- [tests](./tests) contains the the test code
    - Testing is done via `pytest`. Additionally, `pytest-cov` is used for coverage reporting. Minimum of 80% coverage.
- **If** there is documentation, they are located in [docs](./docs) and are built using `sphinx`
- **If** there is a webapp involved
    - It is built with `streamlit`
    - Markdown files are located in [markdown](./webapp/markdown) and loaded into the webapp via `st.markdown(util.read_markdown_file("file.md"))`
- Please see this [ReadMe](./oc-templates/README.md) to learn about how resources are deployed into OpenShift

In order to contribute, prior to making any MR the following is necessary:

1. Run `just pre-mr` to format, lint, and test the code