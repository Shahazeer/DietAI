import logging
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends
from app.database.mongodb import mongodb
from app.models.user import UserCreate, UserLogin, UserOut, UserUpdate, TokenResponse
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.dependencies.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate):
    db = mongodb.get_database()
    existing = await db.users.find_one({"email": body.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    now = datetime.now(timezone.utc)
    doc = {
        "email": body.email,
        "hashed_password": hash_password(body.password),
        "name": body.name,
        "age": body.age,
        "gender": body.gender,
        "dietary_preferences": body.dietary_preferences,
        "allergies": body.allergies,
        "created_at": now,
        "updated_at": now,
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
        logger.warning("Failed login attempt for email=%s", body.email)
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
        dietary_preferences=user.get("dietary_preferences", "non-veg"),
        allergies=user.get("allergies", []),
    )
    return TokenResponse(access_token=token, user=user_out)


@router.get("/me", response_model=UserOut)
async def get_me(user: dict = Depends(get_current_user)):
    return UserOut(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        age=user["age"],
        gender=user["gender"],
        dietary_preferences=user.get("dietary_preferences", "non-veg"),
        allergies=user.get("allergies", []),
    )


@router.patch("/profile", response_model=UserOut)
async def update_profile(body: UserUpdate, user: dict = Depends(get_current_user)):
    db = mongodb.get_database()
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(400, detail="No fields provided to update")

    updates["updated_at"] = datetime.now(timezone.utc)
    await db.users.update_one({"_id": ObjectId(user["id"])}, {"$set": updates})
    logger.info("Profile updated for user=%s fields=%s", user["id"], list(updates.keys()))

    refreshed = await db.users.find_one({"_id": ObjectId(user["id"])}, {"hashed_password": 0})
    return UserOut(
        id=str(refreshed["_id"]),
        email=refreshed["email"],
        name=refreshed["name"],
        age=refreshed["age"],
        gender=refreshed["gender"],
        dietary_preferences=refreshed.get("dietary_preferences", "non-veg"),
        allergies=refreshed.get("allergies", []),
    )
