import asyncio
from backend.app.features.core.services.block_service import BlockService


async def populate_papers():
    block_service = BlockService()

    papers = [
        {
            "name": "Climate Change and Extreme Weather",
            "text": "This paper discusses the relationship between climate change and the increasing frequency of extreme weather events...",
            "block_type": "paper",
            "description": "A study on climate change impacts",
        },
        # Add more papers here...
    ]

    for paper in papers:
        await block_service.create_block(paper)


if __name__ == "__main__":
    asyncio.run(populate_papers())
