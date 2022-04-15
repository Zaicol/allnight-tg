text_found = "Выбранный жанр: {}\nДата:{}\nНайдено {}.\n\n"
the_place = "{}. {}\nВремя: {}\nЦена: {}\nАдрес: {}\n"
place_info_template = "Информация о месте №{}\nНазвание: {}\n📍: {}\n🗓: {}\nЖанр: {}\nЦена: {}\n\n{}"
contact_info = """
Для прохода на мероприятия напишите @bokoyoko10 или @matsha21

Отправьте сообщение:
Хочу на {} 
1) ФИО
2) категория билета (выполнение условия будет проверяться на входе) 

Не забудьте ваш паспорт!"""
startup_new = "Начало работы. Выберите команду"
startup_old = "Добро пожаловать. Снова"
unknown_com = "Неизвестная команда"
place_add_info = """
Чтобы добавить место, введите данные в следующем формате:
Название*
Время начала*
Время окончания
Адрес*
Широта*
Долгота*
Цена (мин)*
Цена (макс)
Жанр (название или ID)*
Описание (можно несколько строк)*

Там, где не стоит *, можно просто поставить 0

Пример:
Вечеринка 1
31.12.2022 18:00
0
Ул. Новый Арбат, д. 7
55.772998
37.62007
500
0
3
Какое-то описание
растянувшееся на
несколько строк.
"""
start_message = """
All-Night это платформа, которая станет твоим проводником в ночной мир столичных вечеринок. Список обновляется каждую среду и дополняется в течении недели. В список попадают только те мероприятия, которые мы посещаем лично и готовы вам порекомендовать. Такой подход повышает конкуренцию и качество проводимых мероприятий, так что оставайтесь с нами и следите за обновлениями."""

place_edit_info = """Введите ID места, имя атрибута и новое значение атрибута.

Доступные аттрибуты:
Название: name
Описание: 
Цена (мин): price_min
Цена (макс): price_max
Дата начала: date_start
Дата окончания: date_end
Жанр (ID): theme
Адрес: address
Широта: lat
Долгота: lon
"""

place_edit_example = """1
name
Изменённое название"""
