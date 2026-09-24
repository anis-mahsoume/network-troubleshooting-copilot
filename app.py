import json
import streamlit as st
from rag.retrieve import load_chunks
from views import ingest_view, retrieve_view, chat_view

st.set_page_config(page_title="Network Troubleshooting Copilot", layout="wide")
st.title("Network Troubleshooting Copilot")
st.caption("AI-powered network troubleshooting assistant")

@st.cache_data
def get_chunks():
    try:
        return load_chunks()
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

chunks = get_chunks()

if chunks is None:
    st.error(
        "No knowledge base found. Run ingestion first "
        "(place PDFs in `data/raw/` and use the Ingest tab, or run `python -m rag.ingest`)."
    )
    st.stop()

tab_ingest, tab_retrieve, tab_chat = st.tabs(["📥 Ingest", "🔍 Retrieve", "💬 Chat"])

with tab_ingest:
    ingest_view.render(chunks)

with tab_retrieve:
    retrieve_view.render(chunks)

with tab_chat:
    chat_view.render(chunks)