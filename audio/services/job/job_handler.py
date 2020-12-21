# OB_NAMESPACE = "default"
# JOB_NAME = "ampl"
# from kubernetes import client, config
#
# JOB_NAME = "pi"
#
#
# def create_smlr_job_object():
#     # Configureate Pod template container
#     container = client.V1Container(
#         name="smlr_job",
#         image="starlover27/private_rep:smlr-job",
#         command=["python", "-m", "smlr_job"])
#     # Create and configurate a spec section
#     template = client.V1PodTemplateSpec(
#         metadata=client.V1ObjectMeta(labels={"app": "smlr_job"}),
#         spec=client.V1PodSpec(restart_policy="Never", containers=[container]))
#     # Create the specification of deployment
#     spec = client.V1JobSpec(
#         template=template,
#         backoff_limit=4)
#     # Instantiate the job object
#     job = client.V1Job(
#         api_version="batch/v1",
#         kind="Job",
#         metadata=client.V1ObjectMeta(name=JOB_NAME),
#         spec=spec)
#
#     return job
#
#
# def create_ampl_job_object():
#     # Configureate Pod template container
#     container = client.V1Container(
#         name="smlr_job",
#         image="starlover27/private_rep:ampl-job",
#         command=["python", "-m", "ampl_job"])
#     # Create and configurate a spec section
#     template = client.V1PodTemplateSpec(
#         metadata=client.V1ObjectMeta(labels={"app": "ampl_job"}),
#         spec=client.V1PodSpec(restart_policy="Never", containers=[container]))
#     # Create the specification of deployment
#     spec = client.V1JobSpec(
#         template=template,
#         backoff_limit=4)
#     # Instantiate the job object
#     job = client.V1Job(
#         api_version="batch/v1",
#         kind="Job",
#         metadata=client.V1ObjectMeta(name=JOB_NAME),
#         spec=spec)
#
#     return job
#
#
# def create_job(api_instance, job):
#     api_response = api_instance.create_namespaced_job(
#         body=job,
#         namespace="default")
#     print("Job created. status='%s'" % str(api_response.status))
#
#
# def delete_job(api_instance):
#     api_response = api_instance.delete_namespaced_job(
#         name=JOB_NAME,
#         namespace="default",
#         body=client.V1DeleteOptions(
#             propagation_policy='Foreground',
#             grace_period_seconds=5))
#     print("Job deleted. status='%s'" % str(api_response.status))
#
#
# def smlr_job_main():
#     config.load_kube_config()
#     batch_v1 = client.BatchV1Api()
#     job = create_smlr_job_object()
#     create_job(batch_v1, job)
#     delete_job(batch_v1)
#
#
# def ampl_job_main():
#     config.load_kube_config()
#     batch_v1 = client.BatchV1Api()
#     job = create_ampl_job_object()
#     create_job(batch_v1, job)
#     delete_job(batch_v1)
