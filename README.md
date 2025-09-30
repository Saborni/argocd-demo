# ArgoCD Demo

A demonstration project showcasing ArgoCD deployment with blue-green deployment strategy using a simple Flask web application.

## Pre-requisites
Knowledge on following is required:
- **Backend:** Python, Flask
- **Frontend:** HTML5, CSS3
- **Containerization:** Docker, Kubernetes


## Project Structure
```
argocd-demo/
├── argo-apps/                   # Helm chart for ArgoCD Applications
│   ├── templates/
│   │   └── applications.yaml    # ArgoCD Application template
│   ├── Chart.yaml               # Helm chart metadata
│   └── values.yaml              # Configuration values
├── images/                      # UI screenshots
│   └── green-ui.png           
├── lnews-app/                   # Flask web application
│   ├── templates/
│   │   └── index.html           # HTML template
│   ├── app.py                   # Flask application
│   ├── Dockerfile               # Container image definition
│   └── requirements.txt         # Python dependencies
├── manifest/                    
│   └── dev/                     
│       ├── deployment.yaml      # Lnews-app K8s deployment manifest
│       └── service.yaml         # Lnews-app K8s service manifest
└── README.md                    # Project documentation
```

## Application Overview

**Learnews App** - A simple Flask web application that serves a landing page with health check endpoint.

### Features
- Home page with gradient background design
- Health check endpoint (`/health`)
- Dockerized for easy deployment

### Endpoints
- `/` - Main landing page
- `/health` - Health check endpoint returning `{"hostname": <Host-IP-address>}`

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
docker buildx build --platform linux/amd64,linux/arm64 -t inrobas/lnews-app:green --push .
```

`--platform` options added to support compatibility across ARM and AMD based environments.

### 3. ArgoCD Setup on Minikube

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Access ArgoCD UI (port-forward)
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

Access ArgoCD at `https://localhost:8080` with username `admin` and the password from above.

### 4. ArgoCD application setup

ArgoCD Application is a Kubernetes custom resource that defines how ArgoCD should deploy and manage your application.
Consider it as a "deployment configuration" that tells ArgoCD about the Source, Destination and Sync policy.

Before deployment, you would need to configure the [values.yaml](/argo-apps/values.yaml) with

- Source - Your application source repository that contains the manifest files.
- Destination - kube-api server endpoint, which is used by ArgoCD to maintain the desired state of your application.

Additionally, you may tweak `syncPolicy` available in [applications.yaml](/argo-apps/templates/applications.yaml) as per your requirements.

```yaml
config:
  spec:
    destination:
      server: https://kubernetes.default.svc
    source:
      repoURL: https://github.com/Saborni/argocd-demo
      targetRevision: main

applications:
  - name: lnews-app
    path: manifest/dev
    namespace: lnews
```
We will use helm charts to create ArgoCD application for enabling Continuous Deployment configuration for your application. For fresh deployment of the configuration, use the following helm command -

```bash
helm install <app-name> ./argo-apps -n argocd
```
For any changes use the following command

```bash
helm upgrade <app-name> ./argo-apps -n argocd
```
replace `<app-name>` with a name of your choice.

### 4. Testing

Observe your application K8s objects in the ArgoCD UI

![](/images/argo-ui.png)

Now use port forwarding to expose your application service over localhost to access it over a browser -

```bash
kubectl port-forward service/lnews-svc 5000:5000 -n lnews
```
On accessing endpoint `http://localhost:5000`, you will observe the following -

![](/images/blue-ui.png)

Now change the image tag from `blue` to `green` in the deployment [manifest](/manifest/dev/deployment.yaml) in your GitHub repo. 

In the ArgoCD UI, you will observe a new replicaset is created and the old pods are shutting down.

![](/images/after-commit.png)

Terminate the port-ward command using `Ctrl+C` and run it again.

```bash
kubectl port-forward service/lnews-svc 5000:5000 -n lnews
```
![](/images/green-ui.png)

Test ArgoCD's drift detection and self-healing capabilities by manually scaling the deployment:

```bash
#Scale deployment to 5 replicas (drift from desired state)
kubectl scale deployment lnews-app --replicas=5 -n lnews

#Scale deployment to 0 replica (drift from desired state)
kubectl scale deployment lnews-app --replicas=0 -n lnews

#Watch ArgoCD automatically restore to desired state (2 replicas)
kubectl get pods -n lnews
```

ArgoCD will detect the configuration drift and automatically scale back to the desired state defined in your Git repository, demonstrating GitOps principles in action.

## CleanUp

Delete the ArgoCD application config
```bash
helm uninstall my-apps -n argocd
```

Alternately, clear everything using -
```bash
minikube delete --all
```