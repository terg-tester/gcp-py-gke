import pulumi
from pulumi import Config, export, get_project, get_stack, Output, ResourceOptions
from pulumi_gcp.config import project, zone
from pulumi_gcp.container import Cluster, ClusterNodeConfigArgs
from pulumi_kubernetes import Provider
import pulumi_docker as docker
from gke_app import GkeApp

# Read in some configurable settings for our cluster:
config = Config(None)

# nodeCount is the number of cluster nodes to provision. Defaults to 3 if unspecified.
NODE_COUNT = config.get_int("node_count") or 3
# nodeMachineType is the machine type to use for cluster nodes. Defaults to n1-standard-1 if unspecified.
# See https://cloud.google.com/compute/docs/machine-types for more details on available machine types.
NODE_MACHINE_TYPE = config.get("node_machine_type") or "e2-micro"
# master version of GKE engine
MASTER_VERSION = config.get("master_version")
# app_message is the message for the Node.js app to display
APP_MESSAGE = config.get("app_message") or "Hello from Pulumi!"

# GCR repository for the Docker image
gcr_repository = f"gcr.io/{project}"

# Docker image for the app
app_image = docker.Image(
    "gke-app-image",
    image_name=f"{gcr_repository}/gke-app",
    build=docker.DockerBuildArgs(
        context="app",
    ),
)

# Now, actually create the GKE cluster.
k8s_cluster = Cluster(
    "gke-cluster",
    initial_node_count=NODE_COUNT,
    node_version=MASTER_VERSION,
    min_master_version=MASTER_VERSION,
    deletion_protection=False,
    node_config=ClusterNodeConfigArgs(
        machine_type=NODE_MACHINE_TYPE,
        disk_size_gb=12,
        oauth_scopes=[
            "https://www.googleapis.com/auth/compute",
            "https://www.googleapis.com/auth/devstorage.read_only",
            "https://www.googleapis.com/auth/logging.write",
            "https://www.googleapis.com/auth/monitoring",
        ],
    ),
)

# Manufacture a GKE-style Kubeconfig.
k8s_info = Output.all(k8s_cluster.name, k8s_cluster.endpoint, k8s_cluster.master_auth)
k8s_config = k8s_info.apply(
    lambda info: f"""apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {info[2]['cluster_ca_certificate']}
    server: https://{info[1]}
  name: {project}_{zone}_{info[0]}
contexts:
- context:
    cluster: {project}_{zone}_{info[0]}
    user: {project}_{zone}_{info[0]}
  name: {project}_{zone}_{info[0]}
current-context: {project}_{zone}_{info[0]}
kind: Config
preferences: {{}}
users:
- name: {project}_{zone}_{info[0]}
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: gke-gcloud-auth-plugin
      installHint: Install gke-gcloud-auth-plugin for use with kubectl by following
        https://cloud.google.com/blog/products/containers-kubernetes/kubectl-auth-changes-in-gke
      provideClusterInfo: true
"""
)

# Make a Kubernetes provider instance that uses our cluster from above.
k8s_provider = Provider("gke_k8s", kubeconfig=k8s_config)

# Create the GkeApp component resource
gke_app = GkeApp(
    "gke-app",
    k8s_provider=k8s_provider,
    image_name=app_image.image_name,
    app_message=APP_MESSAGE,
)

# Finally, export the kubeconfig so that the client can easily access the cluster.
export("kubeconfig", k8s_config)
# Export the Ingress IP to access the app deployment
export("ingress_ip", gke_app.ingress_ip)