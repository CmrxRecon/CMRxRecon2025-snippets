#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
label: Score predictions file

requirements:
  - class: InlineJavascriptRequirement

inputs:
  - id: input_file
    type: File
#  - id: goldstandard
#    type: File
#  - id: check_validation_finished
#    type: boolean?

outputs:
  - id: results
    type: File
    outputBinding:
      glob: Result/results.json
  - id: log_file
    type: File
    outputBinding:
      glob: better_log.zip
  - id: status
    type: string
    outputBinding:
      glob: Result/results.json
      outputEval: $(JSON.parse(self[0].contents)['submission_status'])
      loadContents: true

baseCommand: ["python3", "/app/Main_Score.py"]
arguments:
  - prefix: -f
    valueFrom: $(inputs.input_file.path)
  - prefix: -g
    valueFrom: /GT
  - prefix: -t
    valueFrom: Mapping
    # 此处根据task1还是task2来指定
  - prefix: -r
    valueFrom: results.json

hints:
  DockerRequirement:
    dockerPull: docker.synapse.org/syn51471092/validate:latest