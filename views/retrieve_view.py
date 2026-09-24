import streamlit as st
from openai import OpenAIError
from rag.retrieve import top_k
from views.score_badge import score_badge

def render(chunks):
    st.header("Retrieve")
    st.write(f"Knowledge base loaded: **{len(chunks)} chunks**")

    query = st.text_input("Enter a query to test retrieval:")
    k = st.slider("Number of results (k)", min_value=1, max_value=10, value=3)

    if st.button("Search", key="retrieve_search"):
        if query:
            try:
                with st.spinner("Searching..."):
                    results = top_k(query, chunks, k=k)
            except OpenAIError as e:
                st.error(f"OpenAI API error while embedding your query: {e}")
                results = None
            if results:
                for r in results:
                    st.markdown(f"{score_badge(r['score'])} `{r['source']}` — *{r['category']}*")
                    st.write(r["text"][:300] + "...")
                    st.divider()
        else:
            st.warning("Enter a query first.")