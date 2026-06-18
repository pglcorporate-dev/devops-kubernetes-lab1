# devops-kubernetes-lab1

A hands-on DevOps lab for cloud-native workflows and GitOps. This repository demonstrates:

- Building and containerizing a simple Python Flask application.
- Deploying Kubernetes manifests using `kubectl` and Kustomize.
- Managing deployments with Argo CD GitOps.
- Bootstrapping Kubernetes provider configuration with Terraform.

## Project Overview

The sample app is called **magic-number**. It runs a Flask service that guesses a number between 1 and 100 using a binary search flow and exposes a small browser UI.

## Repository Layout

- `apps/magic-number/`
  - `app.py` – Flask application logic.
  - `Dockerfile` – container image build instructions.
  - `requirements.txt` – Python dependency list.
  - `static/index.html` – frontend UI for the number guessing game.

- `manifests/magic-number/`
  - `deployment.yaml` – Kubernetes Deployment manifest.
  - `service.yaml` – Kubernetes Service manifest.
  - `kustomization.yaml` – Kustomize overlay that pins the container image tag.

- `gitops/`
  - `argocd/ingress.yaml` – Ingress manifest for exposing Argo CD.
  - `dev/application.yaml` – Argo CD Application definition for the sample app.
  - `prod/` – placeholder for production GitOps configuration.

- `infra/bootstrap/provider.tf`
  - Terraform provider configuration for using the local kubeconfig file.

## Architecture

1. Build the `magic-number` container image.
2. Deploy Kubernetes resources from `manifests/magic-number/`.
3. Use Argo CD to sync the Git repository to the Kubernetes cluster.
4. Optionally manage environment-specific overlays in `gitops/dev/` and `gitops/prod/`.

## Prerequisites

- `git`
- `docker`
- `kubectl`
- `terraform`
- A Kubernetes cluster with a valid `~/.kube/config` context
- Access to the image registry used in manifests (`ghcr.io/pglcorporate-dev/magic-number`)

## Local Development

### Run the app locally

From `apps/magic-number/`:

```bash
cd apps/magic-number
python -m venv .venv
source .venv/Scripts/activate   # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

The app listens on port `5000`. Open `http://localhost:5000` in your browser.

### Build the Docker image

From `apps/magic-number/`:

```bash
docker build -t ghcr.io/pglcorporate-dev/magic-number:latest .
```

### Push the image

```bash
docker push ghcr.io/pglcorporate-dev/magic-number:latest
```

> The Kubernetes manifests currently reference `ghcr.io/pglcorporate-dev/magic-number`.

## Kubernetes Deployment

### Apply resources directly

From the repository root:

```bash
kubectl apply -f manifests/magic-number/
```

### Use Kustomize

```bash
kubectl apply -k manifests/magic-number/
```

### Verify

```bash
kubectl get pods,svc -l app=magic
```

## GitOps with Argo CD

The Argo CD Application is defined in `gitops/dev/application.yaml` and targets the `manifests/magic-number` path in this repo.

To deploy via Argo CD:

1. Install Argo CD in your cluster if it is not already installed.
2. Apply the Argo CD ingress if you want external access:

   ```bash
   kubectl apply -f gitops/argocd/ingress.yaml
   ```

3. Create or sync the Argo CD Application:

   ```bash
   kubectl apply -f gitops/dev/application.yaml
   ```

4. Open the Argo CD UI at `http://argocd.lab.local` if your DNS/hosts file resolves that host.

### Notes

- `syncPolicy.automated` in `gitops/dev/application.yaml` enables automatic reconciliation and self-healing.
- `gitops/prod/` is currently a placeholder for future production GitOps configuration.

## Terraform Bootstrap

The `infra/bootstrap/provider.tf` file configures the Kubernetes Terraform provider with the local kubeconfig file.

```hcl
provider "kubernetes" {
  config_path = "~/.kube/config"
}
```

This repo does not currently include additional Terraform resources beyond the provider configuration.

## Helpful Commands

```bash
kubectl config current-context
kubectl apply -k manifests/magic-number/
kubectl describe pod -l app=magic
kubectl logs -l app=magic
```

## Notes for New Developers

- Start by running the app locally in `apps/magic-number/`.
- Build and push the container image before applying Kubernetes manifests.
- Use the `manifests/magic-number` directory as the canonical app deployment source.
- Argo CD watches the Git repo and will deploy changes from `gitops/dev/application.yaml`.
- Keep `gitops/prod/` reserved for staging or production GitOps definitions.
