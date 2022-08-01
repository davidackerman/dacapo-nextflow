from nextflow import Nextflow
import config
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    user_info = {"username": config.username, "api_token": config.api_token}
    nextflow = Nextflow(user_info)

    try:
        setup_status = nextflow.set_compute_parameters(
            config.chargegroup, config.compute_queue
        )
        if setup_status:
            logging.info(setup_status)

        submission_status = nextflow.launch_nextflow_workflow(config.params_text)
        logging.info(submission_status)
    except Exception as e:
        logging.error(str(e))
