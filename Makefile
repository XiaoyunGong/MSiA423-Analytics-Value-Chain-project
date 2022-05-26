EXAMPLE_PATH=data/
S3_PATH = s3://2022-msia423-gong-xiaoyun/data/raw/villagers.csv
LOCAL_PATH = data/raw/villagers.csv
LOCAL_DOWNLOAD_PATH = data/download/villagers.csv

# docker images
image-run:
	docker build -f dockerfiles/Dockerfile.run -t animalcrossing .

image-app:
	docker build -f dockerfiles/Dockerfile.app -t animalcrossingapp .

image-app-ecs:
	docker build --platform linux/x86_64 -f dockerfiles/Dockerfile.app -t msia423-flask . 

# upload to and download from S3
upload-to-S3:
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY animalcrossing run.py upload_file_to_s3 --local_path=${LOCAL_PATH} --s3_path=${S3_PATH}

data/download/villagers.csv:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY animalcrossing run.py download_file_from_s3 \
	--s3_path=${S3_PATH} --local_path=${LOCAL_DOWNLOAD_PATH}

download-from-S3: data/download/villagers.csv

# modeling
data/interim/clean.csv:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ animalcrossing run.py preprocess --config=config/model_config.yaml

preprocess: data/interim/clean.csv

models/kmodes.joblib figures/cost_plot_kmodes.png &:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ animalcrossing run.py train --config=config/model_config.yaml --model_path=models/kmodes.joblib

train: models/kmodes.joblib figures/cost_plot_kmodes.png

data/final/recommendation.csv:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ animalcrossing run.py recommendation --config=config/model_config.yaml

recommendation: data/final/recommendation.csv data/final/recommendation.csv models/kmodes.joblib figures/cost_plot_kmodes.png 

model-all: preprocess train recommendation

remove-all:
	rm data/interim/clean.csv
	rm models/kmodes.joblib
	rm figures/cost_plot_kmodes.png
	rm data/final/recommendation.csv

# to RDS (run only once)
create_db:
	docker run -e SQLALCHEMY_DATABASE_URI animalcrossing run.py create_db

ingest_raw:
	docker run -e SQLALCHEMY_DATABASE_URI animalcrossing run.py ingest_raw

ingest_rec:
	docker run -e SQLALCHEMY_DATABASE_URI animalcrossing run.py ingest_rec

# launch the app locally
launch:
	docker run -e SQLALCHEMY_DATABASE_URI --name test-app --mount type=bind,source="$(shell pwd)"/data,target=/app/data/ -p 5001:5000 animalcrossingapp

rm:
	docker rm test-app

relaunch: rm launch

# launch the app via ECS (for developing purposes)
ecs-push:
	docker push 008395313216.dkr.ecr.us-east-1.amazonaws.com/msia423-flask:latest
ecs-tag:
	docker tag msia423-flask:latest 008395313216.dkr.ecr.us-east-1.amazonaws.com/msia423-flask:latest
ecs-login:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 008395313216.dkr.ecr.us-east-1.amazonaws.com