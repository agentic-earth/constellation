# constellation-backend/api/backend/app/features/core/services/block_service.py

"""
Block Service Module

This module implements the Block Service using a Repository pattern with Prisma ORM.

Design Pattern:
- Repository Pattern: The BlockService class acts as a repository, encapsulating the data access logic.
- Dependency Injection: The Prisma client is injected via the database singleton.

Key Design Decisions:
1. Use of Dictionaries: We use dictionaries for input data to provide flexibility in the API.
   This allows callers to provide only the necessary fields without needing to construct full objects.

2. Prisma Models: We use Prisma-generated models (Block) for type hinting and as return types.
   This ensures type safety and consistency with the database schema.

3. Raw SQL for Unsupported Types: The `vector` field is managed using raw SQL queries since Prisma does not support it.

4. Error Handling: Exceptions are allowed to propagate, to be handled by the caller.

This approach balances flexibility, type safety, and simplicity, leveraging Prisma's capabilities
while providing a clean API for block operations.
"""
import re
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import asyncio

from prisma.errors import UniqueViolationError
from prisma.models import Block as PrismaBlock
from prisma import Prisma
from backend.app.database import database
from backend.app.logger import ConstellationLogger
from sentence_transformers import SentenceTransformer

class BlockService:
    def __init__(self):
        self.prisma = database.prisma
        self.logger = ConstellationLogger()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def connect(self):
        await self.prisma.connect()

    async def disconnect(self):
        await self.prisma.disconnect()

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generates a vector embedding for the provided text.

        Args:
            text (str): The text to generate an embedding for.

        Returns:
            List[float]: The generated vector.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.embedding_model.encode, text)

    async def create_block(self, block_data: Dict[str, Any], vector: Optional[List[float]] = None) -> Optional[PrismaBlock]:
        """
        Creates a new block in the database or retrieves it if it already exists.

        Args:
            block_data (Dict[str, Any]): Dictionary containing block data.
            vector (Optional[List[float]]): Optional vector representation for the block.

        Returns:
            Optional[PrismaBlock]: The created or existing block.
        """
        block_data['block_id'] = str(uuid4())
        block_data['created_at'] = datetime.utcnow()
        block_data['updated_at'] = datetime.utcnow()
        
        try:
            # Generate embedding if text is provided and vector is not
            if 'text' in block_data and not vector:
                print(f"Generating vector for block: {block_data['name']}")
                vector = await self.generate_embedding(block_data['text'])
                print(f"Generated vector: {vector[:5]}...")

            # Create block via Prisma
            created_block = await self.prisma.block.create(data=block_data)
            
            if vector:
                print(f"Associating vector with block: {created_block.name}")
                vector_success = await self.set_block_vector(created_block.block_id, vector)
                print(f"Vector association success: {vector_success}")
                if not vector_success:
                    print("Failed to associate vector with block")

            self.logger.log(
                "BlockService",
                "info",
                "Block created successfully.",
                block_id=created_block.block_id,
                block_name=created_block.name
            )
            return created_block
        
        except UniqueViolationError:
            # Block with this name already exists, retrieve it
            existing_block = await self.get_block_by_name(block_data['name'])
            if existing_block:
                self.logger.log(
                    "BlockService",
                    "info",
                    "Block already exists, retrieved existing block.",
                    block_id=existing_block.block_id,
                    block_name=existing_block.name
                )
                return existing_block
            else:
                # This shouldn't happen, but handle it just in case
                raise ValueError(f"Failed to create or retrieve block with name: {block_data['name']}")
        except Exception as e:
            self.logger.log("BlockService", "error", "Failed to create block", error=str(e))
            return None

    async def get_block_by_id(self, block_id: UUID) -> Optional[PrismaBlock]:
        """
        Retrieves a block by its ID.

        Args:
            block_id (UUID): The ID of the block to retrieve.

        Returns:
            Optional[PrismaBlock]: The retrieved block, or None if not found.
        """
        try:
            block = await self.prisma.block.find_unique(where={"block_id": str(block_id)})

            if block:
                self.logger.log(
                    "BlockService",
                    "info",
                    "Block retrieved successfully.",
                    block_id=block.block_id,
                    block_name=block.name
                )
            else:
                self.logger.log(
                    "BlockService",
                    "warning",
                    "Block not found.",
                    block_id=str(block_id)
                )

            return block
        except Exception as e:
            self.logger.log("BlockService", "error", "Failed to retrieve block by ID", error=str(e))
            return None

    async def get_block_by_name(self, name: str) -> Optional[PrismaBlock]:
        """
        Retrieves a block by its name.

        Args:
            name (str): The name of the block to retrieve.

        Returns:
            Optional[PrismaBlock]: The retrieved block, or None if not found.
        """
        try:
            block = await self.prisma.block.find_unique(where={"name": name})

            if block:
                self.logger.log(
                    "BlockService",
                    "info",
                    "Block retrieved successfully by name.",
                    block_id=block.block_id,
                    block_name=block.name
                )
            else:
                self.logger.log(
                    "BlockService",
                    "warning",
                    "Block not found by name.",
                    block_name=name
                )

            return block
        except Exception as e:
            self.logger.log("BlockService", "error", "Failed to retrieve block by name", error=str(e))
            return None

    async def update_block(self, block_id: UUID, update_data: Dict[str, Any], vector: Optional[List[float]] = None) -> Optional[PrismaBlock]:
        """
        Updates a block's details.

        Args:
            block_id (UUID): The ID of the block to update.
            update_data (Dict[str, Any]): Dictionary containing fields to update.
            vector (Optional[List[float]]): Optional vector data to update.

        Returns:
            Optional[PrismaBlock]: The updated block.
        """
        try:
            update_data['updated_at'] = datetime.utcnow()

            # Generate new embedding if text is updated and vector is not provided
            if 'text' in update_data and not vector:
                vector = await self.generate_embedding(update_data['text'])

            # Remove 'vector' from update_data since it's unsupported by Prisma
            update_vector = update_data.pop('vector', None)

            # Update block via Prisma
            updated_block = await self.prisma.block.update(
                where={"block_id": str(block_id)},
                data=update_data
            )

            if update_vector:
                # Update vector using existing set_block_vector method
                vector_success = await self.set_block_vector(updated_block.block_id, update_vector)
                if vector_success:
                    self.logger.log(
                        "BlockService",
                        "info",
                        "Vector updated successfully.",
                        block_id=updated_block.block_id
                    )
                else:
                    self.logger.log(
                        "BlockService",
                        "warning",
                        "Failed to update vector.",
                        block_id=updated_block.block_id
                    )

            self.logger.log(
                "BlockService",
                "info",
                "Block updated successfully.",
                block_id=updated_block.block_id,
                updated_fields=list(update_data.keys())
            )
            return updated_block
        except Exception as e:
            self.logger.log("BlockService", "error", "Failed to update block", error=str(e))
            return None

    async def delete_block(self, block_id: UUID) -> bool:
        """
        Deletes a block from the database.

        Args:
            block_id (UUID): The ID of the block to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            await self.prisma.block.delete(where={"block_id": str(block_id)})

            self.logger.log(
                "BlockService",
                "info",
                "Block deleted successfully.",
                block_id=str(block_id)
            )

            return True
        except Exception as e:
            self.logger.log("BlockService", "error", "Failed to delete block", error=str(e))
            return False

    async def set_block_vector(self, block_id: str, vector: List[float]) -> bool:
        """
        Associates or updates a vector representation for a block using raw SQL.

        Args:
            block_id (str): The ID of the block.
            vector (List[float]): The vector data.

        Returns:
            bool: True if operation was successful, False otherwise.
        """
        try:
            vector_str = ','.join(map(str, vector))
            raw_query = f"""
                UPDATE "Block"
                SET vector = ARRAY[{vector_str}]::vector, updated_at = NOW()
                WHERE block_id = '{block_id}';
            """
            await self.prisma.execute_raw(raw_query)
            print(f"Vector updated for block: {block_id}")
            return True
        except Exception as e:
            print(f"Error in set_block_vector: {str(e)}")
            return False

    async def get_block_vector(self, block_id: str) -> Optional[List[float]]:
        """
        Retrieves the vector representation of a block.

        Args:
            block_id (str): The ID of the block.

        Returns:
            Optional[List[float]]: The vector representation, or None if not found.
        """
        try:
            raw_query = f"""
                SELECT vector
                FROM "Block"
                WHERE block_id = '{block_id}';
            """
            result = await self.prisma.query_raw(raw_query)
            if result and result[0]['vector']:
                return result[0]['vector']
            return None
        except Exception as e:
            print(f"Error in get_block_vector: {str(e)}")
            return None

    async def search_blocks_by_vector_similarity(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a vector similarity search on blocks.

        Args:
            query_vector (List[float]): The query vector.
            top_k (int): The number of top similar blocks to return.

        Returns:
            List[Dict[str, Any]]: List of similar blocks with their similarity scores.
        """
        try:
            vector_str = ','.join(map(str, query_vector))
            raw_query = f"""
                SELECT block_id, name, block_type, description, 
                       1 - (vector <=> ARRAY[{vector_str}]::vector) as similarity
                FROM "Block"
                WHERE vector IS NOT NULL
                ORDER BY similarity DESC
                LIMIT {top_k};
            """
            print(f"Executing query: {raw_query}")
            results = await self.prisma.query_raw(raw_query)
            print(f"Raw results: {results}")
            return [
                {
                    "block_id": str(row['block_id']),
                    "name": row['name'],
                    "block_type": row['block_type'],
                    "description": row['description'],
                    "similarity": float(row['similarity'])
                }
                for row in results
            ]
        except Exception as e:
            self.logger.log("BlockService", "error", "Failed to perform vector similarity search", error=str(e))
            print(f"Error in search_blocks_by_vector_similarity: {str(e)}")
            return []

    async def get_all_vectors(self) -> List[List[float]]:
        """
        Retrieves all vector representations for blocks using raw SQL.

        Returns:
            List[List[float]]: A list of all vector representations.
        """
        try:
            raw_query = """
                SELECT block_id, vector
                FROM "Block"
                WHERE vector IS NOT NULL;
            """

            results = await self.prisma.execute_raw(raw_query)

            vectors = [row['vector'] for row in results if row['vector']]
            print(f"Raw results: {results}")
            print(f"Extracted vectors: {vectors}")

            self.logger.log(
                "BlockService",
                "info",
                f"Retrieved {len(vectors)} vectors for blocks."
            )

            return vectors
        except Exception as e:
            self.logger.log("BlockService", "error", "Failed to retrieve all vectors", error=str(e))
            return []

 
async def main():
    """
    Main function to demonstrate and test the BlockService functionality.
    """
    print("Starting BlockService test...")

    print("Connecting to the database...")
    await database.connect()
    print("Database connected successfully.")

    block_service = BlockService()

    try:
        # Step 1: Create a new block without vector
        print("\nCreating a new block without vector...")
        new_block_data = {
            "name": "TestBlock1",
            "block_type": "dataset",
            "description": "This is a test block without vector."
        }
        created_block = await block_service.create_block(new_block_data)
        if created_block:
            print(f"Created block: {created_block}")
        else:
            print("Failed to create block 'TestBlock1'.")

        # Step 2: Create a new block with vector
        print("\nCreating a new block with vector...")
        new_block_with_vector_data = {
            "name": "TestBlock2",
            "block_type": "model",
            "description": "This is a test block with vector."
        }
        test_vector = [0.1, 0.2, 0.3, 0.4, 0.5]  # Example vector
        created_block_with_vector = await block_service.create_block(new_block_with_vector_data, vector=test_vector)
        if created_block_with_vector:
            print(f"Created block with vector: {created_block_with_vector}")
        else:
            print("Failed to create block 'TestBlock2'.")

        if created_block_with_vector:
            block_id = created_block_with_vector.block_id

            # Step 3: Retrieve block by ID
            print(f"\nRetrieving block with ID: {block_id}")
            retrieved_block = await block_service.get_block_by_id(UUID(block_id))
            print(f"Retrieved block: {retrieved_block}")

            # Step 4: Retrieve block by Name
            print(f"\nRetrieving block with name: {created_block_with_vector.name}")
            block_by_name = await block_service.get_block_by_name(created_block_with_vector.name)
            print(f"Retrieved block by name: {block_by_name}")

            # Step 5: Update block
            print(f"\nUpdating block with ID: {block_id}")
            update_data = {"description": "Updated description for TestBlock2."}
            updated_block = await block_service.update_block(UUID(block_id), update_data)
            print(f"Updated block: {updated_block}")

            # Step 6: Associate a new vector to the block
            print(f"\nAssociating a new vector to block with ID: {block_id}")
            new_vector = [0.5, 0.4, 0.3, 0.2, 0.1]
            vector_success = await block_service.set_block_vector(block_id, new_vector)
            print(f"Vector associated: {vector_success}")

            # Step 7: Retrieve block vector
            print(f"\nRetrieving vector for block with ID: {block_id}")
            block_vector = await block_service.get_block_vector(block_id)
            print(f"Retrieved vector: {block_vector}")

            # Step 8: Perform a vector similarity search
            print("\nPerforming vector similarity search...")
            query_vector = [0.1, 0.2, 0.3, 0.4, 0.5]
            similar_blocks = await block_service.search_blocks_by_vector_similarity(query_vector, top_k=5)
            print(f"Similar blocks: {similar_blocks}")

            # Step 9: Delete block
            print(f"\nDeleting block with ID: {block_id}")
            deleted = await block_service.delete_block(UUID(block_id))
            print(f"Block deleted: {deleted}")

        # Step 10: List all blocks
        print("\nListing all blocks...")
        all_blocks = await block_service.prisma.block.find_many()
        print(f"Total blocks: {len(all_blocks)}")
        for block in all_blocks:
            print(f"- Block ID: {block.block_id}, Name: {block.name}, Type: {block.block_type}, Description: {block.description}")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        print(traceback.format_exc())

    finally:
        print("\nDisconnecting from the database...")
        await database.disconnect()
        print("Database disconnected.")

if __name__ == "__main__":
    asyncio.run(main())