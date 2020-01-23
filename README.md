# Dispatcher
This service uses AssetStorm, converters and templaters 
to convert article assets.

## Development Setup
This repo makes heavy use of other AssetStorm microservices.
These are meant to be run in separate containers. The
development setup launches the other microservices as a bunch
of contains but not the Dispatcher itself.

Start the auxiliary containers for the development setup with:
```shell script
docker-compose -f docker-compose_development.yml up
``` 

After the contains are running start the tests with:
```shell script
python -m pytest
```

## Production Setup
For production all microservices run in containers. A working 
setup for that is configured in `docker-compose.yml`. For your 
convenience the repo contains a start script:
```shell script
./launch_containers_production.sh
``` 