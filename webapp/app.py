import time
from datetime import datetime
from os import environ

import requests
from datatables import ColumnDT, DataTables
from flask import Blueprint, render_template, redirect, url_for, request, Response
from flask import Flask
from flask import jsonify, abort
from flask.ext.cache import Cache
from flask_bootstrap import Bootstrap
from flask_debug import Debug
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy import create_engine, String
from sqlalchemy import func
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import cast
from urlparse import parse_qs, urlparse
import json
import grequests

import queries.co_network as co
import queries.geo_m as geo_m
import queries.geo_c as geo_c
from queries.dashboard import avg_measures_sql,top_authors_m, time_series_documents, time_series_cited
import queries.compare as cmp

# dotenv_path = join(dirname(__file__), '.env')
# load_dotenv(dotenv_path)

app = Flask(__name__)
app.config.from_object(environ['APP_SETTINGS'])
# app.config.from_object(conf)
Bootstrap(app)
Debug(app)

# Check Configuring Flask-Cache section for more details
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

frontend = Blueprint('frontend', __name__)
app.register_blueprint(frontend)

Base = automap_base()
engine = create_engine(app.config['SQL_ALCHEMY_DATABASE_URI'])
Base.prepare(engine, reflect=True)

# TODO make base classes use the correct engine
# Currently, this uses sqlite o.O: `num_authors = Author.query.count()`
Author = Base.classes.authors
Document = Base.classes.documents
Label = Base.classes.labels

toolbar = DebugToolbarExtension(app)

# Enable SQLAlchemy in Debug Toolbar without flask-sqlalchemy :)
from flask.ext.sqlalchemy import _EngineDebuggingSignalEvents
_EngineDebuggingSignalEvents(engine, app.import_name).register()

session_factory = sessionmaker(bind=engine)
session = flask_scoped_session(session_factory, app)

# From http://flask.pocoo.org/snippets/33/
@app.template_filter()
def friendly_time(dt, past_="ago",
    future_="from now",
    default="just now"):
    """
    Returns string representing "time since"
    or "time until" e.g.
    3 days ago, 5 hours from now etc.
    """

    now = datetime.now()
    if now > dt:
        diff = now - dt
        dt_is_past = True
    else:
        diff = dt - now
        dt_is_past = False

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:

        if period:
            return "%d %s %s" % (period, \
                singular if period == 1 else plural, \
                past_ if dt_is_past else future_)

    return default

# Cache for x seconds
@cache.cached(timeout=180, key_prefix='get_metrics')
def get_metrics():
    # Use func.count to only count ids
    return {
        'num_authors': session.query(func.count(Author.id)).scalar(),
        'num_authors_fully': session.query(Author).filter(Author.measures.isnot(None)).count(),
        'num_documents': session.query(func.count(Document.id)).scalar(),
        'num_fields': session.query(func.count(Label.field_name)).scalar(),
    }


@app.route('/', methods=['GET'])
def index():
    errors = []
    try:
        metrics = get_metrics()
        # num_authors = session.query(func.count(Author.id)).scalar()
    except Exception as e:
        errors.append(e)
        return render_template('pages/index.html', errors=errors,  metrics=None)
    return render_template('pages/index.html', errors=errors,  metrics=metrics, num_authors=metrics['num_authors'])

@app.route('/browse', methods=['GET'])
def browse():
    errors = []
    try:
        metrics = get_metrics()
    except Exception as e:
        errors.append(e)
    return render_template('pages/browse.html', errors=errors, metrics=metrics)

def extract_links(text):
    """Extracts links from a list of links divided by new lines
    """
    # \r\n
    # Split by newline, linefeeds will be stripped with other whitespace
    lines = (l for l in [line.strip() for line in text.split('\n')] if l)
    users = (parse_qs(urlparse(line).query).get('user')[0] for line in lines)
    return list(users)

def request_for_author(author_id):
    'project=gscholar_scraper&spider=author_complete&start_authors={}'
    endpoint = 'http://{0}:{1}/schedule.json'.format(environ.get('SCRAPYD_HOST'), environ.get('SCRAPYD_PORT'))
    params = {'project': 'gscholar_scraper', 'spider' : 'author_complete', 'start_authors' : author_id}
    print params
    return grequests.post(endpoint, data=params)

@app.route('/multisearch', methods=['POST', 'GET'])
def multi_search():
    # POST is used for starting the search/crawling
    # GET will display the form
    # GET is also used for displaying the results (for sharable links)
    researchers = None
    ids = None
    if request.method == 'POST':
        ids = extract_links(request.form['links'])
        # TODO schedule jobs and return job_ids for checking on page

        rs = (request_for_author(i) for i in ids)
        responses = grequests.map(rs)

        # Response object will be something like:
        # {
        #   "status": "ok",
        #   "jobid": "60cd913ac28e11e59a4d0242ac11000d",
        #   "node_name": "58394e5efede"
        # }

        jobs = [json.loads(r.text) for r in responses]
        for idx, author_id in enumerate(ids):
            jobs[idx]['id'] = author_id

        return render_template('pages/multi/progress.html', header='Multi-Search Results', num=len(ids), ids=ids,
                               jobs=jobs)
    elif request.method == 'GET':
        return render_template('pages/multi/search.html', header='Multi-Search')

@app.route('/compare', methods=['GET'])
def compare_authors():
    # This route should enable the user to compare n authors.
    # We have to start a crawling job
    # wait until it is finished
    # redirect to a new/the same page and display the results
    author_ids = request.args.getlist('author_id')
    errors = []
    print author_ids
    try:
        researchers = session.query(Author).filter(Author.id.in_(author_ids)).all()
        authors_cited_per_year_query = cmp.authors_cited_per_year(author_ids)
        # We build our data structure how metricsgraphics.js does expect it
        data = [{'id': a.id, 'name' : a.name, 'fos': a.fields_of_study if a.fields_of_study else [],
                 'cite_counts' : [ {'year': t[1], 'count': t[0]} for t in zip(a.cite_count, a.years)],
                 'pub_counts' : [ {'year': t[1], 'count': t[0]} for t in zip(a.pub_count, a.years)]
                 } for a in session.execute(authors_cited_per_year_query)]

        return render_template('pages/multi/results.html', header='Multi-Search Results', researchers=researchers, metrics=data)
    except Exception as e:
        errors.append(e)
        return render_template('pages/multi/results.html', header='Multi-Search Results', errors=errors, researchers=None, metrics=None)


def field_term(search_term):
    return '_'.join(search_term.lower().split(' '))


@app.route('/top')
def top():
    errors = []
    result = []
    try:
        result = session.execute(top_authors_m(3,10))
    except Exception as e:
        errors.append(e)
    return render_template('pages/top.html',errors=errors, rankings=result)

@app.route('/getRankings/<m>', methods=['GET', 'POST'])
def getRankings(m):
    errors = []
    result = []
    try:
        result = session.execute(top_authors_m(int(m),10))
    except Exception as e:
        errors.append(e)
    return jsonify(results = [dict(row) for row in result], errors =errors)

@app.route('/tempDev')
def temp_home():
    return render_template('pages/temp_dev.html')

@app.route('/getTimeSeries', methods=['GET','POST'])
def getTimeSeries():
    errors = []
    results= []
    try:
        ts_docs_q = time_series_documents()
        ts_cites = time_series_cited()
        docCounts = session.execute(ts_docs_q)
        citeCounts = session.execute(ts_cites)
        results = [[dict(row) for row in docCounts], [dict(row) for row in citeCounts]]
    except Exception as e:
        errors.append(e)
    return jsonify(results = results, errors =errors)


@app.route('/search', methods=['GET', 'POST'])
def search():
    errors = []
    if request.method == 'POST':
        search_term = request.form['entity_value']
        fos_search_term = field_term(search_term)
        print 'Getting %s' % fos_search_term
        try:
            authors = session.query(Author).filter(Author.name.like('%' + search_term + '%')).all()
            fields = session.query(Label).filter(Label.field_name.like('%' + fos_search_term + '%')).all()
            return render_template('pages/search/result.html',
                                   search_term=search_term,
                                   fos_search_term=fos_search_term,
                                   fields=fields,
                                   researchers=authors
                                   )
        except Exception as e:
            errors.append(e)
    return render_template('pages/search/entity.html', entity_name='Researcher or Field', action='/search', errors=errors, header='Search')


def none_to_empty_str(data):
    if not data:
        return None
    else:
        return data

# The main listings of the models are handled by DataTables
# We use DT's ajax calls and server-side processing.
# So we need one route for the html page and one route that returns json
# for the data access.


@app.route('/researchers', methods=['GET'])
def researchers():
    return render_template('pages/researchers.html')



@app.route('/api/researchers', methods=['GET'])
def api_researchers():
    columns = [ColumnDT('id'),
               ColumnDT('name'),
               ColumnDT('fields_of_study'),
               ColumnDT('cited', filter=none_to_empty_str), \
               ColumnDT('measures', filter=none_to_empty_str),
               ColumnDT('org', filter=none_to_empty_str),
               ColumnDT('hasCo', filter=none_to_empty_str),
               ColumnDT('created_at', filter=str),
               ColumnDT('updated_at', filter=str),
               ]
    query = session.query(Author)
    row_table = DataTables(request.args, Author, query, columns)
    return jsonify(**row_table.output_result())


@app.route('/researcher', methods=['GET'])
def find_researcher():
    return redirect(url_for('search'), 302)


@app.route('/researcher/<id>')
def show_researcher_profile(id):
    errors = []
    results = {}
    try:
        res = session.query(Author).get(id)
        pub = session.query(Document).filter(Document.author_id == id).all()
        print 'Num Publications: %d' % len(pub)
        print 'Researcher: %s' % res.id if res else None
        if not res:
            abort(404)
    except Exception as e:
        errors.append(e)
        return render_template('pages/researcher.html', errors=errors, researcher=None, header="Researcher Profile")

    return render_template('pages/researcher.html', researcher=res, publications=pub, header="Researcher Profile")


@app.route('/researcher/<id>/fos/<field_name>')
def compare_researcher_fos(id, field_name):
    errors = []
    results = {}
    try:
        print field_name
        res = session.query(Author).get(id)
        print "Researcher %s" % res.name if res else None
        avg = session.execute(avg_measures_sql([field_name])).fetchone()
        print "Avg: %s " % avg
        return render_template('pages/compare.html', errors=errors, researcher=res, avg=avg, field_name=field_name)
    except Exception as e:
        errors.append(e)
        print e
    return render_template('pages/compare.html', errors=errors, field_name=field_name)



@app.route('/fields', methods=['GET'])
def fields():
    return render_template('pages/fields.html')

@app.route('/api/fields', methods=['GET'])
def api_fields():
    columns = [ColumnDT('field_name'),
               ColumnDT('created_at', filter=str),
               ColumnDT('updated_at', filter=str), ]
    query = session.query(Label)
    row_table = DataTables(request.args, Label, query, columns)
    return jsonify(**row_table.output_result())


@app.route('/fos', methods=['POST', 'GET'])
def find_field():
    return redirect(url_for('search'), 302)


@app.route('/fos/<field_name>')
def show_field(field_name):
    errors = []
    results = {}
    try:
        res = session.query(Author).filter(
            Author.fields_of_study.contains(cast([field_name], postgresql.ARRAY(String)))).all()
    except Exception as e:
        errors.append(e)
        return render_template('pages/fos.html', errors=errors)
    return render_template('pages/fos.html', results=res, field_of_study=field_name)


@app.route('/documents', methods=['GET'])
def documents():
    return render_template('pages/documents.html')


@app.route('/api/documents', methods=['GET'])
def api_documents():
    columns = [ColumnDT('id'),
               ColumnDT('author_id'),
               ColumnDT('title'),
               ColumnDT('cite_count', filter=none_to_empty_str),
               ColumnDT('year', filter=none_to_empty_str),
               ColumnDT('created_at', filter=str),
               ColumnDT('updated_at', filter=str),
               ]

    # Currently we filter out documents that have no publication date or no citations.
    # This has two reasons: 1) documents without publication dates are not really interesting and
    # often times not real publications
    # 2) there exists no option to set SQL order by null behavior in the currently used libraries
    # (sqlalchemy-datatables and datatables.js).
    # Therefore I opened an issue with one of the libraries developers:
    # https://github.com/Pegase745/sqlalchemy-datatables/issues/35

    # Joins do not work with DataTable
    # query = session.query(Document, Author).filter(Document.year != None).filter(Document.cite_count != None)\
    #     .join(Author, Author.id == Document.author_id)
    query = session.query(Document).filter(Document.year != None).filter(Document.cite_count != None)
    row_table = DataTables(request.args, Document, query, columns)
    return jsonify(**row_table.output_result())


@app.teardown_request
def teardown_request(exception):
    if exception:
        session.rollback()
        session.remove()
    session.remove()

# co author networks:

@app.route('/co/EntityByID/<i>',  methods=['POST', 'GET'])
def getEntityById(i):
    errors = []
    results = []
    try:
        ent = session.execute(co.getEntity(i))
        results  = [dict(row) for row in ent]
    except Exception as e:
        errors.append(e)
    return jsonify(results = results, errors =errors)


@app.route('/co/getExtended',  methods=['POST', 'GET'])
def getExtended():
    errors = []
    results = []
    try:
        all =  request.form['all']
        clicked = request.form['clicked']

        limit = request.form['limit']
        print "all" + all
        print "clicked" + clicked
        print "limit" + limit
        ent = session.execute(co.getExtended(clicked, [all], limit))
        results  = [dict(row) for row in ent]
    except Exception as e:
        errors.append(e)
    return jsonify(results = results, errors =errors)

# geoanalytics: measures (dot map)
@app.route('/geo_m/home')
def geo_m_home():
    return render_template('pages/geo_measures.html')

@app.route('/geo_m/getData/<i>',  methods=['GET', 'POST'])
def geo_m_getData(i):
    errors = []
    results = []
    try:
        d = session.execute(geo_m.getData(i))
        results = [dict(row) for row in d]
    except Exception as e:
        errors.append(e)
    return jsonify(results=results, errors=errors)

@app.route('/geo_m/getClosest',  methods=['POST'])
def geo_m_getClosest():
    results = []
    errors = []
    try:
        d = session.execute(geo_m.getClosest(request.json['lat'],request.json['lng'], request.json['zoom']))
        results = [dict(row) for row in d]
    except Exception as e:
        errors.append(e)
    print errors
    return jsonify(results=results, errors=errors)

# geoanalytics: coauthors
@app.route('/geo_c/home')
def geo_c_home():
    return render_template('pages/geo_co.html')

@app.route('/geo_c/getInitData',  methods=['GET', 'POST'])
def geo_c_getInitData():
    errors = []
    results = []
    try:
        d = session.execute(geo_c.initData)
        results = [dict(row) for row in d]
    except Exception as e:
        errors.append(e)
    return jsonify(results=results, errors=errors)

@app.route('/geo_c/getEdgeData/<o>',  methods=['GET', 'POST'])
def geo_c_getEdgeData(o):
    errors = []
    results = []
    try:
        d = session.execute(geo_c.getEdgeData(o))
        results = [dict(row) for row in d]
    except Exception as e:
        errors.append(e)
    return jsonify(results=results, errors=errors)

@app.route('/geo_c/getSugg/<t>',  methods=['POST'])
def geo_c_getSugg(t):
    errors = []
    results = []
    try:
        d = session.execute(geo_c.getSugg(t))
        results = [dict(row) for row in d]
    except Exception as e:
        errors.append(e)
    return jsonify(results=results, errors=errors)

@app.route('/geo_c/getClosest',  methods=['POST'])
def geo_c_getClosest():
    results = []
    errors = []
    try:
        d = session.execute(geo_c.getClosest(request.json['lat'],request.json['lng'], request.json['zoom'], request.json['selected']))
        results = [dict(row) for row in d]
    except Exception as e:
        errors.append(e)
    print errors
    return jsonify(results=results, errors=errors)

@app.route('/schedule', methods=['POST'])
def schedule_spider():
    # project
    project = request.form['project']
    # get spider name
    spider_name = request.form['spider']
    # and start_author for test for now
    start_authors = request.form['start_authors']
    r = requests.post('http://localhost:6800/schedule.json',
                      data={'project': project, 'spider': spider_name, 'start_authors': start_authors})
    return Response(
            r.text,
            status=r.status_code,
            content_type=r.headers['content-type']
    )


@app.route('/explore', methods=['GET'])
def explore():
    return render_template('pages/explore.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
