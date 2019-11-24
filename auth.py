import json
import logging
import os
import sys
import adal
from datetime import datetime
import subprocess

def turn_on_logging():
    logging.basicConfig(level=logging.DEBUG)

parameters_file = (sys.argv[1] if len(sys.argv) == 2 else os.environ.get('ADAL_PARAMETERS_FILE'))

if parameters_file:
    with open(parameters_file, 'r') as f:
        parameters = f.read()
    sample_parameters = json.loads(parameters)
else:
    raise ValueError('Please provide parameter file with account information.')

authority_url = (sample_parameters['AuthorityHostUrl'] + '/' + sample_parameters['Tenant'])

# uncomment for verbose logging
turn_on_logging()

context = adal.AuthenticationContext(
    authority_url, api_version=1.0,
    )

# fetch token using adal
token = context.acquire_token_with_username_password(
    sample_parameters['Resource'],
    sample_parameters['UserName'],
    sample_parameters['Password'],
    sample_parameters['ClientId'])

# use kubetl to append token values to config
subprocess.run(['kubectl', \
    'config', \
    'set-credentials', \
    'clusterUser_' + sample_parameters["RGName"] + '_' + sample_parameters["ClusterName"], \
    '--auth-provider-arg=expires-on=' + str(int(datetime.timestamp(datetime.strptime(token["expiresOn"],"%Y-%m-%d %H:%M:%S.%f")))), \
    '--auth-provider-arg=expires-in=' + str(token["expiresIn"]), \
    '--auth-provider-arg=access-token=' + token["accessToken"], \
    '--auth-provider-arg=refresh-token=' + token["refreshToken"]])
