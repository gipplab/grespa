# GRESPA Web Frontend

The web frontent uses the *Flask* web framework and relies on JavaScript.

## Dependencies

Installation details are provided by the readme located in the projects root directory.

## Configuration

To configure the web frontend, configure the variables in `database.env` and `webapp.env` (you might have to strip the `-sample` suffix from the filename).

Additionally, set the desired application settings via the env key `APP_SETTINGS=...` with one of the following:

 - `config.DevelopmentConfig`
 - `config.ProductionConfig`

If you are running the web frontent in production, be sure to set the env key `SECRET_KEY` to a long and random value.
The production settings disable the *Debug Toolbar*, for example.

## Running the Web Frontend

```
source activate grespa-webapp    # activate the environment
export $(cat ../*.env | xargs)  # set environment variables
python app.py                   # start the server
```

Visit [`http://localhost:5000`](http://localhost:5000) to access the web frontend.

If your database is slow, you may want to create indexes over appropriate columns.