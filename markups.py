from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from models import AdmDist, Themes, Session


def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def make_kb(btns):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for btn in btns:
        if isinstance(btn, list):
            kb.add(*[KeyboardButton(b) for b in btn])
        else:
            kb.add(KeyboardButton(btn))
    return kb


def make_inline(p):
    kb = InlineKeyboardMarkup()
    for i in range(len(p)):
        kb.add(InlineKeyboardButton(i + 1, callback_data=str(i)))
    return kb


markup_main = make_kb([['Подобрать ивент', 'Инфо']])
markup_main_adm = make_kb([['Подобрать ивент', 'Инфо'], 'Панель'])


_ses = Session()

distlist = _ses.query(AdmDist).all()
distlist = [x.name for x in distlist]
markup_dist = make_kb([['Назад', 'Любой']] + build_menu(distlist, 3))

themelist = _ses.query(Themes).all()
themelist = [x.name for x in themelist]
markup_genre = make_kb([['Назад', 'Любой']])  # + build_menu(themelist, 3))

_ses.close()

markup_adm = make_kb([['ID', 'Тест', 'Админы'], ['Статистика', 'Места', 'Назад']])
markup_adm_list = make_kb([['Добавить админа', 'Удалить админа'], 'Назад'])
markup_places_list = make_kb([['Добавить место', 'Удалить место', 'Изменить место'], ['Добавить картинку', 'Удалить картинку', 'Назад']])
markup_stat = make_kb([['Районы', 'Пользователи', 'Назад']])
markup_final = make_kb(['Назад'])
markup_yes_no = make_kb(['Да', 'Нет'])