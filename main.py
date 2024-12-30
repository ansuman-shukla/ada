from fastapi import FastAPI
from router.taskRouter import router as task_router

app = FastAPI()

app.include_router(task_router)

# if __name__ == "__main__":
    # import uvicorn
    # uvicorn.run(app, host="", port=8000)