import json

from django.test import TestCase, Client

from accounts.models import Profile
from activities.constants import TestActivityData


class TestActivities(TestCase):

    # Выполнение перед всеми тестами единожды
    @classmethod
    def setUpTestData(cls):
        cls.ACTIVITIES_URL = '/api/v1/activities/'
        cls.data = TestActivityData()
        cls.profile_6 = Client().post(path='/api/v1/accounts/',
                                      data=TestActivityData().user_1)

        p_6 = Profile.objects.get(id=cls.profile_6.data['profile']['id'])
        p_6.position = 'BOSS'
        p_6.save()

        cls.profile_7 = Client().post(path='/api/v1/accounts/',
                                      data=TestActivityData().user_2)

    # Успешное создание новости 1
    def test_create_news_1(self):
        response = self.client.post(path=f'{self.ACTIVITIES_URL}news/',
                                    data=self.data.news_1,
                                    headers={'Authorization': f'Token {self.profile_6.data['token']}'})
        self.assertEqual(response.status_code, 201)
        return response.data

    # Успешное создание новости 2
    def test_create_news_2(self):
        response = self.client.post(path=f'{self.ACTIVITIES_URL}news/',
                                    data=self.data.news_2,
                                    headers={'Authorization': f'Token {self.profile_6.data['token']}'})
        self.assertEqual(response.status_code, 201)
        return response.data

    # Получение списка новостей
    def test_get_all_news(self):
        self.test_create_news_1()
        self.test_create_news_2()
        response = self.client.get(path=f'{self.ACTIVITIES_URL}news/',
                                   headers={'Authorization': f'Token {self.profile_6.data['token']}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    # Успешное создание встречи 1
    def test_create_meeting_1(self):
        response = self.client.post(path=f'{self.ACTIVITIES_URL}meeting/',
                                    data=self.data.meeting_1,
                                    headers={'Authorization': f'Token {self.profile_6.data['token']}'})
        self.assertEqual(response.status_code, 201)
        return response.data

    # Успешное создание встречи 2
    def test_create_meeting_2(self):
        response = self.client.post(path=f'{self.ACTIVITIES_URL}meeting/',
                                    data=self.data.meeting_2,
                                    headers={'Authorization': f'Token {self.profile_6.data['token']}'})
        self.assertEqual(response.status_code, 201)

    # Создание встречи с неправильными датами
    def test_create_meeting_fail(self):
        response = self.client.post(path=f'{self.ACTIVITIES_URL}meeting/',
                                    data=self.data.meeting_3,
                                    headers={'Authorization': f'Token {self.profile_6.data['token']}'})

        self.assertEqual(response.status_code, 400)

    # Получение списка со встречами
    def test_get_all_meetings(self):
        self.test_create_meeting_1()
        self.test_create_meeting_2()
        response = self.client.get(path=f'{self.ACTIVITIES_URL}meeting/',
                                   headers={'Authorization': f'Token {self.profile_6.data['token']}'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    # Удаление встречи
    def test_delete_meeting(self):
        meeting = self.test_create_meeting_1()
        response = self.client.get(path=f'{self.ACTIVITIES_URL}meeting/{meeting['data']['id']}/',
                                   headers={'Authorization': f'Token {self.profile_6.data['token']}'})

        self.assertEqual(response.status_code, 200)

    # Добавление участника встречи
    def test_add_participant(self):
        meeting = self.test_create_meeting_1()

        response = self.client.post(
            path=f'{self.ACTIVITIES_URL}meeting/{meeting['data']['id']}/add-participant/',
            data={'name': 'Second'},
            headers={'Authorization': f'Token {self.profile_6.data['token']}'})
        self.assertEqual(response.status_code, 200)

    # Успешное создание задачи 1
    def test_create_task_1(self):
        response = self.client.post(path=f'{self.ACTIVITIES_URL}task/',
                                    data=self.data.task_1,
                                    headers={'Authorization': f'Token {self.profile_6.data['token']}'})
        self.assertEqual(response.status_code, 201)
        return response.data

    # Успешное создание задачи 2
    def test_create_task_2(self):
        response = self.client.post(path=f'{self.ACTIVITIES_URL}task/',
                                    data=self.data.task_2,
                                    headers={'Authorization': f'Token {self.profile_6.data['token']}'})
        self.assertEqual(response.status_code, 201)
        return response.data

    # Успешное обновление задачи
    def test_update_task(self):
        task = self.test_create_task_1()
        response = self.client.put(
            path=f'{self.ACTIVITIES_URL}task/{task['data']['id']}/',
            data=json.dumps(self.data.new_task),
            headers={'Authorization': f'Token {self.profile_6.data['token']}',
                     'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 202)

    # Удаление задачи
    def test_delete_task_1(self):
        task = self.test_create_task_1()
        response = self.client.delete(path=f'{self.ACTIVITIES_URL}task/{task['data']['id']}/',
                                      headers={'Authorization': f'Token {self.profile_6.data['token']}'})
        self.assertEqual(response.status_code, 200)

    # Обновление статуса задачи
    def test_update_task_status(self):
        task = self.test_create_task_1()
        response = self.client.post(
            path=f'{self.ACTIVITIES_URL}task/{task['data']['id']}/update-status/',
            data=self.data.new_status,
            headers={'Authorization': f'Token {self.profile_7.data['token']}', }
        )
        self.assertEqual(response.status_code, 202)

    # Обновление статуса задачи не для исполнителя
    def test_update_task_status_fail(self):
        task = self.test_create_task_1()
        response = self.client.post(
            path=f'{self.ACTIVITIES_URL}task/{task['data']['id']}/update-status/',
            data=self.data.new_status,
            headers={'Authorization': f'Token {self.profile_6.data['token']}', }
        )
        self.assertEqual(response.status_code, 400)

    # Оценка задачи
    def test_estimate_task(self):
        task = self.test_create_task_1()
        response = self.client.post(
            path=f'{self.ACTIVITIES_URL}task/{task['data']['id']}/estimate-task/',
            data=self.data.task_mark_1,
            headers={'Authorization': f'Token {self.profile_6.data['token']}', }
        )
        self.assertEqual(response.status_code, 201)

    # Получение своих оценок
    def test_get_marks(self):
        response = self.client.get(
            path=f'{self.ACTIVITIES_URL}task/get-marks/',
            headers={'Authorization': f'Token {self.profile_6.data['token']}'},
        )
        self.assertEqual(response.status_code, 200)
