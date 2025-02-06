from django.test import TestCase, Client


class TestExhibition(TestCase):

    # Выполнение перед всеми тестами единожды
    @classmethod
    def setUpTestData(cls):
        cls.AUTH_URL = 'api/v1/accounts/'
        cls.BUSINESS_URL = 'api/v1/business/'
        cls.ACTIVITIES_URL = 'api/v1/activities/'

    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two.")
        self.assertEqual(1 + 1, 2)
