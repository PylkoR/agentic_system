import sys
from pathlib import Path

# Ensure project root is in sys.path when running script directly from subfolders
project_root = Path(__file__).resolve().parents[2] if "src" in Path(__file__).resolve().parts else Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from src.tools.tools import ALL_SANDBOX_TOOLS

# Tool lookup map
tools_by_name = {t.name: t for t in ALL_SANDBOX_TOOLS}

# 1. Initialize LLM with bound sandbox tools
llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0.0  # Zero temperature for deterministic tool calls
)
llm_with_tools = llm.bind_tools(ALL_SANDBOX_TOOLS)

# 2. Define system prompt instructions
system_prompt = SystemMessage(content="""
You are an autonomous software engineer operating inside an isolated 'sandbox' environment.
You have access to the following tools:
- write_sandbox_file: Create and save code/files
- read_sandbox_file: Inspect existing code and files
- list_sandbox_files: View available directory contents
- execute_python_sandbox_file: Run Python scripts inside sandbox

Workflow:
1. When asked to solve a task, write clean code and save it using write_sandbox_file.
2. Execute the script using execute_python_sandbox_file to verify it runs without errors.
3. If an error occurs, inspect it, fix the file, and re-run.
4. Present the final verified solution to the user.
Important: Always operate strictly within the sandbox environment.
""")

messages = [system_prompt]

print("=" * 60)
print("🤖 Sandbox Agent initialized (Type 'exit' to quit)")
print("🔒 Human-in-the-loop enabled: every action requires approval [y/n]")
print("=" * 60)

while True:
    user_input = input("\nUser: ").strip()
    if user_input.lower() in ["exit", "quit", "q"]:
        break
    if not user_input:
        continue

    messages.append(HumanMessage(content=user_input))

    # Agent execution loop
    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        # Break loop when model produces standard text without requesting any tools
        if not response.tool_calls:
            print(f"\nAgent: {response.content}")
            break

        # Process requested tool invocations
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            print("\n" + "-" * 50)
            print("⚠️  AGENT ACTION REQUEST:")
            print(f"Tool:   {tool_name}")
            print(f"Params: {tool_args}")
            print("-" * 50)

            # Human authorization prompt
            confirm = input("👉 Allow this action? [y/n]: ").strip().lower()

            if confirm in ["y", "yes", "t"]:
                tool_output = tools_by_name[tool_name].invoke(tool_args)
                print(f"⚙️ Execution result: {tool_output}")
            else:
                tool_output = "DENIED: The user rejected execution of this tool call."
                print("❌ Action blocked by user.")

            # Append tool output back into conversation history
            messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"]))