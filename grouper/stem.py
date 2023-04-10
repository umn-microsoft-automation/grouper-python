import httpx
from .util import call_grouper
# import json
# from typing import Any
# from collections import namedtuple


class Stem:
    def __init__(self, client: httpx.Client, stem_body: dict[str, str]) -> None:
        self.client = client
        self.displayExtension = stem_body['displayExtension']
        self.extension = stem_body['extension']
        self.displayName = stem_body['displayName']
        self.name = stem_body['name']
        self.description = stem_body['description']
        self.uuid = stem_body['uuid']
        # self.sourceId = user_body['sourceId']
        # self.name = user_body['name']
        # self.id = user_body['id']
        # attrs = {}
        # for n in range(len(subject_attr_names)):
        #     attrs[subject_attr_names[n]] = user_body['attributeValues'][n]
        # self.attributes = attrs
        # self.description = attrs['description']


def get_stem_by_name(
    stem_name: str,
    client: httpx.Client
) -> Stem:
    body = {
        "WsRestFindStemsLiteRequest": {
            "stemName": stem_name,
            "stemQueryFilterType": "FIND_BY_STEM_NAME",
            # "includeGroupDetail": "T",
        }
    }
    r = call_grouper(client, '/stems', body)
    return Stem(client, r['WsFindStemsResults']['stemResults'][0])
