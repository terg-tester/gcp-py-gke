# Pulumi Google Cloud GKE with Node.js Application

This project demonstrates how to use Pulumi to provision a Google Kubernetes Engine (GKE) cluster and deploy a configurable Node.js web application to it.

The Pulumi program is written in Python and the application is a simple Express.js server running in a Docker container.

## Features

- Provisions a GKE cluster on Google Cloud.
- Builds a Docker image for a Node.js application.
- Pushes the Docker image to Google Container Registry (GCR).
- Deploys the application to the GKE cluster using Kubernetes resources (`Deployment`, `Service`, `Ingress`).
- The message displayed by the web application is configurable via Pulumi configuration.
- The Kubernetes resources are encapsulated in a reusable `ComponentResource`.

## Prerequisites

Before you begin, ensure you have the following installed and configured:

1.  **Pulumi CLI**: [Installation Guide](https://www.pulumi.com/docs/get-started/install/)
2.  **Google Cloud SDK (`gcloud`)**: [Installation Guide](https://cloud.google.com/sdk/docs/install)
3.  **Docker**: [Installation Guide](https://docs.docker.com/engine/install/)
4.  **Python 3.6+**
5.  **Node.js and npm**

You also need to be authenticated with Google Cloud:
```bash
gcloud auth login
gcloud auth application-default login
```

## Setup & Deployment

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Node.js application dependencies:**
    ```bash
    cd app
    npm install
    cd ..
    ```

4.  **Configure Pulumi for your GCP project:**
    Create a new Pulumi stack (e.g., `dev`):
    ```bash
    pulumi stack init dev
    ```
    Set the required GCP configuration values:
    ```bash
    pulumi config set gcp:project YOUR_GCP_PROJECT_ID
    pulumi config set gcp:zone YOUR_GCP_ZONE (e.g., us-central1-a)
    ```

5.  **Configure Docker to authenticate with GCR:**
    This command configures the Docker CLI to use `gcloud` for credential management.
    ```bash
    gcloud auth configure-docker
    ```

6.  **Deploy the infrastructure:**
    Run `pulumi up` to preview and deploy the changes.
    ```bash
    pulumi up --yes
    ```
    This will provision the GKE cluster, build and push the Docker image, and deploy the application. The process can take several minutes.

7.  **Access your application:**
    Once the deployment is complete, Pulumi will output the public IP address of the Ingress.
    ```
    Outputs:
        ingress_ip: "34.149.168.17"
    ```
    You can access your application by navigating to this IP address in your browser or by using `curl`:
    ```bash
    curl http://<ingress_ip>
    ```
    By default, it will display: `Hello from Pulumi!`

## Configuration

You can customize the message displayed by the web application by setting the `app_message` configuration value:

```bash
pulumi config set app_message "Hello from my custom configuration!"
```

After setting the new value, run `pulumi up --yes` again to apply the changes. The application will update to display the new message.

## Cleanup

To tear down all the resources created by this project, run the following command:

```bash
pulumi destroy --yes
```