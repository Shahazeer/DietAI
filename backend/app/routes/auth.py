import logging
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.database.mongodb import mongodb
from app.models.user import UserCreate, UserLogin, UserOut, TokenResponse
from app.services.auth_service import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate):
    db = mongodb.get_database()
    existing = await db.users.find_one({"email": body.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    doc = {
        "email": body.email,
        "hashed_password": hash_password(body.password),
        "name": body.name,
        "age": body.age,
        "gender": body.gender,
        "dietary_preferences": body.dietary_preferences,
        "allergies": body.allergies,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db.users.insert_one(doc)
    user_id = str(result.inserted_id)
    logger.info("New user registered: %s", body.email)

    token = create_access_token(user_id, body.email)
    user_out = UserOut(
        id=user_id,
        email=body.email,
        name=body.name,
        age=body.age,
        gender=body.gender,
        dietary_preferences=body.dietary_preferences,
        allergies=body.allergies,
    )
    return TokenResponse(access_token=token, user=user_out)


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin):
    db = mongodb.get_database()
    user = await db.users.find_one({"email": body.email})
    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])
    token = create_access_token(user_id, user["email"])
    logger.info("User logged in: %s", body.email)

    user_out = UserOut(
        id=user_id,
        email=user["email"],
        name=user["name"],
        age=user["age"],
        gender=user["gender"],
        dietary_preferences=user.get("dietary_preferences", ""),
        allergies=user.get("allergies", []),
    )
    return TokenResponse(access_token=token, user=user_out)


@router.get("/me", response_model=UserOut)
async def get_me(user: dict = __import__('fastapi').Depends(
    __import__('app.dependencies.auth', fromlist=['get_current_user']).get_current_user
)):
    return UserOut(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        age=user["age"],
        gender=user["gender"],
        dietary_preferences=user.get("dietary_preferences", ""),
        allergies=user.get("allergies", []),
    )
