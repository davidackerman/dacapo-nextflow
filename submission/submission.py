import requests
import json
from config.settings import *

nextflow_api = f"http://{hostname}/api"
headers = {
    "Authorization": f"Bearer {api_token}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}


def get_login_node_credentials():
    res = requests.get(url=f"{nextflow_api}/credentials", headers=headers)
    for credential in res.json()["credentials"]:
        if credential["name"] == "login_node":
            credential_id = credential["id"]

    return credential_id


def get_or_setup_compute_environment(credential_id):
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
                    "workDir": work_dir,
                    "launchDir": launch_dir,
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
        compute_env_id = res.json()["computeEnvId"]
    res = requests.get(url=f"{nextflow_api}/compute-envs", headers=headers)

    return compute_env_id


def launch_workflow(compute_env_id):
    workflow = {
        "launch": {
            "computeEnvId": compute_env_id,
            "pipeline": pipeline_repo,
            "workDir": workflow_workdir,
            "revision": revision,
            "configProfiles": config_profiles,
            "paramsText": json.dumps(params_text),
            "mainScript": main_script,
            "pullLatest": True,
        }
    }

    res = requests.post(
        url=f"{nextflow_api}/workflow/launch",
        data=json.dumps(workflow),
        headers=headers,
    )

    workflow_id = res.json()["workflowId"]
    res = requests.get(
        url=f"{nextflow_api}/workflow/{workflow_id}",
        data=json.dumps(workflow),
        headers=headers,
    )

    print(
        f'Monitor run at http://{hostname}/user/{res.json()["workflow"]["userName"]}/watch/{workflow_id}.'
    )


if __name__ == "__main__":
    credential_id = get_login_node_credentials()
    compute_env_id = get_or_setup_compute_environment(credential_id)
    launch_workflow(compute_env_id)
