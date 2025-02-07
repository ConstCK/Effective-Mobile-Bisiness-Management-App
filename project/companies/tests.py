from django.test import TestCase, Client

from accounts.models import Profile
from companies.constants import TestCompanyData


class TestCompany(TestCase):

    # Выполнение перед всеми тестами единожды
    @classmethod
    def setUpTestData(cls):
        cls.BUSINESS_URL = '/api/v1/business/'
        cls.data = TestCompanyData()
        cls.profile_4 = Client().post(path='/api/v1/accounts/',
                                      data=TestCompanyData().user_1)

        p_4 = Profile.objects.get(id=cls.profile_4.data['profile']['id'])
        p_4.position = 'BOSS'
        p_4.save()

        cls.profile_5 = Client().post(path='/api/v1/accounts/',
                                      data=TestCompanyData().user_2)

    # Успешное создание организационной структуры
    def test_create_structure(self):
        response = self.client.post(path=f'{self.BUSINESS_URL}structures/',
                                    data={'name': 'Линейная'},
                                    headers={'Authorization': f'Token {self.profile_4.data['token']}'})
        self.assertEqual(response.status_code, 201)
        return response.data

    # Создание организационной структуры не администратором
    def test_create_structure_fail(self):
        response = self.client.post(path=f'{self.BUSINESS_URL}structures/',
                                    data={'name': 'Линейная'},
                                    headers={'Authorization': f'Token {self.profile_5.data['token']}'})
        print(response.data)
        self.assertEqual(response.status_code, 403)

    # Добавление членов организационной структуры
    def test_add_member(self):
        self.test_create_structure()
        response = self.client.post(path=f'{self.BUSINESS_URL}structures/1/add-member/',
                                    data=self.data.structure_member,
                                    headers={'Authorization': f'Token {self.profile_4.data['token']}'})

        self.assertEqual(response.status_code, 201)

    # Успешное удаление организационной структуры
    def test_delete_structure(self):
        structure = self.test_create_structure()

        response = self.client.delete(path=f'{self.BUSINESS_URL}structures/{structure['id']}/',
                                      headers={'Authorization': f'Token {self.profile_4.data['token']}'})
        self.assertEqual(response.status_code, 204)

    # Получение организационной структуры
    def test_get_structure(self):
        structure = self.test_create_structure()

        response = self.client.get(path=f'{self.BUSINESS_URL}structures/{structure['id']}/',
                                   headers={'Authorization': f'Token {self.profile_4.data['token']}'})
        self.assertEqual(response.status_code, 200)

    # Успешное создание компании
    def test_create_company(self):
        structure = self.test_create_structure()
        response = self.client.post(path=f'{self.BUSINESS_URL}companies/',
                                    data={'name': 'Main', 'structure': structure['id']},
                                    headers={'Authorization': f'Token {self.profile_4.data['token']}'})
        self.assertEqual(response.status_code, 201)
        return response.data

    # Получение данных компании
    def test_get_company(self):
        company = self.test_create_company()
        response = self.client.get(path=f'{self.BUSINESS_URL}companies/{company['id']}/',
                                   headers={'Authorization': f'Token {self.profile_4.data['token']}'})
        self.assertEqual(response.status_code, 200)

    # Удаление компании
    def test_delete_company(self):
        company = self.test_create_company()
        response = self.client.delete(path=f'{self.BUSINESS_URL}companies/{company['id']}/',
                                      headers={'Authorization': f'Token {self.profile_4.data['token']}'})
        self.assertEqual(response.status_code, 200)
