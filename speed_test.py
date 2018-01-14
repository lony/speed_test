#!/usr/bin/env python3

import subprocess
import re
import json
import datetime
import logging
import os

from googleapiclient import discovery
from google.oauth2 import service_account

logging.basicConfig(level=logging.INFO)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

CONFIG_FILE_NAME = 'speed_test_conf.json'

def execute_cmd(cmd):
    return subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        ).stdout.decode('utf-8')


def datetime_iso():
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def hosts_get(network_mask):
    cmd_nmap = execute_cmd(['nmap -sn ' + network_mask])
    cmd_nmap_lastline = cmd_nmap.splitlines()[-1]
    cmd_nmap_regex = re.search('addresses \((\d+).*hosts up', cmd_nmap_lastline)
    cmd_nmap_hosts = cmd_nmap_regex.group(1) if cmd_nmap_regex is not None else None
    return cmd_nmap_hosts


def sheet_get_service(sa_credentials_file):
    # https://google-auth.readthedocs.io/en/latest/
    credentials = service_account.Credentials.from_service_account_file(sa_credentials_file).with_scopes(
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )

    service = discovery.build(
            'sheets',
            'v4',
            credentials=credentials,
            cache_discovery=False   # https://stackoverflow.com/questions/40154672/importerror-file-cache-is-unavailable-when-using-python-client-for-google-ser
        )

    return service


def sheet_append(service, sheet_id, sheet_range, data):
    # https://developers.google.com/sheets/api/reference/rest/
    request_data = {
        'values': [
            data
        ]
    }

    result = service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=sheet_range,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            includeValuesInResponse=False,
            body=request_data
        ).execute()

def speedtest_get(server_id):
    # http://www.speedtest.net/

    data = execute_cmd(['speedtest-cli --json --server {}'.format(server_id)])

    try:
        return json.loads(data)
    except ValueError:
        logger.error("Speed test could not be executed for server={}, the output was: \n{}".format(
            server_id,
            data,
        ))
        return None


def data_map_output(datetime_iso, hosts, data):

    if data is None:        
        return [
            datetime_iso,
            hosts,
        ]
    else:
        return [
            datetime_iso,
            hosts,
            data['ping'],
            data['upload'],
            data['bytes_sent'],
            data['download'],
            data['bytes_received'],
        ]

def main():
    try:
        config_data = json.load(open(
                os.path.join(os.path.dirname(__file__), CONFIG_FILE_NAME)
            ))
    except Exception:
        logger.error("No config file provided under name='{}'".format(
            CONFIG_FILE_NAME
        ))
        return

    now = datetime.datetime.now()
    now_iso = datetime_iso()
    hosts = hosts_get(config_data['network_mask']) # Run nmap - host detection
    result_list = {}

    # Run speed tests
    for value in config_data['test_locations']:
        data = speedtest_get(value['id'])
        data_out = data_map_output(now_iso, hosts, data)
        result_list[value['location']] = data_out

    # Save data
    sheet_service = sheet_get_service(
            os.path.join(os.path.dirname(__file__), config_data['sa_credential_file'])
        )
    for key, value in result_list.items():
        sheet_append(sheet_service, config_data['google_sheet_id'], key, value)

    logger.info("Speed test finished after {}\n\n{}".format(
        datetime.datetime.now() - now,
        json.dumps(result_list, indent=4)
    ))


if __name__ == "__main__":
    main()
