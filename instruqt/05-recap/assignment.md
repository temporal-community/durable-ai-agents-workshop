---
slug: recap
id: ""
type: quiz
title: "What did the plugin actually replace?"
teaser: One question before you go.
answers:
- "The retry logic, the state store, and the loop's resume point"
- "The agentic loop itself"
- "The OpenAI SDK's HTTP client"
- "The MCP server"
solution:
- 0
difficulty: basic
timelimit: 300
---

# Question

You never wrote `execute_activity`, never wrote a retry, and never stored the conversation
anywhere. The agent still survived an outage and a `SIGKILL`.

What did `OpenAIAgentsPlugin` take over on your behalf?
