from typing import Optional
from fastapi import FastAPI, Response, status, Path
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, BaseSettings
import hashlib
import base64
import json
from pathlib import Path

app = FastAPI()

if not Path('/app/urls.json').exists():
    with open('/app/urls.json', 'w')as file:
        json.dump({}, file)
    internal_url_db = {}
else:
    with open('/app/urls.json')as file:
        internal_url_db = json.load(file)


class Settings(BaseSettings):
    user: Optional[str] = "mysql"
    password: Optional[str] = "12345678"
    hostname: Optional[str] = "mysql"
    db: Optional[str] = "db"


settings = Settings()


def create_short_link(original_url: str):
    to_encode = original_url
    b64_encoded_str = base64.urlsafe_b64encode(
        hashlib.sha256(to_encode.encode()).digest()).decode()
    return b64_encoded_str[:10]


def lookup(identifier: str):
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
        if url.split(':')[0].startswith('http'):
            short = create_short_link(url)
            internal_url_db.setdefault(short, url)
            with open('/app/urls.json', 'w') as file:
                json.dump(internal_url_db, file)
            # result = mycol.insert_one(
            #     {"original": url, "shortened": short, "message": 'Succesfully shortened'})
            # print(result)
            response.status_code = status.HTTP_200_OK
            return {"original": url, "shortened": short, "message": 'Succesfully shortened'}
        else:
            short = create_short_link(f'https://{url}')
            internal_url_db.setdefault(short, url)
            with open('/app/urls.json', 'w') as file:
                json.dump(internal_url_db, file)
            # result = mycol.insert_one(
            #     {"original": url, "shortened": short, "message": 'Succesfully shortened'})
            # print(result)
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
    return internal_url_db
