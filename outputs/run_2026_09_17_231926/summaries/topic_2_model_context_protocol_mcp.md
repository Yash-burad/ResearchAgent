# Model Context Protocol (MCP)

## One-Line Explanation
The Model Context Protocol (MCP) is an open standard introduced by Anthropic that standardizes how AI models securely connect to external data sources, tools, and prompts.

## Simple Explanation
Think of MCP like the USB-C standard for AI applications. Before USB-C, every device required a proprietary cable, making hardware integration a combinatorial nightmare. Similarly, AI applications previously required custom, hardcoded integrations for every database, API, or file system they needed to access. MCP provides a universal, standardized interface so any LLM client can plug into any data provider or tool without writing custom adapter code.

## Why This Is Trending
As generative AI moves from chat interfaces to autonomous agents executing complex workflows, context fragmentation has become a primary engineering bottleneck. Developers waste significant time writing fragile, custom integrations connecting LLMs to internal enterprise tools (e.g., GitHub, Postgres, Slack). MCP is trending because it decouples model clients from data providers, establishing a unified protocol that drastically reduces integration overhead, accelerates enterprise adoption, and prevents vendor lock-in.

## How It Works
MCP follows a client-server architecture built on JSON-RPC 2.0:
- **MCP Hosts:** The AI applications (like Claude Desktop or custom agent runtimes) that initiate connections.
- **MCP Clients:** Components within the host that maintain secure 1:1 connections with servers.
- **MCP Servers:** Lightweight programs that expose specific capabilities through three core primitives:
  - **Resources:** Contextual data the model can read (files, database schemas, API payloads).
  - **Prompts:** Pre-configured templates and workflows provided by the server to guide user interaction.
  - **Tools:** Executable functions that allow the model to take actions (running code, writing files, executing database mutations).

Communication occurs locally via standard input/output (stdio) or remotely via Server-Sent Events (SSE), ensuring strict security and sandboxing boundaries.

## Real-World Example
A software engineering team builds an internal MCP server connected to their staging Kubernetes cluster and PostgreSQL database. When an engineer asks their IDE-integrated AI assistant, "Why is the payment service crashing?", the AI uses the MCP server's exposed tools to query recent logs from Kubernetes and inspect the relevant database schema. The model processes this structured context securely without requiring the engineering team to build a bespoke integration for that specific AI client.

## Interview Explanation
When discussing MCP in an architecture review or system design interview, frame it as an **abstraction and decoupling layer**. Emphasize how it solves the $N \times M$ integration problem (where $N$ LLMs need to talk to $M$ internal tools) by reducing it to $N + M$ standard connections. Highlight its security boundaries: because MCP servers run locally or in isolated containers with explicitly granted permissions, you mitigate the risk of arbitrary code execution or unauthorized data exfiltration common in naive LLM tool-calling setups.

## System Design Relevance
In large-scale enterprise architectures, MCP sits at the edge of the AI inference layer and internal microservices:
- **Security & Sandboxing:** MCP servers act as policy enforcement points (PEP), ensuring LLMs only access authorized schemas and endpoints through defined schemas.
- **Latency:** Local stdio transports introduce negligible latency, whereas remote SSE transports add network overhead that must be accounted for in synchronous agent workflows.
- **Failure Modes:** If an MCP server crashes or becomes unresponsive, the client must handle timeouts gracefully without crashing the core agent loop or corrupting ongoing model context windows.

## Pros
- **Standardized Integration:** Reduces custom connector maintenance by enforcing a universal protocol for tools, resources, and prompts.
- **Enhanced Security Boundaries:** Isolates data access and execution logic away from the core LLM runtime via well-defined JSON-RPC interfaces.
- **Ecosystem Interoperability:** Allows developers to write an MCP server once and use it across any supporting LLM client or agent framework.

## Cons / Limitations
- **Protocol Overhead:** JSON-RPC serialization and abstraction layers can add slight latency overhead compared to direct, native function calls.
- **Immature Ecosystem:** Being a relatively new standard, enterprise-grade tooling, authentication mechanisms, and authorization frameworks are still evolving.
- **State Management Complexity:** Handling long-running asynchronous tool executions and maintaining state across distributed MCP servers requires careful architectural design.

## Common Interview Questions
1. How does the Model Context Protocol (MCP) solve the integration complexity between LLMs and enterprise data sources?
2. What are the architectural differences between MCP's local (stdio) and remote (SSE) transport layers, and when would you use each?
3. How do you handle security, authentication, and authorization when exposing internal databases or microservices through an MCP server?

## Strong Sample Answer
"Model Context Protocol, or MCP, is an open standard designed to solve the fragmentation of data and tool integrations in AI applications. Instead of developers writing custom adapters for every LLM and data source combination—an $N \times M$ problem—MCP standardizes communication using a client-server model over JSON-RPC. 

From an architectural perspective, MCP introduces three primitives: resources, prompts, and tools. This allows AI hosts to securely query data and execute actions without tightly coupling the model to the underlying infrastructure. In terms of tradeoffs, while MCP drastically reduces integration overhead and establishes clear security boundaries via sandboxed servers, it introduces an abstraction layer that can add serialization overhead and requires robust handling of transport-level failures and state synchronization in distributed agentic workflows."

## Related Concepts To Learn Next
- Function Calling / Tool Use in LLMs
- Agentic Workflows & Multi-Agent Systems
- JSON-RPC 2.0 and Server-Sent Events (SSE)

## Sources
- [Introduction to Model Context Protocol](https://modelcontextprotocol.io/) (Anthropic)