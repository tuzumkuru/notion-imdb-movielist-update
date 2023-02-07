# Notion IMDB Integration

Notion-IMDB Integration is a Python script that automizes updating ones movie database with information gathered from IMDB

It checks a specific table and fills in the empty cells with the information on IMDB

This is a project that I am developing to learn Python, environments, and APIs. Feel free to comment on the project about anything (structure, design, implementation, etc.). 

## Installation

### Clone the code

Clone the repository using git clone.

```bash
git clone https://github.com/tuzumkuru/notion-imdb.git
```

### Setting up dependencies

The package and dependencies are managed by pipenv (https://pipenv.pypa.io) so it is strongly recommended to be installed and used

You can install pipenv as below or look at the documentation of the tool

```bash
pip install --user pipenv
```

Run pipenv in the project folder

```bash
pipenv install
```

pipenv will create an environment with the necessary dependencies.

Alternatively, you can install the dependencies using pip and the requirements.txt file. 

```bash
pip install -r requirements.txt
```

### Setting up your Notion

Go to https://www.notion.so/my-integrations website and create an internal integration with Read and Update capabilities.

Duplicate this page (https://www.notion.so/tuzumkuru/819881b338594c6e9efa4902a6dcd37b) to your workspace and connect your integration with your page.

To add the connection after duplicating click on the ... on the top right corner of your page and hover on Add Connections and select the integration you created. 


### Setting up .env File

There is a .env_example file created as a template to hold some user-specific values

Rename or copy it as .env and add your specific values in

NOTION_DATABASE_URL is the URL of your page. You can copy it from the address bar of your browser when the page is open. 

NOTION_TOKEN is the token you will get from your Notion application. Copy the Internal Integration Token after NOTION_TOKEN= without any trailing or leading spaces.

NOTION_DATABASE_NAME is the database name you use to store your movie files. It is not necessary if you provide NOTION_DATABASE_URL


## Usage

After finishing the installation steps you can run the script below if you've set up the environment:

```bash
pipenv run python main.py
```

If you did not set up an environment you can run main.py with your python interpreter

```bash
python main.py
```

The script will search the database for missing director and duration properties and when found will try to find the movie from the IMDB database using Cinemagoers. If IMDB URL is provided it will look through the Movie ID and find an exact result if the URL is correct. If not provided, it will search IMDB with the name provided and check for the exact name match. So providing name may give wrong results. 

You can create recurring tasks to run the script in a determined interval. 

## Contributing

Pull requests are welcome.

## Future Work

The script would be better if it is triggered through a new entry event from Notion. 

Creating a docker image would make the script easier to use. 

Will test the script and make it work on different architectures and OSs.


## Acknowledgments

This readme file is created using a template from https://www.makeareadme.com

Thanks to @ramnes for Notion Python SDK (https://github.com/ramnes/notion-sdk-py)

Thanks to the Cinemagoer team (https://github.com/cinemagoer)

Thanks to Notion and IMDB


## License

[MIT](https://choosealicense.com/licenses/mit/)