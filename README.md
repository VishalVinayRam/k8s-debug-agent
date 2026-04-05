# k8s-debug-agent

A conversation-driven agentic debugging system for Linux and Kubernetes environments. This agent allows engineers to describe issues in natural language, automatically executes safe diagnostic commands, and gathers context from logs, code, and tickets to guide toward root causes and resolution.

The system is designed with a "human-in-the-loop" philosophy, ensuring that the agent remains an informative assistant that requires explicit approval for any impactful actions.

---

## Architecture

The system consists of a core agent layer that orchestrates multiple sub-agents and communicates with MCP (Model Context Protocol) servers.

- **OpenCode Agent Layer**: Interacts with the user and coordinates sub-agents for codebase analysis, Jira/Confluence queries, and internal documentation retrieval.
- **MCP Servers**: Exposes localized tools to the agent.
  - `linux-node-1`: A custom Python-based MCP server providing system and Kubernetes diagnostic tools.
  - `github`: Standard GitHub MCP for repository and issue management.
  - `jira`: Standard Jira MCP for ticket lifecycle management.

### MCP Server (`mcp-server/`)

The primary interaction point for system diagnostics is the Python MCP server:
- Implements the `execute_command` tool for safe command execution.
- Uses SSE (Server-Sent Events) for transport.
- Runs within restricted Docker containers with read-only filesystems and minimum required capabilities.
- All commands are validated against a strict guardrails allowlist before execution.

---

## Build & Run

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- `kubectl` configured with cluster access (if diagnosing a Kubernetes cluster)

### Start the MCP Server

```bash
cd mcp-server
docker compose up --build
```

The SSE endpoint is available at `http://localhost:8080/sse` by default.

### Local Development

For development without Docker:

```bash
cd mcp-server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

### OpenCode Configuration

Add the following to your `opencode.json` configuration:

```jsonc
{
  "mcp": {
    "linux-node-1": { "type": "remote", "url": "http://<IP>:8080/sse" }
  }
}
```

---

## Guardrails

The `execute_command` tool enforces an **allowlist-only** policy. Any command not explicitly permitted is blocked by default.

### Permitted Commands

| Category | Allowed Commands |
|---|---|
| Kubernetes | `kubectl get`, `kubectl describe`, `kubectl logs`, `kubectl top`, `kubectl events` |
| System | `ps`, `top`, `free`, `df`, `du`, `uptime`, `uname`, `hostname`, `env` |
| Networking | `ss`, `netstat`, `ip`, `ping`, `dig`, `nslookup`, `traceroute`, `lsof` |
| Logs | `journalctl`, `cat` (verified log paths), `tail` |
| Containers | `docker ps`, `docker inspect`, `docker logs`, `docker stats` |
| Storage | `mount`, `lsblk`, `pvs`, `vgs`, `lvs` |

### Blocked Operations

- **File Mutation**: No `rm`, `mv`, `cp` to system paths, or output redirection (`>`).
- **Device Operations**: No `dd`, `mkfs`, or disk partitioning tools.
- **Network Mutation**: No `iptables` modification or interface manipulation.
- **K8s Mutation**: No `kubectl delete`, `apply`, `patch`, or `edit`.
- **Privilege Escalation**: No `sudo`, `su`, or file permission changes (`chmod`, `chown`).
- **System Control**: No `reboot`, `shutdown`, or `systemctl` stop/disable.

All commands are subject to a **30-second timeout** to prevent hanging processes.

---

## Development

### Python Standards
- Async-first implementation using `asyncio`.
- Full type hinting with `typing`.
- No mutable global state.
- Structured JSON error reporting.

### Docker Standards
- Base image: `python:3.11-slim`.
- Execution as non-root `appuser`.
- Read-only root filesystem.
- Minimal capabilities (no `--privileged`).

### Testing
Unit tests are located in `mcp-server/tests/` and can be executed via `pytest`. Guardrails must be independently tested for allowlist enforcement and edge-case handling.
