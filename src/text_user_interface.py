import app_main_user_interface_prototype as user_interface

ui = None

while(True):
    user_srtring = input().split()

    if user_srtring[0] in ["login", "log", "l"]:
        uname = user_srtring[1]
        pword = user_srtring[2]
        #---------------------
        ui = user_interface.user_interface(uname, pword)
        
    if user_srtring[0] in ["register", "reg", "r"]:

        #---------------------
        uname = user_srtring[1]
        pword = user_srtring[2]
        #---------------------
        ui = user_interface.user_interface(uname, pword, register=True)
    
    if ui == None:
        print("you need to log in first")
        continue
    
    if user_srtring[0] in ["post", "p"]:
        ptext = ' '.join(user_srtring[1:])
        #---------------------
        ui.post(ptext)
        
    if user_srtring[0] in ["posts", "load", "show"]:
        ui.load_my_posts()
        #---------------------
        print("")
        
    if user_srtring[0] in ["comment", "com", "c"]:
        # слишком сложно
        #user_srtring[0]
        #---------------------
        print("")
        
    if user_srtring[0] in ["subscribe", "sub", "s"]:
        subj = user_srtring[1]
        #---------------------
        ui.subscribe(subj)
        
    if user_srtring[0] in ["unsubscribe", "unsub", "u"]:
        subj = user_srtring[1]
        #---------------------
        ui.unsubscribe(subj)

    if user_srtring[0] in ["subs", "loads", "wall"]:
        
        #---------------------
        ui.load_posts_form_subscriptions()
        
    if user_srtring[0] in ["clear"]:
        
        #---------------------
        ui.clear_subs()
        
    if user_srtring[0] in ["relog", "unlog", "leave", "ul"]:
        
        #---------------------
        ui = None