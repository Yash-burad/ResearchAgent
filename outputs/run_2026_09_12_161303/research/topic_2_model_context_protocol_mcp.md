# Research Notes: Model Context Protocol (MCP)

## Definition
An open protocol developed to standardize how AI models and agent runtimes discover, connect to, and execute external tools and contextual resources.

## Why It Matters
- Eliminates bespoke point-to-point integrations between LLM apps and developer environments.
- Provides standardized schema discovery, tool invocation, and prompt template sharing.
- Enables secure context isolation and local execution via stdio or Server-Sent Events (SSE).

## Technical Details
- Transport layer: Supports stdio for local processes and SSE (Server-Sent Events) over HTTP for networked servers.
- Message Protocol: Standard JSON-RPC 2.0 request/response and notification primitives.
- Primitives: Resources (data/files), Prompts (templates), Tools (executable functions with JSON schema), and Sampling.

## Use Cases
- Enterprise developer tooling
- Database and filesystem contextualization for coding agents
- Multi-agent collaborative tool networks

## Code or Practical Examples
- Connecting an IDE assistant to a PostgreSQL database server via a local MCP server.
- Fetching GitHub issue context directly into an AI coding workflow via GitHub MCP server.

## Limitations & Drawbacks
- Early-stage ecosystem with evolving specifications.
- Transport overhead and connection management for distributed multi-hop agents.

## Related Topics
- JSON-RPC 2.0
- Language Server Protocol (LSP)
- Function Calling
- Agent Tooling

## Sources & References
1. [Model Context Protocol Specification](https://modelcontextprotocol.io) (Anthropic)
   - **Retrieved at**: 2026-06-13 12:00:00
   - **Credibility Score**: 10/10
   - **Key Points**:
     - Defines client-server architecture
     - JSON-RPC 2.0 foundation
