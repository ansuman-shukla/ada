from fastapi import APIRouter , status

router = APIRouter(
    prefix="/ai",
    tags=["ai"],
    responses={404: {"description": "Not found"}},
)

@router.get("/" , status_code=status.HTTP_200_OK)
async def get_ai(user_query:str):
    return await interact_with_llm_and_tools(user_query)