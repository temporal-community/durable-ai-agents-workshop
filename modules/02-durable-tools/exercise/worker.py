import asyncio
from datetime import timedelta

from temporalio.client import Client
from temporalio.contrib.openai_agents import ModelActivityParameters, OpenAIAgentsPlugin
from temporalio.envconfig import ClientConfig
from temporalio.worker import Worker

from agent_workflow import AgentWorkflow
from tool_activities import (
    get_coordinates,
    get_ip_address,
    get_location_info,
    get_weather,
)

TASK_QUEUE = "durable-tools-tq"


async def main() -> None:
    plugin = OpenAIAgentsPlugin(
        model_params=ModelActivityParameters(
            start_to_close_timeout=timedelta(seconds=60),
        )
    )

    config = ClientConfig.load_client_connect_config()
    config.setdefault("target_host", "localhost:7233")
    client = await Client.connect(**config, plugins=[plugin])

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[AgentWorkflow],
        # TODO: Uncomment the block below.
        # activities=[
        #     get_ip_address,
        #     get_location_info,
        #     get_coordinates,
        #     get_weather,
        # ],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
