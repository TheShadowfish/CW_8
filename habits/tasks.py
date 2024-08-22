from datetime import datetime

from django.utils import timezone
from celery import shared_task
from habits.services import send_telegram_message
from habits.models import Habits


@shared_task
def send_information_about_habit(message, tg_chat_id):
    """Отправляет сообщение пользователю о поставленном лайке"""
    send_telegram_message(message, tg_chat_id)


@shared_task
def find_all_habits():
    habit_time = datetime.now().replace(second=0, microsecond=0)

    habit_weekday = timezone.now().today().weekday()

    habits = Habits.objects.filter(owner__isnull=False, utc_time=habit_time)

    for h in habits:
        habit_weekday += h.weekday_offset
        if habit_weekday > 6:
            habit_weekday -= 7
        elif habit_weekday < 0:
            habit_weekday += 7

        tg_chat_id = h.owner.tg_chat_id
        message = f"Я буду (действие): [{h.action}] в (место): [{h.place}] (время): [{h.time}]"

        if habit_weekday == 0:
            if h.monday:
                send_information_about_habit.delay(tg_chat_id, message)
        elif habit_weekday == 1:
            if h.tuesday:
                send_information_about_habit.delay(tg_chat_id, message)
        elif habit_weekday == 2:
            if h.wednesday:
                send_information_about_habit.delay(tg_chat_id, message)
        elif habit_weekday == 3:
            if h.thursday:
                send_information_about_habit.delay(tg_chat_id, message)
        elif habit_weekday == 4:
            if h.friday:
                send_information_about_habit.delay(tg_chat_id, message)
        elif habit_weekday == 5:
            if h.saturday:
                send_information_about_habit.delay(tg_chat_id, message)
        else:
            if h.sunday:
                send_information_about_habit.delay(tg_chat_id, message)
