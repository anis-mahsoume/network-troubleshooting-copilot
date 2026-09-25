import json
import streamlit as st
from openai import OpenAI, OpenAIError
from rag.retrieve import top_k
from agent.tools import TOOL_FUNCTIONS
from agent.schemas import TOOLS
from views.score_badge import score_badge

client = OpenAI()

SCENARIOS = {
    "-- Free text --": None,
    "VPN - intermittent drops": "My VPN keeps dropping every few minutes during video calls",
    "VPN - gateway health + connectivity": "VPN gateway vpn-gw-01 seems unstable — can you check if it's healthy and also test connectivity to it?",
    "DNS - specific domain failure": "Can you check why internal-api.company.com isn't resolving for some users?",
    "DHCP - client can't get lease": "A laptop with MAC address 00:1A:2B:3C:4D:5E isn't getting an IP address, can you check its lease status?",
    "Firewall - device health": "Is firewall-02 currently healthy? We've had reports of intermittent connectivity through it.",
    "Routing - slow connection between subnets": "Users on the 10.0.4.0/24 subnet report slow connections to 10.0.8.50 — can you check what's going on?",
}


def format_context(retrieved_chunks):
    if not retrieved_chunks:
        return "No relevant documentation found."
    parts = []
    for r in retrieved_chunks:
        parts.append(f"[Source: {r['source']}]\n{r['text']}")
    return "\n\n---\n\n".join(parts)


def run_conversation_ui(user_message, chunks, k=3):
    """Same logic as chat_loop.py's run_conversation, but returns data instead of printing it."""
    retrieved = top_k(user_message, chunks, k=k)
    context = format_context(retrieved)

    tool_calls_made = []

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
                "a bullet list of every document and every tool you actually used.\n\n"
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
            return retrieved, tool_calls_made, msg.content

        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)
            result = TOOL_FUNCTIONS[fn_name](**fn_args)
            tool_calls_made.append({"name": fn_name, "args": fn_args, "result": result})

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })


def render(chunks):
    st.header("Chat")

    scenario_choice = st.selectbox("Choose a scenario, or write your own below:", list(SCENARIOS.keys()))
    default_text = SCENARIOS[scenario_choice] or ""
    user_message = st.text_area("Describe the network/IT problem:", value=default_text)

    if st.button("Diagnose", key="diagnose_button"):
        if user_message:
            try:
                with st.spinner("Retrieving documentation and reasoning..."):
                    retrieved, tool_calls_made, answer = run_conversation_ui(user_message, chunks)
            except OpenAIError as e:
                st.error(f"OpenAI API error: {e}")
                retrieved, tool_calls_made, answer = None, None, None

            if answer:
                st.subheader("Sources retrieved")
                for r in retrieved:
                    st.markdown(f"{score_badge(r['score'])} `{r['source']}` — *{r['category']}*")

                st.subheader("Tools called")
                if tool_calls_made:
                    for t in tool_calls_made:
                        st.markdown(f"**{t['name']}**({t['args']})")
                        st.json(t["result"])
                else:
                    st.write("No tools were called for this query.")

                st.subheader("Diagnosis")
                st.markdown(answer)
        else:
            st.warning("Enter a problem description first.")