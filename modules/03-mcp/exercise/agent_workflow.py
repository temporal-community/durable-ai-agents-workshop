from __future__ import annotations

from datetime import timedelta

from temporalio import workflow
from temporalio.contrib.openai_agents.workflow import (
    activity_as_tool,
    stateless_mcp_server,
)

with workflow.unsafe.imports_passed_through():
    # Pre-imported so the workflow sandbox snapshots pydantic before the first Agent(...).
    import annotated_types  # noqa: F401
    import pydantic_core  # noqa: F401
    import pydantic_core.core_schema  # noqa: F401

    from agents import Agent, Runner

    from tool_activities import (
        get_coordinates,
        get_ip_address,
        get_location_info,
        get_weather,
    )

INSTRUCTIONS = """
You are a conference assistant. Use the provided tools to answer the user's question.
You can look up conference sessions and speakers, and you can look up the weather.
When you have enough information, reply in plain text.
Today's date is {date}.
"""

TOOL_TIMEOUT = timedelta(seconds=30)


@workflow.defn
class AgentWorkflow:
    @workflow.run
    async def run(self, question: str) -> str:
        # workflow.now() is stable across replay, unlike datetime.now().
        today = workflow.now().strftime("%Y-%m-%d")

        sessions = stateless_mcp_server(name="sessions", cache_tools_list=True)

        agent = Agent(
            name="Conference Assistant",
            instructions=INSTRUCTIONS.format(date=today),
            model="gpt-4o",
            # TODO: Uncomment the line below.
            # mcp_servers=[sessions],
            tools=[
                activity_as_tool(get_ip_address, start_to_close_timeout=TOOL_TIMEOUT),
                activity_as_tool(get_location_info, start_to_close_timeout=TOOL_TIMEOUT),
                activity_as_tool(get_coordinates, start_to_close_timeout=TOOL_TIMEOUT),
                activity_as_tool(get_weather, start_to_close_timeout=TOOL_TIMEOUT),
            ],
        )
        result = await Runner.run(agent, input=question)
        return result.final_output
