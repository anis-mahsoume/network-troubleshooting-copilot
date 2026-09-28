import streamlit as st
from rag.ingest import get_ingestion_status, process_folder


def render(chunks):
    st.header("Ingest")
    st.write(
        f"Knowledge base loaded: **{len(chunks)} chunks** "
        f"across **{len(set(c['source'] for c in chunks))} documents**"
    )

    st.divider()
    st.subheader("Ingestion status")

    status = get_ingestion_status()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Ingested ({len(status['ingested'])})**")
        for f in status["ingested"]:
            st.write(f"- {f}")

    with col2:
        st.markdown(f"**Pending ({len(status['pending'])})**")
        for f in status["pending"]:
            st.write(f"- {f}")

    if status["pending"]:
        st.divider()
        confirm = st.checkbox("I understand this will call the OpenAI embeddings API and may take a moment.")
        if st.button("Run ingestion on pending files", disabled=not confirm):
            with st.spinner(f"Ingesting {len(status['pending'])} file(s)..."):
                process_folder()
            st.success("Ingestion complete. Reloading knowledge base...")
            st.cache_data.clear()  # force get_chunks() in app.py to reload chunks.json
            st.rerun()

    st.divider()
    st.subheader("Browse knowledge base")

    by_source = {}
    for c in chunks:
        by_source.setdefault(c["source"], []).append(c)

    for source, source_chunks in sorted(by_source.items()):
        category = source_chunks[0]["category"]
        with st.expander(f"{source} — {category} ({len(source_chunks)} chunks)"):
            for c in source_chunks:
                st.markdown(f"**Chunk {c['chunk_id']}**")
                st.write(c["text"])
                st.divider()