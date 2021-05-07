from flask import current_app
from app import db

class Goal(db.Model):
    __tablename__ = 'goal'
    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    tasks = db.relationship("Task", lazy=True, backref="goal")
    
    def goal_data_structure(self):
        goal_data_structure = {
                    "goal":{
                    "id":self.goal_id,
                    "title":self.title
                }}

        return goal_data_structure