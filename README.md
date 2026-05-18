# ENYRAX Cloud Portal

ENYRAX Cloud Portal is a cloud-hosted enterprise operation platform prototype deployed on Akamai Cloud / Linode Tokyo 3.

It demonstrates how SOC Monitoring, ServiceOps, ProjectOps and AI-assisted decision workflows can be integrated into one cloud portal.

## Live Demo

- https://portal.soc-monitoring.dev

## Architecture

```text
Browser
  ↓ HTTPS
Nginx
  ├── Static Portal Pages
  │   ├── /
  │   ├── /soc/
  │   ├── /serviceops/
  │   ├── /projectops/
  │   └── /status/
  │
  └── Reverse Proxy /api/
        ↓
      FastAPI Backend
        ├── /api/health
        ├── /api/modules
        ├── /api/soc/summary
        ├── /api/serviceops/summary
        └── /api/projectops/summary
