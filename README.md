# Sunday
A cross country results app for finding, saving, and generating statistics about Iowa high school cross country results.

## Repo overview
This repo has a separate folder for the ResultsService backend API. That folder includes a tests directory as well as the Flask app packages.

## How to install
The ResultsService backend API runs on Python 3.X. You can install all required packages by going into the directory and running the following command:

`pip3 install -r requirements.txt`

The ResultsService backend also needs a couple of packages to be installed -- mongodb and chromedriver. The following instructions are how to install on Ubuntu 20.04 (Focal).

#### To install mongodb and chromedriver:

`sudo apt update`

`sudo apt install -y mongodb chromium-chromedriver`

#### To start mongodb service

Check mongodb status

`sudo systemctl status mongodb`

If it isn't active, start it with

`sudo systemctl start mongodb`

## How to run the program
Currently, this application is in alpha and is not ready to be deployed. Eventually, a Dockerfile will be created to ease in setting up and running this app and exposing the API. For now, functionality can be tested through scripts found in the test directory.

To run tests, just launch a script from the [ResultsService/test](ResultsService/test) directory.