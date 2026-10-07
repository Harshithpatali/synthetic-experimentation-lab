<div align="center">

# 🧪 Synthetic Experimentation Lab

### *Test the experiment before testing it on real customers.*

**A full-stack data-science experimentation platform that builds a synthetic Indian customer population, stores it in Neon PostgreSQL, visualizes it as a cyber-intelligence customer network, simulates randomized control/treatment experiments, and produces statistically rigorous experiment reports.**

<br/>

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/Neon-PostgreSQL-00E599?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)
![Streamlit Cloud](https://img.shields.io/badge/Deploy-Streamlit%20Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-None%20Required-8A2BE2?style=for-the-badge)

<br/>

[**Core Idea**](#-the-core-idea) · [**Architecture**](#-production-architecture) · [**Workflow**](#-product-workflow) · [**API**](#-fastapi-api) · [**Data Model**](#️-neon-postgresql-data-model) · [**Deploy**](#-render-deployment) · [**Repo**](https://github.com/Harshithpatali/synthetic-experimentation-lab)

</div>

---

## 🎯 The Core Idea

> **Business idea → Synthetic population → Randomized experiment → Statistical inference → Decision about a real pilot.**

```mermaid
flowchart TD
    A["💡 Business Idea"] --> B["👥 Synthetic Customer Population"]
    B --> C["👁️ Observable Behavior"]
    B --> D["🔒 Hidden Simulator Behavior"]
    C --> E["🎲 Randomized Treatment / Control"]
    D --> E
    E --> F["📊 Simulated Outcomes"]
    F --> G["📈 Uplift + Uncertainty + Statistical Test"]
    G --> H["✅ Decision About a Real-World Pilot"]
    H -.->|"Validate"| I["🧪 Real Controlled A/B Test"]

    style A fill:#1f2937,stroke:#60a5fa,stroke-width:2px,color:#fff
    style B fill:#1f2937,stroke:#a78bfa,stroke-width:2px,color:#fff
    style C fill:#1f2937,stroke:#34d399,stroke-width:2px,color:#fff
    style D fill:#1f2937,stroke:#f87171,stroke-width:2px,color:#fff
    style E fill:#1f2937,stroke:#fbbf24,stroke-width:2px,color:#fff
    style F fill:#1f2937,stroke:#38bdf8,stroke-width:2px,color:#fff
    style G fill:#1f2937,stroke:#c084fc,stroke-width:2px,color:#fff
    style H fill:#1f2937,stroke:#4ade80,stroke-width:2px,color:#fff
    style I fill:#111827,stroke:#94a3b8,stroke-width:2px,stroke-dasharray: 5 5,color:#fff
