# dacapo-nextflow
This repository is to be used for running [dacapo](https://github.com/funkelab/dacapo) via [Nextflow Tower](https://cloud.tower.nf/)

# Template config file
```python
username = "{myUserName}"
api_token = "{myApiToken}"
hostname = "nextflow.int.janelia.org"
work_dir = "/path/to/workdir"
launch_dir = "/path/to/launchdir"
head_queue = "local"
compute_queue = "local"
head_job_options = "-P cellmap"
pipeline_repo = "https://github.com/davidackerman/dacapo-nextflow"
revision = "main"
workflow_workdir = "output"
config_profiles = ["lsf"]
main_script = "dacapo.nf"
params_text = {
    "run_name": "distance_task_20211130_six_class_distances_datasplit_20211130_dummy_architecture_20211130_gunpowder_trainer_20211130:2",
    "cpus": 5,
    "lsf_opts": "-P cellmap",
}
```
# First time setup
Before running dacapo via Tower, you need to setup a couple of one-time settings. Run `ssh-keygen -t rsa -b 4096` on a node that can submit to the Janelia Cluster (eg. login1). Log into https://nextflow.int.janelia.org/ using your Janelia credentials. Go to the "Credentials" tab and press "New credentials" and select "SSH" as the provider. Copy the contents of ~/.ssh/id_rsa (containing the private key) to the SSH private key field. Name it "login1_credential" and click create. Next go to the dropdown by your icon in the top right and select "Your Tokens." Click "New token" name and copy the resulting token. Paste this Tower API token into the corresponding part in the `config.py` file.

## Running via command line
1. Clone or download this repository.
2. Update `config.py` to reflect your settings.
3. Run `python submission.py`. This will use your API token to get your login node credentials via Tower. It will then use your token and credential to get (or setup) a compute environment for your job. It will then launch your workflow and provide a link to monitor it.


