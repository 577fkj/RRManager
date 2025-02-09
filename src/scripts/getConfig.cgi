#!/usr/bin/python

import os
import json
import sys
import subprocess

from pathlib import Path
path_root = Path(__file__).parents[1]
sys.path.append(str(path_root)+'/libs')

import libs.yaml as yaml
print("Content-type: application/json\n")

#Function to read user configuration from a YAML file
def read_user_config():
    try:
        with open('/mnt/p1/user-config.yml', 'r') as file:
            return yaml.safe_load(file)  # Load and parse the YAML file
    except IOError as e:
        return f"Error reading user-config.yml: {e}"
    except e:
        return "{}"
    
def read_rrmanager_config(file_path):
    try:
        config = {}
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=')
                    config[key.strip()] = value.strip().replace('"', '')
        return config
    except IOError as e:
        return f"Error reading user-config.yml: {e}"
    except e:
        return "{}"

def read_rrmanager_privilege(file_path):
    try:
        with open(file_path, 'r') as file:
            # Parse JSON data directly into a Python dictionary
            config = json.load(file)
        return config
    except IOError as e:
        # Handle I/O errors (e.g., file not found)
        return f"Error reading {file_path}: {e}"
    except json.JSONDecodeError as e:
        # Handle errors caused by incorrect JSON formatting
        return f"Error decoding JSON from {file_path}: {e}"
    except Exception as e:
        # Generic exception handler for any other unforeseen errors
        return "{}"

# implement check that the file exists and read it to get progress and if exists return status "awaiting_reboot". If not return status "healthy"
def read_rr_awaiting_update(fileName):
    file_path = os.path.join('/tmp', fileName)
    try:
        with open(file_path, 'r') as file:
            return "awaiting_reboot"
    except IOError as e:
        return "healthy"
    except e:
        return "healthy"

def callMountLoaderScript(action):
    process = subprocess.run(['sudo','/usr/bin/rr-loaderdisk.sh', action],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

def mountLoader():
    callMountLoaderScript('mountLoaderDisk')

def unmountLoader():
    callMountLoaderScript('unmountLoaderDisk')
# Authenticate the user
f = os.popen('/usr/syno/synoman/webman/modules/authenticate.cgi', 'r')
user = f.read().strip()

response = {}

if len(user) > 0:
    mountLoader()
    response["status"] = "authenticated"
    response["user"] = user

    # Read and add rr_version to the response
    rrData = read_rrmanager_config('/usr/rr/VERSION')
    response["rr_version"] = rrData.get('LOADERVERSION')
    # response["rr_data"] = rrData
    response["user_config"] = read_user_config()
    response["rr_manager_config"] = read_rrmanager_config('/var/packages/rr-manager/target/app/config.txt')
    response["rr_manager_privilege"] = read_rrmanager_privilege('/var/packages/rr-manager/conf/privilege')
    # response["rr_manager_resource"] = read_rrmanager_privilege('/var/packages/rr-manager/conf/resource')
    response["rr_health"] = read_rr_awaiting_update(response["rr_manager_config"].get("RR_UPDATE_PROGRESS_FILE"))
    unmountLoader()
else:
    response["status"] = "not authenticated"

# Print the JSON response
print(json.dumps(response))
