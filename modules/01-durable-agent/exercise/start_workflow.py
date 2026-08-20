import asyncio
import sys
import uuid
from datetime import timedelta

from agents import trace
from temporalio.client import Client
from temporalio.contrib.openai_agents import ModelActivityParameters, OpenAIAgentsPlugin
from temporalio.envconfig import ClientConfig

from agent_workflow import AgentWorkflow

TASK_QUEUE = "durable-agent-tq"


async def main() -> None:
    plugin = OpenAIAgentsPlugin(
        model_params=ModelActivityParameters(
            start_to_close_timeout=timedelta(seconds=60),
        )
    )

    config = ClientConfig.load_client_connect_config()
    config.setdefault("target_host", "localhost:7233")
    client = await Client.connect(**config, plugins=[plugin])

    question = sys.argv[1] if len(sys.argv) > 1 else "What is the weather in Melbourne?"

    # trace() gives the workflow's spans a parent, so the Agents SDK can export them.
    with trace("AgentWorkflow"):
        result = await client.execute_workflow(
            AgentWorkflow.run,
            question,
            id=f"durable-agent-{uuid.uuid4()}",
            task_queue=TASK_QUEUE,
        )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
