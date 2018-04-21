# msgbot
A Python Discord selfbot that stores user messages in individual .csv (comma-separated value) files.

Currently persists a timestamp, Author ID, Guild ID (where applicable), channel ID, and message contents. Private messages are persisted in files corresponding to recipient channel IDs, while guild messages are stored in files corresponding to the guild ID.

## Setup

* Setup your venv with `virtualenv .`
* Activate venv with `source bin/activate`
    * If `python` on your system does not point to python >= 3.6, specify your python >= 3.6 executable with --python (e.g. `virtualenv --python=python3.6 .`)
* Install deps with `pip install -r requirements.txt`

## Usage

* Activate venv: `source bin/activate`
* Run `python bot.py <token>`

