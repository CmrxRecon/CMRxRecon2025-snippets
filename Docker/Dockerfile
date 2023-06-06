FROM python:3.9.1-slim-buster

# RUN pip install nibabel medpy rarfile 
RUN pip install numpy h5py scipy pandas rarfile  scikit-image nibabel
COPY *.py /app
COPY data/GT /GT
# RUN chmod +x /usr/local/bin/*.py
# RUN cd /usr/local/bin/