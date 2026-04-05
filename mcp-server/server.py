import asyncio
import subprocess
import os
import sys
from typing import List, Optional

from mcp.server.fastapi import FastApiServer
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import BaseModel, Field

from guardrails import validate_command, clean_command

# Initialize the MCP Server via FastAPI
server = FastApiServer("k8s-debug-agent", version="0.1.0")

class ExecuteCommandInput(BaseModel):
    command: str = Field(description="The shell command to execute for diagnostics.")

@server.tool("execute_command")
async def execute_command(input: ExecuteCommandInput) -> List[TextContent]:
    """
    Executes a system diagnostic command. 
    Only allowlisted, read-only commands (kubectl, ps, top, etc.) are permitted.
    """
    cmd_str = input.command
    
    if not validate_command(cmd_str):
        return [TextContent(type="text", text=f"Error: Command '{cmd_str}' is blocked by guardrails or not allowlisted.")]

    cleaned_args = clean_command(cmd_str)
    
    try:
        # Execute the command with a 30-second timeout
        process = await asyncio.create_subprocess_exec(
            *cleaned_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
        
        output = stdout.decode().strip()
        error = stderr.decode().strip()
        
        full_response = output
        if error:
            full_response += f"\n\n--- Standard Error ---\n{error}"
            
        return [TextContent(type="text", text=full_response)]
        
    except asyncio.TimeoutError:
        return [TextContent(type="text", text="Error: Command timed out after 30 seconds.")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: Execution failed: {str(e)}")]

if __name__ == "__main__":
    import uvicorn
    # Use environment variables for port configuration (default 8080)
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(server.app, host="0.0.0.0", port=port)
