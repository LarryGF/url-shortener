from typing import Optional
from fastapi import FastAPI, Response, status, Request
from fastapi.responses import RedirectResponse
import hashlib
import base64
import json
from pathlib import Path
from mydb import JsonDB as Database

app = FastAPI()
DATA_PATH = 'data/urls.json'

# Using the urls.json file was an easy way to persist state between deployments without having to deploy a DB or any additional code, the R/W operations
# might be a little taxing on performance, so for a second iteration it wouldbe good to use a DB (for this specific scenario MongoDB should work fine)
if not Path(DATA_PATH).exists():
    Path('data').mkdir(exist_ok=True)
    with open(DATA_PATH, 'w') as file:
        json.dump({}, file)


def create_short_link(original_url: str):
    to_encode = original_url
    b64_encoded_str = base64.urlsafe_b64encode(
        hashlib.sha256(to_encode.encode()).digest()).decode()
    return b64_encoded_str[:10]


def lookup(identifier: str):
    with Database(DATA_PATH) as db:
        return db.lookup(identifier, default=None)


@app.get("/api/v1/lookup/{identifier:str}")
def get_url(response: Response, identifier: Optional[str] = None):
    """
        Looks an specific identifier in the _urls_ "database".
        - Identifier: type String

        If the identifier does not exist it will return an error message with *code 400*

    """
    if identifier:
        url = lookup(identifier)
        if url:
            return url
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST

            return {
                'Message': 'That identifier does not exist in our database'
            }
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'Message': 'You need to pass an identifier'
        }


@app.get("/api/v1/lookup/")
def get_url_root(response: Response):
    """
        This is to cover for the case where an identifier does not get passed to the _path_

        If no identifier is passed it will return an error message with *code 400*

    """
    response.status_code = status.HTTP_400_BAD_REQUEST
    return {
        'Message': 'You need to pass an identifier'
    }


@app.post("/api/v1/shorten/{url:path}")
def read_item(response: Response, request: Request, url: Optional[str] = None):
    """
        Shortens the given URL, in the case where no protocol is passed it will default to _https_

        If no URL is passed, it will return an error message with *code 400*
    """
    if url:
        with Database(DATA_PATH) as db:
            if url.split(':')[0].startswith('http'):
                short = create_short_link(url)
                if db.exist(short):
                    return {
                        'Message': 'We already have that url in the database'
                    }
                else:
                    db.set(short, url)

                    response.status_code = status.HTTP_200_OK
                    # This is commented so the reply complies with the requirement, but I consider this gives further insight on what is happening
                    # return {"original": url, "shortened": short, "message": 'Succesfully shortened'}
                    return f'{request.base_url}{short}'
            else:
                short = create_short_link(f'https://{url}')

                db.set(short, url)

                response.status_code = status.HTTP_200_OK
                # This is commented so the reply complies with the requirement, but I consider this gives further insight on what is happening
                # return {"original": url, "shortened": short, "message": 'Provided url did not contain protocol, defaulting to https'}
                return f'{request.base_url}{short}'

    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'Message': 'You need to pass an url to shorten'
        }


@app.get("/{identifier}")
def redirect(response: Response, identifier: Optional[str] = None):
    """
        If an identifier is provided it will redirect the user to the stored URL

        If the identifier does not exist it will return an error message with *code 400*

    """
    if identifier:
        url = lookup(identifier)
        if url:
            return RedirectResponse(url=url)

        else:
            response.status_code = status.HTTP_400_BAD_REQUEST

            return {
                'Message': 'That identifier does not exist in our database'
            }
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'Message': 'You need to pass an identifier'
        }


@app.get("/api/v1/all")
def get_all():
    """
        Returns all _identifier:url_ pairs in the "database"

        It is included mostly for debugging purposes.
    """
    with Database(DATA_PATH) as db:
        internal_url_db = db._db
    return internal_url_db


@app.get("/")
def get_root(request: Request):
    return f'Go to {request.base_url}docs for the documentation'
