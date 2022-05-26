EXAMPLE_PATH=data/
S3_PATH = s3://2022-msia423-gong-xiaoyun/data/raw/villagers.csv
LOCAL_PATH = data/raw/villagers.csv
LOCAL_DOWNLOAD_PATH = data/download/villagers.csv

image-run:
	docker build -f dockerfiles/Dockerfile.run -t animalcrossing .

image-app:
	docker build -f dockerfiles/Dockerfile.app -t animalcrossingapp .

image-app-ecs:
	docker build --platform linux/x86_64 -f dockerfiles/Dockerfile.app -t msia423-flask . 

upload-to-S3:
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY animalcrossing run.py upload_file_to_s3 --local_path=${LOCAL_PATH} --s3_path=${S3_PATH}

data/download/villagers.csv:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY animalcrossing run.py download_file_from_s3 \
	--s3_path=${S3_PATH} --local_path=${LOCAL_DOWNLOAD_PATH}

download-from-S3: data/download/villagers.csv

data/interim/clean.csv:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ animalcrossing run.py preprocess --config=config/model_config.yaml

preprocess: data/interim/clean.csv

models/kmodes.joblib:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ animalcrossing run.py train --config=config/model_config.yaml --model_path=models/kmodes.joblib

train: models/kmodes.joblib

data/final/recommendation.csv:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ animalcrossing run.py recommendation --config=config/model_config.yaml

recommendation: data/final/recommendation.csv

model-all: preprocess train recommendation

create_db:
	docker run -e SQLALCHEMY_DATABASE_URI animalcrossing run.py create_db

ingest_raw:
	docker run -e SQLALCHEMY_DATABASE_URI animalcrossing run.py ingest_raw

ingest_rec:
	docker run -e SQLALCHEMY_DATABASE_URI animalcrossing run.py ingest_rec

launch:
	docker run -e SQLALCHEMY_DATABASE_URI --name test-app --mount type=bind,source="$(shell pwd)"/data,target=/app/data/ -p 5001:5000 animalcrossingapp

rm:
	docker rm test-app

relauch: rm launch

ecs-push:
	docker push 008395313216.dkr.ecr.us-east-1.amazonaws.com/msia423-flask:latest