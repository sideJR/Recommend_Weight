from Recommend import Recommendation
import skfuzzy_dict
import db_aewe
import random

def search_skfuzzy_r(user_id, lst_recommend, lst_recommend_score):
    db = db_aewe.DBAwae(user_id) 
    df = skfuzzy_dict.DictFuzzy()
    lst_dic = df.get_lst_dict(db.select_user_diseases(), db.select_user_indicators_nutrients_day_limit(), db.get_all_user_nutrients(lst_recommend), lst_recommend_score)         
    db.closeDB()

    return lst_dic 


##執行碼
recommend = Recommendation("2")
# 推薦結果
lst_recommend = recommend.list_recommendations()
print("lst_recommend：", lst_recommend)


lst_recommend_id = []
lst_recommend_score = []

for i in lst_recommend:
    lst_recommend_id.append(i[0])
    lst_recommend_score.append(i[1])

# 模糊分數
lst_health_score = search_skfuzzy_r("2", lst_recommend_id, lst_recommend_score)
print(lst_health_score)
