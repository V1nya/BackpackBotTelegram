import telebot
from telebot import types

from utils.db_utils import create_dbsession
import utils
from utils import model

bot = telebot.TeleBot("5487695335:AAGFuarc4oPIBHfM9zp88NaNprTTW9AKwMM")

db = create_dbsession()
admin_id = [874872768]


def edit_last_action(telegram_id, action):
    last_action = db.query(model.Last_Action).filter(model.Last_Action.telegram_id == telegram_id).first()
    if last_action is None:
        new_action = utils.model.Last_Action(
            action=action,
            telegram_id=telegram_id
        )
        db.add(new_action)
    else:
        last_action.action = action
    db.commit()


def all_subject(number_course):
    return db.query(model.Subject).filter(model.Subject.numeber_course == number_course).all()


def all_item_subject(subject_name):
    subject = db.query(model.Subject).filter(model.Subject.name == subject_name).first()
    if subject is None:
        return None
    else:
        items = db.query(model.Item).filter(model.Item.subject_id == subject.id).all()
        return items


def print_all_subject(subjects, markup, chat_id, first_message_text):
    message_send_user = first_message_text
    counter_subjects = 0
    while counter_subjects < len(subjects):
        markup.add(types.KeyboardButton(subjects[counter_subjects].name))
        message_send_user += "- " + subjects[counter_subjects].name + "\n"
        counter_subjects += 1

    bot.send_message(chat_id,
                     message_send_user,
                     reply_markup=markup)


def delete_subject(subject):
    db.query(model.Item).filter(model.Item.subject_id == subject.id).delete()
    db.delete(subject)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    one = types.KeyboardButton("1")
    two = types.KeyboardButton("2")
    three = types.KeyboardButton("3")
    four = types.KeyboardButton("4")
    five = types.KeyboardButton("5")

    markup.add(one, two, three, four, five)

    user = db.query(model.User).filter(model.User.telegram_id == message.from_user.id).first()

    if user is None:
        new_item = utils.model.User(
            telegram_id=message.from_user.id,
            user_name=message.from_user.username,
            first_name=message.from_user.first_name,
            number_curse=2

        )
        db.add(new_item)
    edit_last_action(message.from_user.id, "/start_0")
    bot.send_message(message.from_user.id,
                     "Привіт, цей бот допоможе отримати всю інформацію з ваших предметів, виберіть ваш курс",
                     reply_markup=markup)
    bot.send_message(message.from_user.id, f'Вибери свій курс:\n1\n2\n3\n4\n5\n ')


def check_user_name(user, user_name):
    if user.user_name != user_name:
        user.user_name = user_name
        db.commit()


@bot.message_handler(content_types="text")
def get_user_text(message):
    user = db.query(model.User).filter(model.User.telegram_id == message.from_user.id).first()

    if not user.isBannedMessage:
        if not user.isBanned:
            last_action = db.query(model.Last_Action).filter(
                model.Last_Action.telegram_id == message.from_user.id).first()
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

            check_user_name(user, message.from_user.username)

            if message.text == "AdminPanel":

                if user.isPrivilege:
                    edit_last_action(user.telegram_id, "AdminPanel_0")
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                    counter_while = 0
                    markup.add(types.KeyboardButton("Повернутися"))
                    while counter_while < 5:
                        markup.add(types.KeyboardButton(f"{counter_while + 1}"))
                        counter_while += 1
                    bot.send_message(message.from_user.id,
                                     f"З поверненням до панелі адміна!\nТут ви можете:\n-Додавати предмети"
                                     f"\n-Видаляти предмети\n-Додавати файли до них\n-Видаляти файли\n-A також можеш написати мені help\nВибирай з того що пропоную, я все підскажу😉")
                    bot.send_message(message.from_user.id, f'Вибери потрібний курс:\n1\n2\n3\n4\n5\nАбо Повернутися',
                                     reply_markup=markup)

                else:
                    bot.send_message(message.from_user.id, "Вибач, не розумію тебе, вибирай з того що пропоную 👇😉")
            elif message.text[0:14] == "add_new_admin_":
                if user.telegram_id in admin_id:
                    new_adm = db.query(model.User).filter(model.User.user_name == message.text[14:]).first()
                    if new_adm is None:
                        bot.send_message(user.telegram_id, "Він ще не знає про мене(")
                    else:
                        markup.add(types.KeyboardButton("Оновити"))
                        new_adm.isPrivilege = True
                        bot.send_message(new_adm.telegram_id, "Вітаю, ви отримали права адміністратора!🎉")
                        bot.send_message(new_adm.telegram_id, "🎉")
                        bot.send_message(new_adm.telegram_id, "Пиши AdminPanel для користування")
                        subjects = db.query(model.Subject).filter(
                            model.Subject.numeber_course == new_adm.number_curse).all()
                        print_all_subject(subjects, markup, new_adm.telegram_id,
                                          "Вибирай предмет та дивись матеріали з нього\n")
                        for adm in admin_id:
                            bot.send_message(adm, f"Новий адмін @{new_adm.user_name}")
                        db.commit()
                else:
                    bot.send_message(message.from_user.id, "Вибач, не розумію тебе, вибирай з того що пропоную 👇😉")
            elif message.text[0:13] == "remove_admin_":
                if user.telegram_id in admin_id:
                    new_adm = db.query(model.User).filter(model.User.user_name == message.text[13:]).first()
                    if new_adm is None:
                        bot.send_message(user.telegram_id, "Він ще не знає про мене(")
                    else:
                        markup.add(types.KeyboardButton("Оновити"))
                        new_adm.isPrivilege = False
                        bot.send_message(new_adm.telegram_id, "Вітаю, ви більше не адміністратор!🎉")
                        bot.send_message(new_adm.telegram_id, "🎉")
                        for adm in admin_id:
                            bot.send_message(adm, f" @{new_adm.user_name} героїчно покинув пост адміна")
                        edit_last_action(new_adm.telegram_id, f"num_curse_{new_adm.number_curse}")
                        subjects = db.query(model.Subject).filter(
                            model.Subject.numeber_course == new_adm.number_curse).all()
                        print_all_subject(subjects, markup, new_adm.telegram_id,
                                          "Вибирай предмет та дивись матеріали з нього\n")
                        db.commit()
                else:
                    bot.send_message(message.from_user.id, "Вибач, не розумію тебе, вибирай з того що пропоную 👇😉")
            elif message.text == "all_admin":
                if user.isPrivilege:
                    admins = db.query(model.User).filter(model.User.isPrivilege == True).filter(
                        model.User.telegram_id != 874872768).all()
                    admins_counter = 0
                    send_message_user = "Список адміністраторів:\n"
                    while len(admins) > admins_counter:
                        send_message_user += f"{admins_counter + 1}) {admins[admins_counter].first_name}(@{admins[admins_counter].user_name})\n"
                        admins_counter += 1
                    bot.send_message(message.from_user.id, send_message_user)
                else:
                    bot.send_message(message.from_user.id, "Вибач, не розумію тебе, вибирай з того що пропоную 👇😉")

            elif message.text == "all_users":
                if user.isPrivilege:
                    users = db.query(model.User).all()
                    all_user = "Всі користувачі:\n"
                    user_counter = 1
                    for usr in users:
                        if usr.telegram_id == 874872768:
                            user_counter -= 1  # It's me development first this bot) My id - 874872768
                        elif usr.isPrivilege:
                            all_user += f"{user_counter}) {usr.first_name}(@{usr.user_name}) id- {usr.telegram_id} -Admin\n"
                        else:
                            all_user += f"{user_counter}) {usr.first_name}(@{usr.user_name}) id- {usr.telegram_id}\n"
                        user_counter += 1
                    bot.send_message(user.telegram_id, all_user)
                else:
                    bot.send_message(message.from_user.id, "Вибач, не розумію тебе, обирай з того що пропоную 👇😉")
            elif message.text == "my_id":
                if user.isPrivilege:
                    bot.send_message(user.telegram_id, f"Your id: {user.telegram_id}")
                else:
                    bot.send_message(message.from_user.id, "Вибач, не розумію тебе, обирай з того що пропоную 👇😉")
            elif message.text[0:12] == "banned_user_":
                if user.isPrivilege:
                    ban_user = db.query(model.User).filter(model.User.user_name == message.text[12:]).first()
                    if ban_user is None:
                        bot.send_message(message.from_user.id, f"Не знайшов такого користувача {message.text[12:]}")
                    else:
                        if ban_user.telegram_id not in admin_id:
                            ban_user.isBanned = True
                            db.commit()
                            bot.send_message(message.from_user.id,
                                             f"Вітаю ви відправили в бан: {ban_user.first_name}(@{ban_user.user_name})")
                            bot.send_message(ban_user.telegram_id, "Вітаю, вас забанили 🤕")
                            bot.send_message(ban_user.telegram_id, "🎉")
                            bot.send_message(ban_user.telegram_id, "🫡")
                            for adm in admin_id:
                                bot.send_message(adm,
                                                 f"Цей негідник {user.first_name}(@{user.user_name}) тільки що забанив:"
                                                 f"{ban_user.first_name}(@{ban_user.user_name})")
                        else:
                            bot.send_message(message.from_user.id, "Упс, а в тебе не вийде його забанити 😢")
                else:
                    bot.send_message(message.from_user.id, "Вибач, не розумію тебе, обирай з того що пропоную 👇😉")
            elif message.text[0:14] == "unbanned_user_":
                if user.isPrivilege:
                    ban_user = db.query(model.User).filter(model.User.user_name == message.text[14:]).first()
                    if ban_user is None:
                        bot.send_message(message.from_user.id, f"Не знайшов такого користувача  {message.text[14:]}")
                    elif not ban_user.isBanned:
                        bot.send_message(message.from_user.id, f"Помилочка, а він не забанений")
                    else:
                        ban_user.isBanned = False
                        db.commit()
                        bot.send_message(message.from_user.id,
                                         f"Вітаю ви розбанили цього добряка: {ban_user.first_name}(@{ban_user.user_name})")
                        bot.send_message(ban_user.telegram_id, "Вітаю, вас розбанили 😇")
                        bot.send_message(ban_user.telegram_id, "🎉")
                        for adm in admin_id:
                            bot.send_message(adm,
                                             f"Цей добряк {user.first_name}(@{user.user_name}) тільки що розбанив:"
                                             f"{ban_user.first_name}(@{ban_user.user_name})")
                        markup.add(types.KeyboardButton("Оновити"))
                        subjects = db.query(model.Subject).filter(
                            model.Subject.numeber_course == ban_user.number_curse).all()
                        print_all_subject(subjects, markup, ban_user.telegram_id,
                                          "Обирай предмет та дивись матеріали з нього\n")

                else:
                    bot.send_message(message.from_user.id, "Вибач, не розумію тебе, вибирай з того що пропоную 👇😉")
            elif message.text == "help":
                if user.telegram_id in admin_id:
                    bot.send_message(user.telegram_id, "HELP:"
                                                       "\nhelp"
                                                       "\nAdminPanel"
                                                       "\nadd_new_admin_+user_name"
                                                       "\nremove_admin_+user_name"
                                                       "\nbanned_user_+user_name"
                                                       "\nunbanned_user_+user_name"
                                                       "\nall_admin"
                                                       "\nall_users"
                                                       "\nmy_id")
                elif user.isPrivilege:
                    bot.send_message(user.telegram_id, "HELP"
                                                       "\nhelp"
                                                       "\nAdminPanel"
                                                       "\nbanned_user_+user_name"
                                                       "\nunbanned_user_+user_name"
                                                       "\nall_admin"
                                                       "\nall_users"
                                                       "\nmy_id")
                else:
                    bot.send_message(message.from_user.id, "Вибач, не розумію тебе, вибирай з того що пропоную 👇😉")
            else:
                match last_action.action[0:len(last_action.action) - 2]:
                    case "/start":
                        match message.text:
                            case "1":
                                user.number_curse = 1
                                db.commit()
                                subjects = db.query(model.Subject).filter(model.Subject.numeber_course == 1).all()
                                markup.add(types.KeyboardButton("Оновити"))
                                if len(subjects) == 0:
                                    bot.send_message(message.from_user.id,
                                                     "Упс , мені задється адміни погано працюють(",
                                                     reply_markup=markup)
                                else:
                                    edit_last_action(user.telegram_id, "num_curse_1")
                                    print_all_subject(subjects, markup, message.from_user.id,
                                                      "Обирай предмет та дивись матеріали з нього\n")

                            case "2":
                                user.number_curse = 2
                                db.commit()
                                subjects = db.query(model.Subject).filter(model.Subject.numeber_course == 2).all()
                                markup.add(types.KeyboardButton("Оновити"))
                                if len(subjects) == 0:
                                    bot.send_message(message.from_user.id,
                                                     "Упс , мені задється адміни погано працюють(",
                                                     reply_markup=markup)
                                else:
                                    edit_last_action(user.telegram_id, "num_curse_2")
                                    print_all_subject(subjects, markup, message.from_user.id,
                                                      "Обирай предмет та дивись матеріали з нього\n")
                            case "3":
                                user.number_curse = 3
                                db.commit()
                                subjects = db.query(model.Subject).filter(model.Subject.numeber_course == 3).all()
                                markup.add(types.KeyboardButton("Оновити"))
                                if len(subjects) == 0:
                                    bot.send_message(message.from_user.id,
                                                     "Упс , мені задється адміни погано працюють(",
                                                     reply_markup=markup)
                                else:
                                    edit_last_action(user.telegram_id, "num_curse_3")
                                    print_all_subject(subjects, markup, message.from_user.id,
                                                      "Обирай предмет та дивись матеріали з нього\n")

                            case "4":
                                user.number_curse = 4
                                db.commit()
                                subjects = db.query(model.Subject).filter(model.Subject.numeber_course == 4).all()
                                markup.add(types.KeyboardButton("Оновити"))
                                if len(subjects) == 0:
                                    bot.send_message(message.from_user.id,
                                                     "Упс , мені задється адміни погано працюють(",
                                                     reply_markup=markup)
                                else:
                                    edit_last_action(user.telegram_id, "num_curse_4")
                                    print_all_subject(subjects, markup, message.from_user.id,
                                                      "Обирай предмет та дивись матеріали з нього\n")

                            case "5":
                                user.number_curse = 5
                                db.commit()
                                subjects = db.query(model.Subject).filter(model.Subject.numeber_course == 5).all()
                                markup.add(types.KeyboardButton("Оновити"))
                                if len(subjects) == 0:
                                    bot.send_message(message.from_user.id,
                                                     "Упс , мені задється адміни погано працюють(",
                                                     reply_markup=markup)
                                else:
                                    edit_last_action(user.telegram_id, "num_curse_5")
                                    print_all_subject(subjects, markup, message.from_user.id,
                                                      "Обирай предмет та дивись матеріали з нього\n")

                            case "Оновити":
                                subjects = db.query(model.Subject).filter(
                                    model.Subject.numeber_course == user.number_curse).all()
                                markup.add(types.KeyboardButton("Оновити"))
                                if len(subjects) == 0:
                                    bot.send_message(message.from_user.id,
                                                     "Упс , мені задється адміни погано працюють(",
                                                     reply_markup=markup)
                                else:
                                    edit_last_action(user.telegram_id, ("num_curse_" + user.number_curse))
                                    print_all_subject(subjects, markup, message.from_user.id,
                                                      "Обирай предмет та дивись матеріали з нього\n")
                            case _:
                                bot.send_message(message.from_user.id,
                                                 "Вибач, не розумію тебе, вибирай з того що пропоную 👇")

                    case "num_curse":
                        subjects = db.query(model.Subject) \
                            .filter(model.Subject.numeber_course == int(last_action.action[-1])) \
                            .all()
                        markup.add(types.KeyboardButton("Оновити"))
                        if message.text == "Оновити":
                            print_all_subject(subjects, markup, message.from_user.id,
                                              "Оновлено!\nОбирай предмет та дивись матеріали з нього\n")
                        else:

                            subject = db.query(model.Subject) \
                                .filter(model.Subject.numeber_course == int(last_action.action[-1])) \
                                .filter(model.Subject.name == message.text) \
                                .first()

                            items = db.query(model.Item) \
                                .filter(model.Item.subject_id == subject.id) \
                                .all()

                            if len(items) == 0:

                                bot.send_message(message.from_user.id, "Мені здається тут нічого не має 🤔")
                                bot.send_message(message.from_user.id, "Пусто.... 😢")
                                print_all_subject(subjects, markup, message.from_user.id,
                                                  "Обирай предмет та дивись матеріали з нього\n")
                            else:

                                counter_items = 0
                                while counter_items < len(items):
                                    bot.send_document(message.from_user.id, items[counter_items].file,
                                                      visible_file_name=items[counter_items].file_name)
                                    counter_items += 1
                                bot.send_message(message.from_user.id, "Дивись, що завезли 😏👆")
                                print_all_subject(subjects, markup, message.from_user.id,
                                                  "Обирай предмет та дивись матеріали з нього\n")

                    case "AdminPanel":
                        markup.add(types.KeyboardButton("Повернутися"))
                        markup.add(types.KeyboardButton("Додати предмет"))
                        markup.add(types.KeyboardButton("Видалити предмет"))
                        markup.add(types.KeyboardButton("Видалити файли"))

                        match message.text:
                            case "1":
                                edit_last_action(user.telegram_id, "Admin_Panel_All_Subject_1")
                                subjects = all_subject(1)
                                message_send_user = ""
                                if len(subjects) == 0:
                                    message_send_user = f"На даний момент на {1} курсі немає доданих предметів(\n Ви можете:\n Додати предмет або Повернутися"
                                else:

                                    print_all_subject(subjects, markup, message.from_user.id,
                                                      "Обиріть предмет в який додати файли:\n")

                            case "2":
                                edit_last_action(user.telegram_id, "Admin_Panel_All_Subject_2")
                                subjects = all_subject(2)
                                message_send_user = ""
                                if len(subjects) == 0:
                                    message_send_user = f"На даний момент на {2} курсі немає доданих предметів(\n Ви можете:\n Додати предмет або Повернутися"
                                else:
                                    print_all_subject(subjects, markup, message.from_user.id,
                                                      "Обиріть предмет в який додати файли:\n")

                            case "3":
                                edit_last_action(user.telegram_id, "Admin_Panel_All_Subject_3")
                                subjects = all_subject(3)
                                message_send_user = ""
                                if len(subjects) == 0:
                                    message_send_user = f"На даний момент на {3} курсі немає доданих предметів(\n Ви можете:\n Додати предмет або Повернутися"
                                else:
                                    print_all_subject(subjects, markup, message.from_user.id,
                                                      "Обиріть предмет в який додати файли:\n")

                            case "4":
                                edit_last_action(user.telegram_id, "Admin_Panel_All_Subject_4")
                                subjects = all_subject(4)
                                message_send_user = ""
                                if len(subjects) == 0:
                                    message_send_user = f"На даний момент на {4} курсі немає доданих предметів(\n Ви можете:\n Додати предмет або Повернутися"
                                else:
                                    print_all_subject(subjects, markup, message.from_user.id,
                                                      "Обиріть предмет в який додати файли:\n")

                            case "5":
                                edit_last_action(user.telegram_id, "Admin_Panel_All_Subject_5")
                                subjects = all_subject(5)
                                message_send_user = ""
                                if len(subjects) == 0:
                                    message_send_user = f"На даний момент на {5} курсі немає доданих предметів(\n Ви можете:\n Додати предмет або Повернутися"
                                else:
                                    print_all_subject(subjects, markup, message.from_user.id,
                                                      "Обиріть предмет в який додати файли:\n")

                            case "Повернутися":
                                edit_last_action(message.from_user.id, "/start_B")
                                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                                counter_while = 0
                                while counter_while < 5:
                                    markup.add(types.KeyboardButton(f"{counter_while + 1}"))
                                    counter_while += 1
                                bot.send_message(message.from_user.id, f"Ви покинули панель адміністратора 😢")
                                bot.send_message(message.from_user.id, f'Вибери свій курс:\n1\n2\n3\n4\n5\n '
                                                 , reply_markup=markup)
                            case _:
                                bot.send_message(message.from_user.id,
                                                 "Вибач, не розумію тебе, обирай з того що пропоную 👇")
                    case "Admin_Panel_All_Subject":
                        match message.text:
                            case "Додати предмет":
                                markup.add(types.KeyboardButton("Повернутися"))
                                edit_last_action(user.telegram_id,
                                                 f"Add_New_Subject_{last_action.action[-1]}")
                                bot.send_message(message.from_user.id,
                                                 "Напиши мені скорочену назву предмету\nНаприклад:ОС-це Операційні системи",
                                                 reply_markup=markup)
                            case "Повернутися":
                                edit_last_action(user.telegram_id, "AdminPanel_B")
                                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                                markup.add(types.KeyboardButton("Повернутися"))
                                counter_while = 0
                                while counter_while < 5:
                                    markup.add(types.KeyboardButton(f"{counter_while + 1}"))
                                    counter_while += 1
                                bot.send_message(message.from_user.id,
                                                 f'Обери потрібний курс:\n1\n2\n3\n4\n5\nАбо Повернутися',
                                                 reply_markup=markup)
                            case "Видалити предмет":
                                markup.add(types.KeyboardButton("Повернутися"))
                                edit_last_action(user.telegram_id, f"Delete_subject_{last_action.action[-1]}")
                                bot.send_message(message.from_user.id,
                                                 "Добре, обери що хочеш видалити, всі файли також будуть видалені!")
                                print_all_subject(all_subject(last_action.action[-1]), markup, message.from_user.id, "")
                            case "Видалити файли":
                                markup.add(types.KeyboardButton("Повернутися"))
                                edit_last_action(user.telegram_id, f"Delete_items_{last_action.action[-1]}")
                                print_all_subject(all_subject(last_action.action[-1]), markup, message.from_user.id,
                                                  "Обирай предмет в якому будемо видаляти:\n")
                            case _:
                                subjects = db.query(model.Subject).filter(model.Subject.name == message.text) \
                                    .filter(model.Subject.numeber_course == int(last_action.action[-1])).first()
                                if subjects is None:
                                    bot.send_message(message.from_user.id, "😳")
                                    bot.send_message(message.from_user.id, "Такого предмету я не знаю(")
                                else:
                                    edit_last_action(user.telegram_id, f"Add_new_item_{subjects.id}")
                                    markup.add(types.KeyboardButton("Повернутися"))
                                    bot.send_message(message.from_user.id, "Добре, скидуй сюди всі файли що потрібно 👇",
                                                     reply_markup=markup)
                    case "Delete_subject":
                        markup.add(types.KeyboardButton("Повернутися"))
                        markup.add(types.KeyboardButton("Додати предмет"))
                        markup.add(types.KeyboardButton("Видалити предмет"))
                        markup.add(types.KeyboardButton("Видалити файли"))

                        subjects = all_subject(int(last_action.action[-1]))
                        if message.text != "Повернутися":
                            subject = db.query(model.Subject) \
                                .filter(model.Subject.numeber_course == int(last_action.action[-1])) \
                                .filter(model.Subject.name == message.text) \
                                .first()
                            if subject is None:
                                bot.send_message(message.from_user.id,
                                                 "Я звісно вибачаюсь, але я такого предмету не знайшов 😑")
                            else:
                                delete_subject(subject)
                                edit_last_action(user.telegram_id, f"Admin_Panel_All_Subject_{last_action.action[-1]}")
                                bot.send_message(message.from_user.id, f"Видалено {subject.name} і всі файли")
                                print_all_subject(all_subject(last_action.action[-1]), markup, message.from_user.id,
                                                  "Оберіть предмет в який додати файли:\n")
                                for adm in admin_id:
                                    bot.send_message(adm,
                                                     f"Цей добряк {user.first_name}(@{user.user_name}) тільки що видалив {subject.name} {subject.numeber_course} курсу ")

                        else:
                            edit_last_action(user.telegram_id, f"Admin_Panel_All_Subject_{last_action.action[-1]}")
                            if len(subjects) == 0:
                                message_send_user = f"На даний момент на {last_action.action[-1]} курсі немає доданих предметів(\n Ви можете:\n Додати предмет або Повернутися"
                            else:
                                print_all_subject(all_subject(last_action.action[-1]), markup, message.from_user.id,
                                                  "Обиріть предмет в який додати файли:\n")

                    case "Add_New_Subject":
                        if message.text == "Повернутися":
                            markup.add(types.KeyboardButton("Повернутися"))
                            markup.add(types.KeyboardButton("Додати предмет"))
                            markup.add(types.KeyboardButton("Видалити предмет"))
                            markup.add(types.KeyboardButton("Видалити файли"))

                            edit_last_action(user.telegram_id, f"Admin_Panel_All_Subject_{last_action.action[-1]}")
                            subjects = all_subject(int(last_action.action[-1]))
                            message_send_user = ""
                            if len(subjects) == 0:
                                message_send_user = f"На даний момент на {last_action.action[-1]} курсі немає доданих предметів(\n Ви можете:\n Додати предмет або Повернутися"
                            else:
                                print_all_subject(subjects, markup, message.from_user.id,
                                                  "Оберіть предмет в який додати файли:\n")

                        else:
                            subject = db.query(model.Subject).filter(model.Subject.name == message.text) \
                                .filter(model.Subject.numeber_course == last_action.action[-1]) \
                                .first()
                            if subject is None:
                                markup.add(types.KeyboardButton("Повернутися"))
                                markup.add(types.KeyboardButton("Додати предмет"))
                                markup.add(types.KeyboardButton("Видалити предмет"))
                                markup.add(types.KeyboardButton("Видалити файли"))

                                edit_last_action(user.telegram_id, f"Admin_Panel_All_Subject_{last_action.action[-1]}")
                                subject = model.Subject(
                                    numeber_course=int(last_action.action[-1]),
                                    name=message.text
                                )
                                db.add(subject)
                                db.commit()
                                bot.send_message(message.from_user.id,
                                                 f"Чудово!\nДодано {message.text}, тепер вибирай новий предмет та додавай до нього матеріали)")
                                for adm in admin_id:
                                    bot.send_message(adm,
                                                     f"Цей добряк {user.first_name}(@{user.user_name}) додав тільки що новий предмет для {last_action.action[-1]} - {message.text}")
                                subjects = db.query(model.Subject).filter(
                                    model.Subject.numeber_course == last_action.action[-1]).all()

                                print_all_subject(subjects, markup, message.from_user.id,
                                                  "Оберіть предмет в який додати файли:\n")
                            else:
                                bot.send_message(message.from_user.id,
                                                 f"Ой ой, такий предмет вже є на {last_action.action[-1]} курсі 😢\n"
                                                 f"Ти можеш завжди повернутися 😉")
                    case "Delete_items":
                        subject = db.query(model.Subject) \
                            .filter(model.Subject.numeber_course == int(last_action.action[-1])) \
                            .filter(model.Subject.name == message.text) \
                            .first()
                        items = None
                        if message.text == "Повернутися":
                            markup.add(types.KeyboardButton("Повернутися"))
                            markup.add(types.KeyboardButton("Додати предмет"))
                            markup.add(types.KeyboardButton("Видалити предмет"))
                            markup.add(types.KeyboardButton("Видалити файли"))

                            edit_last_action(user.telegram_id, f"Admin_Panel_All_Subject_{last_action.action[-1]}")

                            print_all_subject(all_subject(last_action.action[-1]), markup, message.from_user.id,
                                              "Оберіть предмет в який додати файли:\n")
                        elif subject is None:
                            bot.send_message(message.from_user.id, "Упс, а в мене немає такого предмету")

                        else:
                            items = all_item_subject(subject.name)
                            if items is None:
                                bot.send_message(message.from_user.id,
                                                 "Мені здається не можливо видалити те чого немає 🤔")
                            else:
                                items_counter = 0
                                markup.add(types.KeyboardButton("Повернутися"))
                                bot.send_message(message.from_user.id, "Поїхали!\nДочекайся кінця)",
                                                 reply_markup=markup)
                                edit_last_action(message.from_user.id,
                                                 f"Delete_item_{last_action.action[-1]}_{subject.name}")
                                while len(items) > items_counter:
                                    bot.send_document(message.chat.id, items[items_counter].file,
                                                      visible_file_name=items[items_counter].file_name,
                                                      reply_markup=markup)
                                    bot.send_message(message.from_user.id,
                                                     f"<b>{items_counter + 1}</b>) {items[items_counter].file_name}",
                                                     parse_mode="html")
                                    items_counter += 1
                                bot.send_message(message.from_user.id,
                                                 "Обирай що хочеш видалити та пиши мені номере через <b>пробіл</b>)\nБуду худіти, бо щось багато набрав МБ",
                                                 reply_markup=markup, parse_mode="html")

                    case _:
                        if (last_action.action[0:13] == "Add_new_item_" or last_action.action[
                                                                           0:12] == "Delete_item_") and message.text == "Повернутися":
                            markup.add(types.KeyboardButton("Повернутися"))
                            markup.add(types.KeyboardButton("Додати предмет"))
                            markup.add(types.KeyboardButton("Видалити предмет"))
                            markup.add(types.KeyboardButton("Видалити файли"))
                            if last_action.action[0:13] == "Add_new_item_":
                                subject = db.query(model.Subject).filter(
                                    model.Subject.id == int(last_action.action[13:])).first()
                            else:
                                subject = db.query(model.Subject).filter(
                                    model.Subject.id == int(last_action.action[12:13])).first()

                            edit_last_action(user.telegram_id, f"Admin_Panel_All_Subject_{subject.numeber_course}")
                            subjects = db.query(model.Subject).filter(
                                model.Subject.numeber_course == subject.numeber_course).all()

                            print_all_subject(subjects, markup, message.from_user.id,
                                              "Оберіть предмет в який додати файли:\n")
                        elif last_action.action[0:13] == "Add_new_item_" and (
                                message.text == "Все загрузив(ла)" or message.text == "Все загрузив" or message.text == "Все загрузила"):
                            markup.add(types.KeyboardButton("Додати предмет"))
                            markup.add(types.KeyboardButton("Повернутися"))
                            markup.add(types.KeyboardButton("Видалити предмет"))
                            markup.add(types.KeyboardButton("Видалити файли"))
                            subject = db.query(model.Subject).filter(
                                model.Subject.id == int(last_action.action[13:])).first()
                            edit_last_action(user.telegram_id, f"Admin_Panel_All_Subject_{subject.numeber_course}")
                            subjects = db.query(model.Subject).filter(
                                model.Subject.numeber_course == subject.numeber_course).all()

                            print_all_subject(subjects, markup, message.from_user.id,
                                              "Оберіть предмет в який додати файли:\n")
                        elif last_action.action[0:12] == "Delete_item_":
                            all_delete_items = message.text.split(" ")
                            subject = db.query(model.Subject) \
                                .filter(model.Subject.numeber_course == int(last_action.action[12:13])) \
                                .filter(model.Subject.name == last_action.action[14:]) \
                                .first()
                            items = db.query(model.Item) \
                                .filter(model.Item.subject_id == subject.id) \
                                .all()
                            for remove in all_delete_items:
                                try:
                                    db.delete(items[int(remove)])
                                    db.commit()
                                    bot.send_message(message.from_user.id,
                                                     f"Файл {items[int(remove)].file_name} успішно видалено!")
                                    for adm in admin_id:
                                        bot.send_message(adm,
                                                         f"Негідник {user.first_name}(@{user.user_name}) видалив файл - {items[int(remove)].file_name}")
                                except:
                                    bot.send_message(message.from_user.id, f"Я не знайшов файла під номером - {remove}")
                        else:
                            bot.send_message(message.from_user.id,
                                             "Вибач, не розумію тебе, обери з того що пропоную 👇")
        else:
            bot.send_message(message.from_user.id, "Опа опа, а ви забанені 😢")
            bot.send_message(message.from_user.id, "🫡")
    else:
        bot.send_message(message.from_user.id, "Чекай, я ще не все скинув!")


@bot.message_handler(content_types="document")
def download_file(message):
    user = db.query(model.User).filter(model.User.telegram_id == message.from_user.id).first()
    if user.isPrivilege:
        try:
            last_action = db.query(model.Last_Action).filter(
                model.Last_Action.telegram_id == message.from_user.id).first()
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            subject = db.query(model.Subject).filter(model.Subject.id == int(last_action.action[13:])).first()

            file_info = bot.get_file(message.document.file_id)
            file_download = bot.download_file(file_info.file_path)
            file = db.query(model.Item).filter(model.Item.file_name == message.document.file_name).first()

            markup.add(types.KeyboardButton("Все загрузив(ла)"))

            if file is None:
                new_item = model.Item(
                    subject_id=subject.id,
                    telegram_id=user.telegram_id,
                    file_name=message.document.file_name,
                    file=file_download

                )
                db.add(new_item)
                bot.send_message(message.from_user.id,
                                 f"Чудово! Файл {message.document.file_name} додав, тепер він в {subject.name} {subject.numeber_course} курсу",
                                 reply_markup=markup)
                for adm in admin_id:
                    bot.send_message(adm, f"Цей добряк {user.first_name}(@{user.user_name}) тільки що додав новий файл "
                                          f"для {subject.numeber_course} курсу з предмету {subject.name} - {message.document.file_name}")
            else:
                file.telegram_id = user.telegram_id
                file = file_download
                bot.send_message(message.from_user.id,
                                 f"Упс! Файл {message.document.file_name} з такою назвою,але я його змінив "
                                 f"тепер він повтороно збережений в {subject.name} {subject.numeber_course} курсу",
                                 reply_markup=markup)
                for adm in admin_id:
                    bot.send_message(adm, f"Цей добряк {user.first_name}(@{user.user_name}) тільки що змінив файл "
                                          f"для {subject.numeber_course} курсу з предмету {subject.name} - {message.document.file_name}")
            db.commit()

        except:
            bot.send_message(message.from_user.id,
                             f"Упс! Сталася помилка😢\nФайл(и) не були добавлені\nСпробуй ще раз, а я поки піду будити адміна😈",
                             reply_markup=markup)
            for adm in admin_id:
                bot.send_message(adm, f"Помилка у {user.first_name}(@{user.user_name}) з завантаженням файлів")
    else:
        bot.send_message(message.from_user.id, "Щоооо")
        bot.send_message(message.from_user.id, "Навіщо мені це -_-")


bot.polling(none_stop=True)
