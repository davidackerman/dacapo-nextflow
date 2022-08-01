from typing import Union
import requests
import json
from os.path import expanduser


class Nextflow:
    """Class for interacting with Nextflow Tower, including setting credentials and launching jobs"""

    # general settings
    _host_name = "nextflow.int.janelia.org"
    _nextflow_api = f"https://{_host_name}/api"

    # compute environment settings
    _head_queue = "local"

    # workflow settings
    _pipeline_repo = f"https://github.com/davidackerman/dacapo-nextflow"
    _revision = "main"
    _config_profiles = ["lsf"]
    _main_script = "dacapo.nf"

    def __init__(self, user_info: dict):
        """Initializes Nextflow class

        Args:
            user_info (dict): Dictionary containing Nextlfow username and api token
        """
        self._username = user_info["username"]
        self._api_token = user_info["api_token"]
        self._headers = {
            "Authorization": f"Bearer {self._api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def setup_nextflow_user(self, ssh_key: str) -> str:
        """Add ssh key to nextflow account using token."""

        # ensure token is valid by making get request
        self._get_request("tokens", "validating API token")

        # set ssh key
        self._set_credentials(ssh_key)

    def set_compute_parameters(
        self, chargegroup: str, compute_queue: str
    ) -> Union[None, str]:
        """Set Nextflow compute environment specified by a charge group and compute queue

        Args:
            chargegroup (str): The group to be charged for the run
            compute_queue (str): The queue the job is submitted to

        Returns:
            Union[None, str]: The compute environment id, if it exists
        """

        # general compute parameters
        self._chargegroup = chargegroup
        self._compute_queue = compute_queue

        # setting of nextflow compute environment
        self._get_compute_environment()
        if not self._compute_env_id:
            self._set_compute_environment()
            return "Succeeded setting up compute parameters"

    def launch_workflow(self, params_text: dict):
        """Launches workflow for job specified in params_text"""

        params_text["lsf_opts"] = f'-P {self._chargegroup} -gpu "num=1"'
        workdir = expanduser(f"~{self._username}/") + ".dacapo/nextflow"
        workflow = {
            "launch": {
                "computeEnvId": self._compute_env_id,
                "pipeline": self._pipeline_repo,
                "workDir": workdir,
                "revision": self._revision,
                "configProfiles": self._config_profiles,
                "paramsText": json.dumps(params_text),
                "mainScript": self._main_script,
                "pullLatest": True,
            }
        }

        task = f'submitting run {params_text["run_name"]}'

        response = self._post_request("/workflow/launch", workflow, task)
        workflow_id = response.json()["workflowId"]

        message = f'Succeeded {task}. Monitor <a href="https://{self._host_name}/user/{self._username}/watch/{workflow_id}" target="_blank">here</a>.'
        return message

    def _get_request(self, endpoint: str, task: str) -> requests.Response:
        """Wrapper for requests.get"""
        try:
            response = requests.get(
                url=f"{self._nextflow_api}/{endpoint}",
                headers=self._headers,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise Exception(self._format_response_error(task, response))
        return response

    def _post_request(self, endpoint: str, data: dict, task: str) -> requests.Response:
        """Wrapper for requests.post"""
        try:
            response = requests.post(
                url=f"{self._nextflow_api}/{endpoint}",
                data=json.dumps(data),
                headers=self._headers,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise Exception(self._format_response_error(task, response))
        return response

    def _format_response_error(self, task: str, response: requests.Response) -> str:
        """Takes a request response and formats it in a string"""
        message = f"Failed {task}. "
        if response.headers.get("content-type") == "application/json":
            response_json = response.json()
            message += f"Response: {response.status_code}."
            if "message" in response_json and response_json["message"]:
                message += f' Error message: {response_json["message"]}.'
        return message

    def _get_credentials(self) -> Union[None, str]:
        """Get "dacapo" credential from Nextflow

        Returns:
            Union[None, str]: The credential id, if it exists
        """
        credential_id = None
        response = self._get_request("credentials", "getting ssh credential")
        for credential in response.json()["credentials"]:
            if credential["name"] == "dacapo":
                credential_id = credential["id"]
        return credential_id

    def _set_credentials(self, ssh_key: str):
        """Set Nextflow ssh key credential"""
        credentials = {
            "credentials": {
                "name": "dacapo",
                "provider": "ssh",
                "keys": {
                    "privateKey": ssh_key,
                    "passphrase": None,
                },
            }
        }
        self._post_request("credentials", credentials, "setting up SSH key")

    def _get_compute_environment(self) -> Union[None, str]:
        """Get Nextflow compute environment specified by charge group and compute queue"""
        message = f"getting up compute environment for chargegroup {self._chargegroup} and compute_queue {self._compute_queue}"
        self._compute_env_id = None
        compute_env_name = f"dacapo_{self._chargegroup}_{self._compute_queue}"
        response = self._get_request("compute-envs", message)
        for compute_env in response.json()["computeEnvs"]:
            if compute_env["name"] == compute_env_name:
                self._compute_env_id = compute_env["id"]

    def _set_compute_environment(self):
        """Set compute environment for jobs"""
        workdir = expanduser(f"~{self._username}/") + ".dacapo/nextflow"
        compute_env = {
            "computeEnv": {
                "name": f"dacapo_{self._chargegroup}_{self._compute_queue}",
                "platform": "lsf-platform",
                "config": {
                    "userName": self._username,
                    "workDir": workdir,
                    "launchDir": workdir,
                    "hostName": self._host_name,
                    "headQueue": self._head_queue,
                    "computeQueue": self._compute_queue,
                    "headJobOptions": f"-P {self._chargegroup}",
                },
                "credentialsId": self._get_credentials(),
            }
        }

        message = f"setting up compute environment for chargegroup {self._chargegroup} and compute_queue {self._compute_queue}"
        response = self._post_request("compute-envs", compute_env, message)
        self._compute_env_id = response.json()["computeEnvId"]
