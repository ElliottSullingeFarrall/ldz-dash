# LDZ-Dash

## Deployment

The web app has been designed to be easily deployed via [PythonAnywhere](https://eu.pythonanywhere.com) but deployment through other services is also possible. The following is an overview of the steps necessary to deploy the application.

#### Clone the Repository

Start by opening a terminal in the location (henceforth referred to as `<repo>`) where you would like to install the application and run
```bash
git clone https://github.com/ElliottSullingeFarrall/LDZ-Apps.git
```
to clone the repository. If you don't have enough space to clone the repository, try using the `--depth` option for `git clone`.

#### Generate the Config File

From the root of the repository, run the `install.sh` script to generate a `config.py` file. This file will contain the `SECREY_KEY` variable. Take note of this key as it will be needed throughout the installation process.

#### Initialise Wep App

Next create a web app but don't auto-configure for any frameworks as we will be making use of virtual environments. Makes sure the Python version is set to **3.10**.

Set the source to `<repo>/src` and the working directory to `<repo>`. Make sure the `wsgi.py` file looks like
```python
import sys

# add your project directory to the sys.path
project_home = '<repo>/src'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# import flask app but need to call it "application" for WSGI to work
from src import app as application
```
and the virtual environment is set to `<repo>/.venv`.

#### Setup Auto-Update

The app is configured to automatically pull any changes that are made via a pull request to the `main` branch. To set this up make sure that GitHub has an action variable `URL` set to the URL of the application and an action secret `SECRET_KEY` that is set to the key in the `config.py` file generated eariler.

#### First Login

The application should now be operational. For the first login use username **default** and password `SECRET_KEY`. It is recommended to create a new admin user as soon as possible and then delete the default user.

## Development

This project is written using Flask (Python), HTML and CSS. The Python dependencies are managed via Poetry and a development envionment is available for Nix uses via the `flake.nix`.

Once all dependcies are installed, run `install.sh` to generate the necessary `conig.py` file. The web app can be run locally on port 4000 using the `run.sh` script. This script will automatically resart the app upon any changes to the source code.