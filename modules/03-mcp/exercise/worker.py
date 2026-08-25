import asyncio
import os
from datetime import timedelta
from pathlib import Path

from agents.mcp import MCPServerStdio
from temporalio.client import Client
from temporalio.contrib.openai_agents import (
    ModelActivityParameters,
    OpenAIAgentsPlugin,
    StatelessMCPServerProvider,
)
from temporalio.envconfig import ClientConfig
from temporalio.worker import Worker

from agent_workflow import AgentWorkflow
from tool_activities import (
    get_coordinates,
    get_ip_address,
    get_location_info,
    get_weather,
)

TASK_QUEUE = "mcp-agent-tq"
MCP_SERVER_NAME = "sessions"
MCP_SERVER_HOME = os.environ.get(
    "MCP_SERVER_HOME", str(Path(__file__).resolve().parents[2] / "mcp-server")
)


def _sessions_server_factory() -> MCPServerStdio:
    return MCPServerStdio(
        name=MCP_SERVER_NAME,
        params={
            "command": "uv",
            "args": ["run", "python", "-m", "server"],
            "cwd": MCP_SERVER_HOME,
        },
        cache_tools_list=True,
    )


async def main() -> None:
    plugin = OpenAIAgentsPlugin(
        model_params=ModelActivityParameters(
            start_to_close_timeout=timedelta(seconds=60),
        ),
        # TODO: Uncomment the block below.
        # mcp_server_providers=[
        #     StatelessMCPServerProvider(
        #         name=MCP_SERVER_NAME,
        #         server_factory=_sessions_server_factory,
        #     ),
        # ],
    )

    config = ClientConfig.load_client_connect_config()
    config.setdefault("target_host", "localhost:7233")
    client = await Client.connect(**config, plugins=[plugin])

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[AgentWorkflow],
        activities=[
            get_ip_address,
            get_location_info,
            get_coordinates,
            get_weather,
        ],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
