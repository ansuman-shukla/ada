from fastapi import APIRouter , status
from typing import List
from schemas.taskSchema import TaskSchema
from services.taskServices import  get_all_tasks_from_db ,get_task_by_date_from_db , get_task_by_time_from_db , get_task_by_date_time_from_db , create_task_in_db , update_task_in_db , delete_task_in_db
router = APIRouter(
    prefix="/task",
    tags=["task"],
    responses={404: {"description": "Not found"}},
)


@router.get("/" , response_model=List[TaskSchema] , status_code=status.HTTP_200_OK)
async def get_all():
    return get_all_tasks_from_db()

@router.get("/{date}" , response_model=TaskSchema , status_code=status.HTTP_200_OK)
async def get_task_by_date(date: str):
    return get_task_by_date_from_db(date)

@router.get("/{time}" , response_model=TaskSchema , status_code=status.HTTP_200_OK)
async def get_task_by_time(time: str):
    return get_task_by_time_from_db(time)

@router.get("/{date}/{time}" , response_model=TaskSchema , status_code=status.HTTP_200_OK)
async def get_task_by_date_time(date: str , time: str):
    return get_task_by_date_time_from_db(date , time)

@router.post("/" , response_model=TaskSchema , status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskSchema):
    return create_task_in_db(task)

@router.put("/" , response_model=TaskSchema , status_code=status.HTTP_200_OK)
async def update_task(task: TaskSchema):
    return update_task_in_db(task)

@router.delete("/{date}/{time}" , status_code=status.HTTP_200_OK)
async def delete_task(date: str , time: str):
    return delete_task_in_db(date , time)

