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
docker-compose -f docker-compose_development.yml pull
docker-compose -f docker-compose_development.yml up
``` 

After the containers are running start the tests from `src/` with:
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

The container can be configured with the following environment
variables:
 - `ASSETSTORM_URL` - default: `http://127.0.0.1:8081`
 - `MARKDOWN2ASSETSTORM_URL` - default: `http://127.0.0.1:8082`
 - `ASSETSTORM2TEMPLATE_URL` - default: `http://127.0.0.1:8083`
