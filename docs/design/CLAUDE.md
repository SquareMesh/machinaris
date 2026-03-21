# Design Documentation — Navigation Guide

> This file is the master index for all Machinaris design documentation.
> Read this first to find the document covering any topic.

## Project Overview

**Machinaris** is a Docker-based web application for managing Chia blockchain farming operations across single or multiple machines. It provides a WebUI dashboard, REST API, automated plotting, monitoring/alerting, and support for 34+ Chia blockchain forks.

**Current Version:** 2.6.0 (forked from SquareMesh/machinaris)
**Original Author:** Guy Davis (guydavis/machinaris — now closed)
**License:** Apache 2.0

## Document Index

| Document | Covers | Key Questions It Answers |
|---|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System overview, tiers, controller-worker model, data flow | How does the system fit together? How do containers communicate? |
| [API.md](API.md) | REST API framework, endpoints, schemas, background scheduler | What endpoints exist? How is data collected? How does the scheduler work? |
| [WEB-FRONTEND.md](WEB-FRONTEND.md) | Flask blueprints, templates, JavaScript, CSS, charts | How is the UI structured? What JS libraries are used? How do pages refresh? |
| [DATA-LAYER.md](DATA-LAYER.md) | SQLAlchemy models, multi-database design, statistics tables | What databases exist? What are the ORM models? How are stats stored? |
| [BLOCKCHAIN-INTEGRATION.md](BLOCKCHAIN-INTEGRATION.md) | Chia RPC, CLI interaction, fork registry, blockchain metadata | How does Machinaris talk to Chia? How are forks supported? |
| [DOCKER-DEPLOYMENT.md](DOCKER-DEPLOYMENT.md) | Dockerfiles, entrypoint, scripts, multi-container orchestration | How is the Docker image built? How does the container start up? |
| [PLOTTING-FARMING.md](PLOTTING-FARMING.md) | Plotman, Bladebit, Madmax, GPU support, archiving, replotting | How does plotting work? What plotters are supported? |
| [MONITORING-ALERTS.md](MONITORING-ALERTS.md) | Chiadog, scheduled jobs, drive monitoring, notifications | How is the farm monitored? What alerts exist? |
| [CONFIGURATION.md](CONFIGURATION.md) | Environment variables, config files, setup flow, i18n | How is the system configured? What env vars are available? |

## Reading Order for New Contributors

1. **ARCHITECTURE.md** — Understand the overall system
2. **DOCKER-DEPLOYMENT.md** — Understand how it runs
3. **CONFIGURATION.md** — Understand how it's configured
4. **BLOCKCHAIN-INTEGRATION.md** — Understand the blockchain layer
5. **DATA-LAYER.md** — Understand the data model
6. **API.md** — Understand the REST API
7. **WEB-FRONTEND.md** — Understand the UI
8. **PLOTTING-FARMING.md** — Understand plotting operations
9. **MONITORING-ALERTS.md** — Understand observability

## Cross-Cutting Concerns

| Concern | Primary Doc | Also Mentioned In |
|---|---|---|
| Security | CONFIGURATION.md | API.md, WEB-FRONTEND.md |
| Internationalization | CONFIGURATION.md | WEB-FRONTEND.md |
| Multi-architecture (amd64/arm64) | DOCKER-DEPLOYMENT.md | PLOTTING-FARMING.md |
| GPU acceleration | PLOTTING-FARMING.md | DOCKER-DEPLOYMENT.md |
| Blockchain fork support | BLOCKCHAIN-INTEGRATION.md | DOCKER-DEPLOYMENT.md, CONFIGURATION.md |
