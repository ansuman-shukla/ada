from models.taskModels import taskModel, taskModelList
from schemas.taskSchema import TaskSchema
from database.mongoDB import task_collection
from repos.taskRepository import get_all_tasks,get_task_by_date,get_task_by_time,get_task_by_date_time,create_task,update_task,delete_task

def get_all_tasks_from_db():
    return taskModelList(get_all_tasks())

def get_task_by_date_from_db(date: str):
    return taskModel(get_task_by_date(date))

def get_task_by_time_from_db(time: str):
    return taskModel(get_task_by_time(time))

def get_task_by_date_time_from_db(date: str , time: str):
    return taskModel(get_task_by_date_time(date , time))

def create_task_in_db(task: TaskSchema):
    task_dict = task_collection.find_one({"date":task.date , "time":task.time} )  # Find task by date and time
    # print(task_dict)
    # print(task)
    print(task)
    # if task_dict is None:
        # return taskModel(create_task(task))
    
    # existing_task_name = task_dict.get("name")  # Get name from existing task
    # return {"error": f"Task '{existing_task_name}' already exists for {task.date} at {task.time}"}  # Return error message

def update_task_in_db(task: TaskSchema):
    return taskModel(update_task(task))

def delete_task_in_db(date: str , time: str):
    return delete_task(date , time)




