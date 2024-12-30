from database.mongoDB import task_collection
from schemas.taskSchema import TaskSchema
from models.taskModels import taskModel

def get_all_tasks():
    return task_collection.find()


def get_task_by_date(date: str):
    return task_collection.find_one({"date": date})

def get_task_by_time(time: str):
    return task_collection.find_one({"time": time})

def get_task_by_date_time(date: str , time: str):
    return task_collection.find_one({"date": date , "time": time})

def create_task(task: TaskSchema):
    task_dict = task.model_dump()
    task_collection.insert_one(task_dict)
    return task_dict
    
def update_task(task: TaskSchema):
    task_exists = task_collection.find_one({"date":task.date , "time":task.time})

    if task_exists:
        task_collection.update_one({"date":task.date , "time":task.time} , {"$set": task.model_dump()})
        return task.model_dump()
    
    return {"error": "Task not found"}

def delete_task(date: str , time: str):
    task = task_collection.find_one({"date":date , "time":time})
    if task:
        task_collection.delete_one({"date": date , "time": time})
        return {"message": f"Task deleted successfully {date} at {time} tittled {task.get('name')}"}
    return {"error": "Task not found"}
