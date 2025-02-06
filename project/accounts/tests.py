import json

from django.test import TestCase, Client

from accounts.constants import TestProfileData
from accounts.models import Profile
from companies.models import Company, Structure


class TestProfile(TestCase):

    # Выполнение перед всеми тестами единожды
    @classmethod
    def setUpTestData(cls):
        cls.AUTH_URL = '/api/v1/accounts/'

        cls.data = TestProfileData()
        cls.profile_1 = Client().post(path='/api/v1/accounts/',
                                      data=TestProfileData().user_1)
        profile = Profile.objects.get(id=1)
        profile.position = 'BOSS'
        profile.save()

        cls.profile_2 = Client().post(path='/api/v1/accounts/',
                                      data=TestProfileData().user_2)
        cls.profile_3 = Client().post(path='/api/v1/accounts/',
                                      data=TestProfileData().user_4)
        profile = Profile.objects.get(id=1)
        profile.position = 'BOSS'
        profile.save()
        cls.structure = Structure.objects.create(name='Linear')
        cls.team = Company.objects.create(name='Primary', structure=cls.structure)

    # Успешная регистрация пользователя 1
    def test_register_user_success(self):
        response = self.client.post(path=self.AUTH_URL,
                                    data=self.data.user_3)
        self.assertEqual(response.data['profile']['name'], 'Volkov')
        self.assertEqual(response.status_code, 201)

    # Регистрация существующего пользователя
    def test_register_same_user(self):
        # with self.assertRaises(IntegrityError):
        response = self.client.post(path=self.AUTH_URL,
                                    data=self.data.user_2)

        self.assertEqual(response.status_code, 400)

    # Регистрация пользователя с коротким паролем
    def test_register_wrong_password_user(self):
        response = self.client.post(path=self.AUTH_URL,
                                    data=self.data.user_fail)
        self.assertEqual(response.status_code, 400)

    # Получение токена
    def test_get_token(self):
        response = self.client.post(path=f'{self.AUTH_URL}get-token/',
                                    data=self.data.login_password)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['token']), 40)
        self.assertEqual(response.data['token'], self.profile_1.data['token'])

    # Смена пароля пользователя
    def test_update_password(self):
        response = self.client.patch(path=f'{self.AUTH_URL}update-profile/',
                                     data=json.dumps({'password': 'newpassword1234'}),
                                     headers={'Authorization': f'Token {self.profile_2.data['token']}',
                                              'Content-Type': 'application/json'}, )

        self.assertEqual(response.status_code, 202)

    # Смена статуса пользователя
    def test_update_status(self):
        response = self.client.get(path=f'{self.AUTH_URL}{self.profile_2.data['profile']['id']}/upgrade-profile/',
                                   headers={'Authorization': f'Token {self.profile_1.data['token']}'})

        self.assertEqual(response.status_code, 202)

    # Изменение статуса профиля пользователя не администратором
    def test_update_status_fail(self):
        response = self.client.get(path=f'{self.AUTH_URL}{self.profile_2.data['profile']['id']}/upgrade-profile/',
                                   headers={'Authorization': f'Token {self.profile_2.data['token']}'})
        print("!", response.data)
        self.assertEqual(response.status_code, 403)

    # Удаление профиля пользователя
    def test_delete_profile(self):
        response = self.client.delete(path=f'{self.AUTH_URL}delete-profile/',
                                      headers={'Authorization': f'Token {self.profile_3.data['token']}'})

        self.assertEqual(response.status_code, 200)

    # Изменение должности профиля пользователя
    def test_update_position(self):
        response = self.client.post(
            path=f'{self.AUTH_URL}{self.profile_2.data['profile']['id']}/change-position-profile/',
            headers={'Authorization': f'Token {self.profile_1.data['token']}'},
            data={'position': 'MANAGER'}
        )
        self.assertEqual(response.status_code, 202)

    # Добавление пользователя к команде
    def test_add_profile_to_team(self):
        response = self.client.post(
            path=f'{self.AUTH_URL}{self.profile_2.data['profile']['id']}/add-profile-to-company/',
            headers={'Authorization': f'Token {self.profile_1.data['token']}'},
            data={'team': '1'}
        )
        self.assertEqual(response.status_code, 202)

    # Получение своих оценок
    def test_get_marks(self):
        response = self.client.get(
            path=f'{self.AUTH_URL}get-marks/',
            headers={'Authorization': f'Token {self.profile_1.data['token']}'},
        )
        self.assertEqual(response.status_code, 200)
