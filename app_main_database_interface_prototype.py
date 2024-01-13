import pymongo
import datetime

class database_interface():

  def __init__(self, client = pymongo.MongoClient("mongodb://localhost:27017/")):
    self.client = client
    self.database = self.client["blog_app_database"]

  # ------------------------- методы для работы с постами -------------------------------------------
  def compose_and_post(self, auth_id : int, content : str):
    # здесь будет проверка на корректность контента в посте
    self.database["posts"].insert_one(
      {"author_id" : auth_id,
      "time_of_creation" : datetime.datetime.now(tz=datetime.timezone.utc),
      "content" : content,
      "comments" : []
      }
    )

  def find_posts(self, auth_id = None, time_span_from = datetime.datetime(2000, 1, 1), time_span_to = datetime.datetime.now(tz=datetime.timezone.utc)):
    # по умолчанию возвращает все посты
    # auth id всегда список из id, не одно значение
    if auth_id != None:
      result = self.database["posts"].find({'author_id' : { "$in" : auth_id}, 'time_of_creation' : {"$gt" : time_span_from}, 'time_of_creation' : {"$lt" : time_span_to}})
    else:
      result = self.database["posts"].find()

    discovered_posts = []
    for elm in result:
      discovered_posts.append(elm)
    return discovered_posts

  def add_comment_to_post(self, post_id, comment_text : str, comment_author : int):
    # модерация комментариев будет тут

    comment = {"comment_text" : comment_text,
              "comment_author" : comment_author,
              "comment_date" : datetime.datetime.now(tz=datetime.timezone.utc)}
    
    comment_list = self.database["posts"].find({'_id' : post_id})[0]["comments"] # берем список коммментарием
    self.database["posts"].update_one({'_id' : post_id}, {"$set" : {"comments" : comment_list + [comment]}}) # перезаписываем его обновленным списком

  # ------------------------- методы для работы с авторами -------------------------------------------

  def create_account(self, u_name, password_hash):

    check = self.database["users"].find({"user_name" : u_name})
    check_sucsessfull = not len([elm for elm in check])

    if not check_sucsessfull:
      return "name_collision_error"

    self.database["users"].insert_one({
      "user_name" : u_name,
      "user_password_hash" : password_hash,
      "user_data" : {},
      "subscriptions" : [],
      "ban" : False #наверное надо, чтобы бан был до какого-то времени
      })

    return "ok"

  def get_account_info(self, u_name, input_password_hash):
    # вернять данные аккаунта, если он существует и пароль верен
    try:
      result = self.database["users"].find({"user_name" : u_name})[0]
    except IndexError:
      return "user_does_not_exist"

    if input_password_hash == result["user_password_hash"]:
      return result # возможно, не стоит возвращать хеш пароля
    else:
      return "password_incorrect"

  def modify_account_data(self, u_name, input_password_hash, new_account_data : dict):
    # для внесения изменений надо подтвердить пароль
    # в принципе можно не просить пароль заново, а просто хранить хеш в данных сессиии где-то выше по уровню абстракции
    try:
      current_account_datails = self.database["users"].find({"user_name" : u_name})[0]
    except IndexError:
      return "user_does_not_exist"
    
    if input_password_hash == current_account_datails["user_password_hash"]:
      #все проверки пройдены, начинаем изменение
      for key in new_account_data.keys():
        # меняем значения в account data по ключам из new_account_data, пропускаем неверные ключи
        # менять id нельзя
        if key == "_id":
          continue
        try:
          current_account_datails[key] = new_account_data[key]
        except KeyError:
          continue
      # перезаписываем данные в базе
      self.database["users"].update_one({'_id' : current_account_datails['_id']}, {"$set" : current_account_datails})
      return "ok"
    else:
      return "password_incorrect"

  def get_user_id(self, user_name):
    try:
      requested_account_datails = self.database["users"].find({"user_name" : user_name})[0]
    except IndexError:
      return "user_does_not_exist"
    return requested_account_datails["_id"]
  
  def get_user_name(self, user_id):
    try:
      requested_account_datails = self.database["users"].find({"_id" : user_id})[0]
    except IndexError:
      return "user_does_not_exist"
    return requested_account_datails["user_name"]

    # добавить:
    

if __name__ == "main":
  database = database_interface()
  #compose_and_post(0, "hello, new visitor!")
  search_res = database.find_posts()
  for a in search_res:
    print(f"id: {a['_id']}, auth id: {a['author_id']}, posted at: {a['time_of_creation']}, {len(a['comments'])} comments, body: {a['content']}")
  print("---------------------")
  search_res = database.find_posts(auth_id = 1)
  for a in search_res:
    print(f"id: {a['_id']}, auth id: {a['author_id']}, posted at: {a['time_of_creation']}, {len(a['comments'])} comments, body: {a['content']}")
  print("---------------------")
  # создание аккаунта
  print(database.create_account("base_accont", 123456789))
  # просмотр данных аккаунта
  search_res = database.get_account_info("base_accont", 123456789)
  if type(search_res) != str:
    print(f"id: {search_res['_id']}, auth name: {search_res['user_name']}\
          , pword hash: {search_res['user_password_hash']}, user data: {search_res['user_data']}\
          , subbed: {search_res['subscriptions']}, banned: {search_res['ban']}")
  else:
    print(search_res)
  # изменениие данных аккаунта
  operation_res = database.modify_account_data("base_accont", 123456789, {"user_data" : {'name' : "edward smith", 'age' : 27}})
  print(operation_res)
  # просмотр обновленных данных аккаунта
  search_res = database.get_account_info("base_accont", 123456789)
  if type(search_res) != str:
    print(f"id: {search_res['_id']}, auth name: {search_res['user_name']}\
          , pword hash: {search_res['user_password_hash']}, user data: {search_res['user_data']}\
          , subbed: {search_res['subscriptions']}, banned: {search_res['ban']}")
  else:
    print(search_res)
  #add_comment_to_post(a['_id'], comment_text = "lol, I can leave comments here!", comment_author=0)