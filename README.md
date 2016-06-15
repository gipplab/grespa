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

- `author_complete`: Crawls the profile page of a single given author (via the `start_authors` param) and colleagues up 
   until the configured link depth (see `settings.py`).
- `author_labels`: Searches for the names in `SEED_NAME_LIST` (see settings.py) and scrapes the labels from author's 
   profiles
- `author_general`: Searches for all labels in the database and scrapes general author information
- `author_detail`: Complements existing author information by requesting the profile page of specific authors
- `author_co`: Scrapes co-authorship information of specified authors

A typical scraping workflow using the above spiders would be, to first scrape label information using the popular names,
then getting authors for these labels and finally augmenting general author information by detail information regarding
scientific measurements or co-authorship.

Or you can issue a *Multi Search* from the webapp to start crawling a list of authors.

## Installation / Usage

Required software:

- PostgreSQL > 9.4
- Python 2.7

### Database

Setup an instance of PostgreSQL. Put the credentials you want to use in the file `database.env-sample` and remove the `-sample`.
To create the database and tables, you can use the provided scripts:

```
export $(cat *.env | xargs) && sh ./create-db.sh && python ./gscholar_scraper/prepare-db.py
```

### `gscholar_scraper`

- Python libraries: see `gscholar_scraper/requirements.txt` (tip: these can be installed by pip using the file!)
- `cd gscholar_scraper && pip install -r requirements.txt`

For usage details see `gscholar_scraper/README.md`.

### `webapp`

- Python libraries: see `webapp/requirements.txt`
- `cd webapp && pip install -r requirements.txt`

To configure the webapp, configure the variables in `database.env` and `webapp.env` (you might have to strip the `-sample` from the filename. 
Additionally, set the desired app settings via the env key `APP_SETTINGS=...` with one of the following:
 
 - config.DevelopmentConfig
 - config.ProductionConfig
 
If you are running the webapp in production, be sure to set the env key `SECRET_KEY` to a long and random value.
The production settings disable the *Debug Toolbar*, for example.

The webapp can be started via `cd webapp && export $(cat ../*.env | xargs) && python app.py` and normally accessed via `http://localhost:5000`.

If your database is slow, you may want to create indexes over appropriate columns.

# Authors

- Philipp Meschenmoser
- Manuel Hotz