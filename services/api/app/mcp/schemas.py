"""JSON-RPC 2.0 request/response schemas for the LabOS MCP Server.

These are intentionally minimal and strict. The server only implements the
subset of MCP required to expose LabOS tools and resources:

  - initialize
  - tools/list, tools/call
  - resources/list, resources/read
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MCPRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    jsonrpc: str = Field(pattern=r'^2\.0$')
    id: int | str | None = None
    method: str = Field(min_length=1, max_length=120)
    params: dict[str, Any] = Field(default_factory=dict)


class MCPError(BaseModel):
    code: int
    message: str
    data: dict[str, Any] | None = None


class MCPResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    jsonrpc: str = '2.0'
    id: int | str | None = None
    result: dict[str, Any] | None = None
    error: MCPError | None = None


class MCPToolDefinition(BaseModel):
    name: str
    description: str
    inputSchema: dict[str, Any]
    annotations: dict[str, Any] = Field(default_factory=dict)


class MCPToolCall(BaseModel):
    model_config = ConfigDict(extra='forbid')

    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    trace_id: str | None = None
    reason: str | None = None
    approve: bool = False


class MCPToolResultContent(BaseModel):
    type: str = 'json'
    data: dict[str, Any]


class MCPToolResult(BaseModel):
    isError: bool = False
    content: list[MCPToolResultContent]
    structuredContent: dict[str, Any] = Field(default_factory=dict)


class MCPResourceDescriptor(BaseModel):
    uri: str
    name: str
    description: str
    mimeType: str = 'application/json'


class MCPResourceRead(BaseModel):
    uri: str
    mimeType: str = 'application/json'
    text: str | None = None
    json_: dict[str, Any] | None = Field(default=None, alias='json')

    model_config = ConfigDict(populate_by_name=True)


# JSON-RPC standard error codes (MCP reuses them)
ERROR_PARSE = -32700
ERROR_INVALID_REQUEST = -32600
ERROR_METHOD_NOT_FOUND = -32601
ERROR_INVALID_PARAMS = -32602
ERROR_INTERNAL = -32603
# MCP-specific
ERROR_UNAUTHORIZED = -32001
ERROR_FORBIDDEN = -32002
ERROR_NOT_FOUND = -32003
