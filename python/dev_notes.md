# Developer Notes : CLI Functions

A collection of notes for the development of the AIGraph4PG project
and not for users of the project.

## Reformatting the Python code with the black library

```
black *.py
black src 
black tests
```

## Docker Builds

```
docker build -f docker\Dockerfile -t cjoakim/aigraph4pg .
docker push cjoakim/aigraph4pg:latest'
```
