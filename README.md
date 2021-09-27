# URL Shortener

This repository includes the code necessary to deploy an _url shortener_ service. 

The _API_ was developed using _Python_, specifically using _fastapi_. The code and the _Dockerfile_ to containerize it are present inside the _api_ folder. 

There is also a _docker-compose_ file to deploy the service.

## Running the application
### Using docker
You just need to run:
```bash
    docker-compose up --build -d
```

This will run the _api_ in the background.
### Using Python
First, you need go to code folder (_api/app_) and then install the dependencies:
```bash
    pip install -r requirements.txt
```
Then you need to run the server by typing:
```bash
    uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

There is no port restriction, port _8080_ was chosen arbitrarily in both cases (in the Python example and in the _docker-compose_)

## Documentation
You can access the _API_ documentation by going to the _/docs_ path, so, assuming you are running it locally with one of the methods above:
> http://localhost:8000/docs

Every endpoint has a description that briefly explains its purpose and there are additional comments in the source code to justify some decisions.
