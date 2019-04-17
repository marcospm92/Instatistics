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
#username = ""

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
show_following = False
show_followers = False
show_unfollows = True
show_new_followers = True

rcParams.update({'figure.autolayout': True})


#################################################################################
#                                                                               #
#                         FUNCIÓN BÚSQUEDA DE FICHEROS                          #
#                                                                               #
#################################################################################
#                                                                               #
#   busqueda_fich(keyword, select)                                              #
#                                                                               #
#   Argumentos:                                                                 #
#       - keyword: palabra clave que se buscará (string)                        #
#       - select: índice del archivo a devolver (string)                        #
#                                                                               #
#   Funcionamiento:                                                             #
#       Busca ficheros cuyo nombre coincida con el primer argumento.            #
#       Si se le pasa un segundo argumento distinto de "", devuelve el fichero  #
#       cuyo orden en la lista que imprime la función corresponda con el        #
#       argumento pasado.                                                       #
#                                                                               #
#   Ejemplos de uso:                                                            #
#       busqueda_fich("ejemplo", "")                                            #
#           1 - ejemplo_a                                                       #
#           2 - ejemplo_b                                                       #
#           3 - ejemplo_c                                                       #
#                                                                               #
#       busqueda_fich("ejemplo", "2")                                           #
#           return ejemplo_b                                                    #
#                                                                               #
#################################################################################

def busqueda_fich(keyword, select):
    """ Busca ficheros cuyo nombre coincida con el primer argumento.
    Si se le pasa un segundo argumento distinto de "", devuelve el fichero
    cuyo orden en la lista que imprime la función corresponda con el
    argumento pasado.

    Ejemplos de uso:
        busqueda_fich("ejemplo", "")
            1 - ejemplo_a
            2 - ejemplo_b
            3 - ejemplo_c

        busqueda_fich("ejemplo", "2")
            return ejemplo_b """

    directorio = os.getcwd()
    indice = 1

    if(len(sys.argv) > 1):
        if(not os.path.isdir(sys.argv[1])):
            print(sys.argv[1],"no se reconoce como directorio")
            sys.exit(1)
        directorio = sys.argv[1]

    for root, dir, ficheros in os.walk(directorio):
        for fichero in sorted(ficheros, reverse = True):
            if (fichero[-1] != "o"): # Filtro los .thrashinfo
                if(keyword in fichero.lower()):
                    if select == "":
                        print(fichero)
                        print (indice, " - ", fichero[-8:-6], "/", fichero[-10:-8], "/", fichero[-12:-10],"  ", fichero[-6:-4], ":", fichero[-4:-2], ":", fichero[-2:])
                    else:
                        if(indice == int(select)):
                            return fichero
                    indice = indice + 1


#################################################################################
#                                                                               #
#                        FUNCIÓN LOGIN Y PETICIONES API                         #
#                                                                               #
#################################################################################
#                                                                               #
#   login_peticiones()                                                          #
#                                                                               #
#   Argumentos:                                                                 #
#                                                                               #
#   Funcionamiento:                                                             #
#       Hace login en la API y guarda en archivos posts, media likers,          #
#       media commenters, followers, followings y actividad reciente,           #
#       para no tener que hacer luegp muchas peticiones y saturar servidores.   #
#                                                                               #
#   Ejemplo de uso:                                                             #
#       login_peticiones()                                                      #
#           guarda:                                                             #
#               - usuario_posts_fecha                                           #
#               - usuario_likers_fecha                                          #
#               - usuario_commenters_fecha                                      #
#               - usuario_following_fecha                                       #
#               - usuario_followers_fecha                                       #
#               - usuario_activity_fecha                                        #
#                                                                               #
#################################################################################

def login_peticiones():
    """ Hace login en la API y guarda en archivos posts, media likers,
    media commenters, followers, followings y actividad reciente,
    para no tener que hacer luegp muchas peticiones y saturar servidores.

    Ejemplo de uso:
        login_peticiones()
            guarda:
                - usuario_posts_fecha
                - usuario_likers_fecha
                - usuario_commenters_fecha
                - usuario_following_fecha
                - usuario_followers_fecha
                - usuario_activity_fecha """

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

    print("\nObteniendo followings...")
    API.getUserFollowings(my_id)
    following_list = API.LastJson['users']
    fwng_filename = username + "_following_" + str(time.strftime("%y%m%d%H%M%S"))
    pickle.dump(following_list, open(fwng_filename, "wb"))
    print("Operación finalizada. Número de followings:", len(following_list))
    print ("¡Hecho!")

    print("\nObteniendo followers...")
    followers_list = []
    nxt_mx_id = ''
    while True:
        API.getUserFollowers(my_id, nxt_mx_id)
        temp = API.LastJson
        for item in temp["users"]:
            followers_list.append(item)
        time.sleep(2)
        if not temp['big_list']:
            break
        nxt_mx_id = temp["next_max_id"]
    fws_filename = username + "_followers_" + str(time.strftime("%y%m%d%H%M%S"))
    pickle.dump(followers_list, open(fws_filename, "wb"))
    print("Operación finalizada. Número de followers:", len(followers_list))
    print ("¡Hecho!")

    API.getRecentActivity()
    recent_activity = API.LastJson['old_stories']
    activity_filename = username + "_activity_" + str(time.strftime("%y%m%d%H%M%S"))
    pickle.dump(recent_activity, open(activity_filename, "wb"))


#################################################################################
#                                                                               #
#                     FUNCIÓN MEDIA LIKERS Y LIKES TOTALES                      #
#                                                                               #
#################################################################################
#                                                                               #
#   media_likers()                                                              #
#                                                                               #
#   Argumentos:                                                                 #
#                                                                               #
#   Funcionamiento:                                                             #
#       Muestra un listado de los archivos que se pueden abrir para elegir      #
#       uno de ellos. A partir de ese archivo se genera lo siguiente:           #
#           - Likes totales                                                     #
#           - Usuarios únicos que han dado like                                 #
#           - Media de likes por usuario                                        #
#           - Top usuarios que dan like. (Cantidad definida por n_users)        #
#           - Número de usuarios con 1, 2, 3, ... likes                         #
#           - Plot barras top usuarios que dan like a más posts                 #
#           - Plot barras total de likes                                        #
#           - Plot pie chart usuarios que dan like a más posts                  #
#           - Plot barras número de usuarios con 1, 2, 3, ... likes             #
#       Cada plot se puede comentar para decidir si mostrarlo o no              #
#                                                                               #
#   Ejemplo de uso:                                                             #
#       media_likers()                                                          #
#                                                                               #
#################################################################################

def media_likers():
    """ Muestra un listado de los archivos que se pueden abrir para elegir
    uno de ellos. A partir de ese archivo se genera lo siguiente:
        - Likes totales
        - Usuarios únicos que han dado like
        - Media de likes por usuario
        - Top usuarios que dan like. (Cantidad definida por n_users)
        - Número de usuarios con 1, 2, 3, ... likes
        - Plot barras top usuarios que dan like a más posts
        - Plot barras total de likes
        - Plot pie chart usuarios que dan like a más posts
        - Plot barras número de usuarios con 1, 2, 3, ... likes
    Cada plot se puede comentar para decidir si mostrarlo o no

    Ejemplo de uso:
        media_likers() """

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


#################################################################################
#                                                                               #
#                           FUNCIÓN MEDIA COMMENTERS                            #
#                                                                               #
#################################################################################
#                                                                               #
#   media_commenters()                                                          #
#                                                                               #
#   Argumentos:                                                                 #
#                                                                               #
#   Funcionamiento:                                                             #
#       Muestra un listado de los archivos que se pueden abrir para elegir      #
#       uno de ellos. A partir de ese archivo se genera lo siguiente:           #
#           - Comentarios totales                                               #
#           - Usuarios únicos que han comentado                                 #
#           - Media de comentarios por usuario                                  #
#           - Top usuarios que comentan. (Cantidad definida por n_users)        #
#           - Plot barras comentarios por día de la semana                      #
#           - Plot barras comentarios por hora del día                          #
#           - Plot barras comentarios por mes                                   #
#           - Plot barras comentarios por fecha en el año actual                #
#           - Plot barras comentarios por fecha en el mes actual (Comentado)    #
#           - Plot barras comentarios por fecha en mes escogido                 #
#           - Plot barras top usuarios que comentan                             #
#       Cada plot se puede comentar para decidir si mostrarlo o no              #
#                                                                               #
#   Ejemplo de uso:                                                             #
#       media_commenters()                                                      #
#                                                                               #
#################################################################################

def media_commenters():
    """ Muestra un listado de los archivos que se pueden abrir para elegir
    uno de ellos. A partir de ese archivo se genera lo siguiente:
        - Comentarios totales
        - Usuarios únicos que han comentado
        - Media de comentarios por usuario
        - Top usuarios que comentan. (Cantidad definida por n_users)
        - Plot barras comentarios por día de la semana
        - Plot barras comentarios por hora del día
        - Plot barras comentarios por mes
        - Plot barras comentarios por fecha en el año actual
        - Plot barras comentarios por fecha en el mes actual (Comentado)
        - Plot barras comentarios por fecha en mes escogido
        - Plot barras top usuarios que comentan
    Cada plot se puede comentar para decidir si mostrarlo o no

    Ejemplo de uso:
        media_commenters() """

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

    # Converts date from unix time to YYYY-MM-DD hh:mm:ss
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


#################################################################################
#                                                                               #
#                        FUNCIÓN FOLLOWINGS Y FOLLOWERS                         #
#                                                                               #
#################################################################################
#                                                                               #
#   followings_followers()                                                      #
#                                                                               #
#   Argumentos:                                                                 #
#                                                                               #
#   Funcionamiento:                                                             #
#       Carga el archivo de followings y el de followers que escojamos.         #
#       Muestra el número de followings y followers que existen en esa fecha.   #
#       Si está la variable correspondiente a True, muestra los listados.       #
#       Muestra el número de personas a las que sigo pero no me siguen,         #
#       y si la variable está a True, sus cuentas.                              #
#       Muestra el número de personas que me siguen pero yo no sigo,            #
#       y si la variable está a True, sus cuentas.                              #
#                                                                               #
#   Ejemplo de uso:                                                             #
#       following_followers()                                                   #
#                                                                               #
#################################################################################

def following_followers():
    """ Carga el archivo de followings y el de followers que escojamos.
    Muestra el número de followings y followers que existen en esa fecha.
    Si está la variable correspondiente a True, muestra los listados.
    Muestra el número de personas a las que sigo pero no me siguen,
    y si la variable está a True, sus cuentas.
    Muestra el número de personas que me siguen pero yo no sigo,
    y si la variable está a True, sus cuentas.

    Ejemplo de uso:
        following_followers() """

    # Numero de followings, gente a la que sigo
    busqueda_fich(username+"_following","")
    fwng_filename = input ("Introduce el numero del fichero a abrir: ")
    fwng_filename = busqueda_fich(username+"_following",fwng_filename)
    following_list = pickle.load(open(fwng_filename,"rb"))

    print ("Número de followings: %d" % len(following_list))
    user_list = map(lambda x: x['username'] , following_list)
    following_set = set(user_list)
    if (show_following == True):
        for i in range(len(following_set)):
            print ("    -", sorted((following_set))[i])

    # Numero de followers, gente que me sigue
    busqueda_fich(username+"_followers","")
    fws_filename = input ("Introduce el numero del fichero a abrir: ")
    fws_filename = busqueda_fich(username+"_followers",fws_filename)
    followers_list = pickle.load(open(fws_filename,"rb"))

    print ("Número de followers: %d" % len(followers_list))
    user_list = map(lambda x: x['username'] , followers_list)
    followers_set = set(user_list)
    if (show_followers == True):
        for i in range(len(followers_set)):
            print ("    -", sorted((followers_set))[i])

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


#################################################################################
#                                                                               #
#                     FUNCIÓN UNFOLLOWS Y NUEVOS FOLLOWERS                      #
#                                                                               #
#################################################################################
#                                                                               #
#   unfollows_new_followers()                                                   #
#                                                                               #
#   Argumentos:                                                                 #
#                                                                               #
#   Funcionamiento:                                                             #
#       Carga el archivo de followers reciente que escojamos.                   #
#       Carga el archivo de followers antiguo que escojamos.                    #
#       Compara ambos listados, y muestra el número de unfollows,               #
#       con las diferencias que existan. Si la variable correspondiente está    #
#       a True, muestra el listado de usuarios implicados.                      #
#       Compara ambos listados, y muestra el número de nuevos followers,        #
#       con las diferencias que existan. Si la variable correspondiente está    #
#       a True, muestra el listado de usuarios implicados.                      #
#                                                                               #
#   Ejemplo de uso:                                                             #
#       unfollows_new_followers()                                               #
#                                                                               #
#################################################################################

def unfollows_new_followers():
    """ Carga el archivo de followers reciente que escojamos.
    Carga el archivo de followers antiguo que escojamos.
    Compara ambos listados, y muestra el número de unfollows,
    con las diferencias que existan. Si la variable correspondiente está
    a True, muestra el listado de usuarios implicados.
    Compara ambos listados, y muestra el número de nuevos followers,
    con las diferencias que existan. Si la variable correspondiente está
    a True, muestra el listado de usuarios implicados.

    Ejemplo de uso:
        unfollows_new_followers() """

    count = 0

    busqueda_fich(username+"_followers","")
    print("Selecciona primero el fichero más reciente de los que quieres comparar")
    fws_filename_new = input ("Introduce el numero del fichero a abrir: ")
    fws_filename_new = busqueda_fich(username+"_followers",fws_filename_new)
    followers_list_new = pickle.load(open(fws_filename_new,"rb"))

    print("Selecciona ahora el fichero más antiguo de los que quieres comparar")
    fws_filename_old = input ("Introduce el numero del fichero a abrir: ")
    fws_filename_old = busqueda_fich(username+"_followers",fws_filename_old)
    followers_list_old = pickle.load(open(fws_filename_old,"rb"))

    print("Comparando " + fws_filename_new[-8:-6] + "/" + fws_filename_new[-10:-8] + "/" + fws_filename_new[-12:-10] + " " + fws_filename_new[-6:-4] + ":" + fws_filename_new[-4:-2] + ":" + fws_filename_new[-2:]
    + " con " + fws_filename_old[-8:-6] + "/" + fws_filename_old[-10:-8] + "/" + fws_filename_old[-12:-10] + " " + fws_filename_old[-6:-4] + ":" + fws_filename_old[-4:-2] + ":" + fws_filename_old[-2:])

    followers_new = map(lambda x: x['username'] , followers_list_new)
    followers_new = set(followers_new)

    followers_old = map(lambda x: x['username'] , followers_list_old)
    followers_old = set(followers_old)

    if (show_unfollows == True):
        print("\nLista de unfollows")
    for follower in followers_old:
        if follower not in followers_new:
            if (show_unfollows == True):
                print("-", follower)
            count +=1
    print("\nTotal de unfollows:", count)

    count = 0

    if (show_new_followers == True):
        print("\nLista de nuevos followers")
    for follower in followers_new:
        if follower not in followers_old:
            if (show_new_followers == True):
                print("-", follower)
            count +=1
    print("\nTotal de nuevos followers:", count)


#################################################################################
#                                                                               #
#                          FUNCIÓN ACTIVIDAD RECIENTE                           #
#                                                                               #
#################################################################################
#                                                                               #
#   actividad()                                                                 #
#                                                                               #
#   Argumentos:                                                                 #
#                                                                               #
#   Funcionamiento:                                                             #
#       Carga el archivo de actividad reciente que escojamos.                   #
#       Muestra el número de notificaciones, y si la variable correspondiente   #
#       está a True, muestra también el listado de notificaciones.              #
#       Muestra el número de follows, y si la variable correspondiente          #
#       está a True, muestra también el listado de notificaciones de follow.    #
#       Muestra las notificaciones de un usuario en particular, el que          #
#       esté definido en la variable user_notif.                                #
#       Muestra un plot con el número de notificaciones por hora (últimas 24h). #
#                                                                               #
#   Ejemplo de uso:                                                             #
#       actividad()                                                             #
#                                                                               #
#################################################################################

def actividad():
    """ Carga el archivo de actividad reciente que escojamos.
    Muestra el número de notificaciones, y si la variable correspondiente
    está a True, muestra también el listado de notificaciones.
    Muestra el número de follows, y si la variable correspondiente
    está a True, muestra también el listado de notificaciones de follow.
    Muestra las notificaciones de un usuario en particular, el que
    esté definido en la variable user_notif.
    Muestra un plot con el número de notificaciones por hora (últimas 24h).

    Ejemplo de uso:
        actividad() """

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


#################################################################################
#                                                                               #
#                   FUNCIÓN MENÚ PRINCIPAL INTERFAZ CONSOLA                     #
#                                                                               #
#################################################################################
#                                                                               #
#   modo_consola()                                                              #
#                                                                               #
#   Argumentos:                                                                 #
#                                                                               #
#   Funcionamiento:                                                             #
#       Muestra el menú principal de la aplicación en modo consola.             #
#       Gestiona la elección de la función a ejecutar según input.              #
#                                                                               #
#   Ejemplo de uso:                                                             #
#       modo_consola()                                                          #
#                                                                               #
#################################################################################

def modo_consola():
    """ Muestra el menú principal de la aplicación en modo consola.
    Gestiona la elección de la función a ejecutar según input.

    Ejemplo de uso:
        modo_consola() """

    while 1:

        print ("* INSTATISTICS *")
        print ("\n\t1. Login y peticiones")
        print ("\t2. Media Likers, Likes totales")
        print ("\t3. Media Commenters")
        print ("\t4. Following y Followers")
        print ("\t5. Encontrar unfollows y nuevos followers")
        print ("\t6. Notificaciones de actividad")
        print ("\t7. Posts")
        print ("\t8. Salir")

        if usr != "":
            print ("\nConectado como:", usr)
        else:
            print ("\nSin conectar")

        menu_ppal = int(input("Introduce un número (1-5) y pulsa Enter: "))

        if menu_ppal == 1:
            print ("LOGIN Y PETICIONES")

            login_peticiones()

        elif menu_ppal == 2:

            print ("MEDIA LIKERS, LIKES TOTALES")

            media_likers()

        elif menu_ppal == 3:

            print ("MEDIA COMMENTERS")

            media_commenters()

        elif menu_ppal == 4:

            print ("FOLLOWING Y FOLLOWERS")

            following_followers()

        elif menu_ppal == 5:
            print ("ENCONTRAR UNFOLLOWS Y NUEVOS FOLLOWERS")

            unfollows_new_followers()

        elif menu_ppal == 6:

            print ("NOTIFICACIONES DE ACTIVIDAD")

            actividad()

        elif menu_ppal == 7:

            print("POSTS")

        elif menu_ppal == 8:

            break

        else:
            print ("Error en la selección")



def main():

    modo_consola()
    return 0

if __name__ == '__main__':
    main()
