import uuid
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver


from ai_engine.utils import logger
from ai_engine.agents.registry import State, BaseAgent
from ai_engine.agents.utils import load_chat_model, get_cur_time_with_utc
from ai_engine.agents.chatbot.configuration import ChatbotConfiguration
from ai_engine.agents.tools_factory import get_all_tools

class ChatbotAgent(BaseAgent):
    name = "chatbot"
    description = "Basic chatbot that can answer questions. By default, it doesn't use any tools, but needed tools can be enabled in the configuration."
    requirements = ["TAVILY_API_KEY", "ZHIPUAI_API_KEY"]
    config_schema = ChatbotConfiguration

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_tools(self, tools: list[str]):
        """Get tools based on configuration.
        By default, no tools are used.
        If the configuration is a list, use the tools in the list.
        """
        platform_tools = get_all_tools()
        if tools is None or not isinstance(tools, list) or len(tools) == 0:
            # By default, no tools are used
            logger.info("No tools configured or configuration is empty, no tools will be used")
            return []
        else:
            # Use tools specified in the configuration
            tool_names = [tool for tool in platform_tools.keys() if tool in tools]
            logger.info(f"Using tools: {tool_names}")
            return [platform_tools[tool] for tool in tool_names]

    def llm_call(self, state: State, config: RunnableConfig = None) -> dict[str, Any]:
        """Call the LLM model"""
        config_schema = config or {}
        conf = self.config_schema.from_runnable_config(config_schema)

        system_prompt = f"{conf.system_prompt} Now is {get_cur_time_with_utc()}"
        model = load_chat_model(conf.model)
        model_with_tools = model.bind_tools(self._get_tools(conf.tools))
        logger.info(f"llm_call with config: {conf}, {conf.model}")

        res = model_with_tools.invoke(
            [{"role": "system", "content": system_prompt}, *state["messages"]]
        )
        return {"messages": [res]}

    def get_graph(self, config_schema: RunnableConfig = None, **kwargs):
        """Build the graph"""
        conf = self.config_schema.from_runnable_config(config_schema)
        workflow = StateGraph(State, config_schema=self.config_schema)
        workflow.add_node("chatbot", self.llm_call)
        workflow.add_node("tools", ToolNode(tools=self._get_tools(conf.tools)))
        workflow.add_edge(START, "chatbot")
        workflow.add_conditional_edges(
            "chatbot",
            tools_condition,
        )
        workflow.add_edge("tools", "chatbot")
        workflow.add_edge("chatbot", END)

        graph = workflow.compile(checkpointer=MemorySaver())
        return graph


def main():
    agent = ChatbotAgent(config=ChatbotConfiguration())

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    from ai_engine.agents.utils import agent_cli
    agent_cli(agent, config)


if __name__ == "__main__":
    main()
    # asyncio.run(main())
