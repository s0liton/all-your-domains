import asyncio
import json

from okta_jwt_verifier import AccessTokenVerifier, IDTokenVerifier

try:
    loop = asyncio.get_event_loop()
except RuntimeError as ex:
    if "There is no current event loop in thread" in str(ex):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)


def access_token_valid(token, issuer, audience):
    verifier = AccessTokenVerifier(issuer=issuer, audience=audience)
    try:
        loop.run_until_complete(verifier.verify(token))
        return True
    except Exception:
        return False


def id_token_valid(token, issuer, client_id, nonce, audience):
    verifier = IDTokenVerifier(issuer=issuer, client_id=client_id, audience=audience)
    try:
        loop.run_until_complete(verifier.verify(token, nonce=nonce))
        return True
    except Exception:
        return False


def get_config(fname='./client.json'):
    confi = None
    with open(fname) as f:
        config = json.load(f)
    return config


configuration = get_config()
