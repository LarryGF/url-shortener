from typing import Optional
from fastapi import FastAPI, Response, status, Path
from fastapi.responses import RedirectResponse
import hashlib
import base64
import json
from pathlib import Path
app = FastAPI()

if not Path('/app/urls.json').exists():
    with open('/app/urls.json', 'w') as file:
        json.dump({}, file)


def create_short_link(original_url: str):
    to_encode = original_url
    b64_encoded_str = base64.urlsafe_b64encode(
        hashlib.sha256(to_encode.encode()).digest()).decode()
    return b64_encoded_str[:10]


def lookup(identifier: str):
    with open('/app/urls.json') as file:
        internal_url_db = json.load(file)
    if identifier in internal_url_db:
        return internal_url_db.get(identifier)
    else:
        return None


@app.get("/api/v1/lookup/{identifier:str}")
def get_url(response: Response, identifier: Optional[str] = None):
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


@app.post("/api/v1/shorten/{url:path}")
def read_item(response: Response, url: Optional[str] = None):
    if url:
        with open('/app/urls.json') as file:
            internal_url_db = json.load(file)
        if url.split(':')[0].startswith('http'):
            short = create_short_link(url)
            internal_url_db[short] = url
            with open('/app/urls.json', 'w') as file:
                json.dump(internal_url_db, file)

            response.status_code = status.HTTP_200_OK
            return {"original": url, "shortened": short, "message": 'Succesfully shortened'}
        else:
            short = create_short_link(f'https://{url}')
            internal_url_db[short] = url
            with open('/app/urls.json', 'w') as file:
                json.dump(internal_url_db, file)
            response.status_code = status.HTTP_200_OK
            return {"original": url, "shortened": short, "message": 'Provided url did not contain protocol, defaulting to https'}
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'Message': 'You need to pass an url to shorten'
        }


@app.get("/{identifier}")
def redirect(response: Response, identifier: Optional[str] = None):
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
    with open('/app/urls.json') as file:
        internal_url_db = json.load(file)
    return internal_url_db
