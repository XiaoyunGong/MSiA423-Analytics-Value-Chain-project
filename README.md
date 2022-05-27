# MSiA423 Project: Animal Crossing Villager Recommender
Author: Xiaoyun Gong


## Table of Contents
- [MSiA423 Project: Animal Crossing Villager Recommender](#msia423-project-animal-crossing-villager-recommender)
	- [Table of Contents](#table-of-contents)
	- [Project charter](#project-charter)
		- [Vision](#vision)
		- [Mission](#mission)
		- [Success criteria](#success-criteria)
			- [Machine learning performance metric](#machine-learning-performance-metric)
		- [Business Metrics](#business-metrics)
	- [Directory structure](#directory-structure)
	- [Setup](#setup)
		- [Environment Variable and Credentials](#environment-variable-and-credentials)
			- [AWS S3](#aws-s3)
			- [AWS RDS](#aws-rds)
		- [Docker images](#docker-images)
			- [Create the docker image for `run.py`](#create-the-docker-image-for-runpy)
			- [Create the docker image for `app.py`](#create-the-docker-image-for-apppy)
			- [Create the docker image for testing](#create-the-docker-image-for-testing)
	- [Data Source](#data-source)
	- [Model Pipeline](#model-pipeline)
		- [Run everything as a pipeline](#run-everything-as-a-pipeline)
		- [Create the recommendation results step by step](#create-the-recommendation-results-step-by-step)
			- [Download raw data from S3](#download-raw-data-from-s3)
			- [Preprocess the data](#preprocess-the-data)
			- [Train model](#train-model)
			- [Generate recommendation results](#generate-recommendation-results)
	- [Database storing](#database-storing)
		- [Remote database Connection](#remote-database-connection)
	- [Launch the App](#launch-the-app)
		- [Launch the App locally](#launch-the-app-locally)
		- [Launch the app via AWS ECS](#launch-the-app-via-aws-ecs)
	- [Testing](#testing)
	- [Pylint](#pylint)

## Project charter
### Vision
Releasied in March 2020, **Animal Crossing: New Horizon** ([official website](https://animal-crossing.com/), [wikipedia](https://en.wikipedia.org/wiki/Animal_Crossing)) is a social simulation game developed by Nintendo as the fifth main entry in the Animal Crossing series. The game was a huge commercial success with 37.62 million copies sold worldwide. 

In Animal Crossing, each player usually has 10 villagers on their island. These villagers have different personalitiies, color preferences, and home decor styles. These villagers interact with players all the time. When one villager chooses to leave the island, the player has the opportunity to invite another villager from a deserted island to their island. Which villager should they invite? Should they invite the first villager they meet at the deserted island?

This app aims to solve these problems by building a recommender system based on players' preferences on villagers. The app will identify villagers that the player will like better.

### Mission
Users will be prompted to choose their ideal villager, and the recommender will output the top 10 villagers with similar properties. The dataset of this project is from the [**Animal Crossing Dataset**](https://www.kaggle.com/datasets/jessicali9530/animal-crossing-new-horizons-nookplaza-dataset). This dataset contains information on all 392 villagers and 9000+ items in the game.


### Success criteria

#### Machine learning performance metric

This app will be using the k-modes algorithm. There will not be a fixed value set as the deployement threshold. Optimal k (number of clusters) will be found using scree plot of the cost. Other metrics can be evalutated when the app goes live. For example, the precision and recall of the recommendation provided. 

### Business Metrics
From a business perspective, the number of visits to the app and retention rate can be measured. There can also be surveys sent to users asking whether they think the recommendation is helpful. 


## Directory structure 

```
├── README.md                         <- You are here
├── api
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs│    
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│   ├── raw/                 	      <- Raw data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project.
|
├── dockerfiles/                      <- Directory for all project-related Dockerfiles 
│   ├── Dockerfile.app                <- Dockerfile for building image to run web app
│   ├── Dockerfile.run                <- Dockerfile for building image to execute run.py  
│   ├── Dockerfile.test               <- Dockerfile for building image to run unit tests
│   ├── Dockerfile.rds	              <- Dockerfile for building image to creare data schema to rds
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup. 
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project. No executable Python files should live in this folder.  
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the web app 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```

## Setup

### Environment Variable and Credentials

#### AWS S3

The data of this project is stored using AWS S3, an AWS data storage service. To be able to reproduce the data aquisition step, the user's `AWS_ACCESS_KEY_ID` and `AWS_SUCRET_ACCESS_KEY` are needed. 
Running the commands below will load user's credentials as environment variables. 

```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY"
```
**Note:**
Replace `YOUR_ACCESS_KEY_ID` and `YOUR_SECRET_ACCESS_KEY` with user's own AWS credentials. 

#### AWS RDS
An AWS RDS (Relational Database Service by AWS) instance is used to contain the MySQL database for this project. To be able to create database and ingest data into the remote database, `SQLALCHEMY_DATABASE_URI` needs to be loaded as an enviromental variable. The `SQLALCHEMY_DATABASE_URI`  is defined by a string with the following format:

```bash
dialect+driver://username:password@host:port/database
```
Running the commands below will load user's `SQLALCHEMY_DATABASE_URI` as environment variables. 
**Note:**
Replace `username`, `password`, `host`, `port`, and `database` with user's own RDS setups.

```bash
export SQLALCHEMY_DATABASE_URI = "YOUR_DATABASE_URI"
```

To be able to enter the interactive session for the remote mysql database, the some connection credentials are needed. The following commands will load the credentials as environment variables.
```bash
export MYSQL_USER="YOUR_SQL_USER_NAME"
export MYSQL_PASSWORD="YOUR_SQL_PASSWORD"
export MYSQL_HOST="YOUR_SQL_HOST"
export MYSQL_PORT="YOUR_SQL_PORT"
export MYSQL_DATABASE="YOUR_DATABASE_NAME"
```

### Docker images

There are three(?) docker images used in this project. The first one is for the steps before launching the app, the second one is for the app, and the third one is for testing.

#### Create the docker image for `run.py`

```bash
make image-run
```

#### Create the docker image for `app.py`

```bash
make image-app
```

#### Create the docker image for testing

(HERE, TODO)

## Data Source

After setting up environment variables and docker images, the first step is to get the data.

The dataset used for this app comes from Kaggle. To download the data, users can go to this [**Animal Crossing dataset website**](https://www.kaggle.com/datasets/jessicali9530/animal-crossing-new-horizons-nookplaza-dataset) and click the Download button at the top of the page. Note that users will need to register a Kaggle account in order to download dataset if user do not have one. Because the dataset is relatively small, a copy was saved in `data/external/villagers.csv`. Another copy is uploaded to S3. The following command will upload the data form `data/external/villagers.csv` (or any local location) to the user's S3 bucket.

```bash
make upload-to-S3
```

The current default for the local path to the data is `data/raw/villagers.csv`, and the S3 path to the data is `s3://2022-msia423-gong-xiaoyun/data/raw/villagers.csv`. If the user needs to upload the data from another local location or upload the data to another destination in S3, the following command can address that.

```bash
make upload-to-S3 LOCAL_PATH=<YOUR_LOCAL_PATH> S3_PATH=<YOUR_S3_PATH>
```

**Note:**
To run these commands, `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` need to be loaded as environment variables, and the docker image `animalcrossing` needs to be built.

## Model Pipeline
### Run everything as a pipeline
If user want to create everything in one command, the user can use the command below. This command will take the raw data, preprocess it, train the model, and generate the recommendation results.

```bash
make model-all
```
The final result is going to be saved in `data/final/recommendations.csv`. 
**Instead**, the user can also run it step by step (see below).
### Create the recommendation results step by step

#### Download raw data from S3
Although stored in local in `data\external\villagers.csv`, data can be downloaded from S3. The following command will download the data to `data/raw/villagers.csv` (by default).
```bash
make download-from-S3
```

The current default for the local path to the data is `data/raw/villagers.csv`, and the S3 path to the data is `s3://2022-msia423-gong-xiaoyun/data/raw/villagers.csv`. If the user needs to download the data to another local location or download the data from another destination in S3, the following command can address that.

```bash
make download-from-S3 LOCAL_DOWNLOAD_PATH=<YOUR_LOCAL_DOWNLOAD_PATH> S3_PATH=<YOUR_S3_PATH>
```

#### Preprocess the data
With the data in a local folder, now user can start to preprocess the data. The command below will allow users to preprocess the data. This function read in data from `data/raw/villagers.csv` and the preprocessed dataframe is stored in `data/interim/clean.csv` by default.

```bash
make preprocess
```

#### Train model
With the preprocessed data, the user can train the model. The command below will train the kmodes model. A cost by number of cluster plot will be generated and saved in `figures/cost_plot_kmodes.png`. The kmodes model is saved in `models/kmodes.joblib` for reference. 

**Note:** This will take a little bit. 
```bash
make train
```

#### Generate recommendation results
With the model ready to go, the user can now generate the recommendations by running the command below. This command will take in the cleaned data and generate a table of recommendations that is saved in `data/final/recommendations.csv` by default.

```bash
make recommendation
```


## Database storing

### Remote database Connection
As mentioned before, the database used for this project is stored in AWS RDS. The command below will connect user to the database on RDS, and load the raw data (**villagers**) and the recommendation data (**recommendations**) to RDS.

```bash
make create_db
```

```bash
make ingest_raw
```

```bash
make ingest_rec
```

**Note:**
For security reasons, this database can only be accessed for users connected to the Northwetsern VPN. Besides, the RDS credential `SQLALCHEMY_DATABASE_URI` must be loaded into environment before running the command. There is no default values of the credentials for this command. 

These data should only be ingested once. If there is any problem with it, user will need to connect to RDS and drop the tables that are already created. 

**Optional: Test the connection to RDS**

The following command will connect users to their RDS MySQL databases.
```bash
docker run -it --rm mysql:5.7.33 mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD}
```
For users whose computers that have the Apple M1 Chips, the following command should be used instead.

```bash
docker run --platform linux/x86_64  -it --rm  mysql:5.7.33 mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD}
```
**Note:** To test the connection to RDS, the RDS credentials `MYSQL_HOST`, `MYSQL_USER`, and `MYSQL_PASSWORD` need to be loaded in the environment. 

If successfully connected, the following may run the following commands:

To show all the databases: `show databases`;

To use a particular database: `use <database_name>`;

After selecting a database, you can see all the tables in it by running: `show tables`;

You may check the columns within a table by running: `show columns from <table_name>`;

## Launch the App
There are two ways to launch the App: lauching it locally, or accessing it via AWS ECS.

### Launch the App locally
To launch the app locally, a docker image need to be built. The command below will build the image.
```bash
make image-app
```
The command below will launch the App at `http://127.0.0.1:5001/`.
```bash
make launch
```

(for developing: if need to relauch, run)
```bash
make relaunch
```

### Launch the app via AWS ECS
```bash
make image-app-ecs
```

```bash
make ecs-push
```

The web app is available at `http://msia423-1454829810.us-east-1.elb.amazonaws.com/`.

## Testing

Run the following:

```bash
 docker build -f dockerfiles/Dockerfile.test -t pennylanetest .
```

To run the tests, run: 

```bash
 docker run pennylanetest
```

The following command will be executed within the container to run the provided unit tests under `test/`:  

```bash
python -m pytest
``` 

## Pylint

Run the following:

```bash
 docker build -f dockerfiles/Dockerfile.pylint -t pennylint .
```

To run pylint for a file, run:

```bash
 docker run pennylint run.py 
```

(or any other file name, with its path relative to where you are executing the command from)

To allow for quick iteration, mount your entire repo so changes in Python files are detected:


```bash
 docker run --mount type=bind,source="$(pwd)"/,target=/app/ pennylint run.py
```
