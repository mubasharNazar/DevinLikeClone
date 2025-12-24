from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from .prompts import *
from .states import *
from .tools import *
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from langgraph.constants import END
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.callbacks.base import BaseCallbackHandler
import time

load_dotenv()


# ------------------------------
# LLM Debug Callback Handler
# ------------------------------
class DebugLLMCallback(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        self.start_time = time.time()
        print(f"[LLM START] Prompts: {prompts}")

    def on_llm_end(self, response, **kwargs):
        elapsed = time.time() - self.start_time
        print(f"[LLM END] Response: {response} (Time: {elapsed:.2f}s)")

    def on_llm_error(self, error, **kwargs):
        print(f"[LLM ERROR] {error}")

# ------------------------------
# Tool Debug Decorator
# ------------------------------
def debug_tool(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        print(f"[TOOL START] {func.__name__} called with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"[TOOL END] {func.__name__} returned {result} (Time: {elapsed:.2f}s)")
        return result
    return wrapper


llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0,
    callbacks=[StreamingStdOutCallbackHandler(), DebugLLMCallback()] 
)


def planner_agent(state: dict) -> dict:
    """Converts user prompt into a structured Plan."""
    user_prompt = state["user_prompt"]
    resp = llm.with_structured_output(Plan).invoke(
        planner_prompt(user_prompt)
    )
    if resp is None:
        raise ValueError("Planner did not return a valid response.")
    return {"plan": resp}


def architect_agent(state: dict) -> dict:
    """Creates TaskPlan from Plan."""
    plan: Plan = state["plan"]
    resp = llm.with_structured_output(TaskPlan, method="function_calling").invoke(
        architect_prompt(plan=plan.model_dump_json())
    )
    if resp is None:
        raise ValueError("Planner did not return a valid response.")
    resp.plan = plan
    return {"task_plan": resp}


def coder_agent(state: dict) -> dict:
    """LangGraph tool-using coder agent."""
    coder_state: CoderState = state.get("coder_state")
    if coder_state is None:
        coder_state = CoderState(task_plan=state["task_plan"], current_step_idx=0)

    steps = coder_state.task_plan.implementation_steps
    if coder_state.current_step_idx >= len(steps):
        return {"coder_state": coder_state, "status": "DONE"}

    current_task = steps[coder_state.current_step_idx]
    existing_content = read_file.run(current_task.filepath)

    system_prompt = coder_system_prompt()
    user_prompt = (
        f"Task: {current_task.task_description}\n"
        f"File: {current_task.filepath}\n"
        f"Existing content:\n{existing_content}\n"
        "Use write_file(path, content) to save your changes."
    )

    coder_tools = [read_file, write_file, list_files, get_current_directory]
    react_agent = create_react_agent(llm, coder_tools)

    react_agent.invoke({"messages": [{"role": "system", "content": system_prompt},
                                     {"role": "user", "content": user_prompt}]})

    coder_state.current_step_idx += 1
    return {"coder_state": coder_state}


graph = StateGraph(dict)

graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)
graph.add_node("coder", coder_agent)

graph.add_edge("planner", "architect")
graph.add_edge("architect", "coder")
graph.add_conditional_edges(
    "coder",
        lambda s: "END" if s.get("status") == "DONE" else "coder",
    {"END": END, "coder": "coder"}
)

graph.set_entry_point("planner")
agent = graph.compile()

if __name__ == "__main__":
    result = agent.invoke({"user_prompt": "Build a colourful modern todo app in html css and js"},
                          {"recursion_limit": 100})
    print("Final State:", result)