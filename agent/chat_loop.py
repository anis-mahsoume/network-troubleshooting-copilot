import json
from openai import OpenAI
from agent.schemas import TOOLS
from agent.tools import TOOL_FUNCTIONS
from rag.retrieve import load_chunks, top_k

client = OpenAI()
chunks = load_chunks()

def format_context(retrieved_chunks):
    if not retrieved_chunks:
        return "No relevant documentation found."
    parts = []
    for r in retrieved_chunks:
        parts.append(f"[Source: {r['source']}]\n{r['text']}")
    return "\n\n---\n\n".join(parts)

def run_conversation(user_message, k=3):
    retrieved = top_k(user_message, chunks, k=k)
    context = format_context(retrieved)

    print("[RETRIEVAL] Retrieved the following relevant documentation chunks:")
    for r in retrieved:
        print(f"  [{r['score']:.3f}] {r['source']}")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a network troubleshooting assistant. "
                "Use the retrieved documentation below and the available tools to diagnose the user's issue.\n\n"
                "Citation rules:\n"
                "- When referencing documentation inline, use: [Doc: filename]\n"
                "- When referencing a tool result inline, use: [Tool: tool_name] — plain tool name only "
                "(e.g. 'ping_host'), never prefixed with 'functions.' or any namespace.\n"
                "- Never use markdown links for citations — plain text labels only.\n\n"
                "At the end of every answer, add a final section titled exactly 'Sources used:' followed by "
                "a bullet list of every document and every tool you actually used to reach your answer. "
                "Example:\n"
                "Sources used:\n"
                "- [Doc: troubleshoot-vpn-connectivity.pdf]\n"
                "- [Tool: ping_host]\n"
                "- [Tool: check_device_status]\n\n"
                "If you called a tool or used a retrieved document, it must appear in this list. "
                "If you didn't use retrieved documentation or didn't call any tools, state that explicitly "
                "in the Sources used section (e.g. 'No tools called — answered from documentation only').\n\n"
                f"Retrieved documentation:\n{context}"
            )
        },
        {"role": "user", "content": user_message}
    ]

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS
        )
        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return msg.content

        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)
            print(f"[TOOL CALL] {fn_name}({fn_args})")

            result = TOOL_FUNCTIONS[fn_name](**fn_args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })


if __name__ == "__main__":
    test_message = "VPN gateway vpn-gw-01 seems unstable — can you check if it's healthy and also test connectivity to it?"
    answer = run_conversation(test_message)
    print(f"\nFinal answer:\n{answer}")