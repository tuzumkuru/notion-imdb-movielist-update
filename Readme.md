# Notion IMDB Integration

Notion-IMDB Integration is a Python script that automizes updating ones movie database with information gathered from IMDB

It checks a specific table and fills in the empty cells with the information on IMDB

This is a project that I've developed to learn Python, environments, and APIs. Feel free to comment on the projects for any aspects. 

## Installation

### Setting up dependencies
The package and dependencies are managed by pipenv (https://pipenv.pypa.io) so it is strongly recommended to be installed and used

You can install pipenv as below or look at the documentation of the tool

```bash
pip install --user pipenv
```

After installing pipenv, clone the repository using git clone.

```bash
git clone https://github.com/tuzumkuru/notion-imdb.git
```

### Setting up your Notion
Go to https://www.notion.so/my-integrations web site and create an internal integration with Read and Update capabilities.

Duplicate this page (will be provided soon) to your workspace and connect your integration with your page.
For doing this click to the ... on the top right corner of your page and hover on Add Connections and select your integration you created. 


### Setting up .env File

There is an .env_example file created as a template to hold some user specific values

Rename or copy it as .env and add your specific values in

NOTION_TOKEN is the token you will get from your Notion application. Copy the Internal Integration Token after NOTION_TOKEN= without any trailing or leading spaces.

NOTION_DATABASE_NAME is the database name you use to store your movie files

### Rest

Run pipenv in the project folder

```bash
pipenv install
```

pipenv will create an environment with necessery dependencies.

## Usage
After finishing the installation steps you can run the script as below:

```bash
pipenv run python main.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)