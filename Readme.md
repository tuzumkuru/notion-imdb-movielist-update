# Notion-IMDB Movie List Update

Notion-IMDB Movie List Update is a Python script that automizes updating ones movie database with information gathered from IMDB.

It checks a specific table and fills in the empty cells using the information on IMDB.

This is a project that I am developing to learn Python, environments, and APIs. Feel free to comment on the project about anything (structure, design, implementation, etc.). 


## Before Installation

### Cloning the code

Clone the repository using git clone.

```bash
git clone https://github.com/tuzumkuru/notion-imdb-movielist-update.git
```


### Setting up your Notion

Go to https://www.notion.so/my-integrations page and create an internal integration with Read and Update capabilities.

Duplicate this page (https://www.notion.so/tuzumkuru/819881b338594c6e9efa4902a6dcd37b) to your workspace and connect your integration with your page.

To add the connection after duplicating click on the ... on the top right corner of your page and hover on Add Connections and select the integration you created. 


### Environmental Variables

**NOTION_DATABASE_URL** is the URL of your page. You can copy it from the address bar of your browser when the page is open. 

**NOTION_TOKEN** is the token you will get from your Notion application. Copy the Internal Integration Token after NOTION_TOKEN= without any trailing or leading spaces.

**NOTION_DATABASE_NAME** is the database name you use to store your movie files. It is not necessary if you provide NOTION_DATABASE_URL


## Running as a Python script


### Setting up an Environment

Setting up a Python environment is like giving your project its own little cozy space to live in. It's important because different projects might need different versions of Python or specific libraries, and environments help keep everything organized.

I prefer using venv for Python environment management. 

You can install venv as below or look at the documentation of the tool:

```bash
sudo apt install python3.11-venv # You should use the appropriate version for your Python
```

Create an environment using venv in the project folder:

```bash
python -m venv .venv
```

Python venv will create an environment that you can use isolated from the system.

To use the environment source the activate file:

```bash
source .venv/bin/activate
```

### Installing the dependencies

Now, you can install the dependencies using the requirements.txt:

```bash
pip install -r requirements.txt
```


### Setting up .env File

There is a .env_example file created as a template to hold some user-specific values

Rename or copy it as .env and add your specific values.

You can find more information about these variables [here](#environmental-variables)


### Running the Script

After finishing the installation steps you can run the script with the following command:

```bash
python main.py
```

The script will search your Notion database for pages where the 'Director' or 'Duration [min]' properties are empty. For each of these pages, it will:
1.  Attempt to find the movie on IMDb using the 'IMDB' URL property if it exists.
2.  If no IMDb URL is present, it will search IMDb by the movie's 'Title'.
3.  Once found, it will populate the empty properties in your Notion page with the information from IMDb, such as director, duration, rating, plot, and genres.

You can create recurring tasks to run the script in a determined interval. 


## Running in a Docker container

This project can be containerized using Docker. Follow the steps below to run it as a Docker container.


### Prerequisites

Make sure you have Docker installed on your machine ([Docker Installation Guide](https://docs.docker.com/get-docker/)) and you succesfully cloned the repository. 


### Build Docker Image

Enter the directory cloned and run the following command

```bash
docker build -t notion-imdb-movielist-update .
```


### Running Docker Container

Replace _your_token_ and _your_database_url_ or _your_database_name_ with your actual values.

```bash
docker run -d --name movielist_update -e NOTION_DATABASE_URL=your-database-url -e NOTION_TOKEN=your-token -e NOTION_DATABASE_NAME=your-database-name notion-imdb-movielist-update
```

Alternatively you can pass a .env file that contains the variables.

```bash
docker run -d --name movielist_update --env-file .env notion-imdb-movielist-update
```

## Contributing

Issues & Pull requests are welcome.


## Future Work

The script would be better if it is triggered through a new entry event from Notion. 

Will test the script and make it work on different architectures and OSs.


## Acknowledgments

This readme file is created using a template from https://www.makeareadme.com

Thanks to @ramnes for Notion Python SDK (https://github.com/ramnes/notion-sdk-py)

Thanks to @tveronesi for the imdbinfo library (https://github.com/tveronesi/imdbinfo)

Thanks to Notion and IMDB


## License

[MIT](https://choosealicense.com/licenses/mit/)