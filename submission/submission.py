import requests
import json
from .config import *

nextflow_api = f"http://{hostname}/api"
headers = {
    "Authorization": f"Bearer {api_token}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# get login credentials
res = requests.get(url=f"{nextflow_api}/credentials", headers=headers)
for credential in res.json()["credentials"]:
    if credential["name"] == "login_node":
        credential_id = credential["id"]

# get or setup compute environment
res = requests.get(url=f"{nextflow_api}/compute-envs", headers=headers)
compute_env_id = None
for compute_env in res.json()["computeEnvs"]:
    if compute_env["name"] == "dacapo_env":
        compute_env_id = compute_env["id"]

if not compute_env_id:
    compute_env = {
        "computeEnv": {
            "name": "dacapo_env",
            "platform": "lsf-platform",
            "config": {
                "userName": username,
                "hostName": hostname,
                "headQueue": head_queue,
                "computeQueue": compute_queue,
                "headJobOptions": head_job_options,
            },
            "credentialsId": credential_id,
        }
    }

    res = requests.post(
        url=f"{nextflow_api}/compute-envs",
        data=json.dumps(compute_env),
        headers=headers,
    )
    computeEnvId = res.json()["computeEnvId"]
res = requests.get(url=f"{nextflow_api}/compute-envs", headers=headers)
print(computeEnvId)

# setup workflow
# TODO: unable to recognize profile if submit it via workflow and pipeline is defined in nextflow.config
# works if you define it in a pipeline...don't know why

workflow = {
    "launch": {
        "computeEnvId": compute_env_id,
        "pipeline": pipeline_repo,
        "workDir": workflow_workdir,
        "revision": revision,
        "configProfiles": config_profiles,
        "paramsText": json.dumps(params_text),
        "mainScript": "dacapo.nf",
        "pullLatest": True,
    }
}

print(json.dumps(workflow))
res = requests.post(
    url=f"{nextflow_api}/workflow/launch", data=json.dumps(workflow), headers=headers
)

print(res.json())
