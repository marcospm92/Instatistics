# Imports y login

from InstagramAPI.InstagramAPI import InstagramAPI
import numpy as np
import time
import getpass
import pickle
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib import rcParams
import operator
import pandas as pd
from pandas.io.json import json_normalize
import sys, os
from datetime import datetime
import calendar


username = input("Usuario: ")
username = ""

usr = ""
myposts = []
has_more_posts = True
max_id = ""
likers = []
commenters = []
users = []
m_id = 0
l_dict = {}
n_users = 15 # Numero de usuarios que queremos para plots
user_notif = "nombre_usuario" # Para filtrar las notificaciones de un único usuario
show_not_following_back = False # Si lo pongo a true detalla las cuentas que sigo y no me siguen
show_fans = False # Si lo pongo a True detalla las cuentas que me siguen y yo no sigo
show_notificaciones = False
show_notificaciones_follow = False

rcParams.update({'figure.autolayout': True})

def busqueda_fich(keyword, select):
    directorio = os.getcwd()
    indice = 1

    if(len(sys.argv) > 1):
        if(not os.path.isdir(sys.argv[1])):
            print(sys.argv[1],"no se reconoce como directorio")
            sys.exit(1)
        directorio = sys.argv[1]

    for root, dir, ficheros in os.walk(directorio):
        for fichero in sorted(ficheros, reverse = True):
            if(keyword in fichero.lower()):
                if select == "":
                    print (indice, " - ", fichero[-8:-6], "/", fichero[-10:-8], "/", fichero[-12:-10],"  ", fichero[-6:-4], ":", fichero[-4:-2], ":", fichero[-2:])
                else:
                    if(indice == int(select)):
                        return fichero
                indice = indice + 1

while 1:

    print ("* INSTATISTICS *")
    print ("\t1. Login y peticiones")
    print ("\t2. Media Likers, Likes totales")
    print ("\t3. Media Commenters")
    print ("\t4. Following y Followers")
    print ("\t5. Notificaciones de actividad")
    print ("\t6. Posts")

    if usr != "":
        print ("\nConectado como:", usr)
    else:
        print ("\nSin conectar")

    menu_ppal = int(input("Introduce un número (1-5) y pulsa Enter: "))

    if menu_ppal == 1:
        print ("LOGIN Y PETICIONES")

        pwd = getpass.getpass("Contraseña:")
        #pwd = ""

        API = InstagramAPI(username, pwd)

        API.login()
        time.sleep(2)
        # Datos generales del perfil. Muestro el status y el nombre

        API.getProfileData()
        result = API.LastJson
        my_id = API.LastJson['user']['pk']

        usr = result['user']['full_name']
        print ("Conectado como:", usr)

        # Datos del TimeLine. Puedo acceder a un montón de datos, revisar en código si interesa

        API.timelineFeed()
        result = API.LastJson
        #print(result)


        # Recorro mis posts, lo guardo todo en usuario_posts. De esta manera no tengo que acceder al servidor cada vez
        print("\nObteniendo posts...")
        while has_more_posts:
            API.getSelfUserFeed(maxid = max_id)
            if API.LastJson['more_available'] is not True:
                has_more_posts = False # Stop condition

            max_id = API.LastJson.get('next_max_id', '')
            myposts.extend(API.LastJson['items']) # Merge lists
            time.sleep(2) # Slows the script down to avoid flooding the servers

            if has_more_posts:
                print ("Operación en proceso. Leídos", len(myposts), "posts")

        print ("Operación finalizada. Número de posts:",len(myposts))

        posts_filename = username + "_posts_" + str(time.strftime("%y%m%d%H%M%S"))
        pickle.dump(myposts,open(posts_filename,"wb")) # Guardo en un fichero para cuando sean muchos que no tarde en cargar. Falta cargarlo más adelante


        print("\nObteniendo Media Likers...")
        if((len(myposts)*2/60.) >= 1):
            print ("Espera %.1f minutos" % (len(myposts)*2/60.))
        else:
            print ("Espera %.d segundos" % (len(myposts)*2))

        for i in range(len(myposts)):
            m_id = myposts[i]['id']
            API.getMediaLikers(m_id)
            likers += [API.LastJson]
            likers[i]['post_id'] = m_id

            time.sleep(2)

        likers_filename = username + "_likers_" + str(time.strftime("%y%m%d%H%M%S"))
        pickle.dump(likers,open(likers_filename,"wb")) # Guardo en un fichero para cuando sean muchos que no tarde en cargar
        print ("¡Hecho!")

        print("\nObteniendo Media Commenters...")
        if((len(myposts)*2/60.) >= 1):
            print ("Espera %.1f minutos" % (len(myposts)*2/60.))
        else:
            print ("Espera %.d segundos" % (len(myposts)*2))

        for i in range(len(myposts)):
            m_id = myposts[i]['id']
            API.getMediaComments(m_id)
            commenters += [API.LastJson]
            commenters[i]['post_id'] = m_id

            time.sleep(2)

        commenters_filename = username + "_commenters_" + str(time.strftime("%y%m%d%H%M%S"))
        pickle.dump(commenters,open(commenters_filename,"wb")) # Guardo en un fichero para cuando sean muchos que no tarde en cargar
        print ("¡Hecho!")


        API.getUserFollowings(my_id)
        following_list = API.LastJson['users']
        fwng_filename = username + "_following_" + str(time.strftime("%y%m%d%H%M%S"))
        pickle.dump(following_list, open(fwng_filename, "wb"))


        API.getUserFollowers(my_id)
        followers_list = API.LastJson['users']
        fws_filename = username + "_followers_" + str(time.strftime("%y%m%d%H%M%S"))
        pickle.dump(followers_list, open(fws_filename, "wb"))


        API.getRecentActivity()
        recent_activity = API.LastJson['old_stories']
        activity_filename = username + "_activity_" + str(time.strftime("%y%m%d%H%M%S"))
        pickle.dump(recent_activity, open(activity_filename, "wb"))

    elif menu_ppal == 2:

        print ("MEDIA LIKERS, LIKES TOTALES")
        # Recoge los media likers
        busqueda_fich(username+"_likers","")
        likers_filename = input ("Introduce el numero del fichero a abrir: ")
        likers_filename = busqueda_fich(username+"_likers",likers_filename)
        likers = pickle.load(open(likers_filename,"rb"))

        # PROBANDO DATAFRAMES. Each row of df_likers represents a single like

        # Normalize likers by getting the 'users' list and the post_id of each like
        df_likers = json_normalize(likers, 'users', ['post_id'])
        # Add 'content_type' column to know the rows are likes
        df_likers['content_type'] = 'like'
        # Añado una columna de numero de likes de cada usuario
        df_likers['num_likes'] = df_likers.groupby('username')['username'].transform('count')

        # Numero total de likes en publicaciones
        print ("Likes totales:", df_likers.shape[0]) # shape[0] representa el numero de filas

        # Numero total de usuarios únicos que han dado like
        print ("Usuarios únicos que han dado like:", df_likers.username.nunique()) # nunique cuenta valores unicos en una columna

        # Media de likes por usuario [likes totales / usuarios que han dado like alguna vez]
        print ("Media de likes por usuario: %.2f" % (df_likers.shape[0] / df_likers.username.nunique()))

        # As each row represents a like, we can perform a value_counts on username and slice it to the first 10 items (pandas already order it for us)
        print("\nTop", n_users, "Media Likers")
        print(df_likers.username.value_counts()[:n_users])

        # ESTA PARTE HAY QUE RETOCARLA, NO ME GUSTA COMO SE VE LA TABLA
        print("Numero Likes     Numero usuarios")
        print(df_likers.sort_values(by=['num_likes'])['num_likes'].value_counts(sort=False))
        # PLOTS

        # Plot barras top usuarios que dan like a más posts
        plt.figure()
        df_likers.username.value_counts()[:n_users].plot(kind='bar', title='Top Media Likers', grid=False, figsize=(12,6))

        # Plot barras total likes
        plt.figure()
        df_likers.username.value_counts().plot(kind='bar', title='Top Media Likers', grid=False, figsize=(12,6))

        # Plot pie chart usuarios que dan like a más posts
        plt.figure()
        df_likers.username.value_counts()[:n_users].plot(kind='pie', title='Top Media Likers distribution', autopct='%1.1f%%', figsize=(12,6))

        # Plot numero de usuarios con X likes
        plt.figure()
        plt.title("Numero de usuarios con X likes")
        df_likers.sort_values(by=['num_likes'])['num_likes'].value_counts(sort=False).plot(kind='bar')

        plt.show()

    elif menu_ppal == 3:

        print ("MEDIA COMMENTERS")
        # Recoge los media commenters
        busqueda_fich(username+"_commenters","")
        commenters_filename = input ("Introduce el numero del fichero a abrir: ")
        commenters_filename = busqueda_fich(username+"_commenters",commenters_filename)
        commenters = pickle.load(open(commenters_filename,"rb"))

        # PROBANDO DATAFRAMES. Each row of df_commenters represents a single comment

        # Include username and full_name of commenter in 'comments' list of dicts
        for i in range(len(commenters)):
            if len(commenters[i]['comments']) > 0: # checks if there is any comment on the post
                for j in range(len(commenters[i]['comments'])):
                    # Puts username/full_name one level up
                    commenters[i]['comments'][j]['username'] = commenters[i]['comments'][j]['user']['username']
                    commenters[i]['comments'][j]['full_name'] = commenters[i]['comments'][j]['user']['full_name']

        # Create DataFrame
        # Normalize commenters to have 1 row per comment, and gets 'post_id' from parent
        df_commenters = json_normalize(commenters, 'comments', 'post_id')

        # Get rid of 'user' column as we already handled it above
        del df_commenters['user']

        # Numero total de comentarios en publicaciones
        print ("Comentarios totales:", df_commenters.shape[0]) # shape[0] representa el numero de filas

        # Numero total de usuarios únicos que han comentado
        print ("Usuarios únicos que han comentado:", df_commenters.username.nunique()) # nunique cuenta valores unicos en una columna

        # Media de comentarios por usuario [comentarios totales / usuarios que han comentado alguna vez]
        print ("Media de comentarios por usuario: %.2f" % (df_commenters.shape[0] / df_commenters.username.nunique()))


        # As each row represents a like, we can perform a value_counts on username and slice it to the first 10 items (pandas already order it for us)
        print("\nTop", n_users, "Commenters")
        print(df_commenters.username.value_counts()[:n_users])

        # Converts date from unix time to YYYY-MM-DD hh24:mm:ss
        df_commenters.created_at = pd.to_datetime(df_commenters.created_at, unit='s')
        df_commenters.created_at_utc = pd.to_datetime(df_commenters.created_at_utc, unit='s')
        # Create a column to show when a a comment was created in Spain time
        df_commenters['created_at_sp'] = df_commenters.created_at_utc.dt.tz_localize('UTC').dt.tz_convert('Europe/Madrid')

        # PLOTS

        # Plot que muestra el número de mensajes por dia de la semana
        # Load example data into DataFrame
        df3 = pd.DataFrame({"created_at_sp":df_commenters['created_at_sp']})
        # Transform to a count
        a = df3.groupby(df_commenters['created_at_sp'].dt.weekday).count()
        # Si no aparece el dia en la cuenta (porque hay 0 valores), lo añado a mano. Un poco lioso pero sale bien
        for day in range(1,7):
            if day not in a.created_at_sp:
                c = a[:day]
                b = pd.DataFrame([0], columns=["created_at_sp"], index = [day])
                c = c.append(b)
                a = c.append(a[day:])
        a.plot(kind="bar", title="Comments por día de la semana")
        plt.xticks(ticks=range(7), labels=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])


        # Plot que muestra el número de mensajes por hora del día
        # Transform to a count
        a = df3.groupby(df_commenters['created_at_sp'].dt.hour).count()
        # Si no aparece la hora en la cuenta (porque hay 0 valores), lo añado a mano. Un poco lioso pero sale bien
        for hour in range(24):
            if hour not in a.created_at_sp:
                c = a[:hour]
                b = pd.DataFrame([0], columns=["created_at_sp"], index = [hour])
                c = c.append(b)
                a = c.append(a[hour:])
        a.plot(kind="bar", title="Comments por hora")


        # Plot que muestra el número de mensajes por mes
        # Transform to a count
        a = df3.groupby(df_commenters['created_at_sp'].dt.month).count()
        # Si no aparece el mes en la cuenta (porque hay 0 valores), lo añado a mano. Un poco lioso pero sale bien
        for month in range(13):
            if month not in a.created_at_sp:
                c = a[:month]
                b = pd.DataFrame([0], columns=["created_at_sp"], index = [month])
                c = c.append(b)
                a = c.append(a[month:])
        # En este caso he tenido que hacerlo un poco diferente, si partía de 1 no me lo ordenaba bien, así que parto de 0 y corto ese valor
        a = a[1:]
        a.plot(kind="bar", title="Comments por mes")
        plt.xticks(ticks=range(12), labels=["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])


        # Plot que muestra el número de mensajes por fecha en el año actual
        # Transform to a count
        a = df3.groupby(df_commenters['created_at_sp'].dt.date).count()
        # Si no aparece el dia en la cuenta (porque hay 0 valores), lo añado a mano. Un poco lioso pero sale bien
        for date in pd.date_range("2019-01-01", pd.datetime.today()):
            if date.date() not in a.created_at_sp:
                c = a[:date.date()]
                b = pd.DataFrame([0], columns=["created_at_sp"], index = [date.date()])
                c = c.append(b)
                a = c.append(a[date.date():])
        # En este caso he tenido que hacerlo un poco diferente, si partía de 1 no me lo ordenaba bien, así que parto de 0 y corto ese valor
        #a = a[1:]
        a.plot(kind="bar", figsize=(12,6), title="Comments por fecha en 2019")


        # Plot que muestra el número de mensajes por fecha en el mes actual. Un poco inútil teniendo el siguiente
        #df4 = df3.copy()
        #for i in range(len(df4)):
    #        if (df_commenters['created_at_sp'][i].month != datetime.today().month):
    #            df4 = df4.drop([i], axis = 0)
    #    a = df4.groupby(df_commenters['created_at_sp'].dt.date).count()
        # Si no aparece la fecha en la cuenta (porque hay 0 valores), lo añado a mano. Un poco lioso pero sale bien
    #    for date in pd.date_range(datetime(datetime.today().year, datetime.today().month, 1), pd.datetime.today()):
    #        if date.date() not in a.created_at_sp:
    #            c = a[:date.date()]
    #            b = pd.DataFrame([0], columns=["created_at_sp"], index = [date.date()])
    #            c = c.append(b)
    #            a = c.append(a[date.date():])

        #a.plot(kind="bar", figsize=(12,6), title="Comments por fecha en el mes actual")


        # Plot que muestra el número de mensajes por fecha en el mes escogido
        mes = input("Escribe el número de mes a visualizar: ")
        df4 = df3.copy()
        for i in range(len(df4)):
            if (df_commenters['created_at_sp'][i].month != int(mes)):
                df4 = df4.drop([i], axis = 0)
        a = df4.groupby(df_commenters['created_at_sp'].dt.date).count()
        # Si no aparece la fecha en la cuenta (porque hay 0 valores), la añado a mano. Un poco lioso pero sale bien
        for date in pd.date_range(datetime(2019, int(mes), 1), datetime(2019, int(mes), calendar.monthrange(2019, int(mes))[1])):
            if date.date() not in a.created_at_sp:
                c = a[:date.date()]
                b = pd.DataFrame([0], columns=["created_at_sp"], index = [date.date()])
                c = c.append(b)
                a = c.append(a[date.date():])

        a.plot(kind="bar", figsize=(12,6), title="Comments por fecha en el mes escogido")

        # Plot top commenters
        plt.figure()
        df_commenters['username'].value_counts()[:n_users].plot(kind='bar', figsize=(12,6), title='Top Commenters')

        plt.show()

    elif menu_ppal == 4:

        print ("FOLLOWING Y FOLLOWERS")

        # Numero de followings, gente a la que sigo
        busqueda_fich(username+"_following","")
        fwng_filename = input ("Introduce el numero del fichero a abrir: ")
        fwng_filename = busqueda_fich(username+"_following",fwng_filename)
        following_list = pickle.load(open(fwng_filename,"rb"))

        print ("Número de followings: %d" % len(following_list))
        user_list = map(lambda x: x['username'] , following_list)
        following_set = set(user_list)

        # Numero de followers, gente que me sigue

        busqueda_fich(username+"_followers","")
        fws_filename = input ("Introduce el numero del fichero a abrir: ")
        fws_filename = busqueda_fich(username+"_followers",fws_filename)
        followers_list = pickle.load(open(fws_filename,"rb"))

        print ("Número de followers: %d" % len(followers_list))
        user_list = map(lambda x: x['username'] , followers_list)
        followers_set = set(user_list)

        # Numero de personas a las que sigo pero no me siguen, y sus cuentas
        not_following_back = following_set - followers_set
        print ("Número de gente a la que sigo y no me sigue:", len(not_following_back))
        if (show_not_following_back == True):
            for i in range(len(not_following_back)):
                print ("    -", sorted((not_following_back))[i])

        # Numero de personas que me siguen pero no sigo, y sus cuentas
        fans = followers_set - following_set
        print ("Número de gente que me sigue y yo no sigo:", len(fans))
        if (show_fans == True):
            for i in range(len(fans)):
                print ("    -", sorted((fans))[i])


    elif menu_ppal == 5:

        print ("NOTIFICACIONES DE ACTIVIDAD")

        # Notificaciones de actividad de las últimas 24h
        act_dates = []
        follow_dates = []

        busqueda_fich(username+"_activity","")
        activity_filename = input ("Introduce el numero del fichero a abrir: ")
        activity_filename = busqueda_fich(username+"_activity",activity_filename)
        activity = pickle.load(open(activity_filename,"rb"))

        print ("Número de notificaciones:",len(activity))
        for notification in activity:
            act_dates.append (pd.to_datetime(time.ctime(notification['args']['timestamp'])))
            if (show_notificaciones == True):
                print (pd.to_datetime(time.ctime(notification['args']['timestamp'])), ":", end = " ")
                print (notification['args']['text'])

        for notification in activity:
            if(notification['type']==3): # FOLLOW
                follow_dates.append (pd.to_datetime(time.ctime(notification['args']['timestamp'])))
                if (show_notificaciones_follow == True):
                    print (pd.to_datetime(time.ctime(notification['args']['timestamp'])), ":", end = " ")
                    print (notification['args']['text'])

        print ("Número de follows:",len(follow_dates))


        # Notificaciones de un sólo usuario (el definido al principio)

        for notification in activity:
            text = notification['args']['text']
            if user_notif in text:
                print (text)

        # Plot que muestra el número de notificaciones por hora (del listado total de últimas notificaciones)
        # Load example data into DataFrame
        df = pd.DataFrame({"Hora":act_dates})
        # Transform to a count
        a = df.groupby(df["Hora"].dt.hour).count()
        # Si no aparece la hora en la cuenta (porque hay 0 valores), lo añado a mano. Un poco lioso pero sale bien
        for hour in range(24):
            if hour not in a.Hora:
                c = a[:hour]
                print(c)
                b = pd.DataFrame([0], columns=["Hora"], index = [hour])
                c = c.append(b)
                a = c.append(a[hour:])
                print(a)
        a.plot(kind="bar", title="Notificaciones por hora")
        plt.show()

    elif menu_ppal == 6:

        print("POSTS")

    else:
        print ("Error en la selección")
