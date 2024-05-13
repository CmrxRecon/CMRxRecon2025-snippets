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

baseCommand: ["python3", "/app/Main_Score2024.py"]
arguments:
  - prefix: -i
    valueFrom: $(inputs.input_file.path)
  - prefix: -g
    valueFrom: /GT
  - prefix: -t
    valueFrom: Task2
    # 此处根据task1还是task2来指定
  - prefix: -o
    valueFrom: ./

hints:
  DockerRequirement:
    dockerPull: dev.passer.zyheal.com:8087/playground/cmrxrecon2024-validation:latest