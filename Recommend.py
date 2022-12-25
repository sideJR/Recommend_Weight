from Connect_DB import DB
from Get_User_Foods import Get_User_Foods

class Recommendation:
    def __init__(self, user_id) -> None: 
        # 使用者id   
        self.user_id = user_id
        # 總和權重
        self.weight_all_ingredients = {}
        # DB連接
        db = DB.db
        self.cursor = db.cursor()
        # 取得使用者瀏覽、食用、收藏紀錄
        self.user = Get_User_Foods(self.user_id, self.cursor)
        
    
    # 列出推薦清單
    def list_recommendations(self):
        # 取得使用者瀏覽、食用、收藏紀錄
        self.user_foods()
        # 計算食材權重
        self.weight_ingredients()

        # 取得推薦列表
        list_recommend = self.recommend()

        return list_recommend

    # 取得使用者瀏覽、食用、收藏紀錄
    def user_foods(self):        
        self.user.get_browse_not_record()
        self.user.get_record_food()
        self.user.get_collect_food()

        # 顯示使用者瀏覽、食用、收藏紀錄
        # user.show_count_ingredients()

    # 計算食材權重
    def weight_ingredients(self):        
        # 瀏覽權重
        weight_browse = 0.5
        # 食用權重
        weight_record = 1
        # 收藏權重
        weight_collect = 1.5
        

        sql = "SELECT DISTINCT name FROM `restaurant_dish_ingredients` "
        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        for i in result:
            self.weight_all_ingredients.update({i[0]: 0})

        # 統整
        user_all_ingredients = []
        user_all_ingredients.append(self.user.browse_foods)
        user_all_ingredients.append(self.user.record_foods)
        user_all_ingredients.append(self.user.collect_foods)        

        for i in range(0, len(user_all_ingredients)):
            weight = 0

            if (i == "0"):
                weight = weight_browse
            elif (i == "1"):
                weight = weight_record
            else:
                weight = weight_collect
            
            for j in user_all_ingredients[i]: 
                # Null食材不計算
                if(j == "Null"):
                    continue 
                count = user_all_ingredients[i].count(j) * weight
                count += self.weight_all_ingredients[j]

                self.weight_all_ingredients.update({j: count})
                                                         
        self.weight_all_ingredients = {k: v for k, v in sorted(self.weight_all_ingredients.items(), key=lambda item: item[1], reverse=True)}
        # print("self.weight_all_ingredients", self.weight_all_ingredients)

    # 預測喜好飲食
    def recommend(self):
        sql = "SELECT `id` FROM `restaurant_dish`"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        # 所有飲食
        all_dishs_id = []
        # 推薦列表
        list_recommend = []

        for i in result:
            all_dishs_id.append(i)

        for dish_id in all_dishs_id:
            sql = "SELECT name FROM `restaurant_dish_ingredients` WHERE `restaurant_dish_ingredients`.`restaurant_dish_id` = '{}'".format(str(dish_id[0]))
            self.cursor.execute(sql)
            result = self.cursor.fetchall()

            # 喜好分數
            score = 0

            for i in result:
                score += self.weight_all_ingredients[i[0]]
            
            list_recommend.append([dish_id[0], score])

        list_recommend.sort(key=lambda x: x[1], reverse=True)

        for i in list_recommend:
            index = list_recommend.index(i)
           
            if(i[-1] == 0):
                del list_recommend[index:len(list_recommend)]
                break

        return list_recommend