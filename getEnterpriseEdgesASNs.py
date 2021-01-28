#!/usr/bin/env python3
""" This script retrieves all edge devices from VCO Portal

--

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Peet van de Sande"
__contact__ = "pvandesande@tmhcc.com"
__license__ = "GPLv3"

import requests
import json
import csv

url = "https://vco47-usvi1.velocloud.net/portal/"
headers = {
    'Authorization': 'Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlblV1aWQiOiIyZGMyNjRkNC0wYjMzLTQyZDEtYjg4Yi1jMTU4MjcwM2IzOWMiLCJleHAiOjE2NDA5NDg2NjYwMDAsInV1aWQiOiI5Yzg5NzUzYS03YzFkLTExZTctYjdhYy0wYWJlMzBlYmFlYTgiLCJpYXQiOjE2MDk1ODIzMDB9.nTD0kU-1fyq1sqvuPT5Ua1gMzklIaMnQah59NeX8OqU',
    'Content-Type': 'application/json'
}

def getDevices():
    global url, headers
    payload="""{
        \"jsonrpc\": \"2.0\",
        \"id\": 1,
        \"method\": \"enterprise/getEnterpriseEdges\",
        \"limit\": 0,
        \"_count\": \"false\"
    }"""

    response = json.loads(requests.request("POST", url, headers=headers, data=payload).text)
    devices = response['result']

    output = []
    for device in devices:
        id = ''
        name = ''
        for key, value in device.items():
            if key == "id":
                id = value
            if key == "name":
                name = value
        d = {'id': id, 'name': name}
        output.append(d)

    return output

def getConfig(devices):
    global url, headers
    output = []

    for device in devices:
        payload=(
                """{"""
                    """\"jsonrpc\": \"2.0\","""
                    """\"id\": 1,"""
                    """\"method\": \"edge/getEdgeConfigurationModules\","""
                    """\"params\": {"""
                        f"""\"edgeId\": {device['id']},"""
                        """\"modules\": ["""
                            """\"deviceSettings\""""
                        """]"""
                    """}"""
                """}"""
        )
        response = json.loads(requests.request("POST", url, headers=headers, data=payload).text)
        bgp = response['result']['deviceSettings']['data']['segments'][0]['bgp']
        asn = bgp['ASN']
        if len(bgp['neighbors']) > 0:
            nasn = bgp['neighbors'][0]['neighborAS']
        else:
            nasn = None

        data = {
            'id': device['id'],
            'name': device['name'],
            'asn': asn,
            'nasn': nasn
        }
        output.append(data)

    return output

def write_csv(data, outfile):
    count = 0
    with open(outfile, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        for entry in data:
            if count == 0:
                header = entry.keys()
                writer.writerow(header)
                count = 1
            writer.writerow(entry.values())

def main():
    write_csv(getConfig(getDevices()), 'out.csv')

if __name__ == "__main__":
    main()
