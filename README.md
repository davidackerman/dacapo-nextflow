# dacapo-nextflow
This repository is to be used for running [dacapo](https://github.com/funkelab/dacapo) via [Nextflow Tower](https://cloud.tower.nf/)

# Template config file
To run Tower using this repo you need a configuration file, to be placed in `submission_demo/config.py`. A template config file is provided in `submission_demo/template_config.py`. Below find a specific example `submission_demo/config.py`:
```python
username = "{my_user_name}"
api_token = "{my_api_token}"
hostname = "nextflow.int.janelia.org"
work_dir = "/path/to/workdir"
launch_dir = "/path/to/launchdir"
head_queue = "local"
compute_queue = "local"
chargegroup = "cellmap"
pipeline_repo = "https://github.com/davidackerman/dacapo-nextflow"
revision = "main"
workflow_workdir = "output"
config_profiles = ["lsf"]
main_script = "dacapo.nf"
params_text = {
    "run_name": "signed_distances_mito_sum159-4_mito_mini_upsample_unet_test_gunpowder__0",
    "cpus": 5,
    "lsf_opts": f"{chargegroup}",
}
```
# First time setup
Before running dacapo via Tower, you need to setup a couple of one-time settings. The first is to copy your ssh key into Nextflow. To do so, run `ssh-keygen -t rsa -b 4096` on a node that can submit to the Janelia Cluster (eg. login1). Log into https://nextflow.int.janelia.org/ using your Janelia credentials. Go to the "Credentials" tab and press "New credentials" and select "SSH" as the provider. Copy the contents of ~/.ssh/id_rsa (containing the private key) to the SSH private key field. Name it "dacapo" and click create. Next go to the dropdown by your icon in the top right and select "Your Tokens." Click "New token" name and copy the resulting token. Paste this Tower API token into the corresponding part in the `config.py` file.

# Running via command line
Note that this will currently only work if you have a dacapo.yaml file set up in eg. `~/.config/dacapo/`:
1. Clone or download this repository.
2. Update `submission_demo/config.py` to reflect your settings.
3. Run `python submission_demo/submission.py`. This will use your API token to get your login node credentials via Tower. It will then use your token and credential to get (or setup) a compute environment for your job based on the chargegroup and compute queue. It will then launch your workflow and provide a link to monitor it. 