import pymysql
 
db = pymysql.connect("104.199.159.110", "root", "k0KyAFJNmzuqkogB", "t4_21", charset="utf8")
cursor = db.cursor()
sql = """select * from dep limit 10"""
cursor.execute(sql)
db.commit()
results = cursor.fetchall()
for row in results:
    print(row)
db.close()
