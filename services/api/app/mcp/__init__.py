"""LabOS MCP Server V1.

The only official Tool-Surface for ABrain. This package is a pure adapter:
it translates JSON-RPC 2.0 MCP requests into calls against the existing
LabOS services (`abrain_actions`, `abrain_execution`, `abrain_context`).
No business logic, no agent loop, no dynamic discovery.
"""
