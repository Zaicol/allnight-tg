from models import *
from strings import *


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


def place_info(place, place_number_in_list=0):
    rep = place_info_template
    nm = place.name
    adr = place.address if place.address else 'Нет'
    dt = place.date_start.strftime("%d.%m %H:%M")
    theme = theme_checker(place.theme)["name"]
    price = f"от {place.price_min} до {place.price_max}" if place.price_max else str(place.price_min)
    desc = place.description
    return rep.format(str(place_number_in_list), nm, adr, dt, theme, price, desc)
