from Recommend import Recommendation

user_id = 2
recommend = Recommendation(user_id)
list_recommend = recommend.list_recommendations()

print(list_recommend)
