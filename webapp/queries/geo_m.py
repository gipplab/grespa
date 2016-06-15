import math
def getData(i):
    i = int(i)
    if i == 0:
        agg = 'COUNT(*)'
    else:
        agg = 'SUM' if i % 2 == 1 else 'CAST(AVG'
        agg += '(measures['+str((i+(i % 2)))+'])'
        if i % 2 == 0:
            agg += '  AS DECIMAL(10,3))::character varying '
    q = 'SELECT id,val, org.name,  org.lat,org.lng FROM'
    q += '(SELECT '+agg + ' AS val, org FROM authors WHERE org IS NOT NULL GROUP BY org) a, orgfinal org '
    q += ' WHERE a.org=org.id AND org.lng IS NOT NULL'
    return q

def getClosest(lat,lon,zoom):
    maxDist = 156543.03392 * math.cos(lat * math.pi / 180) / math.pow(2, zoom)
    maxDist /= 5000
    q = 'WITH click AS (SELECT ST_MakePoint('+str(lon)+','+str(lat)+') AS coord) '
    q += 'SELECT * FROM orgfinal org, click WHERE ST_Distance(click.coord, ST_MakePoint(org.lat,org.lng))<'+ str(maxDist)
    q += ' AND org.lng IS NOT NULL ORDER BY ST_Distance(click.coord, ST_MakePoint(org.lng,org.lat)) ASC LIMIT 5'
    return q
