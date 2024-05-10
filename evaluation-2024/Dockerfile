FROM python:3.9.1-slim-buster

# RUN pip install nibabel medpy rarfile 
RUN apt update && apt install -y zip && pip install -r ./requirements.txt
COPY *.py /app/
COPY data/GT/ /GT
COPY path-to-csv '/home/wangfw/CMRxRecon2024Organizer/Code/newID.csv'
# RUN chmod +x /usr/local/bin/*.py
# RUN cd /usr/local/bin/
