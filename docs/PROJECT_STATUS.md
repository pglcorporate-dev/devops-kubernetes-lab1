# Estado del Proyecto — devops-kubernetes-lab1

Fecha: 2026-09-21

Resumen
------
Este repositorio es un laboratorio DevOps con la aplicación `magic-number`. Su objetivo es demostrar pipelines CI/CD, GitOps con Argo CD, y despliegues en Kubernetes.

Estado Actual
------------
- Aplicación: `magic-number` (Python Flask). Código funcional y con endpoints `/`, `/health`, `/guess`.
- Tests: Existe una suite básica en `apps/magic-number/tests/test_app.py` que cubre rutas principales. No hay métricas de cobertura actuales en el repositorio.
- Docker: `apps/magic-number/Dockerfile` presente y validado parcialmente. Image tag en [manifests/magic-number/kustomization.yaml](manifests/magic-number/kustomization.yaml#L1-L20) está fijado en `0220c5a`.
- GitOps: `gitops/dev/application.yaml` configurado para sincronizar `manifests/magic-number` en `main`.
- Infra: `infra/bootstrap/provider.tf` solo incluye provider para Kubernetes; no hay recursos gestionados por Terraform.
- CI/CD: El repositorio cuenta con recomendaciones de mejora documentadas en `INFORME_MEJORAS_CI_CD.md`. Actualmente CI realiza checks básicos y CD buildea/pushea imagen y realiza Trivy scan.

Riesgos y Observaciones
-----------------------
- Falta de ejecución de tests en CI y ausencia de cobertura reportada (riesgo crítico).
- CD activa la creación de PRs en GitOps sin garantizar que CI haya pasado (riesgo de despliegue de código roto).
- Dependencias no auditadas automáticamente en CI (posible vulnerabilidad).
- No hay sistema de notificaciones para despliegues ni retención de artefactos de escaneo.

Acciones Recomendadas (Resumidas)
--------------------------------
- Prioridad Inmediata: Habilitar `pytest` en CI y exigir que CI pase antes de disparar CD (workflow_run o status checks).
- Alta: Añadir `flake8`, `bandit`, y `safety`/`pip-audit` al pipeline de CI.
- Media: Añadir `hadolint` en CI; archivar reportes de `trivy` y `safety` como artefacts.
- Backlog: Notificaciones (Slack), SBOM, matriz de testing, pruebas de integración.

Referencias
----------
- Informe mejoras CI/CD: [INFORME_MEJORAS_CI_CD.md](INFORME_MEJORAS_CI_CD.md)
- ADR relevante: [docs/ADR-0001-ci-cd-improvements.md](docs/ADR-0001-ci-cd-improvements.md)

Estado: Informativo — cambios de código no aplicados, solo documentación.
