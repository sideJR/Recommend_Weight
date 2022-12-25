import pymysql

class DB():
    db = pymysql.connect(host="127.0.0.1", user="sideJR", passwd="08130263", db="at_ease_with_eating")