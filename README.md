# Google Scholar Research Performance Analyzer (GRESPA)

## Project Architecture

The tool consists of two applications. A web scraper (a collection of *scrapy* spiders) to scrape information
 from Google Scholar and a *flask* web application to show and analyze the scraped data. The scraping process can be invoked
 interactively from the web application.

Annotated directory structure and useful files:
```
.
├── README.md                   -- current readme
├── database.env-sample         -- sample database variables
├── proxy.env-sample            -- sample proxy variables
├── webapp.env-sample           -- sample webapp variables
├── create-db.sh                -- script for creation of the database
├── gscholar_scraper            -- scraper project root
│   ├── README.md               -- more information on the scraper
│   ├── gscholar_scraper        -- scraper implementation
│   │   ├── models.py
│   │   ├── ...
│   │   ├── settings.py
│   │   ├── spiders
│   │   │   ├── ...
│   ├── main.py                 -- programmatic access to the spiders
│   ├── prepare-db.py           -- script for creation of tables
│   ├── names.txt               -- list of 1000 most frequent english names
│   ├── requirements.txt
│   └── scrapy.cfg              -- config for scrapy
└── webapp                      -- webapp project root
    ├── __init__.py             -- python file that contains the small webapp (view & controller logic)
    ├── config.py
    ├── queries
    │   ├── ...
    ├── requirements.txt
    ├── static                  -- static files, like css and js
    │   ├── ...
    └── templates               -- page templates
        ├── ...
```

The scraper consists of a couple of *scrapy* spiders, notably:

- `author_complete`: Crawls the profile page of a single given author (via the `start_authors` param) and colleagues until reaching the configured link depth (see `settings.py`).
- `author_labels`: Searches for the names in `SEED_NAME_LIST` (see settings.py) and scrapes the labels from author's
   profiles
- `author_general`: Searches for all labels in the database and scrapes general author information
- `author_detail`: Complements existing author information by requesting the profile page of specific authors
- `author_co`: Scrapes co-authorship information of specified authors

A typical scraping workflow using the above spiders would be, to first scrape label information using the popular names,
then getting authors for these labels and finally augmenting general author information with detail information regarding
scientific measurements or co-authorship.

Or you can issue a *Multi Search* from the webapp to start crawling a list of authors.

## Installation / Usage

For an easier installation, the project uses [Anaconda](https://docs.continuum.io/anaconda/index) environments (enabled by [conda-env](https://github.com/conda/conda-env)).

The basic software requirements are:

- PostgreSQL > 9.4
- Python 2.7
- *Optional:* Anaconda/Miniconda, conda-env

If you are new to Anaconda, we recommend using [miniconda](http://conda.pydata.org/miniconda.html), for which the link provides installation instructions for Windows, OS X and Linux and a quick start guide.

### Preparing the Database

First, you have to set up an instance of PostgreSQL, although--technically--you can use every database for which there exist compatible SQLAlchemy drivers. Put the credentials you want to use in the file `database.env-sample` and remove the `-sample` suffix. `.env` files are used to store secrets, because these files are exempt from version control.

To create the database and tables, you can use the provided scripts from the project's root directory:

```
export $(cat *.env | xargs)             # set the environment variables from all secret files
sh ./create-db.sh                       # create the database
python ./gscholar_scraper/prepare-db.py # prepare the database
```

### Dependencies/Environment

To install all necessary dependencies, invoke `conda env` on the provided environment specifications.

```
conda env create --file webapp/environment.yml
conda env create --file gscholar_scraper/environment.yml
```

Now you should have two conda environments (`conda env list`):
```
grespa-scraper            ~/miniconda3/envs/grespa-scraper
grespa-webapp             ~/miniconda3/envs/grespa-webapp
root                   *  ~/miniconda3
```

Activate the environment you want to use with:
```
source activate ENV_YOU_WANT_TO_ACTIVATE_HERE
```

You should not need to use `pyenv`, `virtualenv`, `virtualenvwrapper` or other tools, if everything went smoothly.


### Usage

- `gscholar_scraper`: Readme located at `gscholar_scraper/README.md`
- `webapp`: Readme located at `webapp/README.md`

**Note:**: Do not forget to activate the scraper or webapp environment!


# Authors

- [Philipp Meschenmoser](mailto:philipp.meschenmoser@uni.kn)
- [Manuel Hotz](mailto:manuel.hotz@uni.kn)
- [Norman Meuschke](norman.meuschke@uni.kn)
- [Bela Gipp](bela.gipp@uni.kn)


# Troubleshooting


## If You Are Using `fish` Instead of Bash

### Environment Variables
You should export variables in the following way, because the syntax of sub-shells differs to `bash`:
```
export (cat ../*.env);
```

### Activate an Environment

If your conda installation did not provide a working fish config, use `conda.fish` from [conda/conda](https://github.com/conda/conda/blob/645e39dfc3cee1db73de294faaa7f33ca1c981cf/shell/conda.fish), remember to include the conda directory in your path and source the `conda.fish` file.

To activate an environment, you should use:
```
conda activate ENV_YOU_WANT_TO_ACTIVATE_HERE
```