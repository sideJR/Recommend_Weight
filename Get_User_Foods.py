class Get_User_Foods:
    def __init__(self, user_id, cursor):
        # 使用者id
        self.user_id = user_id
        self.browse_foods = []
        self.record_foods = []
        self.collect_foods = []

        self.cursor = cursor

    # 取得瀏覽紀錄且沒有食用紀錄
    def get_browse_not_record(self):
        sql = 'SELECT restaurant_dish_id FROM `user_browse` Browse \
                WHERE NOT EXISTS( \
                    SELECT restaurant_dish_id FROM `user_record_food` WHERE Browse.restaurant_dish_id = restaurant_dish_id) \
                AND user_id = {}'.format(str(self.user_id))
        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        # 對應食材
        self.ingredient("Browse", result)        
           
    # 取得食用紀錄
    def get_record_food(self):
        sql = "SELECT restaurant_dish_id FROM `user_record_food` WHERE EXISTS(SELECT user_id FROM `user_record` WHERE user_id = {})".format(str(self.user_id))
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        
        # 對應食材
        self.ingredient("Record", result)

    # 取得收藏紀錄
    def get_collect_food(self):
        sql = "SELECT restaurant_dish_id FROM `user_collect` WHERE user_id = {}".format(str(self.user_id))
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        
        # 對應食材
        self.ingredient("Collect", result)
    
    # 找食材
    def ingredient(self, type, dish_ids):
        temp_ingredients = []

        for dish_id in dish_ids:
            sql = 'SELECT name FROM `restaurant_dish_ingredients` WHERE restaurant_dish_id = {}'.format(dish_id[0])
            self.cursor.execute(sql)
            ingredients = self.cursor.fetchall()

            # 找成分
            for item in ingredients:
                temp_ingredients.append(item[0])
            
            if type == 'Browse':
                self.browse_foods = temp_ingredients
            elif type == 'Record':
                self.record_foods = temp_ingredients
            else:
                self.collect_foods = temp_ingredients
    # 顯示瀏覽、食用、收藏紀錄對應之食材
    def show_count_ingredients(self):
        print("Browse =>", self.browse_foods)
        print("Record =>", self.record_foods)
        print("Collect =>", self.collect_foods)