import json
from unittest.mock import patch
import requests
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import CarMake,CarModel

class ApplicationTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user(username="driver",password="Journey!2026Safe",first_name="Demo",last_name="Driver")
        self.brand=CarMake.objects.create(name="Toyota")
        self.car=CarModel.objects.create(car_make=self.brand,name="Camry",type="Sedan",year=2023)
    def post(self,path,data):
        return self.client.post('/djangoapp/'+path,json.dumps(data),content_type='application/json')
    def test_registration_and_session(self):
        r=self.post('register',{'userName':'newdriver','password':'Roadtrip!9988Safe','firstName':'New'})
        self.assertEqual(r.status_code,201)
        self.assertEqual(self.client.get('/djangoapp/session').json()['userName'],'newdriver')
        self.assertEqual(self.post('register',{'userName':'newdriver','password':'Roadtrip!9988Safe'}).status_code,409)
    def test_weak_password_rejected(self):
        self.assertEqual(self.post('register',{'userName':'short','password':'123'}).status_code,400)
    def test_login_logout(self):
        self.assertEqual(self.post('login',{'userName':'driver','password':'incorrect'}).status_code,401)
        self.assertEqual(self.post('login',{'userName':'driver','password':'Journey!2026Safe'}).status_code,200)
        self.assertEqual(self.post('logout',{}).status_code,200)
        self.assertIsNone(self.client.get('/djangoapp/session').json()['userName'])
    def test_csrf_enforced(self):
        client=Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/djangoapp/login','{}',content_type='application/json').status_code,403)
        client.get('/djangoapp/session')
        token=client.cookies['csrftoken'].value
        self.assertEqual(client.post('/djangoapp/login',json.dumps({'userName':'driver','password':'Journey!2026Safe'}),content_type='application/json',HTTP_X_CSRFTOKEN=token).status_code,200)
    def test_bad_json(self):
        self.assertEqual(self.client.post('/djangoapp/login','{',content_type='application/json').status_code,400)
    def test_car_catalog(self):
        self.assertEqual(self.client.get('/djangoapp/get_cars').json()['CarModels'][0]['CarMake'],'Toyota')
    @patch('djangoapp.views.get_request',return_value=[{'id':1,'state':'Kansas'}])
    def test_state_filter_proxy(self,backend):
        self.assertEqual(self.client.get('/djangoapp/get_dealers/Kansas').status_code,200)
        backend.assert_called_once_with('fetchDealers/Kansas')
    @patch('djangoapp.views.get_request',side_effect=requests.ConnectionError())
    def test_backend_failure(self,backend):
        self.assertEqual(self.client.get('/djangoapp/get_dealers').status_code,502)
    @patch('djangoapp.views.analyze_review_sentiments',return_value='positive')
    @patch('djangoapp.views.get_request',return_value=[{'id':1,'review':'Excellent!'}])
    def test_review_sentiment(self,backend,sentiment):
        self.assertEqual(self.client.get('/djangoapp/reviews/dealer/1').json()['reviews'][0]['sentiment'],'positive')
    @patch('djangoapp.views.post_review',return_value={'id':100})
    @patch('djangoapp.views.get_request',return_value=[{'id':1}])
    def test_authenticated_review_and_author(self,backend,post):
        data={'dealership':1,'review':'Great service','purchase_date':'2025-01-01','car_year':2023,'car_id':self.car.id,'name':'Impersonated'}
        self.assertEqual(self.post('add_review',data).status_code,401)
        self.client.force_login(self.user)
        self.assertEqual(self.post('add_review',data).status_code,201)
        self.assertEqual(post.call_args.args[0]['name'],'Demo Driver')
        data['car_year']=1900
        self.assertEqual(self.post('add_review',data).status_code,400)
    def test_method_restrictions(self):
        self.assertEqual(self.client.get('/djangoapp/logout').status_code,405)
