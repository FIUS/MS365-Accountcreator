# MS365-Accountcreator
A small python flask server to allow users to create groups and accounts via the Microsoft Graph API

## Prerequesits
- python 3.7
- pipenv [python 3.7]

## Preparations:
```shell

# Setup pipenv and install dependencies
pipenv install --dev
#pipenv install #when not wanting dev depedencies.
```

## Start server for development:

First start:
```shell
source "$(pipenv --venv)/bin/activate"
export FLASK_APP=ms365_accountcreator
export FLASK_DEBUG=1  # to enable autoreload
export MODE=debug
# export MODE=production
# export MODE=test

flask create_db

# start server
flask run
```

Subsequent starts:
```shell
flask run
```

### Shell.nix

Instead the file shell.nix can be used with the program nix-shell:
```shell
nix-shell
```
Then everything is set up for you and you only need to start the server:
```shell
flask run
```

## Installing in a Production Environment
See flask wsgi documentation. The preparations as shown above are required.

### Docker
This project can be deployed using docker with the following command:
`docker run -p 80:80 -e JWT_SECRET_KEY="put a random secret here" fius/ms365-accountcreator`
During the first run you need to create the db with `docker exec ms365test pipenv run flask create_db`
You can mount a host directory into `/app-mnt` to have the database persistent.
You can alse create the file `ms365-accountcreator.conf` in that directory to configure the application.


## Configuration
TODO: Fix for flask config
The configuration must be in the [python configparser](https://docs.python.org/3.6/library/configparser.html) format.
The program will look for config in these locations in this order: 
 * The file specified in the environment variable `MS365AC_CONFIG_FILE`
 * The file specified to the command line with the config option
 * The file `ms365accountcreator.cfg` in the current working directory on execution
The first file found will be used and the other files ignored.
See [ms365accountcreator.cfg.example](ms365accountcreator.cfg.example) for a complete list of settings and their format as well as short descriptions.

### `auth` sections
To authenticate against the Graph API, OAuth2 with a client certificate is used.
For that an app needs to be registered with your Microsoft Azure Active Directory Tenant.
To do this go to [the azure portal](portal.azure.com) and naviagte to `Azure Active Directory` (in the left sidepanel) and then to `App Registrations`.
There create a new Registration with a fitting name, and support for Accounts in this organizational directory only (Single tenant) and without a redirect URI. 
Then you should be taken to the Overview page of the new app.
Here you can see the `Application (client) ID`, which you need to put in the config as `AUTH_CLIENT_ID`.
You should also see the `Directory (tenant) ID`, which needs to be appended to `https://login.microsoftonline.com/` and the result put in the config as `AUTH_AUTHORITY`
Now generate the key pair for authentication using [openssl](https://www.openssl.org/):
``` bash
# Generate key
openssl genrsa -out ms365AccountCreator.key 2048
# Generate certificate request, fill out as you see fit
openssl req -new -key ms365AccountCreator.key -out ms365AccountCreator.csr
# Generate certificate
openssl x509 -req -days 3650 -in ms365AccountCreator.csr -signkey ms365AccountCreator.key -out ms365AccountCreator.crt
```
Upload the `ms365AccountCreator.crt` file to the azure portal under `Certificates and Secrets` and copy the generated thumbprint to the config as `AUTH_PUBKEY_THUMBPRINT`.
For more details see [this example](https://github.com/Azure-Samples/ms-identity-python-daemon/tree/master/2-Call-MsGraph-WithCertificate)
### `AUTH_AUTHORITY`
The authority URL of your Azure AD tenant. Prepend `https://login.microsoftonline.com/` to your `Directory (tenant) ID`.
Alternatively: Go to tab endpoints of the app, copy OAuth 2.0 authorization endpoint (v2) and remove everything after the UUID part.
### `AUTH_CLIENT_ID`
The id of the app registered with Azure AD. See Overview page of the app (`Application (client) ID`).
### `AUTH_PUBKEY_THUMBPRINT`
The thumbprint generated by Azure AD when you upload the public key of your keypair.
### `AUTH_PRIVKEY_PATH`
The path to the private key of your keypair.