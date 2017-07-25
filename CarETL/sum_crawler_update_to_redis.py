from dbconfig import Redisdb, mySQL_project
import pymysql
import redis
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def push_to_redis(links):
    que = redis.StrictRedis(host=Redisdb.host, port=Redisdb.port, db=0, password=Redisdb.password)
    for link in links:
        que.rpush('sum_update_url', link[0])
    
def get_database_data():
    count = 0
    while count < 50:
        try:
            conn = pymysql.connect(host=mySQL_project.IP, port=3306,
                                   user='team1', passwd=mySQL_project.passwd, db='team1', charset='utf8')
            break
        except pymysql.OperationalError:
            count += 1
            if count == 50:
                logger.error('at data getting mysql server cannot connect')
    #     cur.set_character_set('utf8')
    c = conn.cursor()
    existing_data = []
    sql = "select url from {} where source ='{}' and (oostock != '1' or oostock is null)"
    c.execute(sql.format(mySQL_project.final_table, 'SUM'))
    for row in c:
        existing_data.append(row)
    conn.commit()
    conn.close()
    return existing_data


def main():
    que = redis.StrictRedis(host=Redisdb.host, port=Redisdb.port, db=0, password=Redisdb.password)
    que.delete('sum_update_url')
    existing_data = get_database_data()
    push_to_redis(existing_data)
    end = ['end']*1000
    push_to_redis(end)
    print('\n'+'data upload finished')

if __name__=="__main__":
    main()