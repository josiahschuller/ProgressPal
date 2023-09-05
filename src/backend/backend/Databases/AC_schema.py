import mysql.connector
import hashlib
import secrets
import string
import re  # import the match function


class database:
    # connect information
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host="127.0.0.1",
                user="", # Do not commit your user, password and database name to Git
                passwd="",
                database="",
                auth_plugin='mysql_native_password'
            )
        except:
            raise Exception(
                "Either your connection is not set-up, or you have not filled in your username, password and database name")
        # set cursor buffer for allowing large output
        self.cursor = self.connection.cursor(buffered=True)
        self.hashlib = hashlib.sha256()


    def createDB(self, database):
        self.cursor.execute("CREATE DATABASE %s", database)

    def createTable(self, table, typeLst):
        formula = "CREATE TABLE " + table + " ("

        for i in range(len(typeLst)):
            if i == len(typeLst) - 1:
                formula += typeLst[i][0] + " " + typeLst[i][1]
            else:
                formula += typeLst[i][0] + " " + typeLst[i][1] + ','
        formula += ")"
        self.cursor.execute(formula)

    def dropTb(self, table):
        formula = "DROP table IF EXISTS %s"
        self.cursor.execute(formula, table)

    def commit(self):
        self.connection.commit()

    def __del__(self):
        self.connection.close()

class api:
    def __init__(self):
        # initialize the database
        self.db = database()
        self.db.connection.cursor(buffered=True)

    def login(self, username, password):
        """
        This function is used to log in the account
        """
        access_token = None
        hash_pw = self._myHash(password)
        Q1 = "SELECT user_id FROM users where user_username = %s"
        self.db.cursor.execute(Q1, (username,))
        user_id = self.db.cursor.fetchone()
        if user_id is not None:
            user_id = user_id[0]
            Q2 = "SELECT pwd FROM password where user_id = %s"
            self.db.cursor.execute(Q2, (user_id,))
            pwd = self.db.cursor.fetchone()[0]
            # password is not correct
            if pwd != hash_pw:
                # print("Your password is incorrect!")
                return False, 2, 2
            else:
                # create new access token and update it
                access_token = self._generate_access_token()
                Q3 = "UPDATE users SET access_token = %s where user_id = %s"
                self.db.cursor.execute(Q3, (access_token, user_id))
                self.db.commit()
                # print("Successfully login!")
                return True, access_token, user_id
        else:
            # print("This user does not exist!")
            return False, 0, 0

    def sign_up(self, username, password):
        access_token = None
        sql = "SELECT user_id FROM users where user_username = %s"
        values = (username,)
        self.db.cursor.execute(sql, values)
        user_id = self.db.cursor.fetchone()
        # if the name does not exist
        if user_id is None:
            # hash the password
            hash_pw = self._myHash(password)
            # random generate access token
            access_token = self._generate_access_token()
            # set the queries
            Q1 = "INSERT INTO users (user_username,access_token) VALUES (%s,%s)"
            Q2 = "SELECT user_id FROM users where user_username = %s"
            Q3 = "INSERT INTO password (pwd,user_id) VALUES (%s,%s)"
            # set input value
            values = (username, access_token)
            # insert the info for users table
            self.db.cursor.execute(Q1, values)
            # commit the update
            self.db.commit()
            # update the insert values
            values = (username,)
            # search the user id
            self.db.cursor.execute(Q2, values)
            user_id = self.db.cursor.fetchone()[0]
            # use the user id to input the password value
            values = (hash_pw, user_id)
            self.db.cursor.execute(Q3, values)
            self.db.commit()
            return True, access_token, user_id
        # if the account does exist, return none
        else:
            # print("Your sign-up account is already existed.")
            return False, 1, 1

    def reset_password(self, username, access_token, new_pw):
        """this function is used to reset the pass word if the password and access token is correct"""
        # if the username is in email form
        if self._check_email(username):
            if self._correct_access_Token(access_token, self._get_user_id(username)):
                user_id = self._get_user_id(username)
                # update the password to new password
                q1 = "UPDATE password SET pwd = %s where user_id = %s"
                # hash the new password and store it to the database
                new_hash_pw = self._myHash(new_pw)
                self.db.cursor.execute(q1, (new_hash_pw, user_id))
                self.db.commit()
                return True, None

            else:
                return False, -1
        else:
            # the username is not an email
            return False, 4

    def _correct_reset_link(self, url):
        # this function is used to return the correct reset link, if the link is correct, return True, url, email,
        # access_token, else return False, None, None, None
        # example url = "http://localhost:3000?username=EMAIL@ADDRESS.COM&access_token=ACCESS_TOKEN"
        url_pat = re.compile(r'(http://localhost:3000\?)')  # just an example url, change it if the url change
        email_pat = re.compile(r'username=([^&]+)')
        access_token_pat = re.compile(r'access_token=([^&]+)')
        # check the match email, return correct email if the email is valid
        email_match = email_pat.search(url)
        if email_match:
            email = email_match.group(1)
        else:
            email = None
        # check the access token, return correct access token if it is correct
        access_token_match = access_token_pat.search(url)
        if access_token_match:
            access_token = access_token_match.group(1)
        else:
            access_token = None

        url_match = url_pat.search(url)
        if url_match:
            url = url_match.group(1)
            access_token = None

        if bool(email and access_token and url and self._check_email(email)):
            return True, url, email, access_token
        else:
            return False, None, None, None

    def _check_email(self, username):
        """
        check whether a username is an email address
        reference from: https://www.c-sharpcorner.com/article/how-to-validate-an-email-address-in-python/
        """
        # check whether the username is email address
        # the pattern for email address
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        return bool(re.search(regex, username))

    def _get_Token_by_Name(self, username):
        sql = "SELECT access_token FROM users where user_username = %s"
        self.db.cursor.execute(sql, (username,))
        Token = self.db.cursor.fetchone()
        if Token is not None and len(Token) != 0:
            return Token[0]
        return Token

    def _get_Token_by_Id(self, Id):
        sql = "SELECT access_token FROM users where user_id = %s"
        self.db.cursor.execute(sql, (Id,))
        Token = self.db.cursor.fetchone()
        if Token is None:
            return None
        else:
            return Token[0]

    def _correct_access_Token(self, access_token, user_id):
        return self._get_Token_by_Id(user_id) == access_token

    def _internal_get_goals(self, goal_id, access_token, user_id):
        # if the access token is correct
        if self._correct_access_Token(access_token, user_id):
            sql = "SELECT goal_id FROM goal where user_id = %s"
            self.db.cursor.execute(sql, (user_id,))
            user = self.db.cursor.fetchone()
            if user is not None and len(user) != 0:
                # output the new goal info
                q1 = "SELECT goal_id, goal_name, goal_desc, goal_initial_state, goal_current_state, goal_date, notes FROM goal where goal_id = %s"
                self.db.cursor.execute(q1, (goal_id,))
                goal = self.db.cursor.fetchone()
                res = {"goal_id": goal[0], "goal_name": goal[1], "goal_desc": goal[2], "goal_initial_state": goal[3],
                       "goal_current_state": goal[4], "goal_date": goal[5], "goal_activities": [],
                       "goal_notes": goal[6]}
                # select the related activities
                # q2 = "SELECT activity_name, activity_desc, activity_impact FROM activity where goal_id = %s"
                # self.db.cursor.execute(q2, (goal_id,))
                # activities = self.db.cursor.fetchall()
                flg, activities = self.get_activities(access_token, goal_id)
                if flg:
                    for i in range(len(activities)):
                        # Get the activities
                        flg, activity = self._internal_get_activity(activities[i], access_token)
                        # Add them to the goal dict
                        res["goal_activities"].append(activity)
                return True, res
            else:
                # unable to find the user
                return False, 0
        else:
            return False, -1


    def add_goal(self, goal_name, goal_desc, access_token, user_id, notes=None):
        # if the access token is correct
        if self._correct_access_Token(access_token, user_id):
            # check whether the goal is unique
            Q1 = "SELECT goal_name FROM goal where user_id = %s"
            self.db.cursor.execute(Q1, (user_id,))
            res = self.db.cursor.fetchall()
            # if the user has set up some goal, check the goal in the goal list
            if res is not None and len(res) != 0:
                for name in res[0]:
                    if name == goal_name:
                        # print("Same goal exists!")
                        return False, 1
            if notes is None:
                # if the new goal does set up by the user, insert the goal to the goal lists
                Q2 = "INSERT INTO goal (goal_name,goal_desc,goal_date,user_id) VALUES (%s,%s,CURDATE(),%s)"
                values = (goal_name, goal_desc, user_id)
                self.db.cursor.execute(Q2, values)
                self.db.commit()
            else:
                # if the new goal does set up by the user, insert the goal to the goal lists
                Q2 = "INSERT INTO goal (goal_name,goal_desc,goal_date,user_id,notes) VALUES (%s,%s,CURDATE(),%s,%s)"
                values = (goal_name, goal_desc, user_id, notes)
                self.db.cursor.execute(Q2, values)
                self.db.commit()
            # print("Successfully added")
            Q3 = "SELECT goal_id FROM goal WHERE goal_name = %s AND user_id = %s"
            self.db.cursor.execute(Q3, (goal_name, user_id,))
            res = self.db.cursor.fetchone()
            self.db.commit()
            return True, res[0]
        # if the access token is incorrect
        else:
            # print("Illegal access token!")
            return False, -1

    def add_activity(self, impact_score, activity_name, activity_desc, access_token, goal_id):
        # get the user id by goal id
        user_id = self._get_user_id_by_goal(goal_id)
        # if the access token is correct
        if self._correct_access_Token(access_token, user_id):
            # check whether the activity is unique
            Q2 = "SELECT activity_name FROM activity where goal_id = %s"
            self.db.cursor.execute(Q2, (goal_id,))
            res = self.db.cursor.fetchall()
            # if the user has set up some goal, check the goal in the goal list
            if res is not None and len(res) != 0:
                for name in res[0]:
                    if name == activity_name:
                        # print("Same activity exists!")
                        return False, 1
            # print("Successfully added")
            Q3 = "INSERT INTO activity (activity_name,activity_desc,activity_impact,goal_id) VALUES (%s,%s,%s,%s)"
            self.db.cursor.execute(Q3, (activity_name, activity_desc, impact_score, goal_id))
            self.db.commit()
            return True, None
        else:
            # print("Illegal access token!")
            return False, -1

    def _get_user_id_by_goal(self, goal_id):
        # check the user id by the goal_id
        Q1 = "SELECT user_id FROM goal WHERE goal_id = %s"
        self.db.cursor.execute(Q1, (goal_id,))
        user = self.db.cursor.fetchone()
        # try whether the user is none
        try:
            user_id = user[0]
        except:
            return None
        return user_id

    def _get_user_id_by_activity(self, activity_id):
        Q1 = "SELECT goal_id FROM activity WHERE activity_id = %s"
        self.db.cursor.execute(Q1, (activity_id,))
        goal = self.db.cursor.fetchone()
        try:
            goal_id = goal[0]
        except:
            return None
        return self._get_user_id_by_goal(goal_id)

    def get_goals(self, access_token, user_id):
        # if the access token is correct
        if self._correct_access_Token(access_token, user_id):
            Q1 = "SELECT goal_id FROM goal WHERE user_id = %s"
            self.db.cursor.execute(Q1, (user_id,))
            goal_id_lst = self.db.cursor.fetchall()
            # if the goal list of the user is not None, return the goal list
            if goal_id_lst is not None and len(goal_id_lst) != 0:
                goal_list = dict()
                for i in range(len(goal_id_lst)):
                    flag, goal = self._internal_get_goals(goal_id_lst[i][0], access_token, user_id)
                    name = 'goal_' + str(i + 1)
                    goal_list[name] = goal
                return True, goal_list
            else:
                # print("You have not insert any goal!")
                return True, []
        else:
            # print("Illegal access token!")
            return False, -1

    def get_goals_id(self, access_token, user_id):
        # if the access token is correct
        if self._correct_access_Token(access_token, user_id):
            Q1 = "SELECT goal_id FROM goal WHERE user_id = %s"
            self.db.cursor.execute(Q1, (user_id,))
            goal_lst = self.db.cursor.fetchall()
            # if the goal list of the user is not None, return the goal list
            if goal_lst is not None and len(goal_lst) != 0:
                return True, [i[0] for i in goal_lst]
            else:
                # print("You have not insert any goal!")
                return False, 0
        else:
            # print("Illegal access token!")
            return False, -1

    # front end passes a goal object
    # goal_obj = {goal_name: "", goal_desc: "" ... activity1: {activity_name: "" ..}.. }
    # (goal_obj.goal_name, goal_obj.goal_desc, goal.activity1.activity_name)

    # q2 = "UPDATE goal SET goal_name = %s, goal_desc = %s, goal_date = %date,  where goal_id = %s"
    # input_data = (goal_name, activity_desc, activity_id)
    # self.db.cursor.execute(q2, input_data)
    # self.db.commit()

    # do the same for activity table
    # 1. in activity table look for activities that have the goal_id that's been given to you
    # 2. somehow remember them (extract and save them somewhere or whatever) - remember their IDs
    # 3. only those activities that match those IDs - update them

    def edit_goal(self, goal_id, goal_name, goal_desc, goal_initial_state, goal_current_state, goal_date, access_token):
        # get the user id by goal id
        # check whether the goal existing first
        q1 = "SELECT goal_name FROM goal where goal_id = %s"
        self.db.cursor.execute(q1, (goal_id,))
        goal = self.db.cursor.fetchone()
        if goal is None:
            return False, 0

        user_id = self._get_user_id_by_goal(goal_id)
        # if the access token is correct
        if self._correct_access_Token(access_token, user_id):
            user_id = self._get_user_id_by_goal(goal_id)
            # check for existing goal
            q1 = "SELECT goal_name, goal_id FROM goal where goal_name = %s and user_id = %s"
            self.db.cursor.execute(q1, (goal_name, user_id))
            goal = self.db.cursor.fetchone()
            if goal is not None and len(goal) != 0:
                original_name = goal[0]
                if original_name == goal_name and goal_id != goal[1]:
                    return False, 1
            # delete the related activity which belong to that goal
            q2 = "UPDATE goal SET goal_name = %s, goal_desc = %s" \
                 ", goal_initial_state = %s, goal_current_state = %s, " \
                 "goal_date = %s where goal_id = %s"
            input_data = (goal_name, goal_desc, goal_initial_state, goal_current_state, goal_date, goal_id)
            self.db.cursor.execute(q2, input_data)
            self.db.commit()
            return True, None
            # if can not find the goal
        else:
            # print("Illegal access token!")
            return False, -1

    def delete_goal(self, goal_id, access_token):
        # get the user id by goal id
        user_id = self._get_user_id_by_goal(goal_id)
        if user_id is None:
            # print("Can not find the goal!")
            return False, 0
        # if the access token is correct
        if self._correct_access_Token(access_token, user_id):
            q1 = "SELECT goal_name FROM goal where goal_id = %s"
            self.db.cursor.execute(q1, (goal_id,))
            goal = self.db.cursor.fetchone()
            if goal is not None and len(goal) != 0:
                # delete the related activity which belong to that goal
                q2 = "SELECT activity_id FROM activity WHERE goal_id = %s"
                self.db.cursor.execute(q2, (goal_id,))
                activity_lst = self.db.cursor.fetchall()
                for activity_id in activity_lst:
                    self.delete_activity(activity_id[0], access_token)
                # delete the goal
                q3 = "DELETE FROM goal WHERE goal_id = %s"
                self.db.cursor.execute(q3, (goal_id,))
                self.db.commit()
                # return true if successfully delete
                # print("Successfully delete the goal and it related activities!")

                return True, None
            else:
                # print("Can not find the goal!")
                return False, 0
        else:
            # print("Illegal access token!")
            return False, -1

    def edit_activity(self, activity_id, activity_name, activity_desc, activity_impact, goal_id, access_token):
        # get the user id by goal id
        user_id = self._get_user_id_by_activity(activity_id)
        q1 = "SELECT activity_name FROM activity where activity_id = %s"
        self.db.cursor.execute(q1, (activity_id,))
        activity = self.db.cursor.fetchone()
        if activity is None:
            return False, 0
        # if the access token is correct
        if self._correct_access_Token(access_token, user_id):
            q1 = "SELECT activity_name, activity_id FROM activity INNER JOIN goal ON goal.goal_id = activity.goal_id WHERE activity.activity_name = %s AND goal.goal_id = %s"
            self.db.cursor.execute(q1, (activity_name, goal_id))
            activity = self.db.cursor.fetchone()
            # update the activity info if we find the activity
            # check whether the old name is same with the new name
            if activity is not None and len(activity) != 0:
                original_name = activity[0]
                if original_name == activity_name and activity[1] != activity_id:
                    return False, 1

            q2 = "UPDATE activity SET activity_name = %s, activity_desc = %s, \
                 activity_impact = %s,goal_id = %s where activity_id = %s"
            input_data = (activity_name, activity_desc, activity_impact, goal_id, activity_id)
            self.db.cursor.execute(q2, input_data)
            self.db.commit()
            # q3 = "SELECT activity_name, activity_desc, activity_impact, goal_id FROM activity where activity_id = %s"
            # self.db.cursor.execute(q3, (activity_id,))
            # activity = self.db.cursor.fetchone()
            # res = {"activity_name": activity[0], "activity_desc": activity[1], "activity_impact": activity[2],
            #        "goal_id":
            #            activity[3]}
            # print("Successfully edit the activity")
            self.goal_progression_calculate(goal_id,access_token)
            return True, None
        else:
            # print("Illegal access token!")
            return False, -1

    def _internal_get_activity(self, activity_id, access_token):
        user_id = self._get_user_id_by_activity(activity_id)
        if self._correct_access_Token(access_token, user_id):
            q1 = "SELECT activity_id, activity_name, activity_desc, activity_impact FROM activity where activity_id = %s"
            self.db.cursor.execute(q1, (activity_id,))
            activity = self.db.cursor.fetchone()
            if activity is not None and len(activity) != 0:
                res = {"activity_id": activity[0], "activity_name": activity[1], "activity_desc": activity[2],
                       "activity_impact": activity[3]}
                q2 = "SELECT activity_date, activity_frequency FROM activity_log where activity_id = %s"
                self.db.cursor.execute(q2, (activity_id,))
                # activity_log_lst = self.db.cursor.fetchall()
                q3 = "SELECT CURDATE()"
                self.db.cursor.execute(q3)
                curdate = self.db.cursor.fetchone()[0]
                activity_log = self.get_activity_log_before_date(access_token, user_id, activity[0], curdate)
                # if activity_log_lst is not None and len(activity_log_lst) != 0:
                #     pass
                # else:
                #     for i in range(len(activity_log_lst)):
                #         name = "log_" + str(i + 1)
                #         activity_log[name] = {"activity_date": activity_log_lst[i][0],
                #                               "activity_frequency": activity_log_lst[i][1]}
                res['activity_log'] = activity_log
                return True, res
            else:
                return False, 0
        else:
            return False, -1

    def delete_activity(self, activity_id, access_token):
        q1 = "SELECT activity_name FROM activity where activity_id = %s"
        self.db.cursor.execute(q1, (activity_id,))
        activity = self.db.cursor.fetchone()
        if activity is None:
            return False, 0
        user_id = self._get_user_id_by_activity(activity_id)
        if self._correct_access_Token(access_token, user_id):
            q1 = "SELECT activity_name FROM activity where activity_id = %s"
            self.db.cursor.execute(q1, (activity_id,))
            activity = self.db.cursor.fetchone()
            if activity is not None and len(activity) != 0:
                # delete the activity logs
                q3 = "DELETE FROM activity_log WHERE activity_id = %s"
                self.db.cursor.execute(q3, (activity_id,))
                self.db.commit()
                # delete the related activity which belong to that goal
                q2 = "DELETE FROM activity WHERE activity_id = %s"
                self.db.cursor.execute(q2, (activity_id,))
                self.db.commit()
                # return true if successfully delete
                # print("Successfully delete activity!")

                return True, None
            else:
                # print("Can not find the activity!")
                return False, 0
        else:
            # print("Illegal access token!")
            return False, -1

    def get_activities(self, access_token, goal_id):
        # get the user id by goal id
        user_id = self._get_user_id_by_goal(goal_id)
        # if the access token is correct
        if self._correct_access_Token(access_token, user_id):
            Q1 = "SELECT activity_id FROM activity WHERE goal_id = %s"
            self.db.cursor.execute(Q1, (goal_id,))
            activity_lst = self.db.cursor.fetchall()
            # if the activity list of the goal is not None, return the goal list
            if activity_lst is not None and len(activity_lst) != 0:
                return True, [i[0] for i in activity_lst]
            else:
                # print("You have not insert any activities!")
                return True, []
        else:
            # print("Illegal access token!")
            return False, -1

    def get_activities_obj(self,access_token,goal_id):
        # this function is return the all activities object with the sepecified goal id
        user_id = self._get_user_id_by_goal(goal_id)
        if self._correct_access_Token(access_token, user_id):
            flg, activity_id_lst = self.get_activities(access_token, goal_id)

            if flg and len(activity_id_lst) != 0:
                # if there are some activities in the activities id list.
                activities_obj = []
                for activity_id in activity_id_lst:
                    exist, obj = self._internal_get_activity(activity_id, access_token)
                    activities_obj.append(obj)
                return True, activities_obj
            else:
                # there is no activity for this goal
                return False, 0
        else:
            return False, -1
    def edit_impact_score(self, activity_id, activity_impact, access_token):
        user_id = self._get_user_id_by_activity(activity_id)
        # if the access token is correct search for the activity
        goal_id = self._get_goal_id_by_activity(activity_id)
        if user_id is None:
            return False, 0

        if self._correct_access_Token(access_token, user_id):
            Q1 = "SELECT * FROM activity where activity_id = %s"
            self.db.cursor.execute(Q1, (activity_id,))
            activity = self.db.cursor.fetchone()
            # if the activity exists
            if activity is not None and len(activity) != 0:
                Q2 = "UPDATE activity SET activity_impact = %s where activity_id = %s"
                self.db.cursor.execute(Q2, (activity_impact, activity_id))
                self.db.commit()
                self.goal_progression_calculate(goal_id,access_token)
                return True, None
        else:
            # illegal access token
            return False, -1

    def get_impact_score(self, activity_id, access_token):
        user_id = self._get_user_id_by_activity(activity_id)
        # if the access token is correct search for the activity
        if self._correct_access_Token(access_token, user_id):
            Q1 = "SELECT * FROM activity where activity_id = %s"
            self.db.cursor.execute(Q1, (activity_id,))
            activity = self.db.cursor.fetchone()
            # if the activity exists
            if activity is not None and len(activity) != 0:
                Q1 = "SELECT activity_impact FROM activity where activity_id = %s"
                self.db.cursor.execute(Q1, (activity_id,))
                impact_score = self.db.cursor.fetchone()[0]
                return True, impact_score
        else:
            # illegal access token
            return False, -1

    def get_goal_progression(self, access_token, goal_id):
        # get the user id by goal id
        user_id = self._get_user_id_by_goal(goal_id)
        if user_id is None:
            # print("This goal does not exist!")
            return False, 0
        if self._correct_access_Token(access_token, user_id):

            # if the access token is correct
            q1 = "SELECT goal_current_state FROM goal where goal_id = %s"
            self.db.cursor.execute(q1, (goal_id,))
            return True, self.db.cursor.fetchone()[0]
        else:
            # print("access token is invalid!")
            return False, -1

    def _get_user_id(self, username):
        sql = "SELECT user_id FROM users where user_username= %s"
        self.db.cursor.execute(sql, (username,))
        res = self.db.cursor.fetchone()
        if res is not None and len(res) != 0:
            return res[0]
        else:
            return None

    def goal_progression_calculate(self, goal_id, access_token):
        # get the user id by goal id
        user_id = self._get_user_id_by_goal(goal_id)
        if user_id is None:
            return False, 0
        if self._correct_access_Token(access_token, user_id):
            # get the activity id activity impact and frequency with the specified id
            q1 = "SELECT activity_id, activity_impact FROM activity where goal_id = %s"
            self.db.cursor.execute(q1, (goal_id,))
            res = self.db.cursor.fetchall()
            if res is not None and len(res) != 0:
                # q2 = "SELECT goal_initial_state FROM goal where goal_id = %s"
                # self.db.cursor.execute(q2, (goal_id,))
                # initialise score variable
                total_score = 0
                TARGET_SCORE = 100
                # if the goal is existing and valid
                flg, goal = self._internal_get_goals(goal_id, access_token, user_id)
                if flg:
                    # if activities of the goal exist and

                    flg, activity_id_lst = self.get_activities(access_token, goal_id)
                    # if activity exists
                    if flg:
                        for activity in goal["goal_activities"]:
                            # calculate the impact score for each activity
                            flg, activity_log = activity['activity_log']
                            # print(activity)
                            for each_activity in activity_log:
                                # print(activity['activity_impact'])
                                total_score += activity['activity_impact'] * each_activity[
                                    "activity_frequency"]
                        # update the goal progression when successfullly created
                        current_progression = total_score / TARGET_SCORE * 100
                        q3 = "UPDATE goal SET goal_current_state = %s where goal_id = %s"
                        self.db.cursor.execute(q3, (current_progression, goal_id))
                        self.db.commit()
                        return True, current_progression
                    else:
                        # there is no activity for this goal
                        return False, 3
                else:
                    # goal does not exist
                    return False, 0
            else:
                # activity does not exist
                return False, 3
        else:
            # print("access token is invalid!")
            return False, -1

    def add_notes(self, goal_id, access_token, notes):
        user_id = self._get_user_id_by_goal(goal_id)
        if user_id is None:
            return False, 0
        if self._correct_access_Token(access_token, user_id):
            q1 = "SELECT notes FROM goal where goal_id = %s"
            self.db.cursor.execute(q1, (goal_id,))
            res = self.db.cursor.fetchone()
            # if we do not
            if res is not None and len(res) != 0:
                q2 = "UPDATE goal SET notes = %s"
                self.db.cursor.execute(q2, (notes,))
                self.db.commit()
                return True, None
        else:
            # print("access token is invalid!")
            return False, -1

    def delete_notes(self, goal_id, access_token):
        user_id = self._get_user_id_by_goal(goal_id)
        if user_id is None:
            return False, 0
        if self._correct_access_Token(access_token, user_id):
            q1 = "SELECT notes FROM goal where goal_id = %s"
            self.db.cursor.execute(q1, (goal_id,))
            res = self.db.cursor.fetchone()
            # if we do not
            if res is not None and len(res) != 0:
                q2 = "UPDATE goal SET notes = '' WHERE goal_id = %s"
                self.db.cursor.execute(q2, (goal_id,))
                self.db.commit()
                return True, None
        else:
            # print("access token is invalid!")
            return False, -1

    def get_notes(self, goal_id, access_token):
        user_id = self._get_user_id_by_goal(goal_id)
        if user_id is None:
            return False, 0
        if self._correct_access_Token(access_token, user_id):
            q1 = "SELECT notes FROM goal where goal_id = %s"
            self.db.cursor.execute(q1, (goal_id,))
            res = self.db.cursor.fetchone()
            if res is not None and len(res) != 0:
                return True, res[0]
            else:
                return True, ""
        else:
            return False, -1

    def edit_notes(self, goal_id, access_token, notes):
        user_id = self._get_user_id_by_goal(goal_id)
        if user_id is None:
            return False, 0
        if self._correct_access_Token(access_token, user_id):
            q1 = "SELECT notes FROM goal where goal_id = %s"
            self.db.cursor.execute(q1, (goal_id,))
            res = self.db.cursor.fetchone()
            q2 = "UPDATE goal SET notes = %s where goal_id = %s"
            self.db.cursor.execute(q2, (notes,goal_id))
            self.db.commit()
            return True, None
        else:
            return False, -1

    def edit_goal_name_and_notes(self,goal_id,access_token,notes,goal_name):
        user_id = self._get_user_id_by_goal(goal_id)
        if user_id is None:
            return False, 0
        if self._correct_access_Token(access_token, user_id):
            q1 = "SELECT notes FROM goal where goal_id = %s"
            self.db.cursor.execute(q1, (goal_id,))
            res = self.db.cursor.fetchone()
            if res is None or len(res) == 0:
                # Note: it's ok for res[0] to be None
                return False, 0
            else:
                q2 = "UPDATE goal SET notes = %s, goal_name = %s where goal_id = %s"
                self.db.cursor.execute(q2, (notes,goal_name,goal_id))
                self.db.commit()
                return True, None
        else:
            return False, -1
        
    def update_activity_frequency(self, access_token, activities_obj, user_id):
        # activity_obj[i] = (activity_id, activity_date, activity_frequency)
        if self._correct_access_Token(access_token, user_id):
            for activity_id, activity_date, activity_frequency in activities_obj:
                q1 = "SELECT * FROM activity where activity_id = %s"
                self.db.cursor.execute(q1, (activity_id,))
                id = self.db.cursor.fetchone()
                if id is None or len(id) == 0:
                    return False, 0
            for activity_id, activity_date, activity_frequency in activities_obj:

                # q1 = "SELECT frequency FROM activity where activity_id = %s"
                q2 = "INSERT INTO activity_log (activity_id, activity_date, activity_frequency) VALUES (%s, %s ,%s)"
                self.db.cursor.execute(q2, (activity_id, activity_date, activity_frequency))
                self.db.commit()
                # self.db.cursor(q1,(activity_id,))
                # res = self.db.cursor.fetchone()[0]
                # res += res + frequency
                # q2 = "UPDATE activity SET frequency = %s where activity_id = %s"
                # self.db.cursor(q2,(frequency,activity_id))
                # self.db.commit()
                # calculate each after update the frequency of the acitivity
                self.goal_progression_calculate(self._get_goal_id_by_activity(activity_id), access_token)
            #     print("update once")
            # print("update successfully")
            return True, None
        else:

            return False, -1

    def get_activity_log_before_date(self, access_token, user_id, activity_id, activity_date):
        if self._correct_access_Token(access_token, user_id):
            activity_logs = []
            # find all the activity dates and activity frequencies for that activity until that date
            q2 = "SELECT activity_date, activity_frequency FROM activity_log where activity_id = %s AND (activity_date < %s OR activity_date = %s)"
            self.db.cursor.execute(q2, (activity_id, activity_date, activity_date))
            res = self.db.cursor.fetchall()
            # for iterate all
            for i in range(len(res)):
                activity_logs.append({
                    "activity_id": activity_id,
                    "activity_date": res[i][0],
                    "activity_frequency": res[i][1],
                })
            return True, activity_logs
        else:
            return False, -1

    def get_all_activities_log(self, access_token, user_id, activity_date):
        if self._correct_access_Token(access_token, user_id):
            activity_logs = []
            # search the activity id with inner join goal and users and with the given user_id
            q1 = "SELECT activity_id FROM activity INNER JOIN goal ON activity.goal_id = goal.goal_id INNER JOIN users ON goal.user_id = users.user_id where users.user_id = %s"
            self.db.cursor.execute(q1, (user_id,))
            res = self.db.cursor.fetchall()
            # find each activity_id match with that date
            for i in res:
                activity_id = i[0]
                q2 = "SELECT activity_frequency FROM activity_log WHERE activity_date = %s and activity_id = %s"
                self.db.cursor.execute(q2,(activity_date,activity_id))
                logs_info = self.db.cursor.fetchone()
                if logs_info is not None and len(logs_info) != 0:
                    activity_logs.append({
                        "activity_id": activity_id,
                        "activity_date": activity_date,
                        "activity_frequency": logs_info[0],
                    })
            return True, activity_logs
        else:
            return False, -1

    def edit_activities_log(self, access_token, user_id, activity_obj):
        # activity_obj[i] = activity_log
        # activity_log = (activity_id, activity_date, activity_frequency)
        if self._correct_access_Token(access_token, user_id):
            for activity_log in activity_obj:
                # Check if the activity log exists
                q1 = "SELECT * from activity_log WHERE activity_id = %s AND activity_date = %s"
                self.db.cursor.execute(q1, (activity_log[0], activity_log[1]))
                res = self.db.cursor.fetchone()
                log_exists = False
                if res is not None:
                    if len(res) != 0:
                        log_exists = True
                if log_exists:
                    # update the activity_log if the activity log exists
                    q2 = "UPDATE activity_log SET activity_frequency = %s WHERE activity_id = %s AND activity_date = %s"
                    self.db.cursor.execute(q2, (activity_log[2], activity_log[0], activity_log[1]))
                    self.db.commit()
                else:
                    # Add a new activity log if the activity log does not exist
                    q2 = "INSERT INTO activity_log (activity_id, activity_date, activity_frequency) VALUES (%s, %s ,%s)"
                    self.db.cursor.execute(q2, (activity_log[0], activity_log[1], activity_log[2]))
                    self.db.commit()
            
                self.goal_progression_calculate(self._get_goal_id_by_activity(activity_log[0]), access_token)
            return True, None
        else:
            return False, -1

    def delete_activities_log(self, access_token, user_id, activity_id, activity_date):
        # activity_log = (activity_id, activity_date, activity_frequency)
        if self._correct_access_Token(access_token, user_id):
            q1 = "SELECT * from activity_log WHERE activity_id = %s AND activity_date = %s"
            self.db.cursor.execute(q1, (activity_id, activity_date))
            res = self.db.cursor.fetchone()
            if res is not None:
                if len(res) != 0:
                    # delete the activity_log if it doest exists
                    q2 = "DELETE FROM activity_log WHERE activity_id = %s AND activity_date = %s"
                    self.db.cursor.execute(q2, (activity_id, activity_date))
                    self.db.commit()
                    self.goal_progression_calculate(self._get_goal_id_by_activity(activity_id), access_token)
                    return True, None
            else:
                return False, 0
        else:
            return False, -1

    def get_all_activity_logs_by_user_id(self, access_token, user_id):
        if self._correct_access_Token(access_token, user_id):
            # if the access token is correct set up the activity logs
            activity_logs_obj = []
            q2 = "SELECT goal_id FROM goal WHERE user_id = %s"
            self.db.cursor.execute(q2, (user_id,))
            goal_lst = self.db.cursor.fetchall()
            for goal_obj in goal_lst:
                # print(goal_obj)
                # store the activity logs by goal id in the dict
                goal_id = goal_obj[0]
                flg, activity_logs = self._get_all_activities_logs_by_goal(goal_id)
                if flg:

                    activity_logs_obj.append({"goal_id": goal_id,"logs": activity_logs})
            return True, activity_logs_obj

        else:
            return False, -1

    def _get_all_activities_logs_by_goal(self,goal_id):
        q1 = "SELECT activity_log.activity_id, activity_log.activity_date, activity_log.activity_frequency FROM activity_log INNER JOIN activity On activity_log.activity_id = activity.activity_id WHERE activity.goal_id = %s"
        self.db.cursor.execute(q1,(goal_id,))
        activity_logs = self.db.cursor.fetchall()
        res = []
        for activity_log in activity_logs:
            res.append({"activity_id":activity_log[0],"activity_date":activity_log[1],"activity_frequency":activity_log[2]})
        return True, res



    def _get_goal_id_by_activity(self, activity_id):
        q1 = "SELECT goal_id FROM activity where activity_id = %s"
        self.db.cursor.execute(q1, (activity_id,))
        res = self.db.cursor.fetchone()
        try:
            return res[0]
        except TypeError:
            return None

    def _myHash(self, text: str):
        """
        Simple hash function reference from:
        https://stackoverflow.com/questions/27522626/hash-function-in-python-3-3-returns-different-results-between-sessions
        """
        hash = 0
        for ch in text:
            hash = (hash * 281 ^ ord(ch) * 997) & 0xFFFFFFFF
        return hash

    def _generate_access_token(self):
        """
        return na access token generated by only ascii letters and digits
        Referenced from: https://docs.python.org/3/library/secrets.html
        """
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for i in range(32))
        return token



def generate_database():
    db = database()
    # delete all the foreign keys
    # disable the foreign key check
    db.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    # db.cursor.execute("ALTER TABLE activity DROP constraint activity_ibfk_1")
    # db.cursor.execute("ALTER TABLE password DROP constraint password_ibfk_1")
    # db.cursor.execute("ALTER TABLE goal DROP constraint goal_ibfk_1")
    # db.cursor.execute("ALTER TABLE activity_log DROP constraint activity_log_ibfk_1")
    # drop the table
    db.cursor.execute("DROP TABLE IF EXISTS users")
    db.cursor.execute("DROP TABLE IF EXISTS goal")
    db.cursor.execute("DROP TABLE IF EXISTS activity")
    db.cursor.execute("DROP TABLE IF EXISTS password")
    db.cursor.execute("DROP TABLE IF EXISTS activity_log")
    db.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    # create the table
    db.cursor.execute(
        "CREATE TABLE users (user_id INT NOT NULL AUTO_INCREMENT,user_username varchar(100) NOT NULL, user_email varchar(32),access_token varchar(32) NOT NULL, PRIMARY KEY (user_id), UNIQUE (user_username))")
    db.cursor.execute(
        "CREATE TABLE goal (goal_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,goal_name varchar(52) NOT NULL, goal_desc varchar(500) NOT NULL ,goal_initial_state numeric(4,1) NOT NULL DEFAULT 0,goal_current_state numeric(4,1) NOT NULL DEFAULT 0, goal_date DATE, user_id INT NOT NULL, FOREIGN KEY (user_id) REFERENCES users(user_id), notes varchar(500))")
    db.cursor.execute(
        "CREATE TABLE activity (activity_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, activity_name varchar(52) NOT NULL, activity_desc varchar(500) NOT NULL , activity_impact NUMERIC(4,1) NOT NULL ,goal_id INT NOT NULL , FOREIGN KEY(goal_id) REFERENCES goal(goal_id))")
    db.cursor.execute(
        "CREATE TABLE password (password_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, pwd NUMERIC(32) NOT NULL, user_id INT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(user_id))")

    db.cursor.execute(
        "CREATE TABLE activity_log (activity_id INT NOT NULL, activity_date DATE, activity_frequency INT NOT NULL DEFAULT 0, PRIMARY KEY (activity_id, activity_date), FOREIGN KEY (activity_id) REFERENCES  activity(activity_id))"
    )
    # show results




if __name__ == "__main__":
    api = api()
