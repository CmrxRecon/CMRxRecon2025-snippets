python /app/Main_Score2024.py -i SubmissionTask1.zip -g /GT -t task1 -o o1
python /app/Main_Score2024.py -i SubmissionTask2.zip -g /GT -t task2 -o o2
tag='dev.passer.zyheal.com:8087/playground/cmrxrecon2024-validation:latest' && docker build -t $tag . && docker push $tag
