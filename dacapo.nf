#!/usr/bin/env nextflow
nextflow.enable.dsl=2

process dacapo {
    container: "ackermand/dacapo"
    cpus params.cpus
    script:
      """
      /dacapo.sh train -r ${params.run_name}
      """
}

workflow {
  dacapo()
}
