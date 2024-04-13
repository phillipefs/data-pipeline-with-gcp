from fastapi import FastAPI, HTTPException
import requests
from google.cloud import storage
from pydantic import BaseModel

app = FastAPI()

class Params(BaseModel):
    url: str
    bucket_name: str
    output_file_prefix: str


@app.get('/')
async def read_root():
    return {"Hello":"World"}

def get_data(remote_url):
    response = requests.get(remote_url)
    return response

async def download_data_fuel(params: Params):
    try:
        data = get_data(params.url)

        return {
            "Status":"Ok",
            "Bucket_name":params.bucket_name,
            "url":params.url
        }

    except Exception as e:
        raise HTTPException(status_code=e.code, detail = f"{e}")