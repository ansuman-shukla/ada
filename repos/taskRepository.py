from database.mongoDB import task_collection
from schemas.taskSchema import TaskSchema
from models.taskModels import taskModel , taskModelList

def get_all_tasks():
    return task_collection.find()


def get_task_by_date(date: str):
    task_entity =  task_collection.find({"date": date})

    if not task_entity:
        return {"error": "Task not found"}
    return taskModelList(task_entity)


def get_task_by_time(time: str):
    task_entity = task_collection.find({"time": time})

    if not task_entity:
        return {"error": "Task not found"}
    
    return taskModelList(task_entity)

def get_task_by_date_time(date: str, time: str):
    task_entity = task_collection.find_one({"date": date, "time": time})
    
    if not task_entity:
        return {"error": "Task not found"}
    
    return taskModel(task_entity)

def create_task(task: TaskSchema):
    task_collection.insert_one(task)
    return task
    
def update_task(date: str , time : str ,task: dict):
    task_exists = task_collection.find_one({"date":date , "time":time})

    if task_exists:
        result = task_collection.update_one(
            {"date": date, "time": time},
            {"$set": task}
        )
        updated_task = task_collection.find_one({"date": task['date'], "time": task['time']})
        return TaskSchema(**updated_task)

    return {"error": "Task not found"}

def delete_task(date: str , time: str):
    task = task_collection.find_one({"date":date , "time":time})
    if not task:
        return {"error": "Task not found"}
        
    task_collection.delete_one({"date": date , "time": time})
    return {"message": f"Task deleted successfully {date} at {time} tittled {task.get('name')}"}
    
