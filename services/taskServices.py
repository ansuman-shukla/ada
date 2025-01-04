from models.taskModels import taskModel, taskModelList
from schemas.taskSchema import TaskSchema
from database.mongoDB import task_collection
from repos.taskRepository import get_all_tasks,get_task_by_date,get_task_by_time,get_task_by_date_time,create_task,update_task,delete_task

def get_all_tasks_from_db():
    return taskModelList(get_all_tasks())

def get_task_by_date_from_db(date: str):
    return get_task_by_date(date)

def get_task_by_time_from_db(time: str):
    return get_task_by_time(time)

def get_task_by_date_time_from_db(date: str , time: str):
    return get_task_by_date_time(date , time)

def create_task_in_db(task:dict):
    task_dict = task_collection.find_one({"date":task['date'] , "time":task['time']} )  # Find task by date and time
    
    if task_dict is None:
        task_model = taskModel(create_task(task))
        return task_model
        # return TaskSchema(task_model)
    
    existing_task_name = task_dict.get("name")  # Get name from existing task
    return {"error": f"Task '{existing_task_name}' already exists for {task['date']} at {task['time']}"}  # Return error message

def update_task_in_db(date:str , time:str ,task: TaskSchema):
    return (update_task(date , time ,task))

def delete_task_in_db(date: str , time: str):
    return delete_task(date , time)




