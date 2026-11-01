# Project Overview: AI-Based PDF Question Answering and Document Intelligence System
*(Foundation for the GGSIPU minor project report. Replace bracketed items with your own work and measured results.)*

## Abstract
This project presents a web application that lets users upload PDF documents and ask natural-language questions about them. It uses Retrieval-Augmented Generation (RAG): document text is split into page-aware chunks, converted to semantic embeddings, and indexed for similarity search. For each question the most relevant chunks are retrieved and used either by a free-tier large language model or by a local extractive answerer. Every answer cites document names, page numbers and source excerpts, and the system reports when evidence is insufficient.

## Introduction
Documents such as reports, manuals and papers are long and hard to search by keyword. Large language models can answer questions but may produce unsupported statements. RAG grounds answers in retrieved text.

## Problem statement
Users need a fast, trustworthy, low-cost way to query their own PDFs with verifiable sources, without paid services.

## Objectives
1. Ingest and index PDFs. 2. Retrieve relevant passages semantically. 3. Produce cited answers. 4. Work without paid APIs. 5. Provide summaries and chat history. 6. Offer a clean web interface.

## Scope
In scope: text-based PDFs, multiple documents, single user, English-language text. Out of scope: OCR, tables/figures understanding, authentication, multi-user collaboration.

## Literature survey outline
Cover: (1) keyword search / TF-IDF / BM25; (2) dense retrieval and sentence embeddings (Sentence-BERT, Reimers & Gurevych, 2019); (3) Retrieval-Augmented Generation (Lewis et al., 2020); (4) vector similarity search libraries (FAISS); (5) extractive vs. generative question answering; (6) hallucination in LLMs. *Read and cite the original papers yourself and add only what you have verified.*

## Existing system
Manual reading and Ctrl+F keyword search; general chatbots that do not cite the user's document; commercial document-chat products that need subscriptions.

## Proposed system
A self-hosted RAG application with page-level citations, an extractive fallback that works offline, and configurable free-tier LLM providers.

## Feasibility study
- **Technical:** all components are open-source and run on a laptop CPU.
- **Economic:** no paid services required; free-tier APIs optional.
- **Operational:** simple web UI; Windows setup documented.
- **Schedule:** achievable within one semester.

## Hardware requirements
Minimum: dual-core CPU, 8 GB RAM, ~2 GB free disk. No GPU needed.

## Software requirements
Windows 10/11, Python 3.11, Node.js LTS, VS Code, modern browser; libraries listed in `requirements.txt` and `package.json`.

## System architecture
See `docs/architecture.md` (React → FastAPI → PDF extraction, chunking, embeddings, vector search, RAG, SQLite).

## Methodology
Incremental development: planning → backend → frontend → integration/testing → documentation. Testing with pytest using a sample PDF; [add manual test cases and your own measured results].

## Algorithms used
- **Chunking:** fixed-size windows (~900 characters) with 150-character overlap, cutting at sentence boundaries where possible, per page.
- **Embedding:** `all-MiniLM-L6-v2` sentence embeddings (L2-normalised).
- **Retrieval:** exact nearest-neighbour search by inner product (= cosine similarity) with FAISS `IndexFlatIP`.
- **Relevance gate:** threshold on top similarity to detect unanswerable questions.
- **Extractive answering:** rank sentences of retrieved chunks by similarity to the question; return top sentences with pages.
- **Extractive summary:** rank sentences by similarity to the document's mean embedding; topics by stop-word-filtered term frequency.
- **Generative answering:** prompt an LLM with retrieved chunks and a "answer only from the excerpts" instruction.

## Advantages
Grounded, cited answers; works offline; free; modular; easy to extend.

## Limitations
No OCR; small embedding model; extractive mode cannot synthesise; threshold may need tuning per corpus; free hosting has ephemeral storage; LLM answers can still be wrong.

## Applications
Study material Q&A, research-paper reading, manuals and policy lookup, legal/administrative document review (with care).

## Future scope
OCR, hybrid search, re-ranking, authentication, persistent cloud storage, retrieval evaluation, multilingual support.

## Conclusion
The system demonstrates a practical, low-cost RAG pipeline with verifiable citations. [Add your measured results and observations.]

## References (technical documentation)
- FastAPI documentation — https://fastapi.tiangolo.com
- PyMuPDF documentation — https://pymupdf.readthedocs.io
- Sentence-Transformers documentation — https://www.sbert.net
- FAISS repository — https://github.com/facebookresearch/faiss
- React — https://react.dev · Vite — https://vitejs.dev · Tailwind CSS — https://tailwindcss.com
- Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", NeurIPS 2020 (verify before citing)
- Reimers & Gurevych, "Sentence-BERT", EMNLP 2019 (verify before citing)
