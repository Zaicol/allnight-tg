from telebot import *
from models import *
from markups import *
from strings import *
from telegram_bot_calendar import DetailedTelegramCalendar
from os import path
from output_methods import *
from datetime import datetime


with open('token-ps.txt') as f:
    url = f.readline()
bot = TeleBot(url)
users_data = {}
print('Начало')
admins = {
    '531704720': 'Alex',
    '289208255': 'Zaicol',
    '460205942': 'Matvey'
}

send = 0

if send:
    for n in admins:
        bot.send_message(int(n), 'Бот (пере)запущен')
else:
    bot.send_message(289208255, 'Бот (пере)запущен')


def do_log(uid, place, other=''):
    uid = str(uid)
    if uid in admins:
        print(admins[uid] + '\t' + place + '\t' + other)
    else:
        print(admins[uid] + '\t' + place + '\t' + other)


def get_users_id(admin=True):
    ses = Session()
    s = ses.query(Users)
    if admin:
        s = s.where(Users.admin == 1)
    s = s.all()
    ses.close()
    users_ids = [x.id for x in s]
    return users_ids


def get_user_data(uid, key, default=""):
    if uid in users_data:
        if key in users_data[uid]:
            return users_data[uid][key]
        users_data[uid][key] = default
    else:
        users_data[uid] = {key: default}
    return default


def add_user_data(uid, key, val):
    if uid in users_data:
        users_data[uid][key] = val
    else:
        users_data[uid] = {key: val}
    return 1


@bot.message_handler(commands=['myid'])
def id_handler(message):
    do_log(message.from_user.id, 'ID')
    bot.register_next_step_handler(message, main_handler)
    bot.send_message(message.from_user.id, message.from_user.id, reply_markup=markup_main)


@bot.message_handler(commands=['test'])
def test_handler(message):
    bot.send_message(message.from_user.id, fp.date.date(), reply_markup=markup_main)


@bot.message_handler(commands=['start'])
def start_handler(message):
    do_log(message.from_user.id, 'Start')
    markup = markup_main
    ses = Session()
    usids = ses.query(Users).all()
    usids = [x.id for x in usids]
    uname = message.from_user.username
    if not uname:
        uname = message.from_user.first_name
    if message.from_user.id in get_users_id():
        markup = markup_main_adm
    if message.from_user.id not in usids:
        rep = startup_new
        new_user = Users(id=message.from_user.id, name=uname, admin=0)
        ses.add(new_user)
        ses.commit()
    else:
        us = ses.query(Users).where(Users.id == message.from_user.id).first()
        if uname != us.name:
            print('\nDatabase update:\n{}\t{} -> {}\n'.format(us.id, us.name, uname))
            us.name = uname
            ses.commit()
        rep = startup_old
    bot.register_next_step_handler(message, main_handler)
    bot.send_message(message.from_user.id, rep, reply_markup=markup)
    ses.close()


@bot.message_handler(commands=['admin'])
def admin_panel(message):
    do_log(message.from_user.id, 'Panel')
    if message.from_user.id not in get_users_id():
        bot.register_next_step_handler(message, main_handler)
        bot.send_message(message.from_user.id, 'Неизвестная команда', reply_markup=markup_main)
        return
    markup = markup_adm
    t = message.text
    rep = unknown_com
    if t == 'Назад':
        ns = main_handler
        rep = 'Возвращаемся в главное меню'
        markup = markup_main_adm
    else:
        ns = admin_panel
        if t == 'ID':
            rep = 'Ваш ID:\n' + str(message.from_user.id)
        elif t == 'Тест':
            rep = 'Кнопка для тестовых штук'
        elif t == 'Админы':
            ses = Session()
            s = ses.query(Users).where(Users.admin == 1).all()
            ses.close()
            admlist = [str(x.id) + '\t' + x.name for x in s]

            rep = "Список администраторов\nID\tИмя\n"
            rep += '\n'.join(admlist)
            markup = markup_adm_list
            ns = admin_list_handler
        elif t == 'Места':
            rep = places_list_for_admins()
            markup = markup_places_list
            ns = place_list_handler

        elif t == 'Статистика':
            rep = "Панель статистики"
            markup = markup_stat
            ns = stats_handler

    bot.register_next_step_handler(message, ns)
    bot.send_message(message.from_user.id, rep, reply_markup=markup)


def admin_list_handler(message):
    do_log(message.from_user.id, 'Admin list')
    t = message.text
    markup = markup_adm_list
    if t == 'Добавить админа':
        rep = 'Введите ID'
        bot.register_next_step_handler(message, admin_add_remove_handler)
    elif t == 'Удалить админа':
        rep = 'Введите ID'
        bot.register_next_step_handler(message, admin_add_remove_handler, False)
    elif t == 'Назад':
        markup = markup_adm
        rep = 'Возвращаемся в панель администратора'
        bot.register_next_step_handler(message, admin_panel)
    else:
        rep = unknown_com
        bot.register_next_step_handler(message, admin_list_handler)
    bot.send_message(message.from_user.id, rep, reply_markup=markup)


def place_list_handler(message):
    t = message.text
    uid = message.from_user.id
    markup = markup_places_list
    next_step = place_list_handler
    if t == 'Добавить место':
        markup = markup_final
        bot.send_message(uid, place_add_info)
        bot.send_message(uid, "Пример:")
        rep = place_add_example
        to_log = 'Add'
        next_step = place_add_handler
    elif t == 'Удалить место':
        rep = 'Введите ID'
        to_log = 'Delete'
        next_step = place_remove_handler
    elif t == 'Изменить место':
        markup = markup_final
        bot.send_message(uid, place_edit_info)
        bot.send_message(uid, "Пример:")
        rep = place_edit_example
        to_log = 'Edit'
        next_step = place_edit_handler
    elif t == 'Добавить картинку':
        rep = 'Отправьте изображение и ID'
        to_log = 'AddPic'
        next_step = image_add_handler
        markup = markup_final
    elif t == 'Удалить картинку':
        rep = 'Введите ID'
        to_log = 'DeletePic'
        next_step = image_delete_handler
    elif t == 'Назад':
        markup = markup_adm
        rep = 'Возвращаемся в панель администратора'
        to_log = 'Back'
        next_step = admin_panel
    elif t and t.isdigit():
        ses = Session()
        place = ses.query(Places).where(Places.id == int(t)).first()
        ses.close()
        if place:
            rep = places_list_for_admins()
            p_info = place_info(place, int(t))
            if place.image:
                bot.send_photo(uid, place.image, caption=p_info, reply_markup=markup)
            else:
                bot.send_message(uid, p_info, reply_markup=markup)
        else:
            rep = "Место с таким ID не найдено"
        to_log = 'ID'
    else:
        rep = unknown_com
        to_log = 'Unknown'
    bot.register_next_step_handler(message, next_step)
    bot.send_message(uid, rep, reply_markup=markup)
    do_log(uid, 'Place list', to_log)


def place_add_handler(message):
    do_log(message.from_user.id, 'Place add')
    markup = markup_places_list
    inp = message.text.split('\n', 9)
    uid = message.from_user.id
    params = ['name', 'date_start', 'date_end', 'address', 'lat',
              'lon', 'price_min', 'price_max', 'theme', 'priority', 'description']
    dat = {}
    if len(inp) == len(params):
        markup = markup_yes_no
        for i in range(len(params)):
            if inp[i] != '0':
                dat[params[i]] = inp[i]
        try:
            nm = dat["name"]
            desc = dat["description"]
            dat["date_start"] = datetime.strptime(dat["date_start"], "%d.%m.%Y %H:%M")
            f_dt = dat["date_start"].strftime("%d.%m %H:%M")
            if "date_end" in dat:
                dat["date_end"] = datetime.strptime(dat["date_end"], "%d.%m.%Y %H:%M")
                if dat["date_start"].day == dat["date_end"].day:
                    t_dt = dat["date_end"].strftime("%H:%M")
                else:
                    t_dt = dat["date_end"].strftime("%d.%m %H:%M")
                dt = "с {} до {}".format(f_dt, t_dt)
            else:
                dt = f_dt
            adr = dat["address"]
            theme_info = theme_checker(dat["theme"], True)
            theme = theme_info["name"]
            dat["theme"] = theme_info["id"]
            price = f"от {dat['price_min']} до {dat['price_max']}" if dat.get('price_max', False) else dat['price_min']
            place_preview = place_info_template.format('0', nm, adr, dt, theme, price, desc)
            bot.send_message(uid, "Превью:")
            bot.send_message(uid, place_preview)
            if adr:
                bot.send_location(uid, dat["lat"], dat["lon"])
            rep = "Подтвердить?"
            bot.register_next_step_handler(message, place_add_confirm)
            add_user_data(message.from_user.id, "AddPlace", dat)
        except Exception as e:
            rep = "Произошла ошибка с ведёнными данными. Проверьте правильность ввода."
            bot.register_next_step_handler(message, place_add_handler)
            markup = markup_final
            print(e)
    elif message.text == "Назад":
        markup = markup_places_list
        bot.send_message(message.from_user.id, "Возвращаемся в список мест")
        bot.register_next_step_handler(message, place_list_handler)
        rep = places_list_for_admins()
    else:
        rep = "Введены не все данные"
        bot.register_next_step_handler(message, place_add_handler)
    bot.send_message(uid, rep, reply_markup=markup)


def place_add_confirm(message):
    markup = markup_places_list
    bot.register_next_step_handler(message, place_list_handler)
    do_log(message.from_user.id, 'Place add', 'Confirm')
    resp = message.text
    if resp == "Да":
        dat = get_user_data(message.from_user.id, "AddPlace")
        ses = Session()
        ses.execute(Places.__table__.insert(), dat)
        ses.commit()
        ses.close()
        rep = "Место успешно добавлено"
    else:
        rep = "Место не добавлено"
    bot.send_message(message.from_user.id, rep)
    bot.send_message(message.from_user.id, "Возвращаемся в список мест")
    bot.send_message(message.from_user.id, places_list_for_admins(), reply_markup=markup)
    pass


def place_remove_handler(message):
    markup = markup_places_list
    t = message.text
    do_log(message.from_user.id, 'Place remove', t)
    rep = "Неизвестный ID"
    if t.isnumeric():
        pid = int(t)
        ses = Session()
        s = ses.query(Places).where(Places.id == pid).first()
        if s:
            print(s)
            ses.query(Places).filter_by(id=pid).delete()
            rep = "Место успешно удалено"
            ses.commit()
        ses.close()
    bot.register_next_step_handler(message, place_list_handler)
    bot.send_message(message.from_user.id, rep, reply_markup=markup)
    bot.send_message(message.from_user.id, "Возвращаемся в список мест")
    bot.send_message(message.from_user.id, places_list_for_admins(), reply_markup=markup)


def place_edit_handler(message):
    do_log(message.from_user.id, 'Place edit')
    markup = markup_final
    next_step = place_edit_handler
    inp = message.text.lower().split('\n', 2)
    uid = message.from_user.id
    if len(inp) == 3:
        rep = 'Неправильный ID'
        if inp[0].isdigit():
            markup = markup_yes_no
            pid = int(inp[0])
            ses = Session()
            place = ses.query(Places).where(Places.id == pid).first()
            if place:
                if inp[1] in ['id', 'image']:
                    rep = 'Нельзя изменить ID или изображение'
                elif hasattr(place, inp[1]):
                    try:
                        if inp[1] in ['date_start', 'date_end']:
                            inp[2] = datetime.strptime(inp[2], "%d.%m.%Y %H:%M")
                        add_user_data(uid, "EditPlace", [pid, inp[1], inp[2]])
                        setattr(place, inp[1], inp[2])
                        place_info(place, pid, bot, uid)
                        rep = 'Подтвердить?'
                        next_step = place_edit_confirm
                    except ValueError as e:
                        rep = "Неправильный формат даты. Попробуйте снова"
                        print(e)
                else:
                    rep = 'Аттрибут не найден'
            ses.close()
    elif message.text == "Назад":
        bot.send_message(message.from_user.id, "Возвращаемся в список мест")
        markup = markup_places_list
        rep = places_list_for_admins()
        next_step = place_list_handler
    else:
        rep = "Введены не все данные"
        next_step = place_edit_handler
    bot.register_next_step_handler(message, next_step)
    bot.send_message(uid, rep, reply_markup=markup)


def place_edit_confirm(message):
    markup = markup_places_list
    bot.register_next_step_handler(message, place_list_handler)
    do_log(message.from_user.id, 'Place edit', 'Confirm')
    resp = message.text
    if resp == "Да":
        dat = get_user_data(message.from_user.id, "EditPlace")
        ses = Session()
        place = ses.query(Places).where(Places.id == dat[0]).first()
        if place:
            setattr(place, dat[1], dat[2])
            ses.commit()
        ses.close()
        rep = "Место успешно изменено"
    else:
        rep = "Место не изменено"
    bot.send_message(message.from_user.id, rep)
    bot.send_message(message.from_user.id, "Возвращаемся в список мест")
    bot.send_message(message.from_user.id, places_list_for_admins(), reply_markup=markup)
    pass


def image_add_handler(message):
    ses = Session()
    uid = message.from_user.id
    rep = "Место не найдено. Попробуйте снова"
    markup = markup_final
    next_step = image_add_handler
    if message.content_type == "photo":
        try:
            fid = message.photo[-1].file_id
            inp = message.caption
            do_log(uid, "ImageAdd", inp)
            pl = ses.query(Places).where(Places.id == int(inp)).first()
            if pl:
                pl.image = fid
                ses.commit()
                place_info(pl, pl.id, bot, uid)
                rep = "Изображение успешно добавлено"
                markup = markup_places_list
                next_step = place_list_handler
        except TypeError as e:
            rep = "Необходимо указать ID. Попробуйте снова"
            do_log(message.from_user.id, 'Error', str(e))
        except Exception as e:
            rep = "Ошибка:" + str(e)
            do_log(message.from_user.id, 'Error', str(e))
    elif message.text == "Назад":
        do_log(uid, "ImageAdd", "Back")
        rep = "Отмена добавления изображения"
        markup = markup_places_list
        next_step = place_list_handler
    else:
        do_log(uid, "ImageAdd", "WrongInput")
        rep = "Необходимо отправить изображение с подписью. Попробуйте снова"
    ses.close()
    bot.register_next_step_handler(message, next_step)
    bot.send_message(uid, rep)
    if next_step == place_list_handler:
        bot.send_message(uid, "Возвращаемся в список мест")
        bot.send_message(uid, places_list_for_admins(), reply_markup=markup)


def image_delete_handler(message):
    ses = Session()
    t = message.text
    uid = message.from_user.id
    do_log(uid, "ImageDelete", t)
    rep = "Место не найдено. Попробуйте снова"
    markup = markup_final
    next_step = image_delete_handler
    if t.isdigit():
        place = ses.query(Places).where(Places.id == int(t)).first()
        if place:
            place.image = None
            ses.commit()
            bot.send_message(uid, 'Изображение успешно удалено')
            rep = place_info(place, place.id)
            markup = markup_places_list
            next_step = place_list_handler
    elif message.text == "Назад":
        rep = "Отмена удаления изображения"
        markup = markup_places_list
        next_step = place_list_handler
    ses.close()
    bot.register_next_step_handler(message, next_step)
    bot.send_message(uid, rep)
    if next_step == place_list_handler:
        bot.send_message(uid, "Возвращаемся в список мест")
        bot.send_message(uid, places_list_for_admins(), reply_markup=markup)


def admin_add_remove_handler(message, add=True):
    do_log(message.from_user.id, 'Add admin')
    markup = markup_adm_list
    t = message.text
    if t.isnumeric():
        nid = int(t)
        ses = Session()
        s = ses.query(Users).where(Users.id == nid).first()
        if s:
            s.admin = add
            rep = 'Права администратора у пользователя {} изменены на {}'.format(s.name, add)
        else:
            try:
                nuser = bot.get_chat_member(nid, nid).user
                uname = nuser.username
                if not uname:
                    uname = nuser.first_name
                nuser = Users(nid, uname, add)
                ses.add(nuser)
                rep = 'Пользователь {} добавлен в базу данных. Права администратора установлены на {}'
                rep = rep.format(s.name, add)
            except Exception:
                rep = 'Пользователь не найден'
        ses.commit()
        ses.close()
    else:
        rep = "Неизвестный ID"
    bot.register_next_step_handler(message, admin_list_handler)
    bot.send_message(message.from_user.id, rep, reply_markup=markup)


def stats_handler(message):
    do_log(message.from_user.id, 'Stats')
    t = message.text
    markup = markup_stat
    ns = stats_handler
    rep = 'Неизвестная команда'
    ses = Session()
    if t == 'Районы':
        s = ses.query(Districts).all()
        d_count = [x.name + '\t' + str(x.called) for x in s]
        rep = 'Статистика по районам\n\nНазвание\tКоличество запросов\n'
        rep += '\n'.join(d_count)
    elif t == 'Пользователи':
        s = ses.query(Users).all()
        u_count = [str(x.id) + '\t' + x.name for x in s]
        rep = 'Статистика по пользователям\n\nВсего пользователей: {}\n\nID\tИмя\n'.format(len(u_count))
        rep += '\n'.join(u_count)
    elif t == 'Назад':
        ns = admin_panel
        markup = markup_adm
        rep = 'Возвращаемся в панель администратора'
    ses.close()
    bot.register_next_step_handler(message, ns)
    bot.send_message(message.from_user.id, rep, reply_markup=markup)


@bot.message_handler(content_types=['text'])
def main_handler(message):
    do_log(message.from_user.id, 'Main')
    markup = markup_main
    uid = message.from_user.id
    is_adm = message.from_user.id in get_users_id()
    if is_adm:
        markup = markup_main_adm
    rep = "Неизвестная команда"
    if message.text == "Привет":
        rep = "Приветствую, человек"
    elif message.text == "Инфо":
        bot.send_message(message.from_user.id, start_message)
        bot.send_message(message.from_user.id, places_list_for_admins())
        rep = place_info_main_page
    elif message.text in ["Поиск", "Подобрать ивент", "Любой"]:
        rep = "Выберите жанр"
        markup = markup_genre
        bot.register_next_step_handler(message, choose_genre)
    elif message.text in ["Панель", "Назад"] and is_adm:
        rep = "Открыта панель администратора"
        markup = markup_adm
        bot.register_next_step_handler(message, admin_panel)
    elif message.text and message.text.isdigit():
        ses = Session()
        place = ses.query(Places).where(Places.id == int(message.text)).first()
        ses.close()
        if place:
            rep = places_list_for_admins()
            place_info(place, int(message.text), bot, uid)
        else:
            rep = "Место с таким ID не найдено"
    bot.send_message(uid, rep, reply_markup=markup)


def choose_dist(message):
    do_log(message.from_user.id, 'District')
    markup = markup_dist
    t = message.text
    if t == 'Назад':
        markup = markup_main
        if message.from_user.id in get_users_id():
            markup = markup_main_adm
        bot.send_message(message.from_user.id, 'Возвращаемся', reply_markup=markup)
    else:
        ses = Session()
        dis = ses.query(AdmDist).where(AdmDist.name == t).first()
        if dis:
            dis.called += 1
            markup = markup_genre
            rep = 'Введите жанр'
            add_user_data(message.from_user.id, "dis", [dis.id, dis.name])
            bot.register_next_step_handler(message, choose_genre)
        elif t == 'Любой':
            markup = markup_genre
            rep = 'Введите жанр'
            bot.register_next_step_handler(message, choose_genre)
        else:
            rep = 'Район не найден'
            bot.register_next_step_handler(message, choose_dist)
        ses.commit()
        ses.close()
        bot.send_message(message.from_user.id, rep, reply_markup=markup)


def choose_genre(message):
    markup = markup_final
    t = message.text
    calendar, step = DetailedTelegramCalendar(locale='ru').build()
    if t == 'Назад':
        markup = markup_main
        if message.from_user.id in get_users_id():
            markup = markup_main_adm
        bot.send_message(message.from_user.id, 'Главное меню', reply_markup=markup)
        do_log(message.from_user.id, 'Genre Back')
    else:
        do_log(message.from_user.id, 'Genre', t)
        bot.register_next_step_handler(message, choose_genre)
        ses = Session()
        theme = ses.query(Themes).where(Themes.name == t).first()
        ses.close()
        if theme or t == 'Любой':
            add_user_data(message.from_user.id, "genre", t)
            bot.send_message(message.from_user.id,
                             "Выберите дату",
                             reply_markup=calendar)
        else:
            bot.send_message(message.from_user.id, 'Жанр не найден', reply_markup=markup)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def choose_date(c):
    ch_time, key, step = DetailedTelegramCalendar(locale='ru').process(c.data)
    if not ch_time and key:
        bot.edit_message_text(c.message.text,
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif ch_time:
        bot.answer_callback_query(c.id)
        uid = c.message.chat.id
        do_log(uid, 'Date', str(ch_time))

        chosen_genre = get_user_data(uid, "genre", 'Любой')
        ses = Session()
        found_places = ses.query(Places)
        if chosen_genre and chosen_genre != 'Любой':
            found_places = found_places.where(Places.theme == chosen_genre)
        found_places = found_places .all()
        ses.close()

        fp = found_places
        found_places = sorted(list(filter(lambda p: p.date_start.date() == ch_time, fp)),
                              key=lambda p: (-p.priority, p.date_start))
        places_list = []
        markup_num = make_inline(found_places)
        for i in range(len(found_places)):
            x = found_places[i]
            if x.price_max:
                p_price = f"от {x.price_min} до {x.price_max}"
            else:
                p_price = x.price_min
            p_date = x.date_start.strftime("%H:%M")
            p_theme = theme_checker(x.theme)["name"]
            places_list.append(the_place.format(str(i+1), x.name, x.address, p_date, p_theme, p_price))
        add_user_data(uid, "places", found_places)
        rep = text_found.format(chosen_genre, ch_time, sklonenie_mesta(len(places_list)))
        rep += '\n'.join(places_list)

        bot.send_message(uid, rep, reply_markup=markup_num)


@bot.callback_query_handler(func=lambda call: True)
def show_place_info(call):
    markup = markup_final
    uid = call.from_user.id
    p_num = int(call.data)
    places = get_user_data(uid, "places", [])
    if len(places) > p_num:
        place = places[p_num]
        place_info(place, p_num + 1, bot, uid)
        bot.send_message(uid, contact_info.format(place.name))
        bot.answer_callback_query(call.id)
        do_log(uid, 'Place', place.name)
    else:
        rep = f"Информация о месте №{str(p_num + 1)} не найдена"
        bot.send_message(uid, rep, reply_markup=markup)
        bot.answer_callback_query(call.id)
        do_log(uid, 'Place', str(p_num))


def sklonenie_mesta(d):  # Склонение слова
    s = str(d)
    ld = int(s[-1])
    elv = not (11 <= int(s[-2:]) <= 14)
    if ld == 1 and elv:
        return s + ' место'
    elif 2 <= ld <= 4 and elv:
        return s + ' места'
    return s + ' мест'


@bot.message_handler(content_types=['location'])
def handle_location(message):
    print("{0}, {1}".format(message.location.latitude, message.location.longitude))
    uid = message.from_user.id
    add_user_data(uid, "location", {"lat": message.location.latitude, "lon": message.location.longitude})


bot.polling(none_stop=True, interval=0)
