import logging
from time import sleep
import os.path

from edge.config import YADISK, YADISK_ROOT_PATH

import requests
from yadisk.exceptions import YaDiskError
import boto3


logger = logging.getLogger()


def upload_to_yadisk(url, name, folder, meta=None):
    file_path = os.path.join(YADISK_ROOT_PATH, folder, name)

    op_data = YADISK.upload_url(url, file_path)

    while True:

        status = getattr(requests, op_data.method.lower(), 'get')(
            op_data.href,
            headers={'Authorization': 'OAuth ' + YADISK.token},
        ).json().get('status')

        if status == 'success':
            break

        sleep(0.5)

    if meta is not None:
        YADISK.patch(file_path, meta)

    return YADISK.get_meta(file_path)


def delete_from_yadisk(name, folder):
    file_path = os.path.join(YADISK_ROOT_PATH, folder, name)

    try:
        YADISK.remove(file_path)
    except YaDiskError as exc:
        logger.error(exc.__class__.__name__ + ' occurred while deleting a file from YaDisk')
