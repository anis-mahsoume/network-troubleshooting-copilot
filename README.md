# Network Troubleshooting Copilot

A RAG-powered assistant for diagnosing network/IT issues. It retrieves relevant passages from a knowledge base of network troubleshooting documentation (VPN, DNS, DHCP, firewall, routing) and combines them with tool-calling to mocked diagnostic tools (ping, traceroute, DNS lookup, device status, DHCP lease checks). Usable either from the command line or through a Streamlit app.

Built as a hands-on project for RAG, embeddings, and tool/function calling.

## Project structure

```
data/
  raw/                source PDFs, organized by category (vpn/, dns/, dhcp/, firewall/, routing/)
  processed/
    chunks.json       generated output — chunked docs + embeddings (not committed if large)
rag/
  ingest.py           extracts, chunks, and embeds data/raw into data/processed/chunks.json
  retrieve.py         query the knowledge base and inspect top-k results
agent/
  schemas.py          OpenAI tool/function definitions for the mocked diagnostic tools
  tools.py            mocked implementations of those tools (ping, traceroute, DNS lookup, device status, DHCP lease checks)
  chat_loop.py        retrieval + tool-calling agent loop — the actual copilot
views/
  ingest_view.py      Streamlit tab: ingestion status + browse the knowledge base
  retrieve_view.py    Streamlit tab: test retrieval directly
  chat_view.py         Streamlit tab: chat with the copilot
  score_badge.py       shared helper — colored similarity-score label
app.py                Streamlit app entry point (wires the three tabs above together)
demo_scenarios.py     a handful of example troubleshooting prompts to run through the agent
```

## Prerequisites

Install dependencies:

```bash
python -m pip install pymupdf openai numpy streamlit
```

Set your OpenAI API key:

```powershell
$env:OPENAI_API_KEY = "sk-..."   # PowerShell
```
```bash
export OPENAI_API_KEY="sk-..."   # macOS/Linux
```

## Add your troubleshooting documents

Network troubleshooting documents are already included under [data/raw/](data/raw/). You can add your own PDFs there, preferably under a matching subfolder (`vpn/`, `dns/`, `dhcp/`, `firewall/`, `routing/`), or at the root of `data/raw/`.

### Expected PDF format

Ingestion splits each PDF into chunks on a `### ` marker — put one at the start of every distinct symptom/issue section in the document. Everything between one `### ` and the next becomes a single chunk (the marker itself is stripped out), so this is what defines your chunk boundaries:

```
### Symptom: VPN drops during video calls
... troubleshooting steps for this symptom ...

### Symptom: VPN authentication fails intermittently
... troubleshooting steps for this symptom ...
```

A PDF with no `### ` markers ingests as a single chunk covering the whole document, which hurts retrieval precision and risks exceeding the embedding model's input size on longer files.

## 1. Ingest: generate the chunks

```bash
python rag/ingest.py
```

This extracts text from each PDF, splits it into chunks at each `### ` marker (one chunk per Symptom section), generates embeddings via OpenAI's `text-embedding-3-small`, and saves everything to `data/processed/chunks.json`.

## 2. Retrieve: query the knowledge base

`rag/retrieve.py` embeds a query, ranks all chunks by cosine similarity, and returns the top-k matches with their source document, category, and score.

Edit the `test_queries` list in `rag/retrieve.py`, then run:

```bash
python rag/retrieve.py
```

Example output:

```
============================================================
QUERY: A device that got moved to a new switch port still has its old IP address
============================================================

[0.675] troubleshoot-dhcp-address-assignment.pdf (dhcp)
  <matching chunk text> ...
```

You can also import and call `top_k(query, chunks, k=3)` directly from Python to use retrieval in other scripts.

## 3. Chat: ask the copilot

`agent/chat_loop.py` combines retrieval with tool-calling: it retrieves relevant documentation for your message, then lets the model call mocked diagnostic tools (`ping_host`, `traceroute`, `check_device_status`, `lookup_dns`, `check_dhcp_lease` — defined in `agent/schemas.py`, implemented in `agent/tools.py`) until it has enough information to answer. Every answer ends with a "Sources used" section citing the docs and tools it actually relied on.

Edit `test_message` in `agent/chat_loop.py`, then run it as a module from the project root (needed since it imports across the `rag`/`agent` packages):

```bash
python -m agent.chat_loop
```

Or call it directly from Python:

```bash
python -c "from agent.chat_loop import run_conversation; print(run_conversation('your question here'))"
```

### Demo scenarios

`demo_scenarios.py` runs the copilot through a handful of example troubleshooting prompts (VPN, DNS, DHCP, firewall, routing) in one go:

```bash
python demo_scenarios.py
```

## 4. Or run the Streamlit app

`app.py` wraps ingestion, retrieval, and chat into one UI with three tabs (`views/ingest_view.py`, `views/retrieve_view.py`, `views/chat_view.py`):

```bash
streamlit run app.py
```

- **Ingest tab** — shows which PDFs under `data/raw/` are already ingested vs. pending, lets you run ingestion on pending files from the UI, and lets you browse the resulting chunks.
- **Retrieve tab** — run ad-hoc queries against the knowledge base and inspect the top-k matches with similarity scores.
- **Chat tab** — same retrieval + tool-calling flow as `agent/chat_loop.py`, with a scenario picker, and showing retrieved sources and tool calls alongside the final diagnosis.
