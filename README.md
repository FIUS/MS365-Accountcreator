# MS365-Accountcreator
A small python flask server to allow users to sign up to a Microsoft Azure Tenant using the Microsoft Graph API.

[![Open source](https://img.shields.io/badge/OpenSource-github-green.svg)](https://github.com/FIUS/MS365-Accountcreator)
[![GitHub license](https://img.shields.io/github/license/FIUS/MS365-Accountcreator.svg)](https://github.com/FIUS/MS365-Accountcreator/blob/master/LICENSE)
[![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/fius/ms365-accountcreator)](https://hub.docker.com/r/fius/ms365-accountcreator)

## Installation
This project is a flask app, which should be deployed using a wsgi server.

### Manual
See the flask wsgi documentation for instrcutions. \
The required packages need to be installed: \
`poetry install` \
The name of the module is `ms365_accountcreator`.
The name of the callable is `APP`. \
Please make sure the environment variable `JWT_SECRET_KEY` is set to something sensible or the `JWT_SECRET_KEY` is configured in the config.

### Docker
This project can be deployed using docker with the following command:
`docker run -p 80:80 -e JWT_SECRET_KEY="put a random secret here" fius/ms365-accountcreator`

During the first run you need to create the db with `docker exec <container name> pipenv run flask create_db`

You can mount a host directory into `/app-mnt` to have the database persistent.
You can alse create the file `ms365-accountcreator.conf` in that directory to configure the application.

Some defaults are different when deployed using a container than otherwise. See [docker](docker) for the exact changes.

The container is based on [tiangolo/uwsgi-nginx-flask-docker](https://github.com/tiangolo/uwsgi-nginx-flask-docker). See the documentation there for finetuning.

### Reverseproxy
This project can run behind a reverse proxy with the help of [ProxyFix](https://werkzeug.palletsprojects.com/en/1.0.x/middleware/proxy_fix/). \
ProxyFix uses the headers set by the reverseproxy to adjust the wsgi environment accordingly. For more info visit their website. \
The number of trusted reverse proxies can be configured using the [REVERSE_PROXY_COUNT](#reverse_proxy_count) config or environment variable.

### Custom UI texts
If you want to deploy this project but use your own translations, follow the steps detailed in [Changing translations](#changing-translations). \
Note: You need to setup the development environment as detailed in [Development](#development) for this.

Then just replace the existing `messages.mo` files with the ones you generated.

For deployment with a docker container this may be done by mounting an external directory over `/app/translations`.

## Configuration
The confuration is done through flask. \
The configuration can contain configuration options for flask itself, the various flask extensions, the database engine (called SQLALCHEMY) and for this project itself.\
For the flask and SQLALCHEMY configuration please check the respective documentation ([flask](https://flask.palletsprojects.com/en/1.1.x/config/#builtin-configuration-values), [SQLALCHEMY](https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/), ...)\
For the defaults of any variables and a complete list of variables introduced by this project see [config.py](ms365_accountcreator/config.py).

The configuration files must be actual Python files, where values are asigned to constants.

The app will load the config in this order:
 * The config variabel `MODE` is read from the environment.
   * Supported values are `PRODUCTION`, `DEBUG`, `TEST`
   * If there is no such environment variable `PRODUCTION` is assumed
 * Based on the mode the default values are read from [config.py](ms365_accountcreator/config.py).
 * The file `/etc/ms365_accountcreator.conf` is read.
 * The file `instance/ms365_accountcreator.conf` relative to the current working directory is read.
 * If the environment variable `CONFIG_FILE` is set, the file specified in that variable is read
 * The following config variables are read directly from the environment:
   * `SQLALCHEMY_DATABASE_URI`
   * `JWT_SECRET_KEY`
   * `REVERSE_PROXY_COUNT`

Later loads overwrite values from previous loads.
Here are an explanation of some of the most important environment variables

### General
Some important general variables
#### `SQLALCHEMY_DATABASE_URI`
The URI for the database. \
See [the flask-sqlalchemy doku](https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/#connection-uri-format) for more info.

#### `REVERSE_PROXY_COUNT`
The number of reverseproxies to trust. \
This is used to set each of the options for number of `X-Forward-**` headers ProxyFix should trust. \
See [the ProxyFix doku](https://werkzeug.palletsprojects.com/en/1.0.x/middleware/proxy_fix/) for more info.

#### `LOGGING_CONFIGS`
This is a list of json files to configure [python logging](https://docs.python.org/3/library/logging.config.html). They are merged into one big dict and then loaded as the pyhton logging configuration. For an example see [the default logging config](logging_config.json)

#### `DEBUG_DONT_CONNECT_TO_API`
This disables the connection to the graph api when set to `True`.

#### `GENERATED_PASSWORD_BYTES`
The number of bytes generated for the passwords. \
The generated bytes will be url encoded and appended to a static prefix. \
The prefix is to prevent Micrsoft from rejecting the password because requirements are not fullfilled.

#### `EMAIL_ADDRESS_FILTER`
A regular expression to filter what mails are allowed. \
Should be regex compatible with https://docs.python.org/3/library/re.html as well as https://www.w3schools.com/TAGS/att_input_pattern.asp

#### `SUPPORT_EMAIL`
The email address the frontend shows as the support address.

### Graph API Configuration
This project uses the Micrsoft Graph API to actually create the users.
Some configuration is neccessary for it, especially for the authentication.

To authenticate against the Graph API, OAuth2 with a client certificate is used.
For that an app needs to be registered with your Microsoft Azure Active Directory Tenant. \
To do this go to [the azure portal](portal.azure.com) and naviagte to `Azure Active Directory` (in the left sidepanel) and then to `App Registrations`.
There create a new Registration with a fitting name, and support for Accounts in this organizational directory only (Single tenant) and without a redirect URI. \
Then you should be taken to the Overview page of the new app.
Here you can see the `Application (client) ID`, which you need to put in the config as `AUTH_CLIENT_ID`. \
You should also see the `Directory (tenant) ID`, which needs to be appended to `https://login.microsoftonline.com/` and the result put in the config as `AUTH_AUTHORITY`. \
Now generate the key pair for authentication using [openssl](https://www.openssl.org/):
``` bash
# Generate key
openssl genrsa -out ms365AccountCreator.key 2048
# Generate certificate request, fill out as you see fit
openssl req -new -key ms365AccountCreator.key -out ms365AccountCreator.csr
# Generate certificate
openssl x509 -req -days 3650 -in ms365AccountCreator.csr -signkey ms365AccountCreator.key -out ms365AccountCreator.crt
```
Upload the `ms365AccountCreator.crt` file to the azure portal under `Certificates and Secrets` and copy the generated thumbprint to the config as `AUTH_PUBKEY_THUMBPRINT`. \
For more details see [this example](https://github.com/Azure-Samples/ms-identity-python-daemon/tree/master/2-Call-MsGraph-WithCertificate).

#### `GRAPH_API_AUTH_AUTHORITY`
The authority URL of your Azure AD tenant. Prepend `https://login.microsoftonline.com/` to your `Directory (tenant) ID`.
Alternatively: Go to tab endpoints of the app, copy OAuth 2.0 authorization endpoint (v2) and remove everything after the UUID part.

#### `GRAPH_API_AUTH_CLIENT_ID`
The id of the app registered with Azure AD. See Overview page of the app (`Application (client) ID`).

#### `GRAPH_API_AUTH_PUBKEY_THUMBPRINT`
The thumbprint generated by Azure AD when you upload the public key of your keypair.

#### `GRAPH_API_AUTH_PRIVKEY_PATH`
The path to the private key of your keypair.

#### `GRAPH_API_USER_MAIL_DOMAIN`
The mail domain to use for the created users.
Example: `example.onmicrosoft.com`

#### `GRAPH_API_GROUPS_FOR_NEW_USERS`
A list of uids of groups to which to new users should be added.\
These can be obtained in the azure portal under groups.

### Mailserver configuration
The generated password will be sent to the users via mail. \
For this to work we need access to a smtp server. \
That can be configured with the following variables.

#### `MAIL_SERVER_HOST`
The hostname / ip address of the smtp server.

#### `MAIL_SERVER_PORT`
The port of the smtp server.

#### `MAIL_SERVER_SSL`
Whether to use a SSL encrypted connection. \
Attention: don't confuse with `MAIL_SERVER_STARTTLS`.

#### `MAIL_SERVER_STARTTLS`
Whether to use the STARTTLS protocol to upgrade the connection to ecnrypted once it has been established. \
Attention: don't confuse with `MAIL_SERVER_SSL`

#### `MAIL_SERVER_LOGIN`
Whether to login to the smtp server. \
If this is `False`, the variables `MAIL_SERVER_USER` and `MAIL_SERVER_PW` are not used.

#### `MAIL_SERVER_USER`
The username to login in to the smtp server. \
Not used if `MAIL_SERVER_LOGIN` is `False`

#### `MAIL_SERVER_PW`
The password to login in to the smtp server. \
Not used if `MAIL_SERVER_LOGIN` is `False`

#### `MAIL_SENDING_ADDRESS`
The address to set as sending address. \
Make sure the user you logged in with is allowed to use this address.

## Development
Here are some steps on how to setup the development environment for this project.

### Getting the sources
Download or clone the sources from github.com/FIUS/MS365-Accountcreator

### Prerequesits
- python >= 3.7
- poetry [for that python version]

### Preparations:
```shell
# Setup pipenv and install dependencies
poetry install
#pipenv install #when not wanting dev depedencies.
```

### Start server for development:

First start:
```shell
export FLASK_APP=ms365_accountcreator
export FLASK_DEBUG=1  # to enable autoreload
export MODE=debug
# export MODE=production
# export MODE=test

poetry run babel-compile

poetry run flask create_db

# start server
poetry run flask run
```

Subsequent starts:
```shell
poetry run flask run
```

### Shell.nix

Instead of the previous step the file shell.nix can be used with the program nix-shell:
```shell
nix-shell
```
Then everything is set up for you and you only need to start the server:
```shell
flask run
```

### Managing translations
The translations are used by [flask-babel](https://flask-babel.tkte.ch/) to be able to show the user translated texts. It uses [babel](http://babel.pocoo.org/en/latest/) and [gettext](https://docs.python.org/3/library/gettext.html) under the hood.

#### Changing translations
To change a translation go to [translations](ms365_accountcreator/translations/), find the langauge to change, go to `LC_MESSAGES` and edit `messages.po`.
After editing `messages.po` run the command `poetry run pybabel compile -d ms365_accountcreator/translations` to recompile the translations, so the updated version can be used.

#### Adding translations
When you want to add new texts to be translated, just use the `gettext()` method with an appropriate argument and run `poetry run pybabel extract -F babel.cfg -o messages.pot .` and `poetry run pybabel update -i messages.pot -d ms365_accountcreator/translations`. This will update the `messages.po` files for all langauges. Then follow the steps in [Changing translations](#changing-translations) to add a translation for the new text to each language.
