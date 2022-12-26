import pymysql
import json
import time # for testingB

class DBAwae:
    def __init__(self, user_id):
        self.user_id = user_id
        self.connectDB()
        self.__cur.execute('SET GLOBAL group_concat_max_len=9999999')
        self.__cur.execute('set global max_allowed_packet = 9999999')
    def select_user_diseases(self): # 使用者疾病
        self.__cur.execute('''SELECT `disease_id` FROM `user_disease`
        WHERE `user_id`={}'''.format(self.user_id))
        lst_user_diseases = []
        for r in self.__cur:
            lst_user_diseases += r
        return lst_user_diseases
    def select_user_indicators_nutrients_day_limit(self): # 一日指標上限
        self.__cur.execute('''SELECT CONCAT(JSON_OBJECT('sodium_upper',`sodium_upper`,'dietary_fiber_lower',`dietary_fiber_lower`,'trans_fat_upper',`trans_fat_upper`,'saturated_fat_lower',`saturated_fat_lower`,'saturated_fat_upper',`saturated_fat_upper`,'protein_lower',`protein_lower`,'protein_upper',`protein_upper`,'calories_upper',`calories`,'carbohydrate_upper',`carbohydrate_upper`,'free_sugar_upper',`free_sugar_upper`,'fat_lower',`fat_lower`,'fat_upper',`fat_upper`)) json 
        FROM `user_indicators_nutrients_day_limit`
        WHERE `user_id`={}'''.format(self.user_id))
        dic_indicators_day = json.loads(self.__cur.fetchone()[0]) # str_json to dict
        return dic_indicators_day
    
    def get_all_user_nutrients(self, lst_recommend): #加入此食物後營養素
        ## 已吃過營養素累加
        self.__cur.execute('''SELECT CONCAT(JSON_OBJECT('sodium', IFNULL(`sodium`,0), 'dietary_fiber', IFNULL(`dietary_fiber`,0), 'trans_fat', IFNULL(`trans_fat`,0), 'saturated_fat', IFNULL(`saturated_fat`,0), 'protein', IFNULL(`protein`,0), 'fat', IFNULL(`fat`,0), 'free_sugar', IFNULL(`sugar`,0), 'carbohydrate', IFNULL(`carbohydrate`,0), 'calories', IFNULL(`calories`,0))) json 
        FROM `user_record` JOIN `user_record_food`, `restaurant_dish` 
        WHERE `user_record`.`id`=`user_record_food`.`user_record_id` 
            AND `user_record_food`.`restaurant_dish_id`=`restaurant_dish`.`id` 
            AND `user_record`.`user_id`={}'''.format(self.user_id))
        dic_record_dish_nutrients = json.loads(self.__cur.fetchone()[0]) #str_json to dict
        ## 此關鍵詞食物
        str_sql_diseases = ''
        count = 0
        for rec in lst_recommend:
            if(count>=1):  str_sql_diseases+= ','
            str_sql_diseases += str(rec)
            count += 1
        str_sql = '''SELECT CONCAT('[', GROUP_CONCAT(JSON_OBJECT('rdish_id', `restaurant_dish`.`id`, 'sodium', IFNULL(`sodium`,0), 'dietary_fiber', IFNULL(`dietary_fiber`,0), 'trans_fat', IFNULL(`trans_fat`,0), 'saturated_fat', IFNULL(`saturated_fat`,0), 'protein', IFNULL(`protein`,0), 'calories', IFNULL(`calories`,0), 'carbohydrate', IFNULL(`carbohydrate`,0), 'free_sugar', IFNULL(`sugar`,0), 'fat', IFNULL(`fat`,0))) ,']') json
        FROM `restaurant_dish`
        WHERE `restaurant_dish`.`id` IN({})
        '''.format(str_sql_diseases)
        self.__cur.execute(str_sql)
        lst_dic_dish_nutrients = json.loads(self.__cur.fetchone()[0]) #str_json to dic
        ## 加入此關鍵詞食物後營養素
        lst_dic_all_user_nutrients = []
        for dn in lst_dic_dish_nutrients:
            lst_dic_all_user_nutrients += [{'id': dn['rdish_id'],
                'sodium': dic_record_dish_nutrients['sodium'] + dn['sodium'],
                'dietary_fiber': dic_record_dish_nutrients['dietary_fiber'] + dn['dietary_fiber'],
                'trans_fat': dic_record_dish_nutrients['trans_fat'] + dn['trans_fat'],
                'saturated_fat': dic_record_dish_nutrients['saturated_fat'] + dn['saturated_fat'],
                'protein': dic_record_dish_nutrients['protein'] + dn['protein'],
                'fat': dic_record_dish_nutrients['fat'] + dn['fat'],
                'carbohydrate': dic_record_dish_nutrients['carbohydrate'] + dn['carbohydrate'],
                'calories': dic_record_dish_nutrients['calories'] + dn['calories'],
                'calories': dic_record_dish_nutrients['free_sugar'] + dn['free_sugar']
            }]
        return lst_dic_all_user_nutrients
    
##推薦用
    def get_restaurant_dish(self):
        sql = '''
        SELECT DISTINCT restaurant_dish.id
        FROM restaurant_dish 
        RIGHT JOIN restaurant_dish_ingredients
        ON `restaurant_dish`.`id` = `restaurant_dish_ingredients`.`restaurant_dish_id`
        WHERE restaurant_dish_ingredients.name NOT LIKE '%null%'
        '''
        self.__cur.execute(sql)
        return self.__cur.fetchall()
    def get_distinct_dish_ingredients(self):
        sql = 'SELECT DISTINCT name FROM `restaurant_dish_ingredients`'
        self.__cur.execute(sql)
        return self.__cur.fetchall()
    def get_restaurant_dish_name(self, dish_id):
        sql = 'SELECT name FROM `restaurant_dish_ingredients` WHERE restaurant_dish_id = {}'.format(dish_id)
        self.__cur.execute(sql)
        return self.__cur.fetchall()
    def get_restaurant_dish_name(self, dish_id):
        sql = 'SELECT name FROM `restaurant_dish_ingredients` WHERE restaurant_dish_id = {}'.format(dish_id)
        self.__cur.execute(sql)
        return self.__cur.fetchall()
    def get_browse_not_record(self):
        sql = '''
        SELECT restaurant_dish_id FROM `user_browse` Browse
        WHERE NOT EXISTS( 
            SELECT restaurant_dish_id FROM `user_record_food` WHERE Browse.restaurant_dish_id = restaurant_dish_id)
        AND user_id = {}
        '''.format(self.user_id)
        self.__cur.execute(sql)
        return self.__cur.fetchall()
    def get_record_food(self):
        sql = "SELECT restaurant_dish_id FROM `user_record_food` WHERE EXISTS(SELECT user_id FROM `user_record` WHERE user_id = {})".format(str(self.user_id))
        self.__cur.execute(sql)
        return self.__cur.fetchall()
    def get_restaurant_dish_ingredients(self, dish_id):
        sql = 'SELECT name FROM `restaurant_dish_ingredients` WHERE restaurant_dish_id = {}'.format(dish_id)
        self.__cur.execute(sql)
        return self.__cur.fetchall()
##

    def connectDB(self):
        self.__conn = pymysql.connect(host="127.0.0.1", user="sideJR", passwd="08130263", db="at_ease_with_eating")
        self.__cur = self.__conn.cursor()
    def closeDB(self):
        self.__cur.close()
        self.__conn.close()
        
    def testsql(self, str_sql, mode): # mode: 'j' = json , 's' = simple
        start = time.time() # for testing
        self.__cur.execute(str_sql)
        end = time.time() # for testing
        out = (json.loads(self.__cur.fetchone()[0]) if (mode == 'j') else self.__cur.fetchone()[0])
        print('test execution time', end - start)
        return out