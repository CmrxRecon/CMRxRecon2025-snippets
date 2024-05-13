FROM dev.passer.zyheal.com:8087/playground/cmrxrecon2024-validation:gt

# RUN pip install nibabel medpy rarfile
#COPY data/ChallengeData /GT/ChallengeData
COPY *.py /app/
COPY requirements.txt /app
COPY sources.list /etc/apt/sources.list
WORKDIR /app
#RUN apt install apt-transport-https ca-certificates && apt update
#RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r ./requirements.txt
#COPY data/GroundTruth4Ranking /GT/GroundTruth4Ranking
#COPY data/newID.csv /home/wangfw/CMRxRecon2024Organizer/Code/newID.csv
