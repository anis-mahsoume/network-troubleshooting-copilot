import streamlit as st
from openai import OpenAIError
from agent.chat_loop import run_agent
from views.score_badge import score_badge


SCENARIOS = {
    "-- Free text --": None,
    "VPN - intermittent drops": "My VPN keeps dropping every few minutes during video calls",
    "VPN - gateway health + connectivity": "VPN gateway vpn-gw-01 seems unstable — can you check if it's healthy and also test connectivity to it?",
    "DNS - specific domain failure": "Can you check why internal-api.company.com isn't resolving for some users?",
    "DHCP - client can't get lease": "A laptop with MAC address 00:1A:2B:3C:4D:5E isn't getting an IP address, can you check its lease status?",
    "Firewall - device health": "Is firewall-02 currently healthy? We've had reports of intermittent connectivity through it.",
    "Routing - slow connection between subnets": "Users on the 10.0.4.0/24 subnet report slow connections to 10.0.8.50 — can you check what's going on?",
}


def render(chunks):
    st.header("Chat")

    scenario_choice = st.selectbox("Choose a scenario, or write your own below:", list(SCENARIOS.keys()))
    default_text = SCENARIOS[scenario_choice] or ""
    user_message = st.text_area("Describe the network/IT problem:", value=default_text)

    if st.button("Diagnose", key="diagnose_button"):
        if user_message:
            try:
                with st.spinner("Retrieving documentation and reasoning..."):
                    retrieved, tool_calls_made, answer = run_agent(user_message, chunks)
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