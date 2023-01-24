from base64 import b64encode
from typing import (
    List,
    Optional,
)

import jsons
import requests

from domain.ndp.serializers import (
    Ink,
    User,
    UserNote,
    UserPage,
)
from hwr_analyzer.settings import (
    NDP_AUTH_BASE_URL,
    NDP_CLIENT_ID,
    NDP_CLIENT_SECRET,
    NDP_INK_BASE_URL,
    NDP_INSTROSPECT_URI,
)


def verify_credentials():  # pragma: no cover
    request_body = {
        "client_id": NDP_CLIENT_ID,
        "client_secret": NDP_CLIENT_SECRET,
    }

    res = requests.post(url=f'{NDP_AUTH_BASE_URL}/oauth/v2/credentials/verify',
                        data=request_body)
    return res.json()


def _acquire_auth_token() -> str:
    request_body = {
        "grant_type": 'client_credentials',
        "authority": 'userdata.read userdata.write profile.read profile.write ink.read ink.write',
    }

    headers = {
        'Authorization': 'Basic ' + b64encode(f'{NDP_CLIENT_ID}:{NDP_CLIENT_SECRET}'.encode('ascii')).decode('ascii'),
    }

    res = requests.post(url=f'{NDP_AUTH_BASE_URL}/oauth/v2/token',
                        headers=headers,
                        data=request_body)
    res.raise_for_status()
    return res.json().get("access_token")


def _get_authenticated_header() -> dict:
    return {
        'Authorization': f'Bearer {_acquire_auth_token()}',
    }


def fetch_entire_users(client_id) -> List[str]:
    res = requests.get(
        url=f'{NDP_AUTH_BASE_URL}/user/v2/users/profiles?clientId={client_id}',
        headers=_get_authenticated_header())
    res.raise_for_status()
    users = jsons.load(res.json(), cls=List[User], key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE)
    return [user.id for user in users]


def fetch_instrospect_token(token):
    request_body = {
        "token": token,
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    res = requests.post(url=NDP_INSTROSPECT_URI,
                        headers=headers,
                        data=request_body)
    res.raise_for_status()
    return res


def _fetch_strokes(uri: str):
    res = requests.get(uri, headers=_get_authenticated_header())
    res.raise_for_status()
    return jsons.load(res.json(), cls=List[Ink], key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE)


def fetch_strokes_by_note(user_id: str,
                          query_type: str,
                          note_uuid: str,
                          page_number: Optional[int] = None):
    uri = f'{NDP_INK_BASE_URL}/inkstore/v2/stroke/{user_id}/note/{note_uuid}/page?queryType={query_type}'

    if note_uuid and page_number:
        uri += f'&pageNumber={page_number}'

    return _fetch_strokes(uri)


def fetch_strokes_by_page(user_id: str,
                          query_type: str,
                          page_uuid: Optional[str] = None):
    uri = f'{NDP_INK_BASE_URL}/inkstore/v2/stroke/{user_id}/page/{page_uuid}?queryType={query_type}'
    return _fetch_strokes(uri)


def fetch_notes(user_id: str):  # pragma: no cover
    res = requests.get(url=f'{NDP_AUTH_BASE_URL}/user/v2/{user_id}/notes?digital=ALL',
                       headers=_get_authenticated_header())
    res.raise_for_status()
    return jsons.load(res.json(), cls=List[UserNote], key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE)


def fetch_pages(user_id: str, note_uuid: str):  # pragma: no cover
    res = requests.get(url=f'{NDP_AUTH_BASE_URL}/user/v2/{user_id}/notes/{note_uuid}/pages?digital=ALL',
                       headers=_get_authenticated_header())
    res.raise_for_status()
    return jsons.load(res.json(), cls=List[UserPage], key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE)
