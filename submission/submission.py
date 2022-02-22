import requests
import json
import config

nextflow_api = f"http://{config.hostname}/api"
headers = {
    "Authorization": f"Bearer {config.api_token}",
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
                "userName": config.username,
                "workDir": config.work_dir,
                "launchDir": config.launch_dir,
                "hostName": config.hostname,
                "headQueue": config.head_queue,
                "computeQueue": config.compute_queue,
                "headJobOptions": config.head_job_options,
            },
            "credentialsId": credential_id,
        }
    }
    res = requests.post(
        url=f"{nextflow_api}/compute-envs",
        data=json.dumps(compute_env),
        headers=headers,
    )
    print(res.json())
    compute_env_id = res.json()["computeEnvId"]
res = requests.get(url=f"{nextflow_api}/compute-envs", headers=headers)
print(compute_env_id)

# setup workflow
# TODO: unable to recognize profile if submit it via workflow and pipeline is defined in nextflow.config
# works if you define it in a pipeline...don't know why

workflow = {
    "launch": {
        "computeEnvId": compute_env_id,
        "pipeline": config.pipeline_repo,
        "workDir": config.workflow_workdir,
        "revision": config.revision,
        "configProfiles": config.config_profiles,
        "paramsText": json.dumps(config.params_text),
        "mainScript": config.main_script,
        "pullLatest": True,
    }
}

print(json.dumps(workflow))
res = requests.post(
    url=f"{nextflow_api}/workflow/launch", data=json.dumps(workflow), headers=headers
)

print(res.json())
