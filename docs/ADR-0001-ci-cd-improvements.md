# ADR 0001: CI/CD Improvements for devops-kubernetes-lab1

Date: 2026-09-21

Status: Proposed

Context
-------
This repository contains a simple Flask application (`magic-number`) and GitOps-based deployment artifacts. Existing CI and CD workflows provide basic validation but lack robust testing, security checks, and deployment guardrails. The `INFORME_MEJORAS_CI_CD.md` outlines a set of recommended improvements covering unit testing, linting, dependency scanning, container image scanning, and GitOps PR controls.

Decision
--------
We will adopt the following decisions for the repository's CI/CD practices:

- Enforce unit tests and coverage reporting in CI using `pytest` + `pytest-cov`.
- Add linting and static analysis with `flake8` and `bandit` in CI pipeline.
- Integrate dependency vulnerability checks using `safety` or `pip-audit` and ensure CI fails or warns according to configured severity.
- Validate Dockerfiles with `hadolint` in both CI and CD workflows.
- Keep image tags immutable using SHA-based tags in CD, optionally adding a `latest` alias for convenience.
- Add Trivy scanning during CD and fail the pipeline if critical vulnerabilities are found; archive scan results as artifacts.
- Trigger CD only after successful CI completion (`workflow_run`) to avoid deploying broken code.
- Create GitOps PRs only when all critical checks pass; do not auto-merge or auto-deploy images flagged with critical vulnerabilities.
- Add optional notifications (Slack) for deployment PR creation and failed critical checks.

Consequences
------------
Positive:
- Increased confidence in builds and deployments.
- Reduced risk of shipping vulnerabilities or broken changes to clusters.
- Better traceability via archived scan reports and coverage artifacts.

Negative / Tradeoffs:
- Increased CI/CD runtime and more required secrets (e.g., registry credentials, safety API key).
- Slightly increased maintenance overhead for CI configuration and dependency pinning.

Implementation Notes
--------------------
- Reference the recommendations in `INFORME_MEJORAS_CI_CD.md` for concrete GitHub Actions steps.
- Keep `gitops/prod/` reserved and follow the same gating patterns before promoting to production.

Related ADRs
------------
- None yet.

Approved-by: Pending
