#!/usr/bin/env python3

import os
import json
import pathlib
import requests
import subprocess
from datetime import datetime

h1_username = "vavkamil"
h1_api_token = os.environ.get("HACKERONE_TOKEN")

handle = "security"


def check_scope(handle):
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }

    res = requests.get(
        f"https://api.hackerone.com/v1/hackers/programs/{handle}",
        auth=(h1_username, h1_api_token),
        headers=headers,
    )

    json_obj = res.json()
    json_scope = json_obj["relationships"]["structured_scopes"]["data"]

    return json_scope


def parse_scope(json_scope):
    in_scope_hosts = []
    in_scope_wildcards = []
    out_of_scope = []

    for scope_item in json_scope:
        if scope_item["attributes"]["eligible_for_submission"]:
            if scope_item["attributes"]["asset_type"] == "URL":
                if scope_item["attributes"]["asset_identifier"].startswith("*."):
                    in_scope_wildcards.append(
                        scope_item["attributes"]["asset_identifier"]
                    )
                else:
                    in_scope_hosts.append(scope_item["attributes"]["asset_identifier"])
                # print(scope_item["attributes"]["asset_identifier"])
        else:
            out_of_scope.append(scope_item["attributes"]["asset_identifier"])
            # print(scope_item["attributes"]["asset_identifier"])

    return (in_scope_wildcards, in_scope_hosts, out_of_scope)


def get_subdomains(in_scope_hosts, in_scope_wildcards):
    for wildcard in in_scope_wildcards:
        sudomains = subprocess.Popen(
            f"chaos -d {wildcard[2:]} -silent", shell=True, stdout=subprocess.PIPE
        ).stdout.read()
        sudomains_array = sudomains.decode("utf-8").rstrip().split("\n")

        in_scope_hosts = in_scope_hosts + sudomains_array

    return in_scope_hosts


def remove_out_of_scope(in_scope_hosts, out_of_scope):
    in_scope = list(set(in_scope_hosts) - set(out_of_scope))

    return in_scope


def get_date():
    # datetime object containing current date and time
    now = datetime.now()

    # yy-mm-dd
    date = now.strftime("%y-%m-%d")

    return date


def save_output(output_path, output_file, output):
    p = pathlib.Path(output_path)
    p.mkdir(parents=True, exist_ok=True)
    file = pathlib.Path(f"{output_path}/{output_file}")
    file.write_text("\n".join(output))

    return 1


def check_httpx(input_path, input_file):

    httpx_input = f"{input_path}{input_file}"
    output_file = input_file.replace("chaos_", "httpx_")
    httpx_output = f"{input_path}{output_file}"

    subprocess.Popen(
        f"httpx -l {httpx_input} -silent -random-agent -o {httpx_output}",
        shell=True,
        stdout=subprocess.PIPE,
    ).stdout.read()

    num_lines = sum(1 for line in open(httpx_output))

    return httpx_output, num_lines


def nuclei_scan(input_file):

    output_file = input_file.replace("httpx_", "nuclei_")

    subprocess.Popen(
        f"nuclei -silent -l {input_file} -config config_nuclei.yaml -o {output_file} | notify -silent",
        shell=True,
        stdout=subprocess.PIPE,
    ).stdout.read()

    num_findings = sum(1 for line in open(output_file))

    return output_file, num_findings


def main():
    print("[ HackerOne 2 Nuclei ]\n")

    print(f"[i] Checking scope for: {handle}")

    json_scope = check_scope(handle)

    print("[i] Parsing scope items\n")

    (in_scope_wildcards, in_scope_hosts, out_of_scope) = parse_scope(json_scope)

    print(f"[i] Wildcards in scope:\t {len(in_scope_wildcards)}")
    print(f"[i] Hosts in scope:\t {len(in_scope_hosts)}")
    print(f"[i] Hosts out of scope:\t {len(out_of_scope)}\n")

    print(f"[i] Checking subdomains with chaos\n")

    in_scope_hosts = get_subdomains(in_scope_hosts, in_scope_wildcards)

    print(f"[i] Hosts in scope:\t {len(in_scope_hosts)}")
    print(f"[i] Hosts out of scope:\t {len(out_of_scope)}\n")

    print("[i] Removing out of scope items\n")

    in_scope = remove_out_of_scope(in_scope_hosts, out_of_scope)

    print(f"[i] Unique hosts in scope: {len(in_scope)}\n")

    date = get_date()
    output_path = f"targets/{handle}/"
    output_file = f"chaos_{handle}_{date}.txt"

    print(f"[i] Saving hosts to: {output_path}{output_file}\n")

    save_output(output_path, output_file, in_scope)

    print("[i] Resolving subdomains with httpx")

    (output_httpx, lines_httpx) = check_httpx(output_path, output_file)

    print(f"[i] Output saved to: {output_httpx}\n")

    print(f"[i] Number of live targets: {lines_httpx}\n")

    print(f"[i] Scannign targets with Nuclei")

    (output_nuclei, nuclei_findings) = nuclei_scan(output_httpx)

    print(f"[i] Output saved to: {output_nuclei}\n")

    print(f"[i] Vulnerabilities found: {nuclei_findings}\n")


if __name__ == "__main__":
    main()
