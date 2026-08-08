import asyncio

from database import Region, async_session, init_db
from lexicon import REGIONS

from sqlalchemy import delete

async def seed_regions():
    async with async_session() as session:

        await session.execute(
            delete(Region)
        )

        for data in REGIONS:
            session.add(
                Region(**data)
            )

        await session.commit()


async def main():
    await init_db()
    await seed_regions()


if __name__ == "__main__":
    asyncio.run(main())
    print("done")
