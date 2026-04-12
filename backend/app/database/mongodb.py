from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


class MongoDB:
    client: AsyncIOMotorClient = None

    async def connect(self):
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        db = self.client[settings.database_name]
        await db.users.create_index("email", unique=True)
        await db.lab_reports.create_index("user_id")
        await db.diet_plans.create_index("user_id")

    async def disconnect(self):
        self.client.close()

    def get_database(self):
        return self.client[settings.database_name]


mongodb = MongoDB()
