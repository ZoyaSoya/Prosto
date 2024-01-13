from app_main_database_interface_prototype import check_text_for_hatespeach
from app_main_database_interface_prototype import database_interface

database = database_interface()

class user_interface:

    def __init__(self, u_name, u_password_hash, register = False, verbal = True):
        # при создании класса пользователь нужно указать имя и пароль
        # имя уникально для каждого пользователя
        # register - создать новый аккаунт
        
        if register:
            operation_result = database.create_account(u_name, u_password_hash)
            if operation_result != 'ok':

                if verbal:
                    print(operation_result)

        account_info = database.get_account_info(u_name, u_password_hash)
        if type(account_info) is str: # ошибка при извлечении данных пользователя

            if verbal:
                print(account_info)
            del self

            return None
        
        self.baned = account_info['ban']
        if self.baned:
            if verbal:
                print("sorry, you are banned!")
            del self
            return

        self.uid = account_info['_id']
        self.uname = account_info['user_name']
        self.udata = account_info['user_data']
        self.subscr = account_info['subscriptions']

        self.pword_hash = u_password_hash

        if verbal:
            print("--------------------------")
            print(f"welcome, {self.uname} !")
            print("your profile data is:")
            for k in self.udata.keys():
                print(f"{k}: {self.udata[k]}")
            print(f"you have {len(self.subscr)} subscriptions:")
            for s in self.subscr:
                print(s)
            print("--------------------------")

    def post(self, post_content):
        database.compose_and_post(self.uid, post_content)

    def load_my_posts(self):
        self.posts = database.find_posts(auth_id = [self.uid])
        print("your posts: ")
        print("--------------------------")
        for p in self.posts:
            print(f"at: {p['time_of_creation']} | {p['content']}")
            if p["comments"] != []:
                for c in p["comments"]:
                    print(f"\tat: {c['comment_date']} | by: {c['comment_author']} | {c['comment_text']}")

    def comment(self, post, coment_content):
        # как передавать сюда пост хз, надо чтобы пользователь его где-то выбрал
        database.add_comment_to_post(post["_id"], comment_text = coment_content, comment_author = self.uname)

    def subscribe(self, user_name_to_sub):
        if user_name_to_sub in self.subscr:
            print("already_subscribed")
            return None
        
        if type(database.get_user_id(user_name_to_sub)) is str: # ошибка при получении данных пользователя
            print("user you want to subscribe to does not exist")
            return None
        else:
            # обновление данных в базе
            operation_result = database.modify_account_data(self.uname, self.pword_hash, {"subscriptions" : self.subscr + [user_name_to_sub]})
            if operation_result != 'ok':
                print(operation_result)
                return None
            # загрузка новых данных у себя
            print("-------------------------")
            print("restarting your session...")
            self.__init__(self.uname, self.pword_hash)
            return('ok')
        
    def unsubscribe(self, user_name_to_unsub, verbal = True):
        if user_name_to_unsub not in self.subscr:
            if verbal:
                print("not subscribed tothis user")
            return None
        else:
            new_subscr_list = [] # составляем новый список подписок без пользователя, от которого отписываемся
            for s in self.subscr:
                if s != user_name_to_unsub:
                    new_subscr_list.append(s)
            # обновление данных в базе
            operation_result = database.modify_account_data(self.uname, self.pword_hash, {"subscriptions" : new_subscr_list})
            if operation_result != 'ok':
                if verbal:
                    print(operation_result)
                return None
            # загрузка новых данных у себя
            if verbal:
                print("-------------------------")
                print("restarting your session...")
            self.__init__(self.uname, self.pword_hash, verbal = verbal)
            return('ok')

    def load_posts_form_subscriptions(self):
        # вот здесь надо как-то переделать, а то мы для каждого имени из списка сначала берем id из базы данных, а затем для каждого id берем имя
        # 2n ображений к базе данных выходит, слишком много
        self.subs_posts = database.find_posts(auth_id = [database.get_user_id(s) for s in self.subscr])
        print("--------------------------")
        print("posts from your subscriptions: ")
        print("--------------------------")
        for p in self.subs_posts:
            print(f"at: {p['time_of_creation']} | by: {database.get_user_name(p['author_id'])} | {p['content']}")
            if p["comments"] != []:
                for c in p["comments"]:
                    print(f"\tat: {c['comment_date']} | by: {c['comment_author']} | {c['comment_text']}")
    

    def clear_cache(self):
        del self.posts
        del self.subs_posts

        
    def clear_subs(self):
        # удаление подписок на несуществующих пользователей
        print("--------------------------")
        print("checking your subscriptions")
        print("--------------------------")
        for s in self.subscr:
            print(f"checking {s}... ", end = '')
            if type(database.get_user_id(s)) is str: # если пользователя нет, то вместо id он вернет строку с ошибкой
                self.unsubscribe(s, verbal= False)
                print(" unexistant account, unsub.")
            else:
                print(" ok")                

    # нужно добавить возможность загружать пользователя в режиме обозревания (когда заходишь на чужую страничку)

    # !!!!!!!!!!!!! больно много раз подглядываем id по имени и наоборот, надо что-то с этим делать
        
#ui = user_interface("base_accont", 123456789)
# ui.post("hi!")
# ui.post("this is my second post")
# ui.post("this is my third post")
# ui.post("this is a post")
#ui.load_my_posts()
#ui.comment(ui.posts[0], "wow, i can leave comments here!")
#print(check_text_for_hatespeach('Ты че сучара?!'))

# ui = user_interface("admin", 0000)
# ui.load_my_posts()
# ui.post("Привет!")
# ui.subscribe("base_accont")
# ui.load_posts_form_subscriptions()
# ui.clear_subs()