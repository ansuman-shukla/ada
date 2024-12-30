from pydantic import BaseModel

class TaskSchema(BaseModel):
    name: str
    description: str
    status: str
    time : str
    date : str
    priority: str