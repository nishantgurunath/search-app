# search-app
A simple search engine to search entities built with streamlit and elasticsearch. 

## Prepare Environments
The codes were tested and ran on Ubuntu 18.04 using python 3.7. 
Create and set up a python environment by running the following command in the terminal
```
# create python venv and install libraries in the requirements.txt
source ./create_env
```

## Docker
Since this app depends on the elasticsearch container, it is preferable to use docker compose. 
Before getting started, let's build the docker container of this app
```
docker-compose build
```
Then use docker compose:
```
docker-compose up
# the webapp should be available in localhost:8501
```
