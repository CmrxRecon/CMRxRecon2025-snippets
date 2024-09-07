## Start from this Docker image
## for the version, we recommend the version xx.xx less than 22.02
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-devel

## Set workdir in Docker Container
# set default workdir in your docker container
# In other words your scripts will run from this directory
WORKDIR /app

## Copy all your files of the current folder into Docker Container
COPY ./ /app

## Install requirements
RUN pip3 install -r requirements.txt

## Make Docker container executable
ENTRYPOINT ["/opt/conda/bin/python", "inference.py"]