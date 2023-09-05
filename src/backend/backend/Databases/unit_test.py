import unittest
from AC_schema import database
from AC_schema import api
from AC_schema import generate_database
import datetime




class MyTestCase(unittest.TestCase):

    def test_signup_success(self):
        # test a success signup
        print('testing for success signup function')
        # clean the database
        generate_database()
        test_object = api()
        result, access_token, user_id = test_object.sign_up("abc", "cba")
        self.assertTrue(result, "failure to sign up")

    def test_signup_failure(self):
        print('testing for failure signup function')
        # test a failed signup
        # clean the database
        generate_database()
        test_object = api()
        # sign up the same account twice
        test_object.sign_up("abc", "cba")
        result, access_token, user_id = test_object.sign_up("abc", "cdda")
        self.assertFalse(result, "success to sign up")

    def test_login_success(self):
        print('testing for success login function')
        # test a success login
        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("abc", "cba")
        result, access_token, user_id = test_object.login("abc","cba")
        self.assertTrue(result, "failure to login")
        self.assertEqual(access_token, test_object._get_Token_by_Name("abc"), "access token is not true")
        self.assertEqual(user_id, test_object._get_user_id("abc"), "user id is not true")

    def test_login_failure(self):
        print('testing for failure login function')
        # test a failure login
        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("abc", "cba")
        print("testing for non-exist user login")
        result, access_token, user_id = test_object.login("cba","cba")
        self.assertFalse(result, "success to login")
        self.assertEqual(access_token, 0)
        self.assertEqual(user_id, 0)

        print("testing for incorrect password login")
        result, access_token, user_id = test_object.login("abc", "cbd")
        self.assertFalse(result, "success to login")
        self.assertEqual(access_token, 2)
        self.assertEqual(user_id, 2)

    def test_reset_password(self):
        print('testing for resetting password')
        generate_database()
        test_object = api()
        # sign up the account first

        print("reset password when the access token is correct username is in email form")
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        result, indicator = test_object.reset_password("hcha0071@student.monash.edu",access_token,"cab")
        self.assertTrue(result, "username is not in email form")
        self.assertEqual(None, indicator, "indicator should return nothing")

        print("reset password when the access toke is correct username is not in email form")
        test_object.sign_up("abc","cbc")
        access_token = test_object._get_Token_by_Name("abc")
        result, indicator = test_object.reset_password("abc",access_token, "cbc")
        self.assertFalse(result,"username should in email form")
        self.assertEqual(4, indicator, "indicator should return 4")

        print("reset password when the access token is not correct username is in email form")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        result, indicator = test_object.reset_password("hcha0071@student.monash.edu",access_token[-1],"bca")
        self.assertFalse(result, "username is not in email form")
        self.assertEqual(-1, indicator, "Access token should be correct")

    def test_add_goal(self):
        print("testing for add goal")
        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")

        print("testing for succeed adding goal")
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        result, indicator = test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        self.assertTrue(result,"failure to add goal")
        self.assertEqual(1, indicator, "goal id is not correct")

        print("testing for same goal adding")
        result, indicator = test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        self.assertFalse(result,"It should return false")
        self.assertEqual(1, indicator, "Error code should return 1")

    def test_add_activity(self):
        print("testing for add activity")
        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        print("testing for succeed adding activity")
        result, indicator = test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)
        self.assertTrue(result,"Not successfully add activity")
        self.assertEqual(None, indicator, "Should return None")

        print("testing for add existing activity")
        result, indicator = test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)
        self.assertFalse(result,"There is no activity exist")
        self.assertEqual(1, indicator, "Wrong error indicator")

    def test_get_goals(self):
        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        print("Testing for not adding any goal")
        result, indicator = test_object.get_goals(access_token, user_id)
        self.assertTrue(result, "failure to get goal_list")
        self.assertEqual([], indicator, "Should return None list")

        print("Testing for adding two goals")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        result, indicator = test_object.get_goals(access_token,user_id)
        self.assertTrue(result, "failure to get goal_list")
        self.assertEqual('become a challenger',indicator['goal_1']['goal_name'], 'goal name is not true')
        self.assertEqual('be happiness', indicator['goal_2']['goal_name'],'goal name is not true')

    def test_get_goals_id(self):
        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        print("Testing for not adding any goal")
        result, indicator = test_object.get_goals_id(access_token,user_id)
        self.assertFalse(result, "Should not get any goal")
        self.assertEqual(0, indicator, "You have added something")
        print("Testing for adding two goals")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        result, indicator = test_object.get_goals_id(access_token,user_id)
        self.assertTrue(result, "failed to get goals id list")
        self.assertEqual([1,2], indicator, "get wrong goals id list")

    def test_edit_goal(self):
        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")

        print("testing edit non-exist goal")
        result, indicator = test_object.edit_goal(3, 'own me money', '1 million', 0, 100, '2023-04-23',access_token)
        self.assertFalse(result, "Goal has been edited")
        self.assertEqual(0, indicator, "Wrong error code")

        print("testing for same goal name exist")
        result, indicator = test_object.edit_goal(2, 'become a challenger', '1 million',0, 100, '2023-04-23', access_token)
        self.assertFalse(result, "Goal has been edited")
        self.assertEqual(1,indicator, "Wrong error code")

        print("testing for successfully editing the goal")
        result, indicator = test_object.edit_goal(1, 'own me money', '1 million', 0, 100, '2023-04-23',access_token)
        self.assertTrue(result, "Goal has not be edited")
        self.assertEqual(None, indicator, "Indicator should not return anything if successfully editing")

    def test_delete_goal(self):
        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")

        print("testing for failure to find the goal")
        result, indicator = test_object.delete_goal(3,access_token)
        self.assertFalse(result, "Goal_id is found")
        self.assertEqual(0,indicator,"Wrong error code")

        print("testing for successfully deleting the goal")
        result, indicator = test_object.delete_goal(2,access_token)
        self.assertTrue(result, "Goal can not found")
        self.assertEqual(None, indicator, "Should return Nothing")

    def test_edit_activity(self):
        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")

        # add an activity
        test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)

        # add another activity
        test_object.add_activity(3, "practice malphite for 50 games", "Easy", access_token, 1)

        print("testing if we cannot find the activity")
        result, indicator = test_object.edit_activity(3, "eat sushi", "oishii", 5, 2, access_token)
        self.assertFalse(result, "The activity is found")
        self.assertEqual(0,indicator,"Wrong error code")

        print("testing if the activity name is still same")
        result, indicator = test_object.edit_activity(2, "practice Aphelios for 100 games", "oishii", 5, 1, access_token)
        self.assertFalse(result, "The new activity name is different")
        self.assertEqual(1, indicator, "Wrong error code")

        print("testing for succeeding editing the activity")
        result, indicator = test_object.edit_activity(1, "eat sushi", "oishii", 5, 2, access_token)
        self.assertTrue(result, "The activity does not be edited")
        self.assertEqual(None, indicator, "Wrong error code")

    def test_delete_activity(self):
        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")

        # add an activity
        test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)

        # add another activity
        test_object.add_activity(3, "practice malphite for 50 games", "Easy", access_token, 2)

        print("testing that cannot find the activity")
        result, indicator = test_object.delete_activity(3, access_token)
        self.assertFalse(result, "The activity is found")
        self.assertEqual(0,indicator,"Wrong error code")

        print("testing successfully delete the activity")
        result, indicator = test_object.delete_activity(2,access_token)
        self.assertTrue(result, "Can not find the activity")
        self.assertEqual(None, indicator, "Should return None")

    def test_get_activities(self):

        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        print("testing get without insert any activities")
        result,indicator = test_object.get_activities(access_token,1)
        self.assertTrue(result, "Should return true")
        self.assertEqual([], indicator, "No selected activities should return empty list")
        # add an activity
        test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)

        # add another activity
        test_object.add_activity(3, "practice malphite for 50 games", "Easy", access_token, 1)
        print("testing when add two activities")
        result, indicator = test_object.get_activities(access_token,1)
        self.assertTrue(result,"Should return true")
        self.assertEqual([1,2], indicator, "Should return the two added activities id")

    def test_get_activity_obj(self):

        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        print("testing get object without insert any activities")
        result, indicator = test_object.get_activities_obj(access_token,1)
        self.assertFalse(result)
        self.assertEqual(0, indicator)
        print("testing if there is one activity in the goal")
        test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)
        result, indicator = test_object.get_activities_obj(access_token,1)
        self.assertTrue(result)
        self.assertEqual([{'activity_id': 1, 'activity_name': 'practice Aphelios for 100 games', 'activity_desc': 'Hardcore', 'activity_impact': 4.0, 'activity_log': (True, [])}],indicator)

    def test_edit_impact_score(self):

        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        # add one activity
        test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)
        print("testing for non existing activity")
        result, indicator = test_object.edit_impact_score(2,3,access_token)
        self.assertFalse(result)
        self.assertEqual(0, indicator)
        print("testing for editing existing impact score")
        result, indicator = test_object.edit_impact_score(1,3,access_token)
        self.assertTrue(result)
        self.assertEqual(None, indicator)

    def test_get_impact_score(self):

        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        # add one activity
        test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)
        result, indicator = test_object.get_impact_score(1,access_token)
        self.assertTrue(result)
        self.assertEqual(4,indicator)

    def test_get_goal_progression(self):

        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        # add one activity
        test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)

        print("testing for non-goal exists")
        result, indicator = test_object.get_goal_progression(access_token,4)
        self.assertFalse(result)
        self.assertEqual(0,indicator)

        print("testing for the existing goal")
        result, indicator = test_object.get_goal_progression(access_token,1)
        self.assertTrue(result)
        self.assertEqual(0, indicator)

    def test_goal_progression_calculate(self):
        generate_database()

        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        # add one activity
        print("testing if calculation without any activity")
        result, indicator = test_object.goal_progression_calculate(1,access_token)
        self.assertFalse(result)
        self.assertEqual(3,indicator)

        test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)
        # add another activity
        test_object.add_activity(3, "practice malphite for 50 games", "easy", access_token, 1)
        # update the activity frequency
        obj = [[1, '2023-04-01', 3], [1, '2023-04-23', 5],[2, '2023-04-23', 5]]
        test_object.update_activity_frequency(access_token, obj, user_id)

        print("testing the goal progression after update the activity logs")
        result, indicator = test_object.goal_progression_calculate(1,access_token)
        self.assertTrue(result)
        self.assertEqual(47,indicator)

        print("testing if goal for calculation does not exist")
        result, indicator = test_object.goal_progression_calculate(3,access_token)
        self.assertFalse(result)
        self.assertEqual(0,indicator)


    def test_add_notes(self):
        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        print("testing for existing goal")
        result, indicator = test_object.add_notes(1,access_token,'2 days added')
        self.assertTrue(result)
        self.assertEqual(None, indicator)
        print("testing for none existing goal")
        result, indicator = test_object.add_notes(3,access_token, '3 days added')
        self.assertFalse(result)
        self.assertEqual(0, indicator)

    def test_delete_notes(self):
        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        print("testing if the goal is not exists")
        result, indicator = test_object.delete_notes(3, access_token)
        self.assertFalse(result)
        self.assertEqual(0, indicator)
        print("testing if the notes exists")
        result, indicator = test_object.delete_notes(2, access_token)
        self.assertTrue(result)
        self.assertEqual(None, indicator)

    def test_get_notes(self):
        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        result, indicator = test_object.get_notes(1,access_token)
        print("testing if the notes exits")
        self.assertTrue(result)
        self.assertEqual("30 days limits",indicator)
        result, indicator = test_object.get_notes(3,access_token)
        print("testing if the goal of the notes does not exist")
        self.assertFalse(result)
        self.assertEqual(0, indicator)

    def test_edit_notes(self):
        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        print("testing for editing note")
        result, indicator = test_object.edit_notes(1,access_token, '23 days limits')
        self.assertTrue(result)
        self.assertEqual(None,indicator)
        print("testing for none existing goal id")
        result, indicator = test_object.edit_notes(4,access_token, '23 days limits')
        self.assertFalse(result)
        self.assertEqual(0,indicator)

    def test_edit_goal_name_and_notes(self):
        generate_database()
        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")

        print("testing for none existing goal id")
        result, indicator = test_object.edit_goal_name_and_notes(4,access_token,'22 days limites', 'new goal')
        self.assertFalse(result)
        self.assertEqual(0, indicator)

        print("testing for editing goal name and notes in goal id")
        result, indicator = test_object.edit_goal_name_and_notes(1,access_token,'22 days limites', 'new goal')
        self.assertTrue(result)
        self.assertEqual(None, indicator)

    def test_update_activity_frequency(self):
        generate_database()

        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        # add one activity
        test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)
        # add another activity
        test_object.add_activity(3, "practice malphite for 50 games", "easy", access_token, 1)
        print("testing for update activity log with existing activity")
        obj = [[1,'2023-04-01', 3], [2, '2023-04-23',5]]
        result, indicator = test_object.update_activity_frequency(access_token,obj,user_id)
        self.assertTrue(result)
        self.assertEqual(None,indicator)
        print("testing for none existing activity")
        obj = [[3,'2023-04-01', 3], [2, '2023-04-23',5]]
        result, indicator = test_object.update_activity_frequency(access_token,obj,user_id)
        self.assertFalse(result)
        self.assertEqual(0,indicator)

    def test_get_activity_log_before_date(self):
        generate_database()

        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        # add one activity
        test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)
        # add another activity
        test_object.add_activity(3, "practice malphite for 50 games", "easy", access_token, 1)
        # update the activity frequency
        obj = [[1, '2023-04-01', 3], [1, '2023-04-23', 5]]
        test_object.update_activity_frequency(access_token, obj, user_id)
        print("testing the activity logs before 2023-04-10")
        result, indicator = test_object.get_activity_log_before_date(access_token,user_id,1,'2023-04-10')
        self.assertTrue(result)
        self.assertEqual([{'activity_date': datetime.date(2023, 4, 1),'activity_frequency': 3,'activity_id': 1}], indicator)

    def test_get_all_activities_log(self):
        generate_database()

        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        # add one activity
        test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)
        # add another activity
        test_object.add_activity(3, "practice malphite for 50 games", "easy", access_token, 1)
        # update the activity frequency
        obj = [[1, '2023-04-01', 3], [1, '2023-04-23', 5],[2, '2023-04-23', 5]]
        test_object.update_activity_frequency(access_token, obj, user_id)
        print("testing get all activities log on 2023-04-01")
        result, indicator = test_object.get_all_activities_log(access_token,user_id,'2023-04-01')
        self.assertTrue(result)
        self.assertEqual([{'activity_date': '2023-04-01', 'activity_frequency': 3, 'activity_id': 1}], indicator)
        print("testing get all activities log on 2023-04-03")
        result, indicator = test_object.get_all_activities_log(access_token,user_id,'2023-04-03')
        self.assertTrue(result)
        self.assertEqual([], indicator)

    def test_edit_activities_log(self):
        generate_database()

        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        # add one activity
        test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)
        # add another activity
        test_object.add_activity(3, "practice malphite for 50 games", "easy", access_token, 1)
        # update the activity frequency
        obj = [[1, '2023-04-01', 3], [1, '2023-04-23', 5],[2, '2023-04-23', 5]]
        test_object.update_activity_frequency(access_token, obj, user_id)
        obj = [[1, '2023-04-01', 6], [1, '2023-04-23', 6],[2, '2023-04-23', 7]]
        print("testing whether the edit activities logs works")
        result, indicator = test_object.edit_activities_log(access_token,user_id,obj)
        self.assertTrue(result)
        self.assertEqual(None, indicator)

    def test_delete_activity_log(self):
        generate_database()

        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        # add one activity
        test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)
        # add another activity
        test_object.add_activity(3, "practice malphite for 50 games", "easy", access_token, 1)
        # update the activity frequency
        obj = [[1, '2023-04-01', 3], [1, '2023-04-23', 5],[2, '2023-04-23', 5]]
        test_object.update_activity_frequency(access_token, obj, user_id)

        print("delete the activity log with activity id 1 on '2023-04-01")
        result, indicator = test_object.delete_activities_log(access_token,user_id,1,'2023-04-01')
        self.assertTrue(result)
        self.assertEqual(None, indicator)
        print("delete the non-existing activity log")
        result, indicator = test_object.delete_activities_log(access_token,user_id,1,'2023-04-03')
        self.assertFalse(result)
        self.assertEqual(0,indicator)

    def test_get_all_activity_logs_by_user_id(self):
        generate_database()

        test_object = api()
        # sign up the account first
        test_object.sign_up("hcha0071@student.monash.edu", "cba")
        # get the user id and access token
        user_id = test_object._get_user_id("hcha0071@student.monash.edu")
        access_token = test_object._get_Token_by_Name("hcha0071@student.monash.edu")
        # add one goal
        test_object.add_goal("become a challenger", "1000 lp challenger", access_token, user_id, "30 days limits")
        # add another goal
        test_object.add_goal("be happiness", "happy everyday", access_token, user_id, "30 days limits")
        # add one activity
        test_object.add_activity(4, "practice Aphelios for 100 games", "Hardcore", access_token, 1)
        # add another activity
        test_object.add_activity(3, "practice malphite for 50 games", "easy", access_token, 1)
        # update the activity frequency
        obj = [[1, '2023-04-01', 3], [1, '2023-04-23', 5],[2, '2023-04-23', 5]]
        test_object.update_activity_frequency(access_token, obj, user_id)
        print("testing get all of the activity log by given user id")
        result, indicator = test_object.get_all_activity_logs_by_user_id(access_token,user_id)
        self.assertTrue(result)
        self.assertEqual([{'goal_id': 1,
  'logs': [{'activity_date': datetime.date(2023, 4, 1),
            'activity_frequency': 3,
            'activity_id': 1},
           {'activity_date': datetime.date(2023, 4, 23),
            'activity_frequency': 5,
            'activity_id': 1},
           {'activity_date': datetime.date(2023, 4, 23),
            'activity_frequency': 5,
            'activity_id': 2}]},
 {'goal_id': 2, 'logs': []}],indicator)
if __name__ == '__main__':
    unittest.main()
