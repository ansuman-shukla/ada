from fastapi import FastAPI
from router.taskRouter import router as task_router
from router.aiRouter import router as ai_router


nayanshi = FastAPI()
nayanshi.include_router(task_router)
nayanshi.include_router(ai_router)