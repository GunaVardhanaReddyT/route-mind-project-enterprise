from fastapi import APIRouter

router = APIRouter()

@router.get("/hubs")
async def get_hubs():
    """Get all available hubs"""
    return {
        "hubs": [
            {"id": 1, "name": "Delhi", "city": "Delhi"},
            {"id": 2, "name": "Mumbai", "city": "Mumbai"},
            {"id": 3, "name": "Bangalore", "city": "Bangalore"}
        ]
    }
