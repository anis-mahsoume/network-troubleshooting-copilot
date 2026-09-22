# Network Troubleshooting Copilot

A RAG-powered assistant for diagnosing network/IT issues. It retrieves relevant passages from a knowledge base of network troubleshooting documentation (VPN, DNS, DHCP, firewall, routing) and will combine them with tool-calling to mocked diagnostic tools (ping, traceroute, DNS lookup, device status, DHCP lease checks).

Built as a hands-on project for RAG, embeddings, and tool/function calling.

## Project structure

```
data/
  raw/                source PDFs, organized by category (vpn/, dns/, dhcp/, firewall/, routing/)
  processed/
    chunks.json       generated output — chunked docs + embeddings (not committed if large)
ingest.py             extracts, chunks, and embeds data/raw into data/processed/chunks.json
retrieve.py           query the knowledge base and inspect top-k results
```

## Prerequisites

Install dependencies:

```bash
python -m pip install pymupdf openai numpy
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

## 1. Ingest: generate the chunks

```bash
python ingest.py
```

This extracts text from each PDF, splits it into chunks at each `### ` marker (one chunk per Symptom section), generates embeddings via OpenAI's `text-embedding-3-small`, and saves everything to `data/processed/chunks.json`.

## 2. Retrieve: query the knowledge base

`retrieve.py` embeds a query, ranks all chunks by cosine similarity, and returns the top-k matches with their source document, category, and score.

Edit the `test_queries` list in `retrieve.py`, then run:

```bash
python retrieve.py
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

## Roadmap

- [x] PDF ingestion + chunking + embeddings
- [x] Retrieval (top-k semantic search)
- [ ] Mocked diagnostic tools (ping, traceroute, DNS lookup, device status, DHCP lease checks)
- [ ] Tool-calling agent that combines retrieval with live diagnostics
