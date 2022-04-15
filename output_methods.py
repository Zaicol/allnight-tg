from models import *
from strings import *
from markups import markup_final


def places_list_for_admins():
    ses = Session()
    s = ses.query(Places).all()
    ses.close()
    plist = [str(x.id) + '\t' + x.name for x in s]
    rep = "Список мест\nID\tНазвание\n"
    rep += '\n'.join(plist)
    return rep


def theme_checker(par, make_new=False):
    ses = Session()
    if isinstance(par, int) or par.isdigit():
        theme = ses.query(Themes).where(Themes.id == int(par)).first()
        if theme:
            theme = {"id": str(theme.id), "name": theme.name}
        else:
            theme = {"id": '5', "name": 'Неизвестный жанр'}
    else:
        theme = ses.query(Themes).where(Themes.name == par).first()
        if theme:
            theme = {"id": str(theme.id), "name": theme.name}
        elif make_new:
            new_theme = Themes(name=par)
            ses.add(new_theme)
            ses.commit()
            theme = ses.query(Themes).where(Themes.name == par).first()
            theme = {"id": str(theme.id), "name": theme.name}
        else:
            theme = {"id": False, "name": False}
    ses.close()
    return theme


def place_info(place, place_number_in_list=0, bot=None, uid=None, markup=markup_final):
    nm = place.name
    adr = place.address if place.address else 'Нет'
    f_dt = place.date_start.strftime("%d.%m %H:%M")
    if place.date_end:
        if place.date_start.day == place.date_end.day:
            t_dt = place.date_end.strftime("%H:%M")
        else:
            t_dt = place.date_end.strftime("%d.%m %H:%M")
        dt = "с {} до {}".format(f_dt, t_dt)
    else:
        dt = f_dt
    theme = theme_checker(place.theme)["name"]
    price = f"от {place.price_min} до {place.price_max}" if place.price_max else str(place.price_min)
    desc = place.description
    rep = place_info_template.format(str(place_number_in_list), nm, adr, dt, theme, price, desc)
    if bot and uid:
        if place.image:
            bot.send_photo(uid, place.image, caption=rep, reply_markup=markup)
        else:
            bot.send_message(uid, rep, reply_markup=markup)
        if place.lat and place.lon:
            bot.send_location(uid, place.lat, place.lon)
        return True
    return rep
