from sqlite3 import Date
from flask import Flask, request, make_response, jsonify, json # pip install Flask
from flask_cors import CORS # pip install Flask-Cors
from backend.Databases.AC_schema import api, database, generate_database
import re

import unittest
from unittest.mock import MagicMock

from queries import app

class TestSign_up(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        generate_database()
        # Create a test user account
        # data = {'username': 'hch@student.monash.edu', 'password': 'carychy'}
        # response = self.client.post('/sign-up?username=hch@student.monash.edu&password=carychy')
        # print(response)
        # self.assertEqual(response.status_code, 200)

    def test_valid_sign_up(self):
        # Test logging in with valid credentials

        response = self.client.post('/sign-up?username=hcha0071@student.monash.edu&password=carychy')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('access_token', data)

    def test_invalid_credentials(self):
        # Test logging in with invalid credentials
        data = {'username': 'hcha0071@student.monash.edu', 'password': 'carysb'}
        response = self.client.post('/sign-up', data=data)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

class TestAddGoal(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        generate_database()
        # Set up test data for user signup
        username = 'test@monash.edu'
        password = 'test_password'

        # Create a test user
        signup_response = self.client.post(f'/sign-up?username={username}&password={password}')
        signup_json = json.loads(signup_response.data)

        # Extract access_token and user_id
        self.access_token = signup_json.get('access_token')
        self.user_id = signup_json.get('user_id')

        # Set up test data for adding a new goal
        self.goal_data = {
            'goal_name': 'test_goal_name',
            'goal_desc': 'test_goal_desc',
            'goal_notes': 'test_goal_notes',
            'goal_activities': [{'activity_name': 'test_activity', 'activity_desc': 'test_desc','activity_score': 5}]
        }

    def test_add_new_goal(self):
        # Send POST request to the /add-new-goal endpoint
        response = self.client.post('/add-new-goal', json=self.goal_data, headers={'Authorization': 'Bearer ' + self.access_token, 'X-User-Id': self.user_id})

        # Verify that the request was successful
        self.assertEqual(response.status_code, 200)

        # Verify the success message in the response
        json_data = json.loads(response.data)
        self.assertEqual(json_data['success'], 'Goal successfully created!')


class TestEditGoal(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Set up test data for user signup
        username = 'hcha0071@monash.edu'
        password = 'carychy'

        generate_database()

        # Create a test user
        signup_response = self.client.post(f'/sign-up?username={username}&password={password}')
        signup_json = json.loads(signup_response.data)

        # Extract access_token and user_id
        self.access_token = signup_json.get('access_token')
        self.user_id = signup_json.get('user_id')

        # Set up test data for adding new goals
        self.goal_data_1 = {
            'goal_name': 'test_goal_name_1',
            'goal_desc': 'test_goal_desc_1',
            'goal_notes': 'test_goal_notes_1',
            'goal_activities': [{'activity_name': 'test_activity_1','activity_desc': 'test_desc_1','activity_score': 5}]
        }

        self.goal_data_2 = {
            'goal_name': 'test_goal_name_2',
            'goal_desc': 'test_goal_desc_2',
            'goal_notes': 'test_goal_notes_2',
            'goal_activities': [{'activity_name': 'test_activity_2','activity_desc': 'test_desc_2' ,'activity_score': 10}]
        }

        # Create test goals
        for goal_data in [self.goal_data_1, self.goal_data_2]:
            response = self.client.post('/add-new-goal', json=goal_data, headers={'Authorization': 'Bearer ' + self.access_token, 'X-User-Id': self.user_id})
            assert response.status_code == 200, 'Failed to set up test goal'


        self.edit_goal_data = {
            'goal_id': 1,
            'goal_name': 'edited_test_goal_name',
            'goal_activities': [{'activity_id':1,'activity_name': 'another_test_activity', 'another_activity_desc': 'anothertest_desc','activity_score': 4}],
            'goal_notes': 'edited_test_goal_notes'
        }

    def test_edit_goal(self):
        # Send PUT request to the /edit-goal endpoint
        response = self.client.put('/edit-goal', json=self.edit_goal_data, headers={'Authorization': 'Bearer ' + self.access_token})

        # Verify that the request was successful
        self.assertEqual(response.status_code, 200)

        # Verify the success message in the response
        json_data = json.loads(response.data)
        self.assertEqual(json_data['success'], 'Successfully edited goal!')

class TestDeleteGoal(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Set up test data for user signup
        username = 'hcha0071@monash.edu'
        password = 'carychy'

        generate_database()

        # Create a test user
        signup_response = self.client.post(f'/sign-up?username={username}&password={password}')
        signup_json = json.loads(signup_response.data)

        # Extract access_token and user_id
        self.access_token = signup_json.get('access_token')
        self.user_id = signup_json.get('user_id')

        # Set up test data for adding new goals
        self.goal_data_1 = {
            'goal_name': 'test_goal_name_1',
            'goal_desc': 'test_goal_desc_1',
            'goal_notes': 'test_goal_notes_1',
            'goal_activities': [{'activity_name': 'test_activity_1','activity_desc': 'test_desc_1','activity_score': 5}]
        }

        self.goal_data_2 = {
            'goal_name': 'test_goal_name_2',
            'goal_desc': 'test_goal_desc_2',
            'goal_notes': 'test_goal_notes_2',
            'goal_activities': [{'activity_name': 'test_activity_2','activity_desc': 'test_desc_2' ,'activity_score': 10}]
        }

        # Create test goals
        for goal_data in [self.goal_data_1, self.goal_data_2]:
            response = self.client.post('/add-new-goal', json=goal_data, headers={'Authorization': 'Bearer ' + self.access_token, 'X-User-Id': self.user_id})

    def test_delete_goal(self):
        # Send DELETE request to the /delete-goal endpoint
        response = self.client.delete('/delete-goal', json={'goal_id': 1}, headers={'Authorization': 'Bearer ' + self.access_token})

        # Verify that the request was successful
        self.assertEqual(response.status_code, 200)

        # Verify the success message in the response
        json_data = json.loads(response.data)
        self.assertEqual(json_data['success'], 'Goal deleted successfully!')

class TestLogActivities(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Set up test data for user signup
        username = 'hcha0071@monash.edu'
        password = 'carychy'

        generate_database()

        # Create a test user
        signup_response = self.client.post(f'/sign-up?username={username}&password={password}')
        signup_json = json.loads(signup_response.data)

        # Extract access_token and user_id
        self.access_token = signup_json.get('access_token')
        self.user_id = signup_json.get('user_id')

        # Set up test data for adding new goals
        self.goal_data_1 = {
            'goal_name': 'test_goal_name_1',
            'goal_desc': 'test_goal_desc_1',
            'goal_notes': 'test_goal_notes_1',
            'goal_activities': [{'activity_name': 'test_activity_1','activity_desc': 'test_desc_1','activity_score': 5}]
        }

        self.goal_data_2 = {
            'goal_name': 'test_goal_name_2',
            'goal_desc': 'test_goal_desc_2',
            'goal_notes': 'test_goal_notes_2',
            'goal_activities': [{'activity_name': 'test_activity_2','activity_desc': 'test_desc_2' ,'activity_score': 10}]
        }

        # Create test goals
        for goal_data in [self.goal_data_1, self.goal_data_2]:
            response = self.client.post('/add-new-goal', json=goal_data, headers={'Authorization': 'Bearer ' + self.access_token, 'X-User-Id': self.user_id})

    def test_log_activities(self):
        # Set up test data for logging activities
        activities_obj = [(1, '2023-5-14', 3)]

        # Send POST request to the /log-activities endpoint
        response = self.client.post('/log-activities', json={'activities_obj': activities_obj}, headers={'Authorization': 'Bearer ' + self.access_token, 'X-User-Id': self.user_id})

        # Verify that the request was successful
        self.assertEqual(response.status_code, 200)

        # Verify the success message in the response
        json_data = json.loads(response.data)
        self.assertEqual(json_data['success'], 'Activities updated successfully!')

if __name__ == '__main__':
    unittest.main()