## simplified guide to uv package manager

adding/removing dependencies to the project

```bash
uv add [PACKAGE]
uv remove [PACKAGE]
```

syncing environment with `uv.lock`, which is what streamlit cloud uses

```bash
uv sync
```

running commands or executing entrypoint

```bash
uv run [COMMAND]
```

Reference uv Docs: https://docs.astral.sh/uv/