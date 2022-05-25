EXAMPLE_PATH=data/
S3_PATH = s3://2022-msia423-gong-xiaoyun/data/raw/villagers.csv
LOCAL_PATH = data/raw/villagers.csv
LOCAL_DOWNLOAD_PATH = data/download/villagers.csv

image-run:
	docker build -f dockerfiles/Dockerfile.run -t animalcrossing .

image-app:
	docker build -f dockerfiles/Dockerfile.app -t animalcrossingapp .

upload-to-S3:
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY animalcrossing run.py upload_file_to_s3 --local_path=${LOCAL_PATH} --s3_path=${S3_PATH}

data/download/villagers.csv:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY animalcrossing run.py download_file_from_s3 \
	--s3_path=${S3_PATH} --local_path=${LOCAL_DOWNLOAD_PATH}

download-from-S3: data/download/villagers.csv

data/interim/clean.csv:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ animalcrossing run.py preprocess --config=config/model_config.yaml

preprocess: data/interim/clean.csv