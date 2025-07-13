
import pulumi
from pulumi import ComponentResource, ResourceOptions, Output
from pulumi_kubernetes import Provider
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.core.v1 import (
    ContainerArgs,
    PodSpecArgs,
    PodTemplateSpecArgs,
    Service,
    ServicePortArgs,
    ServiceSpecArgs,
    EnvVarArgs,
)
from pulumi_kubernetes.meta.v1 import LabelSelectorArgs, ObjectMetaArgs
from pulumi_kubernetes.networking.v1 import (
    Ingress,
    IngressSpecArgs,
    IngressRuleArgs,
    HTTPIngressRuleValueArgs,
    HTTPIngressPathArgs,
    IngressBackendArgs,
    IngressServiceBackendArgs,
    ServiceBackendPortArgs,
)

class GkeApp(ComponentResource):
    """
    A component resource that encapsulates a Kubernetes Deployment, Service, and Ingress
    for a simple web application.

    :param str name: The name of the component resource.
    :param pulumi.ResourceOptions opts: A bag of options that control this resource's behavior.
    :param pulumi_kubernetes.Provider k8s_provider: The Kubernetes provider to use for creating resources.
    :param pulumi.Output[str] image_name: The name of the Docker image to deploy.
    :param str app_message: The message for the application to display.
    """
    def __init__(self, name: str, *, k8s_provider: Provider, image_name: Output[str], app_message: str, opts: ResourceOptions = None):
        super().__init__("pkg:gke:GkeApp", name, {}, opts)

        app_labels = {"app": "gke-app"}

        # Create a deployment for the Node.js app.
        self.deployment = Deployment(
            f"{name}-deployment",
            spec=DeploymentSpecArgs(
                selector=LabelSelectorArgs(match_labels=app_labels),
                replicas=1,
                template=PodTemplateSpecArgs(
                    metadata=ObjectMetaArgs(labels=app_labels),
                    spec=PodSpecArgs(
                        containers=[
                            ContainerArgs(
                                name="gke-app",
                                image=image_name,
                                env=[EnvVarArgs(name="MESSAGE", value=app_message)],
                            )
                        ]
                    ),
                ),
            ),
            opts=ResourceOptions(provider=k8s_provider, parent=self),
        )

        # Create a Kubernetes Service to expose the Deployment
        self.service = Service(
            f"{name}-service",
            spec=ServiceSpecArgs(
                selector=app_labels,
                ports=[ServicePortArgs(port=80, target_port=8080)],
            ),
            opts=ResourceOptions(provider=k8s_provider, parent=self),
        )

        # Create a Kubernetes Ingress to route traffic to the Service
        self.ingress = Ingress(
            f"{name}-ingress",
            metadata=ObjectMetaArgs(
                annotations={"kubernetes.io/ingress.class": "gce"},
            ),
            spec=IngressSpecArgs(
                rules=[
                    IngressRuleArgs(
                        http=HTTPIngressRuleValueArgs(
                            paths=[
                                HTTPIngressPathArgs(
                                    path="/",
                                    path_type="Prefix",
                                    backend=IngressBackendArgs(
                                        service=IngressServiceBackendArgs(
                                            name=self.service.metadata.name,
                                            port=ServiceBackendPortArgs(number=80),
                                        ),
                                    ),
                                )
                            ]
                        )
                    )
                ]
            ),
            opts=ResourceOptions(provider=k8s_provider, parent=self),
        )

        # Export the Ingress IP
        self.ingress_ip = self.ingress.status.apply(
            lambda status: status.load_balancer.ingress[0].ip if status.load_balancer.ingress else None
        )

        self.register_outputs({"ingress_ip": self.ingress_ip})
