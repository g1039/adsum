OpenTax
=======

This repository contains a data pipeline for processing high-volume tax-related financial transactions at OpenTax. It includes:

- **Apache Airflow DAG** for ETL automation  
- **FastAPI service** for exposing transaction insights  
- **Optimized PostgreSQL queries** for high performance  

These components ensure efficient workflows and streamlined data processing.


Requirements:
-------------

- [docker](https://docs.docker.com/desktop/>)

Getting Started
---------------

1. **Clone the repo** :

```
$ git clone https://github.com/g1039/adsum.git
$ cd adsum
```

2. **Start docker** : Ensure Docker is running, then start the services:

```
$ docker compose up
```

3. **Start Airflow** :

a. Open a new terminal & list running containers
```
docker ps
```

b. Create an Airflow Admin User
```
$ docker exec -it <container_name> airflow users create --username foo --firstname foo --lastname bob --role Admin --email 
```

c. Add PostgreSQL Connection to Airflow
```
$ docker exec -it <container_name> airflow connections add 'etl_task' \
    --conn-type 'postgres' \
    --conn-host 'postgres' \
    --conn-schema 'opentax' \
    --conn-login ‘foo’ \
    --conn-password 'mypassword' \
    --conn-port '5432'
```

d. Start Airflow Scheduler
```
$ docker exec -it <container_name> airflow scheduler
```

4. **Access the Services** :

- **FastAPI** : http://localhost:8000/ 
- **Airflow UI** : http://localhost:8080/


Database Query Optimization
---------------------------

When working with big data in Python, be mindful of memory usage, processing speed, and file handling. Avoid loading everything into memory at once. Use efficient tools like Pandas and Numpy, process data in chunks, optimise database queries, leverage parallel processing, and consider distributed computing for extremely large datasets.
