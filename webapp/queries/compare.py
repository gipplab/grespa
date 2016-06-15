def authors_cited_per_year(authors):
    query = 'SELECT * FROM authors JOIN '+\
            '(SELECT author_id as id, array_agg(year) as years, array_agg(pub_count) as pub_count, array_agg(cite_count) as cite_count FROM '+\
            '(SELECT author_id, year, count(*) as pub_count, sum(cite_count) as cite_count '+\
            'FROM documents d '+\
            'WHERE year IS NOT NULL AND d.author_id in ('+ ','.join(['\'' + id + '\'' for id in authors]) + ') '+\
            'GROUP BY year, author_id '+\
            'ORDER BY author_id, year) as timeseries '+\
            'GROUP BY author_id) as aggregates '+\
            'USING (id);'
    return query
