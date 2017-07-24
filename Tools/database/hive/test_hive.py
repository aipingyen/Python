from pyhive import hive

cursor = hive.connect('10.120.37.94').cursor()
cursor.execute('SELECT * FROM google_pop LIMIT 10')
for c in cursor.fetchall():
    print(c[1])
