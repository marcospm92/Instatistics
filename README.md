# Instatistics

Estadísticas para Instagram usando la API no oficial de LevPasha.

## Documentación de las funciones


### Función búsqueda de ficheros
busqueda_fich(keyword, select)

#### Argumentos
- keyword: palabra clave que se buscará (string)
- select: índice del archivo a devolver (string)

#### Funcionamiento
Busca ficheros cuyo nombre coincida con el primer argumento.
Si se le pasa un segundo argumento distinto de "", devuelve el fichero
cuyo orden en la lista que imprime la función corresponda con el
argumento pasado.

#### Ejemplos de uso
busqueda_fich("ejemplo", "")     
  *1 - ejemplo_a*    
  *2 - ejemplo_b*    
  *3 - ejemplo_c*     
  
busqueda_fich("ejemplo", "2")     
  *return ejemplo_b*     

### Función login y peticiones API
login_peticiones()

#### Argumentos

#### Funcionamiento
Hace login en la API y guarda en archivos posts, media likers,
media commenters, followers, followings y actividad reciente,
para no tener que hacer luegp muchas peticiones y saturar servidores.

#### Ejemplo de uso
login_peticiones()

  *guarda:*       
    *- usuario_posts_fecha*       
    *- usuario_likers_fecha*      
    *- usuario_commenters_fecha*      
    *- usuario_following_fecha*   
    *- usuario_followers_fecha*   
    *- usuario_activity_fecha*

### Función Media Likers y Likes totales
media_likers()

#### Argumentos

#### Funcionamiento
Muestra un listado de los archivos que se pueden abrir para elegir
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

#### Ejemplo de uso
media_likers()

### Función Media Commenters
media_commenters()

#### Argumentos

#### Funcionamiento
Muestra un listado de los archivos que se pueden abrir para elegir
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

#### Ejemplo de uso
media_commenters()

### Función Followings y Followers
followings_followers()

#### Argumentos

#### Funcionamiento
Carga el archivo de followings y el de followers que escojamos.
Muestra el número de followings y followers que existen en esa fecha.
Si está la variable correspondiente a True, muestra los listados.
Muestra el número de personas a las que sigo pero no me siguen,
y si la variable está a True, sus cuentas.
Muestra el número de personas que me siguen pero yo no sigo,
y si la variable está a True, sus cuentas.

#### Ejemplo de uso
following_followers()

### Función Unfollows y Nuevos Followers
unfollows_new_followers()

#### Argumentos

#### Funcionamiento
Carga el archivo de followers reciente que escojamos.
Carga el archivo de followers antiguo que escojamos.
Compara ambos listados, y muestra el número de unfollows,
con las diferencias que existan. Si la variable correspondiente está
a True, muestra el listado de usuarios implicados.
Compara ambos listados, y muestra el número de nuevos followers,
con las diferencias que existan. Si la variable correspondiente está
a True, muestra el listado de usuarios implicados.

#### Ejemplo de uso
unfollows_new_followers()

### Función Actividad Reciente
actividad()

#### Argumentos

#### Funcionamiento
Carga el archivo de actividad reciente que escojamos.
Muestra el número de notificaciones, y si la variable correspondiente
está a True, muestra también el listado de notificaciones.
Muestra el número de follows, y si la variable correspondiente
está a True, muestra también el listado de notificaciones de follow.
Muestra las notificaciones de un usuario en particular, el que
esté definido en la variable user_notif.
Muestra un plot con el número de notificaciones por hora (últimas 24h).

#### Ejemplo de uso:
actividad()

### Función Menú Principal Interfaz Consola
modo_consola()

#### Argumentos

#### Funcionamiento
Muestra el menú principal de la aplicación en modo consola.
Gestiona la elección de la función a ejecutar según input.

#### Ejemplo de uso:
modo_consola()
