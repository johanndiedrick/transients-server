# Transients Server

Transients server provides simple REST endpoints for uploading and retrieving transients.

The database is powered by MongoDB

## Setting up the server

On a fresh Amazon EC2 server, you will need to setup the following things:

### Setup the Tornado Server

Update the server

`sudo yum update`

Install gcc

`sudo yum install gcc`

Install git

`sudo yum install git`

Clone this repo

`git clone https://github.com/jdiedrick/transients-server`

Change into the server's directory

`cd transients-server/`

If you are setting up the development server, checkout and switch to that branch.

`git checkout -b development origin/development`

### Setting up supervisord

TODO

### Setting up nginx

TODO

## Running the server

### Setup your global variables

Copy the `transients_globals_templates.py` file and create your own `transients_globals.py`

`cp transients_globals_template.py transients_globals.py`

Fill out the required information in that file.

### Install virtualenv

`virtualenv venv`

### Make that python your source 

`source venv/bin/activate`

### Install requirements

`pip install -r requirements.txt`

### Run the server

`python transients.py`

**Check to make sure the port you want is open on your EC2 instance for http requests*
