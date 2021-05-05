from app import db
from app.models.task import Task
from flask import request, Blueprint, make_response, jsonify

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
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
        print(request_body['title'])
        if request_body['title']:
            print(request_body['title'])
        if request_body['title'] and request_body['description'] and (request_body['completed_at'] or request_body['completed_at']==None):
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
