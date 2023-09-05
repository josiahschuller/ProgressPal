from sqlite3 import Date
from flask import Flask, request, make_response, jsonify, json # pip install Flask
from flask_cors import CORS # pip install Flask-Cors
from backend.Databases.AC_schema import api
import re

app = Flask(__name__)
CORS(app)

# LOGIN query that will take username & password in a query
@app.route('/log-in', methods=['POST'])
def log_in():
    username = request.args.get('username') 
    password = request.args.get('password')
    if username is None or username == "" or password is None or password == "":
        return make_response({"error": "No username or password given"}, 400)
    response = make_response({"error": "There is no user in database for the given username"}, 400)
    flag, access_token, user_id = api.login(username, password) # get from HY
    if (not flag):
        response = make_response({"error": "Incorrect username or password"}, 401)
    elif (access_token is not None):
        response = make_response(jsonify({"user_id": user_id, "access_token": access_token}), 200)
    return response 

# CREATE NEW ACCOUNT - the user provides at the same page as login the username & password
# if the account doesn't already exist - a new account is being created together with an access token
@app.route('/sign-up', methods=['POST'])
def signup():
    username = request.args.get('username')
    password = request.args.get('password')
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    # pattern = r"^[a-zA-Z0-9_.+-]+@(gmail\.com|student\.monash\.edu|monash\.edu)$" 
    if username is None or username == "" or password is None or password == "":
        return make_response({"error": "No username or password given"}, 400)
    if re.match(pattern, username) is None:
        return make_response({"error": "The given username is not of supported format. Please enter a valid email address,"})
    response = make_response({"error": "The user already exists!"}, 400)
    flag, access_token, user_id = api.sign_up(username, password) 
    if (flag):
        response = make_response(jsonify({"user_id": user_id, "access_token": access_token}), 200)
    return response 

# GET THE GOAL PROGRESSION - requires an access token
# @app.route('/get-goal-progression', methods=['GET'])
# def get_goal_progression():
#     data = request.json
#     auth_header = request.headers.get('Authorization')
#     access_token = None
#     if auth_header:
#         access_token = auth_header.split(" ")[1]
#     goal_id = data.get('goal_id')
#     response = make_response("There was an issue while trying to process your request. Please try again!", 400)
#     goal_progression = get_goal_progression(access_token, goal_id) 
#     if (goal_progression[0] == True):
#         goal_progression_val = goal_progression[1]
#         response = make_response("Goal progression: " + goal_progression_val, 200)
#     elif (goal_progression[0] == False and goal_progression[1] == -1):
#         response = make_response("Invalid access token!", 401)
#     return response


# ADDING A NEW GOAL
@app.route('/add-new-goal', methods=['POST'])
def add_new_goal():
    # obtain relevant data from request
    data = json.loads(request.get_data())
    goal_name = data.get('goal_name')
    goal_desc = data.get('goal_desc')
    goal_notes = data.get('goal_notes')
    activities = data.get('goal_activities')

    # Sanitation checks
    if goal_name is None or goal_name == "":
        return make_response({"error": "Goal name required"})
    for activity in activities:
        if activity["activity_name"] is None or activity["activity_name"] == "":
            return make_response({"error": "Activity name required"})
        if len(activity["activity_name"]) > 52:
            print("Activity name too long! Please make a name under 52 characters")
            return make_response({"error": "Activity name too long! Please make a name under 52 characters (spaces included)"})
        if activity["activity_score"] is None or activity["activity_score"] == "" or activity["activity_score"] == 0:
            return make_response({"error": "Invalid activity score"})
    
    user_id = request.headers.get('X-User-Id') # custom headers usually start with 'x'
    auth_header = request.headers.get('Authorization')
    access_token = None
    if auth_header:
        access_token = auth_header.split(" ")[1]
    response = make_response({"error": "Invalid access token!"}, 401) # default response
    
    # Add the goal
    res = api.add_goal(goal_name, goal_desc, access_token, user_id, goal_notes)
    if res[0] is not False:
        goal_id = res[1]

        # Add the activities
        for activity in activities:
            activity_res = api.add_activity(activity["activity_score"], activity["activity_name"], activity["activity_desc"], access_token, goal_id)
            if activity_res[0] is False:
                response = make_response({"error": "Error adding activity. Please try again!"}, 400)
                return response
        
    if res[0] is False and res[1] == -1:
        response = make_response({"error": "Error adding goal. Please try again!"}, 400)
    elif res[0] is False and res[1] == 1:
        response = make_response({"error": "Goal with same name already exists! Please try again!"}, 400)
        print("Goal with same name already exists!")
    elif res[0] is True:
        response = make_response({"success": "Goal successfully created!"}, 200)
    return response

# DELETE A GOAL - the id of a goal will be provided in the body by the user
@app.route('/delete-goal', methods=['DELETE'])
def delete_goal():
    data = json.loads(request.get_data())
    goal_id = data.get('goal_id')

    auth_header = request.headers.get('Authorization')
    access_token = None
    if auth_header:
        access_token = auth_header.split(" ")[1]

    response = make_response({"error": "Invalid access token!"}, 401)

    res = api.delete_goal(goal_id, access_token)
    if res[0] is True:
        response = make_response({"success": "Goal deleted successfully!"}, 200)
    elif res[0] is False and res[1] == 0:
        response = make_response({"error": "Cannot find specified goal!"}, 400)
    return response

# EDITING A GOAL
@app.route('/edit-goal', methods=['PUT'])
def edit_goal():
    data = json.loads(request.get_data())
    # extract goal details
    goal_id = data.get('goal_id')
    goal_name = data.get('goal_name')
    goal_activities = data.get('goal_activities')
    goal_notes = data.get('goal_notes')
    user_id = api._get_user_id_by_goal(goal_id)
    # access token
    auth_header = request.headers.get('Authorization')
    access_token = None
    if auth_header:
        access_token = auth_header.split(" ")[1]
    # response = make_response({"error": "Invalid access token!"}, 401)

    # Sanitation checks
    if goal_name is None or goal_name == "":
        return make_response({"error": "Goal name required"}, 400)
    # check that there is no goal with a same name already
    flag, res = api.get_goals(access_token, user_id)
    if flag and len(res) > 0:
        for value in res.values():
            if goal_name == value['goal_name'] and goal_id != value['goal_id']:
                return make_response({"error": "There is already a goal with a same name!"}, 400)
            
    # get old version of the goal - before we edit it
    old_version_of_goal = None
    for value in res.values():
        if value['goal_id'] == goal_id:
            old_version_of_goal = value
            break
    
    # don't allow users to add activities with same names
    old_activities = old_version_of_goal['goal_activities']
    need_to_be_added_activities = []
    for goal_activity in goal_activities:
        if goal_activity['activity_id'] is None:
            need_to_be_added_activities.append(goal_activity)
        else:
            for old_activity in old_activities:
                if old_activity['activity_id'] != goal_activity['activity_id'] and old_activity['activity_name'] == goal_activity['activity_name']:
                    return make_response({"error": "The activity you wanted to edit contains the same name as an existing one!"}, 400)
            if len(goal_activity['activity_name']) == 0:
                return "Activity name is required and cannot be empty!"
            internal_flag, internal_indicator = api.edit_activity(goal_activity['activity_id'], goal_activity['activity_name'], "", goal_activity['activity_score'], goal_id, access_token)
            if not internal_flag and internal_indicator == -1:
                return make_response({"error": "Illegal access token!"}, 401)

    # add new activities in database - that were added through edit
    for new_activity in need_to_be_added_activities:
        if len(new_activity['activity_name']) == 0:
            return make_response({"error": "Activity name is required and cannot be empty!"}, 400)
        internal_flag, internal_indicator = api.add_activity(new_activity['activity_score'],new_activity['activity_name'], "", access_token, goal_id)
        if not internal_flag and internal_indicator == -1:
            return make_response({"error": "Illegal access token2!"}, 401)

    successful_goal_edit_flag, indicator = api.edit_goal_name_and_notes(goal_id, access_token, goal_notes, goal_name)
    if not successful_goal_edit_flag:
        return make_response({"error": "Illegal access token3!"}, 401)

    return make_response({"success": "Successfully edited goal!"}, 200)

# ADDING AN ACTIVITY
@app.route('/add-new-activity', methods=['POST'])
def add_new_activity():
    # obtain relevant data from request
    data = json.loads(request.get_data())
    activity_score = data.get('activity_score')
    activity_name = data.get('activity_name')
    activity_desc = data.get('activity_desc')
    goal_id = data.get('goal_id')
    user_id = request.headers.get('X-User-Id') # custom headers usually start with 'x'
    auth_header = request.headers.get('Authorization')
    access_token = None
    if auth_header:
        access_token = auth_header.split(" ")[1]
    # generate a response
    response = make_response({"error": "Invalid access token!"}, 401)
    # obtain the result of the action
    res = api.add_activity(activity_score, activity_name, activity_desc,access_token, goal_id)
    if res[0] is False and res[1] == 1:
        response = make_response({"success": "There is already an activity with this name. Please try again!"}, 400)
    elif res[0] is True:
        response = make_response({"success": "Activity successfully created!"}, 200)
    return response

# DELETE AN ACTIVITY - the id of an activity will be provided in the body by the user
@app.route('/delete-activity', methods=['DELETE'])
def delete_activity():
    data = json.loads(request.get_data())
    activity_id = data.get('activity_id')
    auth_header = request.headers.get('Authorization')
    access_token = None
    if auth_header:
        access_token = auth_header.split(" ")[1]
    response = make_response({"error": "Invalid access token!"}, 401)
    res = api.delete_activity(activity_id, access_token)
    if res[0] is True:
        response = make_response({"success": "Activity deleted successfully!"}, 200)
    elif res[0] is False and res[1] == 0:
        response = make_response({"error": "Cannot find specified activity!"}, 400)
    return response 

# EDITING AN ACTIVITY
# @app.route('/edit-activity', methods=['PUT'])
# def edit_activity():
#     data = request.json
#     auth_header = request.headers.get('Authorization')
#     access_token = None
#     if auth_header:
#         access_token = auth_header.split(" ")[1]
#     response = make_response("There was an issue while trying to edit your activity. Please try again!", 400)
#     activity_obj = data.get('activity_obj')
#     # not really sure what HY function is returning TODO
#     activity_edited = edit_activity(activity_obj, access_token)
#     if activity_edited:
#         response = make_response("Activity edited successfully!", 200)
#     return response
    # give me goal_id and activity_id ????

# GET GOALS FOR A SPECIFIC USER
@app.route('/get-goals', methods=['GET'])
def get_goals():
    user_id = request.headers.get('X-User-Id') # custom headers usually start with 'x'
    auth_header = request.headers.get('Authorization')
    access_token = None
    if auth_header:
        access_token = auth_header.split(" ")[1]
    response = make_response({"error": "Invalid access token!"}, 401)
    
    flag, res = api.get_goals(access_token, user_id)
    
    if flag:
        goals_json = json.dumps(res)
        response = make_response({"goals": goals_json}, 200) # i will assume this works - internet not giving me anything
        response.headers['Content-Type'] = 'application/json' # set the content type as JSON
    return response

# LOG THE ACTIVITIES YOU HAVE DONE ON THAT DAY
@app.route('/log-activities', methods=['POST'])
def log_activities():
    user_id = request.headers.get('X-User-Id') # custom headers usually start with 'x'
    auth_header = request.headers.get('Authorization')
    access_token = None
    if auth_header:
        access_token = auth_header.split(" ")[1]
    data = json.loads(request.get_data())
    activities_obj = data.get('activities_obj')
    response = make_response({"error": "Invalid access token!"}, 401)
    flag, indicator = api.update_activity_frequency(access_token, activities_obj, user_id)
    if flag:
        response = make_response({"success": "Activities updated successfully!"}, 200)
    return response

# DELETE THE LOGGED ACTIVITY
@app.route('/delete-logged-activity', methods=['DELETE'])
def delete_logged_activity():
    user_id = request.headers.get('X-User-Id') # custom headers usually start with 'x'
    auth_header = request.headers.get('Authorization')
    access_token = None
    if auth_header:
        access_token = auth_header.split(" ")[1]
    data = json.loads(request.get_data())
    activity_id = data.get('activity_id')
    activity_date = data.get('activity_date')
    response = make_response({"error": "Invalid access token!"}, 401)
    flag, indicator = api.delete_activities_log(access_token, user_id, activity_id, activity_date)
    if flag is True:
        response = make_response({"success": "Logged activity deleted successfully!"}, 200)
    elif flag is False and indicator == 0:
        response = make_response({"error": "Cannot find specified logged activity!"}, 400)
    return response


@app.route('/get-logged-activities', methods=['GET'])
def get_logged_activities():
    user_id = request.headers.get('X-User-Id') # custom headers usually start with 'x'
    auth_header = request.headers.get('Authorization')
    
    activity_date = request.args.get('activity-date') 

    access_token = None
    if auth_header:
        access_token = auth_header.split(" ")[1]

    response = make_response({"error": "Invalid access token!"}, 401)
    flag, res = api.get_all_activities_log(access_token, user_id, activity_date)
    if flag:
        response = make_response({"logs": res}, 200)
    return response

@app.route('/edit-logged-activities', methods=['POST'])
def edit_logged_activities():
    data = json.loads(request.get_data())
    user_id = request.headers.get('X-User-Id') # custom headers usually start with 'x'
    auth_header = request.headers.get('Authorization')
    access_token = None
    if auth_header:
        access_token = auth_header.split(" ")[1]
    activities_obj = data.get('activities_obj')
    response = make_response({"error": "Invalid access token!"}, 401)
    flag, indicator = api.edit_activities_log(access_token, user_id, activities_obj) 
    if flag:
        response = make_response({"success": "Logged activities updated successfuly!"}, 200)
    if not flag and indicator == 0:
        response = make_response({"error": "There was an error while trying to edit your logged activities! Please try again!"}, 401)
    return response

@app.route('/get-logged-activities-for-user', methods=['GET'])
def get_logged_activities_for_user():
    user_id = request.headers.get('X-User-Id') # custom headers usually start with 'x'
    auth_header = request.headers.get('Authorization')
    access_token = None
    if auth_header:
        access_token = auth_header.split(" ")[1]

    response = make_response({"error": "Invalid access token!"}, 401)
    flag, res = api.get_all_activity_logs_by_user_id(access_token, user_id)
    if flag:
        response = make_response({"success": res}, 200)
    return response

def test_get_logged_activities_for_user():
    user_id = 1 # custom headers usually start with 'x'
    access_token = "KVWGKdkudHbcqXKh63aBChfaHywRyb5R"
    response = "Invalid access token!"
    flag, res = api.get_all_activitiy_logs(access_token, user_id) 
    if flag and len(res) == 0:
        response = "You haven't done any activities! Please log some activities to see your progression!"
    if flag and len(res) > 0:
        response = res
    return response


# GET ACTIVITIES FOR A SPECIFIC GOAL
# @app.route('/get-activities', methods=['GET'])
# def get_activities():
#     # how do I obtain the goal_id?
#     data = request.json
#     auth_header = request.headers.get('Authorization')
#     access_token = None
#     if auth_header:
#         access_token = auth_header.split(" ")[1]   
#     activities = get_activities(access_token, goal_id)
    # confused what HY is returning and what am i supposed to show? TODO


"""
{{1, 5}, {2, 3}}

for loop
{
    I get an activity_id and a frequency - obj[i][i], obj[i][1] -> add the frequency to an existing one for that id
    I pass it to you
    You add that frequency to the existing one in the table (search the activity based on the id)
    after that's done you call calculate_goal_progression() again
}
"""

"""
for editing a goal - they give a goal with activities
i call HY function to get goals and get a specific goal by id and then i delete the activities that are associated with that goal and then
just add the new ones 
"""

def test_signup():
    username = "Jovana"
    password = "new"
    # response = make_response("The user already exists!", 400)
    response = "The user already exists!"
    flag, access_token, user_id = api.sign_up(username, password) 
    if (flag):
        response = "Signed up successfully! Access token: " + access_token
        # response_access_token = {'access token': access_token}
        # response = make_response("Signed up successfully! Access token: ", jsonify(response_access_token), 200)
    return response

def test_log_in():
    username = "Jovana"
    password = "new"
    # response = make_response("There is no user in database for the given username", 400)
    response = ("There is no user in database for the given username")
    flag, access_token, user_id = api.login(username, password) # get from HY
    if (not flag) and (access_token == 2):
        # response = make_response("Invalid access!", 401)
        response = "Invalid access - password incorrect"
    elif (access_token!=2 and access_token!=0):
        # response_access_token = {'access token': access_token}
        # response = make_response("Logged in successfully! User ID: ", user_id, " & Access token: ", jsonify(response_access_token), 200)
        response = "logged in successfuly - user id is:" + str(user_id) + " and access token is:" + str(access_token)
    return response 

def test_adding_new_goal():
    # data = request.json
    # goal_name = data.get('goal_name')
    goal_name = "Sleep more"
    # goal_desc = data.get('goal_desc')
    goal_desc = "I am too tired"
    # user_id = request.headers.get('X-User-Id') # custom headers usually start with 'x'
    # auth_header = request.headers.get('Authorization')
    # access_token = None
    # if auth_header:
    #     access_token = auth_header.split(" ")[1]
    user_id = 1
    access_token = "xY5pAyXtrWghe8SJl5BLuVVSE6aqhugs"
    # generate a response
    response = "Invalid access token!"
    # obtain the result of the action
    res = api.add_goal(goal_name, goal_desc, access_token, user_id)
    if res[0] is False and res[1] == 1:
        response = "There is already a goal with this name. Please try again!"
    elif res[0] is True:
        response = "Goal successfully created!"
    return response

def test_adding_new_activity():
    # obtain relevant data from request
    activity_score = 3
    activity_name = "Chilling"
    activity_desc = "I chill every day"
    goal_id = 3
    user_id = 1 # custom headers usually start with 'x'
    access_token = "xY5pAyXtrWghe8SJl5BLuVVSE6aqhugs"
    # generate a response
    response = "Invalid access token!"
    # obtain the result of the action
    res = api.add_activity(activity_score, activity_name, activity_desc,access_token, goal_id)
    if res[0] is False and res[1] == 1:
        "There is already an activity with this name. Please try again!"
    elif res[0] is True:
        response = "Activity successfully created!"
    return response

def test_get_goals():
    user_id = 1
    access_token = "KVWGKdkudHbcqXKh63aBChfaHywRyb5R"
    response = "Invalid access token!"
    flag, res = api.get_goals(access_token, user_id)
    lst_res = list(res) # int object is not iterable
    # print(res)
    # for i in range(len(res)):
    #     print(res[i])
    # if flag:
    #     goals = set()
    #     for i in range(len(res)):
    #         goals.add(res[i])
    #     response = (goals) # i will assume this works - internet not giving me anything
    # elif (not flag) and (res == 0):
    #     response = "You don't have any goals yet!"
    return res

def test_delete_goal():
    goal_id = 3
    access_token = "NVL59TaSjkoblx6uWSxP2SyNkGUxjkPT"
    response = "Invalid access token!"
    res = api.delete_goal(goal_id, access_token)
    if res[0] is True:
        response = "Goal deleted successfully!"
    elif res[0] is False and res[1] == 0:
        response = "Cannot find specified goal!"
    return response

def test_delete_activity():
    activity_id = 1
    access_token = "UXhhakcatgWmWnfqEc60KMzwH38WQKaV"
    response = "Invalid access token!"
    res = api.delete_goal(activity_id, access_token)
    if res[0] is True:
        response = "Activity deleted successfully!"
    elif res[0] is False and res[1] == 0:
        response = "Cannot find specified Activity!"
    return response

def test_logging_activities():
    user_id = 1
    # activities_obj = {(3, Date(2023, 4, 10), 5), (4, Date(2023, 2, 2), 4)}
    activities_obj = {(3, Date(2023, 2, 10), 3)}
    access_token = "xY5pAyXtrWghe8SJl5BLuVVSE6aqhugs"
    response = "Invalid access token!"
    flag, indicator = api.update_activity_frequency(access_token, activities_obj, user_id)
    if flag:
        response = "Activities updated successfuly!"
    return response


def test_edit_logged_activities():
    user_id = 1 # custom headers usually start with 'x'
    access_token = "xY5pAyXtrWghe8SJl5BLuVVSE6aqhugs"
    activity_obj = {(3, Date(2023, 2, 10), 1)}
    response = "Invalid access token!"
    flag, indicator = api.edit_activities_log(access_token, user_id, activity_obj) 
    if flag:
        response = "Logged activities updated successfuly!"
    if not flag and indicator == 0:
        response = "There was an error while trying to edit your logged activities! Please try again!"
    return response

def test_delete_logged_activity():
    user_id = 1 # custom headers usually start with 'x'
    access_token = "xY5pAyXtrWghe8SJl5BLuVVSE6aqhugs"
    activity_id = 3
    activity_date = Date(2023, 2, 10)
    response = "Invalid access token!"
    flag, indicator = api.delete_activities_log(access_token, user_id, activity_id, activity_date) 
    if flag:
        response = "Logged activuity deleted successfuly!"
    if not flag and indicator == 0:
        response = "There was an error while trying to delete your logged activities! Please try again!"
    return response

def again_test_edit():
    goal_obj = {'goal_id': 2, 
                'goal_name': 'Trying empty activity edit goal',
                'goal_activities': [{'activity_id': 3, 'activity_name': '', 'activity_score': 1},
                                    {'activity_id': None, 'activity_name':'try2_new_activity', 'activity_score':2}],
                'goal_notes': "some new cool awesome notes"
                }
    goal_id = goal_obj['goal_id']
    goal_name = goal_obj['goal_name']
    goal_activities = goal_obj['goal_activities']
    goal_notes = goal_obj['goal_notes']
    user_id = api._get_user_id_by_goal(goal_id)
    # access token
    access_token = "KVWGKdkudHbcqXKh63aBChfaHywRyb5R"
    # response = make_response({"error": "Invalid access token!"}, 401)

    # Sanitation checks
    if goal_name is None or goal_name == "":
        return "Goal name required"
    # check that there is no goal with a same name already
    flag, res = api.get_goals(access_token, user_id)
    if flag and len(res) > 0:
        for value in res.values():
            if goal_name == value['goal_name']:
                return "There is already a goal with a same name!"
           
    # get old version of the goal - before we edit it
    old_version_of_goal = None
    for value in res.values():
        if value['goal_id'] == goal_id:
            old_version_of_goal = value

    successful_activity_edit = False
    successful_activity_addition = False
    # don't allow users to add activities with same names
    old_activities = old_version_of_goal['goal_activities']
    need_to_be_added_activities = []
    for goal_activity in goal_activities:
        if goal_activity['activity_id'] is None:
            need_to_be_added_activities.append(goal_activity)
        else:
            for old_activity in old_activities:
                if old_activity['activity_name'] == goal_activity['activity_name']:
                    return "The activity you wanted to edit contains the same name as an existing one!"
                if len(goal_activity['activity_name'] == 0):
                    return "Activity name is required and cannot be empty!"
            internal_flag, internal_indicator = api.edit_activity(goal_activity['activity_id'], goal_activity['activity_name'], "", goal_activity['activity_score'], goal_id, access_token)
            if not internal_flag and internal_indicator == -1:
                return "Illegal access token!"
            if internal_flag:
                successful_activity_edit = True

    # add new activities in database - that were added through edit
    for new_activity in need_to_be_added_activities:
        if len(new_activity['activity_name'] == 0):
            return "Activity name is required and cannot be empty!"
        internal_flag, internal_indicator = api.add_activity(new_activity['activity_score'],new_activity['activity_name'], "", access_token, goal_id)
        if not internal_flag:
            return "Illegal access token!"
        if internal_flag:
            successful_activity_addition = True

    successful_goal_edit = False
    successful_goal_edit_flag, indicator = api.edit_goal_name_and_notes(goal_id, access_token, goal_notes, goal_name)
    if not successful_goal_edit_flag:
        return "Illegal access token!"
    if successful_goal_edit_flag:
        successful_goal_edit = True

    if successful_activity_addition and successful_activity_edit and successful_goal_edit:
        return "Successfully edited goal!"
    
api = api()

if __name__ == "__main__":
    app.run()