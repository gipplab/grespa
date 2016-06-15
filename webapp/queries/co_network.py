def getEntity(id):
    return 'SELECT * FROM author_tmp WHERE id=' + id

def getExtended(id, all, limit):
    query = 'SELECT author_tmp.*, links FROM (' + \
            ' SELECT rel, array_agg(li) AS links FROM (' + \
            ' SELECT DISTINCT ON (direct.rel, li) direct.rel, CASE WHEN co.author1 = direct.rel THEN co.author2  WHEN co.author2 = direct.rel THEN co.author1 END AS li FROM (' + \
            'SELECT CASE WHEN author1 =  '+id+' THEN author2 ELSE author1  END AS rel FROM coauthor_tmp c WHERE c.author1= ' +id+' OR c.author2=' + id + '  ORDER BY freq DESC LIMIT '+limit+' ) direct, coauthor_tmp co WHERE  (direct.rel NOT IN ('+','.join(all)+')) )' + \
            '  snd WHERE (li IS NOT NULL) GROUP BY rel' + \
            ' ) third, author_tmp WHERE author_tmp.id = rel'
    return query