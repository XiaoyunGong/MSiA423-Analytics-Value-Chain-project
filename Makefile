S3_PATH = s3://2022-msia423-gong-xiaoyun/data/raw/villagers.csv
LOCAL_PATH = data/external/villagers.csv
LOCAL_DOWNLOAD_PATH = data/raw/villagers.csv

# for developing: clean up everything for make
cleanup:
	rm data/raw/villagers.csv
	rm data/final/recommendation.csv
	rm data/interim/clean.csv
	rm figures/cost_plot_kmodes.png
	rm models/kmodes.joblib
	rm data/interim/for_model.csv
	rm deliverables/kmodes_result.csv
	rm data/animalcrossing.db
	rm deliverables/metric.csv

# docker images
image-run: dockerfiles/Dockerfile.run
	docker build -f dockerfiles/Dockerfile -t final-project .

image-app: dockerfiles/Dockerfile.app
	docker build -f dockerfiles/Dockerfile.app -t final-project-app .

image-app-ecs: dockerfiles/Dockerfile.app
	docker build --platform linux/x86_64 -f dockerfiles/Dockerfile.app -t msia423-flask . 

upload-to-S3:
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY final-project run.py upload_file_to_s3 --local_path=${LOCAL_PATH} --s3_path=${S3_PATH}

# modeling (start from downloading data)
.PHONY: download-from-S3 data/raw/villagers.csv
data/raw/villagers.csv: 
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY final-project run.py download_file_from_s3 \
	--s3_path=${S3_PATH} --local_path=${LOCAL_DOWNLOAD_PATH}

download-from-S3: data/raw/villagers.csv

.PHONY: preprocess data/interim/clean.csv
data/interim/clean.csv: config/model_config.yaml data/raw/villagers.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py preprocess --config=config/model_config.yaml

preprocess: data/interim/clean.csv

.PHONY: train models/kmodes.joblib
models/kmodes.joblib figures/cost_plot_kmodes.png data/interim/for_model.csv deliverables/kmodes_result.csv &:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py train --config=config/model_config.yaml --model_path=models/kmodes.joblib

train: models/kmodes.joblib figures/cost_plot_kmodes.png data/interim/for_model.csv deliverables/kmodes_result.csv

.PHONY: recommendation data/final/recommendation.csv
data/final/recommendation.csv: config/model_config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py recommendation --config=config/model_config.yaml

recommendation: data/final/recommendation.csv 

.PHONY: get_metric deliverables/metric.csv 
deliverables/metric.csv: config/model_config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ final-project run.py get_metric --config=config/model_config.yaml

get_metric: deliverables/metric.csv

model-all: download-from-S3 preprocess train recommendation get_metric

# to RDS (run only once)
.PHONY: create_db ingest_raw ingest_rec ingest-all
create_db:
	docker run -e SQLALCHEMY_DATABASE_URI --mount type=bind,source="$(shell pwd)"/data,target=/app/data/ final-project run.py create_db

ingest_raw:
	docker run -e SQLALCHEMY_DATABASE_URI --mount type=bind,source="$(shell pwd)"/data,target=/app/data/ final-project run.py ingest_raw

ingest_rec:
	docker run -e SQLALCHEMY_DATABASE_URI --mount type=bind,source="$(shell pwd)"/data,target=/app/data/ final-project run.py ingest_rec

ingest-all: ingest_raw ingest_rec

check:
	docker run --platform linux/x86_64  -it --rm  mysql:5.7.33 mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD}
# launch the app locally
launch:
	docker run -e SQLALCHEMY_DATABASE_URI --name test-app --mount type=bind,source="$(shell pwd)"/data,target=/app/data/ -p 5001:5000 final-project-app

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

ecs-all: ecs-login ecs-tag ecs-push

# test
.PHONY: test
test:
	docker build -f dockerfiles/Dockerfile.test -t final-project-tests .
	docker run final-project-tests
