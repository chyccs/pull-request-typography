import requests
from django.shortcuts import resolve_url

from hwr_analyzer.celery import app
from hwr_analyzer.settings import HWR_API_BASE_URL
from services.restful.documents.request_examples import RECOGNIZE_STROKES


def post(path, data):
    return requests.post(url=f'{HWR_API_BASE_URL}{path}',
                         headers={
                             'Content-Type': 'application/json',
                             'User': 'health_checker',
                             'Await': 'true',
                         },
                         json=data)


@app.task
def try_recognize_to_health_check():
    res = post(resolve_url("recognize_strokes"), data=RECOGNIZE_STROKES)
    res.raise_for_status()
    label = res.json()['contents'][0]['iink']['label']
    assert label == '치약'  # skipcq: BAN-B101
