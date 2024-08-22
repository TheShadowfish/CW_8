from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habits
from users.models import User


class HabitTestCase(APITestCase):
    """Тестирование модели Habits"""

    def setUp(self):
        """Создание тестовой модели Пользователя (с авторизацией) и Привычки"""

        self.user = User.objects.create(
            email="test@test.com",
            password="testpassword",
            tg_chat_id="1567728836"
        )
        self.client.force_authenticate(user=self.user)

        self.habit = Habits.objects.create(
            owner=self.user,
            place="Магазин",
            time="18:00:00",
            action="Пойти в магазин за покупками",
            periodicity=1,
            duration=60
        )

        self.habit_nice_false = Habits.objects.create(
            owner=self.user,
            place="Уборка",
            time="18:00:00",
            action="Убраться в квартире",
            is_nice=False,
            related=self.habit,
            periodicity=1,
            duration=60,
            is_public=False
        )

    def test_create_habit(self):
        """Тестирование создания привычки"""

        url = reverse("habits:habits_create")
        data = {
            "owner": self.user.pk,
            "place": "Магазин",
            "time": "18:00:00",
            "action": "Пойти в магазин за покупками",
            "duration": 60,
            "periodicity": 1,
            "sunday": True,
            "monday": True,
            "tuesday": True,
            "wednesday": True,
            "thursday": True,
            "friday": True,
            "saturday": True
        }

        response = self.client.post(url, data=data)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data.get("owner"), self.user.pk)
        self.assertEqual(data.get("place"), "Магазин")
        self.assertEqual(data.get("time"), "18:00:00")
        self.assertEqual(data.get("action"), "Пойти в магазин за покупками")
        self.assertEqual(data.get("duration"), 60)
        self.assertEqual(data.get("periodicity"), 1)
        self.assertEqual(data.get("friday"), True)

    def test_create_habit_duration_periodicy_validator(self):
        """Тестирование работы валидаиора"""

        url = reverse("habits:habits_create")
        data = {
            "owner": self.user.pk,
            "place": "Магазин",
            "time": "18:00:00",
            "action": "Пойти в магазин за покупками",
            "duration": 180,
            "periodicity": 8
        }

        response = self.client.post(url, data=data)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_week_periodicity_validator(self):
        """Хотя бы один день в неделе должен быть выбран"""

        url = reverse("habits:habits_create")
        data = {
            "owner": self.user.pk,
            "place": "Магазин",
            "time": "18:00:00",
            "action": "Пойти в магазин за покупками",
            "duration": 180,
            "periodicity": 8,
            "sunday": False,
            "monday": False,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_logic_good_habits_1(self):
        """Тестирование работы валидатора логики создания привычек"""

        # У приятной привычки не может быть вознаграждения или связанной привычки.

        url = reverse("habits:habits_create")
        data = {
            "owner": self.user.pk,
            "place": "Магазин",
            "time": "18:00:00",
            "action": "Пойти в магазин за покупками",
            "is_nice": True,
            "duration": 60,
            "periodicity": 1,
            "prize": "выпить коньяка"
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_logic_good_habits_2(self):
        """Тестирование работы валидатора логики создания привычек"""

        # Исключить одновременный выбор связанной привычки и указания вознаграждения.

        url = reverse("habits:habits_create")
        data2 = {
            "owner": self.user.pk,
            "place": "Магазин",
            "time": "19:00:00",
            "action": "Снова пойти в магазин за покупками",
            "is_nice": False,
            "related": self.habit,
            "duration": 60,
            "periodicity": 1,
            "prize": "выпить еще больше коньяка"
        }
        response = self.client.post(url, data=data2)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_logic_good_habits_3(self):
        """Тестирование работы валидатора логики создания привычек"""

        # В связанные привычки могут попадать только привычки с признаком приятной привычки.

        url = reverse("habits:habits_create")

        data3 = {
            "owner": self.user.pk,
            "place": "Магазин",
            "time": "19:00:00",
            "action": "Снова пойти в магазин за покупками",
            "is_nice": False,
            "related": self.habit_nice_false,
            "duration": 60,
            "periodicity": 1,
        }
        response = self.client.post(url, data=data3)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_datetime_convertion(self):
    #     updated_text = str(self.habit.updated_at)
    #     updated = updated_text[0:10] + 'T' + updated_text[11:26] + 'Z'
    #
    #     print(f"{updated} | {datetime.strftime(self.habit.updated_at, '%Y-%m-%dT%H:%M:%S.%fZ')}  ")
    #
    #     self.assertEqual(updated, datetime.strftime(self.habit.updated_at, '%Y-%m-%dT%H:%M:%S.%fZ'))

    def test_list_habit(self):
        """Тестирование вывода всех привычек"""

        url = reverse("habits:habits_list")
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, data.get("count"))

    def test_retrieve_habit(self):
        """Тестирование просмотра одной привычки"""

        url = reverse("habits:habits_retrieve", args=(self.habit.pk,))
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("owner"), self.habit.owner.id)
        self.assertEqual(data.get("place"), self.habit.place)
        self.assertEqual(data.get("time"), self.habit.time)
        self.assertEqual(data.get("action"), self.habit.action)
        self.assertEqual(data.get("duration"), self.habit.duration)
        self.assertEqual(data.get("periodicity"), self.habit.periodicity)
        self.assertEqual(data.get("friday"), True)

    def test_update_habit(self):
        """Тестирование изменений привычки"""

        url = reverse("habits:habits_update", args=(self.habit.pk,))
        data = {
            "owner": self.user.pk,
            "place": "Фитнес-зал",
            "time": "19:00:00",
            "action": "Тренировка в фитнес-зале",
            "duration": 120,
            "periodicity": 1,
        }
        response = self.client.put(url, data)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("owner"), self.habit.owner.id)
        self.assertEqual(data.get("place"), "Фитнес-зал")
        self.assertEqual(data.get("time"), "19:00:00")
        self.assertEqual(data.get("action"), "Тренировка в фитнес-зале")
        self.assertEqual(data.get("duration"), 120)
        self.assertEqual(data.get("periodicity"), 1)
        self.assertEqual(data.get("is_nice"), True)
        self.assertEqual(data.get("sunday"), True)

    def test_delete_habit(self):
        """Тестирование удаления привычки"""

        url = reverse("habits:habits_delete", args=(self.habit.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_public_habit(self):
        """Тестирование вывода публичных привычек"""

        url = reverse("habits:public_list")
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, data.get("count"))
