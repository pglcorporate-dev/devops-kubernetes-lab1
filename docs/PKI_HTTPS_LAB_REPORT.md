# PKI and HTTPS Lab Report

## 1. Objective

This document defines the approved approach for enabling HTTPS in the lab environment without changing the application code. The target design follows Kubernetes and PKI best practices while remaining local-only and fully compatible with the current Minikube + Docker + NGINX Ingress setup.

## 2. Scope and constraints

The project currently has the following constraints:

- App remains local-only and is not exposed to the internet.
- Kubernetes is running inside Minikube using the Docker driver.
- Docker is installed inside the Linux VM, not directly on Windows.
- The lab uses the hostname mapping:
  - `magic-number.local`
  - `192.168.56.101`
- The laptop is Windows and the VM is Linux.
- The application should not be modified unless we explicitly decide to terminate TLS in the app layer.

## 3. Approved architecture

The approved design is:

1. Keep the application internal and HTTP-only.
2. Use NGINX Ingress inside Minikube as the HTTPS entry point.
3. Use cert-manager to manage certificates from a local self-signed Root CA.
4. Use HTTP to HTTPS redirect at the Ingress layer.
5. Trust the local CA on the Windows laptop and Linux VM.
6. Expose the service only inside the lab environment for now.

This design follows the standard Kubernetes model: TLS is terminated at the edge, while the application remains simple and focused on business logic.

## 4. Why this approach is preferred

The Ingress + cert-manager + local CA model is preferred because it is the most realistic and maintainable pattern for Kubernetes.

Benefits:

- Clear separation of concerns: app logic vs TLS termination.
- Standard Kubernetes best practice.
- No need to change application code.
- Better certificate lifecycle management using cert-manager.
- Realistic PKI flow for a lab environment.
- Easier future upgrades to production-like patterns.

## 5. Architecture diagram

```text
Browser (Windows laptop)
        |
        | https://magic-number.local
        v
NGINX Ingress (Minikube)
        |
        | TLS termination
        | routes to service
        v
Kubernetes Service
        |
        v
Flask app (HTTP internally)
```

## 6. Why not terminate TLS in the app?

Terminating TLS in the application would require:

- enabling HTTPS directly in the app
- exposing port 443 in the container
- mounting cert and key files inside the app environment
- handling TLS configuration inside the application runtime
- more operational complexity for certificate management

That would imply an app-level change and would reduce the realism of the lab. Since the requirement is to keep the app unchanged and use the proper Kubernetes pattern, TLS should be terminated at the Ingress layer.

## 7. Trade-off analysis

### Option A: NGINX Ingress + cert-manager + local CA

Recommended.

Advantages:

- Best fit for Kubernetes.
- Standard real-world design.
- Clean separation of application and TLS responsibilities.
- Easy to redirect HTTP to HTTPS.
- Suitable for local PKI testing.

Disadvantages:

- More setup steps than direct app TLS.
- Requires ingress controller and cert-manager in Minikube.
- Requires certificate trust configuration on clients.

### Option B: Reverse proxy on the VM

Possible fallback.

Advantages:

- Simpler to set up quickly.
- Useful for quick lab proof of concept.

Disadvantages:

- Less aligned with Kubernetes-native architecture.
- Adds another network layer.
- Harder to standardize for production-like practice.

### Option C: TLS inside the application

Not recommended for this lab.

Advantages:

- Very direct and explicit.
- Easy to understand in a single-service app.

Disadvantages:

- Not a best practice for Kubernetes.
- More app code and runtime complexity.
- Poor separation of concerns.
- Harder to rotate and manage certificates.

## 8. PKI design for the lab

The lab will use a proper local PKI flow, even though it remains self-signed and internal.

### Root CA

- A local Root Certificate Authority is created inside the Linux VM.
- This acts as the trust anchor for the lab.
- The Root CA is installed into the trust stores of the Windows laptop and Linux VM.

### Server certificate

The certificate must include all required names:

- `magic-number.local`
- `192.168.56.101`
- additional SAN entries as needed if the hostname or IP changes later

This is important because the client will validate both the hostname and the IP mapping in the local environment.

### Certificate chain

The certificate flow should be structured like:

- Root CA
- server certificate signed by the lab CA

Even in a local lab, following that structure is important and demonstrates correct certificate handling.

## 9. Flow of execution

1. Enable the NGINX Ingress controller in Minikube.
2. Install cert-manager in the cluster.
3. Create a local self-signed Root CA in the VM.
4. Create a local CA issuer in Kubernetes.
5. Issue a certificate for the lab hostname and IP.
6. Store the certificate in a Kubernetes TLS secret.
7. Configure the Ingress to serve HTTPS and redirect HTTP.
8. Install the Root CA on the Windows laptop.
9. Validate in browser and with CLI tools.

## 10. Validation checklist

The implementation is considered successful only when all of the following are true:

- `https://magic-number.local` loads without browser warnings.
- `http://magic-number.local` redirects to HTTPS.
- The certificate presented by the Ingress is trusted by the browser.
- The certificate includes the correct SANs.
- The app remains unchanged and still serves over HTTP internally.
- The Linux VM and Windows laptop trust the lab Root CA.

## 11. Commands for validation

### Browser test

Open the following URL after the trust store is configured:

- `https://magic-number.local`

### curl validation

```bash
curl -vk https://magic-number.local
curl -vkI http://magic-number.local
```

### OpenSSL check

```bash
openssl s_client -connect 192.168.56.101:443 -servername magic-number.local -showcerts
```

### Kubernetes validation

```bash
kubectl get ingress
kubectl get secret
kubectl describe certificate
kubectl get pods -n ingress-nginx
```

## 12. Keep-it-local plan

This is intentionally an internal lab exercise and not a public internet deployment. That means:

- no public DNS is required
- no public certificate authority is required
- no internet exposure is necessary
- the hosts file on the laptop is sufficient for local browser access
- trust installation on the Windows laptop is enough for secure browsing locally

This is the safest and simplest way to validate the PKI workflow while staying within the lab boundaries.

## 13. Future extension

Once this local PKI implementation is completed and validated, a future discussion can cover a second path using:

- a direct reverse proxy on the VM, or
- a public CA flow (for example, Let’s Encrypt or another external certificate authority)

That future step is optional and not required for the current local lab objectives.

## 14. Final recommendation

Proceed with:

- NGINX Ingress
- cert-manager
- a self-signed local Root CA
- HTTP to HTTPS redirect
- no app code changes
- local-only trust and validation

This is the proper, best-practice, lab-appropriate implementation for the current environment.
