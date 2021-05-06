from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import request, Blueprint, make_response, jsonify
import requests
import os

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

# waiting to refactor until complete

####################################################################
# helper functions to create often used data structure in responses #
####################################################################
def task_data_structure(task):
    if task.completed_at:
        task.is_complete = True
    else:
        task.is_complete = False

    task_data_structure = {
                "task":{
                "id":task.task_id,
                "title":task.title,
                "description":task.description,
                "is_complete":task.is_complete
            }}

    return task_data_structure

def goal_data_structure(goal):
    goal_data_structure = {
                "goal":{
                "id":goal.goal_id,
                "title":goal.title
            }}

    return goal_data_structure



####################################################################
#                              GOALS ROUTES                        #
####################################################################

@goals_bp.route("", methods=["GET", "POST"])
def handle_goals():
    if request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query == "asc": 
            goals = Goal.query.order_by(goal.title)
        elif sort_query == "desc":
            goals = Goal.query.order_by(goal.title.desc())
        else:
            goals = Goal.query.all()
        goals_response = []
        for goal in goals:
            goal_formatted = {
                "id": goal.goal_id,
                "title": goal.title
            }
            goals_response.append(goal_formatted)

        return make_response(jsonify(goals_response), 200)
    elif request.method == "POST":
        request_body = request.get_json()
        if 'title' in request_body: 
            new_goal = Goal(title=request_body["title"])
            db.session.add(new_goal)
            db.session.commit()

            return make_response(goal_data_structure(new_goal), 201)
        else:
            return make_response(jsonify({"details":"Invalid data"}), 400)

@goals_bp.route("/<goal_id>", methods=["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)
    if request.method == "GET":
        return make_response(jsonify(goal_data_structure(goal)), 200)


####################################################################
#                              TASK ROUTES                        #
####################################################################

@tasks_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    if request.method == "GET":
        sort_query = request.args.get("sort")
        if sort_query == "asc": 
            tasks = Task.query.order_by(Task.title)
        elif sort_query == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        else:
            tasks = Task.query.all()
        tasks_response = []
        for task in tasks:
            task = task_data_structure(task)['task']
            tasks_response.append(task)

        return make_response(jsonify(tasks_response), 200)

    elif request.method == "POST":
        request_body = request.get_json()

        if 'title' in request_body and 'description' in request_body and 'completed_at' in request_body: 
            new_task = Task(title=request_body["title"],
                        description=request_body["description"],
                        completed_at=request_body['completed_at'])

            db.session.add(new_task)
            db.session.commit()
            return make_response(jsonify(task_data_structure(new_task)), 201)
        else:
            return make_response(jsonify({"details":"Invalid data"}), 400)


@tasks_bp.route("/<task_id>", methods=["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("", 404)

    if request.method == "GET":
        return make_response(task_data_structure(task), 200)
    elif request.method == "PUT":
        task_data = request.get_json()

        task.title = task_data["title"]
        task.description = task_data["description"]
        task.completed_at = task_data['completed_at']

        db.session.commit()
        task = Task.query.get(task_id)
        return make_response(jsonify(task_data_structure(task)), 200)

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit() 
        task_response = {"details": f'Task {task.task_id} "{task.title}" successfully deleted'}
        return make_response(jsonify(task_response), 200)


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_complete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("No such path exists", 404)
    
    task.update_completed() # function in Task Module to Update Time
    db.session.commit() 

    url = f"https://slack.com/api/chat.postMessage?channel=general&text={task.title}"
    auth_token = os.environ.get("API_KEY")

    headers = {
    'Authorization': auth_token
    }

    response = requests.request("POST", url, headers=headers)

    print(response.text)

    return make_response(jsonify(task_data_structure(task)), 200)


@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_incomplete(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return make_response("No such path exists", 404)

    task.completed_at = None
    db.session.commit() 

    return make_response(jsonify(task_data_structure(task)), 200)