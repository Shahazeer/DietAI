from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


class MongoDB:
    client: AsyncIOMotorClient = None

    async def connect(self):
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        db = self.client[settings.database_name]

        # Unique constraint on user email
        await db.users.create_index("email", unique=True)

        # Compound indexes for common query patterns — avoids full collection scans
        await db.lab_reports.create_index([("user_id", 1), ("upload_date", -1)])
        await db.lab_reports.create_index([("user_id", 1), ("file_hash", 1)], unique=True, sparse=True)  # deduplication
        await db.diet_plans.create_index([("user_id", 1), ("created_at", -1)])
        await db.diet_plans.create_index("report_id")   # for batch diet-plan lookups

    async def disconnect(self):
        self.client.close()

    def get_database(self):
        return self.client[settings.database_name]


mongodb = MongoDB()
