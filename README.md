# MSiA423 Project: Animal Crossing Villager Recommender
Author: Xiaoyun Gong


# Table of Contents
* [Project charter ](#Project-charter)
* [Directory structure ](#Directory-structure)
* [Running the app ](#Running-the-app)
	* [1. Initialize the database ](#1.-Initialize-the-database)
	* [2. Configure Flask app ](#2.-Configure-Flask-app)
	* [3. Run the Flask app ](#3.-Run-the-Flask-app)
* [Testing](#Testing)
* [Mypy](#Mypy)
* [Pylint](#Pylint)

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

## Running the app 
### 1. Load data into S3 and Download data from S3
#### AWS Credentials Configuration
To configure AWS credentials, run the following commands in terminal to load your credentials as environment variables. These credentials all users to connect to AWS S3.

```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY"
```
**Note:**
Replace `YOUR_ACCESS_KEY_ID` and `YOUR_SECRET_ACCESS_KEY` with your own AWS credentials. 

#### Load data to S3
First, a docker image need to be built. To build the iamge, run from this directory (the root of the repe):

```bash
docker build -f dockerfiles/Dockerfile.run -t animalcrossing .
```

Then, the following command will upload the data file to S3. 
```base
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY animalcrossing run.py upload_file_to_s3 
```

#### Download data from S3 (TO DO)
An optional choise is to download the dataset. The following command will download the file to a desinated location.
```base
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY --mount type=bind,source="$(shell pwd)",target=/app/ animalcrossing run.py download_file_from_s3 --output=test/data.csv
```
### 2. Create the Database on RDS
#### Create a docker container
```bash
docker build -f dockerfiles/Dockerfile.rds -t rds .
```
#### AWS RDS Credentials Configuration
To configure AWS RDS credentials, run the following commands in terminal to load your credentials as environment variables. These credentials all users to connect to AWS RDS.
```bash
export MYSQL_HOST="YOUR_MYSQL_HOST"
export MYSQL_USER="YOUR_MYSQL_USER"
export MYSQL_PASSWORD="YOUR_MYSQL_PASSWORD"
export SQLALCHEMY_DATABASE_URI="YOUR_SQLALCHEMY_DATABASE_URI"
```
#### Add the database to RDS
```bash
docker run -it -e SQLALCHEMY_DATABASE_URI rds
```

#### Check if the database is added to RDS
```bash
docker run -it --rm mysql:5.7.33 mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD}
```
(for apple M1)
```bash
docker run --platform linux/x86_64  -it --rm  mysql:5.7.33 mysql  -h${MYSQL_HOST}  -u${MYSQL_USER}  -p${MYSQL_PASSWORD}
```

If successfully connected, you may run the following commands:

To show all the databases: `show databases`;
To use a particular database: `use <database_name>`;
After selecting a database, you can see all the tables in it by running: `show tables`;
You may check the columns within a table by running: `show columns from <table_name>`;


---------
### 1. Initialize the database 
#### Build the image 

To build the image, run from this directory (the root of the repo): 

```bash
 docker build -f dockerfiles/Dockerfile.run -t pennylanedb .
```
#### Create the database 
To create the database in the location configured in `config.py` run: 

```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/app/data/ pennylanedb create_db  --engine_string=sqlite:///data/tracks.db
```
The `--mount` argument allows the app to access your local `data/` folder and save the SQLite database there so it is available after the Docker container finishes.


#### Adding songs 
To add songs to the database:

```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/app/data/ pennylanedb ingest --engine_string=sqlite:///data/tracks.db --artist=Emancipator --title="Minor Cause" --album="Dusk to Dawn"
```

#### Defining your engine string 
A SQLAlchemy database connection is defined by a string with the following format:

`dialect+driver://username:password@host:port/database`

The `+dialect` is optional and if not provided, a default is used. For a more detailed description of what `dialect` and `driver` are and how a connection is made, you can see the documentation [here](https://docs.sqlalchemy.org/en/13/core/engines.html). We will cover SQLAlchemy and connection strings in the SQLAlchemy lab session on 
##### Local SQLite database 

A local SQLite database can be created for development and local testing. It does not require a username or password and replaces the host and port with the path to the database file: 

```python
engine_string='sqlite:///data/tracks.db'

```

The three `///` denote that it is a relative path to where the code is being run (which is from the root of this directory).

You can also define the absolute path with four `////`, for example:

```python
engine_string = 'sqlite://///Users/cmawer/Repos/2022-msia423-template-repository/data/tracks.db'
```


### 2. Configure Flask app 

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
DEBUG = True  # Keep True for debugging, change to False when moving to production 
LOGGING_CONFIG = "config/logging/local.conf"  # Path to file that configures Python logger
HOST = "0.0.0.0" # the host that is running the app. 0.0.0.0 when running locally 
PORT = 5000  # What port to expose app on. Must be the same as the port exposed in dockerfiles/Dockerfile.app 
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/tracks.db'  # URI (engine string) for database that contains tracks
APP_NAME = "penny-lane"
SQLALCHEMY_TRACK_MODIFICATIONS = True 
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100 # Limits the number of rows returned from the database 
```

### 3. Run the Flask app 

#### Build the image 

To build the image, run from this directory (the root of the repo): 

```bash
 docker build -f dockerfiles/Dockerfile.app -t pennylaneapp .
```

This command builds the Docker image, with the tag `pennylaneapp`, based on the instructions in `dockerfiles/Dockerfile.app` and the files existing in this directory.

#### Running the app

To run the Flask app, run: 

```bash
 docker run --name test-app --mount type=bind,source="$(pwd)"/data,target=/app/data/ -p 5000:5000 pennylaneapp
```
You should be able to access the app at http://127.0.0.1:5000/ in your browser (Mac/Linux should also be able to access the app at http://127.0.0.1:5000/ or localhost:5000/) .

The arguments in the above command do the following: 

* The `--name test-app` argument names the container "test". This name can be used to kill the container once finished with it.
* The `--mount` argument allows the app to access your local `data/` folder so it can read from the SQLlite database created in the prior section. 
* The `-p 5000:5000` argument maps your computer's local port 5000 to the Docker container's port 5000 so that you can view the app in your browser. If your port 5000 is already being used for someone, you can use `-p 5001:5000` (or another value in place of 5001) which maps the Docker container's port 5000 to your local port 5001.

Note: If `PORT` in `config/flaskconfig.py` is changed, this port should be changed accordingly (as should the `EXPOSE 5000` line in `dockerfiles/Dockerfile.app`)


#### Kill the container 

Once finished with the app, you will need to kill the container. If you named the container, you can execute the following: 

```bash
docker kill test-app 
```
where `test-app` is the name given in the `docker run` command.

If you did not name the container, you can look up its name by running the following:

```bash 
docker container ls
```

The name will be provided in the right most column. 

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

## Mypy

Run the following:

```bash
 docker build -f dockerfiles/Dockerfile.mypy -t pennymypy .
```

To run mypy over all files in the repo, run: 

```bash
 docker run pennymypy .
```
To allow for quick iteration, mount your entire repo so changes in Python files are detected:


```bash
 docker run --mount type=bind,source="$(pwd)"/,target=/app/ pennymypy .
```

To run mypy for a single file, run: 

```bash
 docker run pennymypy run.py
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
