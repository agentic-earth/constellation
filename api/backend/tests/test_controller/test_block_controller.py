import pytest
from fastapi import HTTPException
from prisma import Prisma

from backend.app.features.core.controllers.block_controller import BlockController
from backend.app.schemas import (
    BlockCreateSchema,
    BlockUpdateSchema,
    BlockResponseSchema,
    BlockDeleteSchema,
    BlockRetrieveSchema,
    VectorRepresentationCreateSchema,
    VectorRepresentationResponseSchema,
)

from uuid import UUID, uuid4

def generate_block_data():
    block_id = uuid4()
    block_data = {
        "block_id": block_id,
        "name": f"Test Block {block_id}",
        "block_type": "dataset",  # Must be either 'dataset' or 'model'
        "description": f"This is a test block {block_id}.",
        "taxonomy": {"category": "Earth Science"},
    }
    return block_data

# Test data
TEST_USER_ID = "00000000-0000-0000-0000-000000000001"
TEST_USER_DATA = {
    "user_id": TEST_USER_ID,
    "username": "TestUser",
    "email": "testuser@example.com",
    "password_hash": "hashed_password",
    "role": "user",
}


@pytest.fixture
async def prisma_client():
    client = Prisma(datasource={'url': 'postgresql://postgres:password@localhost:5432/postgres'})
    await client.connect()
    yield client
    await client.disconnect()

# @pytest.fixture(autouse=True)
# async def setup_and_teardown(prisma_client):
#     # Setup: Insert necessary test data, e.g., a user
#     await prisma_client.users.create(data=TEST_USER_DATA)
#     yield
#     # Teardown: Clean up the database after tests
#     await prisma_client.execute_raw("TRUNCATE TABLE audit_logs, api_keys, block_categories, block_taxonomies, block_vector_representations, block_versions, blocks CASCADE;")
#     await prisma_client.execute_raw("TRUNCATE TABLE users CASCADE;")

@pytest.mark.asyncio
async def test_setup(prisma_client):
    async for client in prisma_client:
        # Insert necessary test data, e.g., a user
        await client.users.create(data=TEST_USER_DATA)

@pytest.mark.asyncio
async def test_create_block_without_taxonomy(prisma_client):
    block_data = generate_block_data()
    create_block_data = BlockCreateSchema(
        name=block_data["name"],
        block_type=block_data["block_type"],
        description=block_data["description"],
        created_by=TEST_USER_ID,
    )
    async for client in prisma_client:
        block_controller = BlockController(prisma=client)
        block_response = await block_controller.create_block(TEST_USER_ID, create_block_data)

        assert block_response is not None
        assert block_response.name == block_data["name"]
        assert block_response.block_type == block_data["block_type"]
        assert block_response.description == block_data["description"]
        assert block_response.created_by == UUID(TEST_USER_ID)
        assert block_response.taxonomy is None

@pytest.mark.asyncio
async def test_get_block_by_id(prisma_client):
    # First, create a block
    block_data = generate_block_data()
    create_block_data = BlockCreateSchema(
        name=block_data["name"],
        block_type=block_data["block_type"],
        description=block_data["description"],
        created_by=TEST_USER_ID,
    )
    
    async for client in prisma_client:
        block_controller = BlockController(prisma=client)
        # Create the block
        created_block = await block_controller.create_block(TEST_USER_ID, create_block_data)
        # Retrieve the block
        retrieved_block = await block_controller.get_block_by_id(
            TEST_USER_ID,
            BlockRetrieveSchema(block_id=created_block.block_id, user_id=created_block.created_by)
        )

        assert retrieved_block is not None
        assert retrieved_block.block_id == created_block.block_id
        assert retrieved_block.name == block_data["name"]

@pytest.mark.asyncio
async def test_update_block(prisma_client: Prisma):
    # Create a block to update
    block_data = generate_block_data()
    create_block_data = BlockCreateSchema(
        name=block_data["name"],
        block_type=block_data["block_type"],
        description=block_data["description"],
        created_by=TEST_USER_ID,
    )

    # Prepare update data
    update_data = BlockUpdateSchema(
        name="Updated Block",
        block_type="model",  # Must be either 'dataset' or 'model'
        description="Updated description.",
        updated_by=TEST_USER_ID,
    )

    async for client in prisma_client:
        block_controller = BlockController(prisma=client)
        created_block = await block_controller.create_block(TEST_USER_ID, create_block_data)

        # Update the block
        updated_block = await block_controller.update_block(
            TEST_USER_ID,
            block_id=created_block.block_id,
            update_data=update_data,
        )

        assert updated_block is not None
        assert updated_block.name == update_data.name
        assert updated_block.block_type == update_data.block_type
        assert updated_block.description == update_data.description
        assert updated_block.updated_by == UUID(TEST_USER_ID)

@pytest.mark.asyncio
async def test_delete_block(prisma_client: Prisma):
    # Create a block to delete
    block_data = generate_block_data()
    create_block_data = BlockCreateSchema(
        name=block_data["name"],
        block_type=block_data["block_type"],
        description=block_data["description"],
        created_by=TEST_USER_ID,
    )
    async for client in prisma_client:
        block_controller = BlockController(prisma=client)
        created_block = await block_controller.create_block(TEST_USER_ID, create_block_data)

        # Delete the block
        deletion_success = await block_controller.delete_block(
            TEST_USER_ID,
            BlockDeleteSchema(block_id=created_block.block_id, user_id=TEST_USER_ID)
        )

        assert deletion_success is True

        # Verify the block has been deleted
        with pytest.raises(HTTPException) as excinfo:
            await block_controller.get_block_by_id(
                TEST_USER_ID,
                BlockDeleteSchema(block_id=created_block.block_id, user_id=TEST_USER_ID)
            )
        assert excinfo.value.status_code == 404

@pytest.mark.asyncio
async def test_create_vector_embedding(prisma_client: Prisma):
    # Create a block
    block_data = generate_block_data()
    create_block_data = BlockCreateSchema(
        name=block_data["name"],
        block_type=block_data["block_type"],
        description=block_data["description"],
        created_by=TEST_USER_ID,
    )
    async for client in prisma_client:
        block_controller = BlockController(prisma=client)
        created_block = await block_controller.create_block(TEST_USER_ID, create_block_data)

        # Create a vector embedding for the block
        vector_data = VectorRepresentationCreateSchema(
            entity_type="block",
            entity_id=created_block.block_id,
            vector=[0.1, 0.2, 0.3],
            taxonomy_filter={"category": "Test Category"},
        )

        vector_embedding = await block_controller.create_vector_embedding(TEST_USER_ID, vector_data)

        assert vector_embedding is not None
        assert vector_embedding.entity_id == created_block.block_id
        assert vector_embedding.vector == [0.1, 0.2, 0.3]

## TODO: Fix this test
# @pytest.mark.asyncio
# async def test_perform_similarity_search(prisma_client: Prisma):
#     # Create multiple blocks with vector embeddings
#     async for client in prisma_client:
#         block_controller = BlockController(prisma=client)
#         for i in range(5):
#             block_data = BlockCreateSchema(
#                 name=f"Test Block {i}",
#             block_type="dataset",
#             description=f"Test description {i}",
#             created_by=TEST_USER_ID,
#                 updated_by=TEST_USER_ID,
#             )
#             created_block = await block_controller.create_block(block_data)

#             vector_data = VectorRepresentationCreateSchema(
#                 entity_type="block",
#                 entity_id=created_block.block_id,
#                 vector=[0.1 * i, 0.2 * i, 0.3 * i],
#                 taxonomy_filter={"category": "Test Category"},
#             )
#             await block_controller.create_vector_embedding(vector_data)

#             # Perform similarity search 
#             query_text = "test query"
#             taxonomy_filters = {"category": "Test Category"}
#             similar_blocks = await block_controller.perform_similarity_search(query_text, taxonomy_filters, top_k=3)

#             assert isinstance(similar_blocks, list)
#             assert len(similar_blocks) <= 3
#             for block in similar_blocks:
#                 assert isinstance(block, BlockResponseSchema)
#                 assert block.taxonomy["category"] == "Test Category"
