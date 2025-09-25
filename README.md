# ArgoCD Demo

A demonstration project showcasing ArgoCD deployment with blue-green deployment strategy using a simple Flask web application.

## Project Structure

```
argocd-demo/
├── lnews-app/
│   ├── templates/
│   │   └── index.html
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── commands.txt
└── README.md
```

## Application Overview

**Learnews App** - A simple Flask web application that serves a landing page with health check endpoint.

### Features
- Home page with gradient background design
- Health check endpoint (`/health`)
- Dockerized for easy deployment
- Blue-green deployment ready

### Endpoints
- `/` - Main landing page
- `/health` - Health check endpoint returning `{"message": "OK"}`

## Prerequisites

- Docker
- Minikube
- kubectl
- Docker Hub account

## Setup

### 1. Minikube Setup

```bash
# Start minikube cluster
minikube start

# Enable ingress addon (optional)
minikube addons enable ingress

# Verify cluster is running
kubectl cluster-info
```

### 2. Build and Push Docker Images

```bash
cd lnews-app
docker login
docker buildx build --platform linux/amd64,linux/arm64 -t inrobas/lnews-app:blue --push .
docker push inrobas/lnews-app:blue
docker buildx build --platform linux/amd64,linux/arm64 -t inrobas/lnews-app:green --push .
docker push inrobas/lnews-app:green
```

`--platform` options added to support compatibility across multiple environments.

### Docker Deployment

Build and run with Docker:

```bash
cd lnews-app
docker build -t lnews-app .
docker run -p 5000:5000 lnews-app
```

### ArgoCD Setup on Minikube

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for ArgoCD to be ready
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd

# Access ArgoCD UI (port-forward)
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

Access ArgoCD at `https://localhost:8080` with username `admin` and the password from above.

## Technology Stack

- **Backend:** Python 3.12, Flask 2.3.2
- **Frontend:** HTML5, CSS3
- **Containerization:** Docker
- **Deployment:** ArgoCD (Blue-Green strategy)

## Blue-Green Deployment

The project supports blue-green deployment with two image variants (blue and green) that can be switched in ArgoCD for zero-downtime deployments.

## ArgoCD Integration

This project is designed to work with ArgoCD for GitOps-based continuous deployment, supporting blue-green deployment patterns for zero-downtime updates.

helm install argo-apps ./argo-apps -n argocd
helm upgrade argo-apps ./argo-apps -n argocd