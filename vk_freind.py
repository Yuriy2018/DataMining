
import time
import vk_api
from pymongo import MongoClient

MongoDB = MongoClient()

def getMutual(user,users):

    param = {'source_uid': user,
             'order': 'hints',
             'target_uids': users
             }

    return vk_session.method('friends.getMutual', param)

def WriteInBase(User1,User2,result):

    Item = {'person_a': 'https://vk.com/id'+User1, 'person_b': 'https://vk.com/id'+User2, 'chain': result}

    dataBase = MongoDB['vk_handshake']
    collection = dataBase[str(User1) + ' - ' + User2]
    collection.insert_one(Item)

def supplementInfo(result):

    strId = ''
    for userId in result:
        strId = strId + str(userId) + ','


    param = {'user_ids': strId,
             # 'order': 'hints',
             }

    info = vk_session.method('users.get', param)

    resultFin = []
    for inf in info:
        user = 'id: ' + str(inf['id']) + ' ' + str(inf['first_name']) + ' '+ str(inf['last_name'])
        resultFin.append(user)

    return resultFin

def transformSpGet(sp,OwnerUser,OneFiltr):

    if sp['count'] == 0:
        return ''
    list = {}
    st = ''
    for idx,i in enumerate(sp['items']):

        id = str(i['id'])

        if id in OneFiltr:
            continue

        if idx != 0 and idx % 100 == 0:  # нам нужно сделать порции по 100 для списка идентификаторов строк метода friends.getMutual
            st.rstrip(', ')
            if st != '':
                list[st] = OwnerUser
                st = ''

        if i.get('first_name') == 'DELETED' or i.get('deactivated') == 'deleted': # Фильтруем удаленные аккаунты
            continue

        if i.get('deactivated') == 'banned': # Фильтруем забанненые аккаунты
            continue

        if i.get('can_access_closed') == False: # Фильтруем закрытые аккаунты
            continue

        OneFiltr.add(id)
        st = st + id + ','

    st.rstrip(', ')
    if st != '':
        list[st] = OwnerUser
        st = ''

    return list

def check_level1(UserId1,UserId2,list_fr_usr1,list_fr_usr2):

    for i in list_fr_usr1['items']:
        if str(i['id']) == UserId2:
           res = [UserId1]
           res.append([str(i['id'])])
           return res

    for i in list_fr_usr2['items']:
        if str(i['id']) == UserId1:
            res = [str(i['id'])]
            res.append([UserId2])
            return res

def check_conect(Mutal_usr):
    for s in Mutal_usr:
        if s["common_count"] > 0:
            return [str(s['id']), str(s['common_friends'][0])]

def deepsearch(user1, user2,list_fr_usr2,spFreindL2,OneFiltr):

    list_fr_usr1 = vk_session.method('friends.get', {'user_id': user1,
                                                     'fields': 'deactivated',
                                                     'order':'hints',})  # Список друзей первого пользователя  ограничение макс 5000


    result = check_level1(user1, user2, list_fr_usr1, list_fr_usr2)
    if result != None:
        return result

    transform1 = transformSpGet(list_fr_usr1,user1,OneFiltr)

    Mutal_usr2 = []

    for sp in transform1:
        Mutal_usr2 += getMutual(user2, sp)
        result2 = check_conect(Mutal_usr2)
        if result2 != None:
            return result2
        spFreindL2 += Mutal_usr2

def RunSearchLineOne(UserId1,UserId2,listFF):
    list_fr_usr1 = vk_session.method('friends.get', {'user_id': UserId1,
                                                     'fields': 'deactivated'})  # Список друзей первого пользователя
    list_fr_usr2 = vk_session.method('friends.get', {'user_id': UserId2,
                                                     'fields': 'deactivated'})  # Список друзей второго пользователя

    res = check_level1(UserId1, UserId2, list_fr_usr1, list_fr_usr2) # Проверяем входит ли Юзер1 в списокДрузей Юзер2 или наоборот...
    if res != None:
        return res

    OneFiltr = set()
    transform1 = transformSpGet(list_fr_usr1,UserId1,OneFiltr)  # Корректируем список друзей начльного юзера, убераем все аккаунты чьи доступы удалены или заблокированны

    Mutal_usr2 = []

    for sp in transform1:
        Mutal_usr2 += getMutual(UserId2, sp)  # Ищем общих друзей между конечным юзером и друзьями начального юзера

    result = check_conect(Mutal_usr2)
    if result != None:
        result.insert(0, UserId1)
        result.append(UserId2)
        return result


    OneFiltre = set() # Добавлям доаолнительно сет для хранения использованных айди юзеров, чтобы повторно не делать по ним запрос
    for usl2 in Mutal_usr2:  # Обходим всех друзей первого юзера и ищем общих друзей со вторым юзером
        result = deepsearch(str(usl2['id']), UserId2, list_fr_usr2, spFreindL2,OneFiltre)
        if result != None:
            result.insert(0, str(usl2['id']))

            result.insert(0, UserId1)
            result.append(UserId2)
            return result


    for us in spFreindL2:
        listFF.add(us['id'])

if __name__ == '__main__':

    timestart = time.time()
    spFreindL2 = []
    login_user = '****'
    login_pass = '****'

    vk_session = vk_api.VkApi(
        login_user, login_pass,
        app_id=6036185,
        api_version='5.101',
    )

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)

    UserId1 =  '3272139'   #'Укажите ID первого юзера'
    UserId2 =   '2349621'  #'Укажите ID второго юзера'

    listForFuture = set()

    result = RunSearchLineOne(UserId1,UserId2,listForFuture)
    if result != None:
        resultFin = supplementInfo(result)
        WriteInBase(UserId1,UserId2,resultFin)
        print(resultFin)

    currTime = time.time() - timestart

    listForFuture2= set()
    for user in listForFuture:
        print('Обрабатываем круг друзей юзера id: {user}'.format(user=user))
        result =  RunSearchLineOne(user,UserId2,listForFuture2)
        if result != None:
            ress = getMutual(UserId1, user)
            result.insert(0,UserId1)
            result.insert(1,str(ress[0]['common_friends'][0]))
            resultFin = supplementInfo(result)
            WriteInBase(UserId1, UserId2, resultFin)
            print(resultFin)
            break

    currTime = time.time() - timestart
    print('Время поиска {currTime} секунд'.format(currTime=round(currTime)))