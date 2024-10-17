# constellation-backend/api/backend/app/features/core/services/paper_service.py

"""
Paper Service Module

This module implements the Paper Service using a Repository pattern with Prisma ORM.

Design Pattern:
- Repository Pattern: The PaperService class acts as a repository, encapsulating the data access logic.
- Dependency Injection: The Prisma client is injected via the database singleton.

Key Design Decisions:
1. One-to-One Relationship: Each Paper can be associated with at most one Block and vice versa.
   This simplifies the association logic and ensures data integrity.

2. Use of Dictionaries: We use dictionaries for input data to provide flexibility in the API.
   This allows callers to provide only the necessary fields without needing to construct full objects.

3. Prisma Models: We use Prisma-generated models (Paper, Block) for type hinting and as return types.
   This ensures type safety and consistency with the database schema.

4. Error Handling: Comprehensive error handling to manage exceptions and ensure data consistency.

This approach balances flexibility, type safety, and simplicity, leveraging Prisma's capabilities
while providing a clean API for paper operations.
"""

from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from prisma import Prisma
from prisma.models import Paper as PrismaPaper, Block as PrismaBlock
from backend.app.logger import ConstellationLogger
import asyncio

class PaperService:
    def __init__(self):
        self.logger = ConstellationLogger()

    async def create_paper(
        self, tx: Prisma, paper_data: Dict[str, Any], block_id: Optional[UUID] = None
    ) -> Optional[PrismaPaper]:
        """
        Creates a new Paper. Optionally associates it with a single Block.

        Args:
            tx (Prisma): Prisma transaction instance.
            paper_data (Dict[str, Any]): Data for the paper including pdf_url, title, and abstract.
            block_id (Optional[UUID]): Block ID to associate with the paper.

        Returns:
            Optional[PrismaPaper]: The created Paper object or None if failed.
        """
        try:
            # Prepare data for Paper creation
            data = {
                "pdf_url": paper_data.get("pdf_url", ""),
                "title": paper_data.get("title", ""),
                "abstract": paper_data.get("abstract", ""),
            }

            # If block_id is provided, associate the Block
            if block_id:
                data["block"] = {
                    "connect": {"block_id": str(block_id)}
                }

            # Create the Paper
            created_paper = await tx.paper.create(
                data=data
            )

            self.logger.log(
                "PaperService",
                "info",
                "Paper created successfully.",
                paper_id=created_paper.paper_id,
                block_id=block_id
            )
            return created_paper
        except Exception as e:
            self.logger.log(
                "PaperService",
                "error",
                "Failed to create paper.",
                error=str(e),
                paper_data=paper_data,
                block_id=block_id
            )
            return None

    async def get_paper(
        self, tx: Prisma, paper_id: UUID, include_block: bool = False
    ) -> Optional[PrismaPaper]:
        """
        Retrieves a Paper by its ID.

        Args:
            tx (Prisma): Prisma transaction instance.
            paper_id (UUID): ID of the paper to retrieve.
            include_block (bool): Whether to include the associated Block.

        Returns:
            Optional[PrismaPaper]: The Paper object or None if not found.
        """
        try:
            paper = await tx.paper.find_unique(
                where={"paper_id": str(paper_id)},
                include={"block": include_block}
            )
            if paper:
                self.logger.log(
                    "PaperService",
                    "info",
                    "Paper retrieved successfully.",
                    paper_id=paper_id
                )
            else:
                self.logger.log(
                    "PaperService",
                    "warning",
                    "Paper not found.",
                    paper_id=paper_id
                )
            return paper
        except Exception as e:
            self.logger.log(
                "PaperService",
                "error",
                "Failed to retrieve paper.",
                error=str(e),
                paper_id=paper_id
            )
            return None

    async def update_paper(
        self, tx: Prisma, paper_id: UUID, update_data: Dict[str, Any], block_id: Optional[UUID] = None
    ) -> Optional[PrismaPaper]:
        """
        Updates a Paper's details. Optionally updates the associated Block.

        Args:
            tx (Prisma): Prisma transaction instance.
            paper_id (UUID): ID of the paper to update.
            update_data (Dict[str, Any]): Fields to update.
            block_id (Optional[UUID]): Block ID to associate with the paper.

        Returns:
            Optional[PrismaPaper]: The updated Paper object or None if failed.
        """
        try:
            # Prepare data for updating the Paper
            data = {}
            if "pdf_url" in update_data:
                data["pdf_url"] = update_data["pdf_url"]
            if "title" in update_data:
                data["title"] = update_data["title"]
            if "abstract" in update_data:
                data["abstract"] = update_data["abstract"]

            if block_id:
                data["block"] = {
                    "connect": {"block_id": str(block_id)}
                }
            elif "block" in update_data and update_data["block"] is None:
                # Disassociate Block if explicitly set to None
                data["block"] = {
                    "disconnect": True
                }

            # Update the Paper
            updated_paper = await tx.paper.update(
                where={"paper_id": str(paper_id)},
                data=data,
                include={"block": True}
            )
            self.logger.log(
                "PaperService",
                "info",
                "Paper updated successfully.",
                paper_id=paper_id,
                block_id=block_id
            )
            return updated_paper
        except Exception as e:
            self.logger.log(
                "PaperService",
                "error",
                "Failed to update paper.",
                error=str(e),
                paper_id=paper_id,
                update_data=update_data,
                block_id=block_id
            )
            return None

    async def delete_paper(
        self, tx: Prisma, paper_id: UUID
    ) -> bool:
        """
        Deletes a Paper by its ID.

        Args:
            tx (Prisma): Prisma transaction instance.
            paper_id (UUID): ID of the paper to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            await tx.paper.delete(
                where={"paper_id": str(paper_id)}
            )
            self.logger.log(
                "PaperService",
                "info",
                "Paper deleted successfully.",
                paper_id=paper_id
            )
            return True
        except Exception as e:
            self.logger.log(
                "PaperService",
                "error",
                "Failed to delete paper.",
                error=str(e),
                paper_id=paper_id
            )
            return False

    async def list_papers(
        self, tx: Prisma, include_block: bool = False
    ) -> Optional[list]:
        """
        Retrieves all Papers. Optionally includes associated Blocks.

        Args:
            tx (Prisma): Prisma transaction instance.
            include_block (bool): Whether to include the associated Block.

        Returns:
            Optional[list]: List of Papers or None if failed.
        """
        try:
            papers = await tx.paper.find_many(
                include={"block": include_block}
            )
            self.logger.log(
                "PaperService",
                "info",
                f"Retrieved {len(papers)} paper(s) successfully."
            )
            return papers
        except Exception as e:
            self.logger.log(
                "PaperService",
                "error",
                "Failed to retrieve papers.",
                error=str(e)
            )
            return None

    async def associate_block_with_paper(
        self, tx: Prisma, paper_id: UUID, block_id: UUID
    ) -> Optional[PrismaPaper]:
        """
        Associates a Paper with a Block.

        Args:
            tx (Prisma): Prisma transaction instance.
            paper_id (UUID): ID of the paper.
            block_id (UUID): ID of the block.

        Returns:
            Optional[PrismaPaper]: The updated Paper object or None if failed.
        """
        try:
            # Ensure the Block is not already associated with another Paper
            existing_paper = await tx.paper.find_first(
                where={"block_id": str(block_id)}
            )
            if existing_paper:
                raise ValueError(f"Block {block_id} is already associated with another Paper.")

            # Update the Paper to associate with the Block
            updated_paper = await tx.paper.update(
                where={"paper_id": str(paper_id)},
                data={
                    "block": {
                        "connect": {"block_id": str(block_id)}
                    }
                },
                include={"block": True}
            )

            self.logger.log(
                "PaperService",
                "info",
                "Associated Paper with Block successfully.",
                paper_id=paper_id,
                block_id=block_id
            )
            return updated_paper
        except Exception as e:
            self.logger.log(
                "PaperService",
                "error",
                "Failed to associate Paper with Block.",
                error=str(e),
                paper_id=paper_id,
                block_id=block_id
            )
            return None

    async def disassociate_block_from_paper(
        self, tx: Prisma, paper_id: UUID
    ) -> Optional[PrismaPaper]:
        """
        Disassociates a Paper from its Block.

        Args:
            tx (Prisma): Prisma transaction instance.
            paper_id (UUID): ID of the paper.

        Returns:
            Optional[PrismaPaper]: The updated Paper object or None if failed.
        """
        try:
            # Update the Paper to disassociate the Block
            updated_paper = await tx.paper.update(
                where={"paper_id": str(paper_id)},
                data={
                    "block": {
                        "disconnect": True
                    }
                },
                include={"block": True}
            )

            self.logger.log(
                "PaperService",
                "info",
                "Disassociated Paper from Block successfully.",
                paper_id=paper_id
            )
            return updated_paper
        except Exception as e:
            self.logger.log(
                "PaperService",
                "error",
                "Failed to disassociate Paper from Block.",
                error=str(e),
                paper_id=paper_id
            )
            return None

# --------------------- Main Function for Testing ---------------------

async def main():
    """
    Main function to test the PaperService functionalities:
    - Create a paper.
    - Create a block.
    - Associate the block with the paper.
    - Retrieve the associated paper.
    - Update the paper's details and associated block.
    - Disassociate the block from the paper.
    - Delete the paper.
    - List all papers to confirm deletion.
    """
    print("===== Starting PaperService Test =====\n")

    # Initialize Prisma client
    prisma = Prisma()
    await prisma.connect()
    print("Connected to the database.\n")

    # Initialize PaperService
    paper_service = PaperService()

    # --------------------- Create Block ---------------------
    print(">>> Creating Block...")
    try:
        created_block = await prisma.block.create(
            data={
                "name": "Test Block",
                "block_type": "model",
                "description": "This is a test block."
            }
        )
        print("Block Created Successfully:")
        print(f"  ID: {created_block.block_id}")
        print(f"  Name: {created_block.name}")
        print(f"  Type: {created_block.block_type}")
        print(f"  Description: {created_block.description}\n")
    except Exception as e:
        print(f"Failed to create block: {e}\n")
        await prisma.disconnect()
        return

    # Store the created block's ID for further operations
    block_id = UUID(created_block.block_id)

    # --------------------- Create Paper ---------------------
    print(">>> Creating Paper...")
    mock_paper_data = {
        "pdf_url": "https://example.com/papers/test-paper.pdf",
        "title": "Test Paper Title",
        "abstract": "This is an abstract for the test paper."
    }
    print(f"Mock Paper Data for Creation: {mock_paper_data}\n")
    created_paper = await paper_service.create_paper(prisma, mock_paper_data, block_id=block_id)
    if created_paper:
        print("Paper Created Successfully:")
        print(f"  ID: {created_paper.paper_id}")
        print(f"  PDF URL: {created_paper.pdf_url}")
        print(f"  Title: {created_paper.title}")
        print(f"  Abstract: {created_paper.abstract}")
        print(f"  Created At: {created_paper.created_at}")
        print(f"  Updated At: {created_paper.updated_at}")
        print(f"  Associated Block ID: {created_paper.block.block_id}\n")
    else:
        print("Failed to create paper.\n")
        await prisma.disconnect()
        return

    # Store the created paper's ID for further operations
    paper_id = UUID(created_paper.paper_id)

    # --------------------- Retrieve Paper ---------------------
    print(">>> Retrieving Paper...")
    retrieved_paper = await paper_service.get_paper(prisma, paper_id, include_block=True)
    if retrieved_paper:
        print("Paper Retrieved Successfully:")
        print(f"  ID: {retrieved_paper.paper_id}")
        print(f"  PDF URL: {retrieved_paper.pdf_url}")
        print(f"  Title: {retrieved_paper.title}")
        print(f"  Abstract: {retrieved_paper.abstract}")
        print(f"  Created At: {retrieved_paper.created_at}")
        print(f"  Updated At: {retrieved_paper.updated_at}")
        if retrieved_paper.block:
            print("  Associated Block:")
            print(f"    ID: {retrieved_paper.block.block_id}")
            print(f"    Name: {retrieved_paper.block.name}")
            print(f"    Type: {retrieved_paper.block.block_type}")
            print(f"    Description: {retrieved_paper.block.description}")
        print()
    else:
        print("Failed to retrieve paper.\n")

    # --------------------- Update Paper ---------------------
    print(">>> Updating Paper...")
    update_data = {
        "pdf_url": "https://example.com/papers/updated-test-paper.pdf",
        "title": "Updated Test Paper Title",
        "abstract": "This is an updated abstract for the test paper."
    }
    print(f"Update Data: {update_data}\n")
    updated_paper = await paper_service.update_paper(prisma, paper_id, update_data)
    if updated_paper:
        print("Paper Updated Successfully:")
        print(f"  ID: {updated_paper.paper_id}")
        print(f"  PDF URL: {updated_paper.pdf_url}")
        print(f"  Title: {updated_paper.title}")
        print(f"  Abstract: {updated_paper.abstract}")
        print(f"  Created At: {updated_paper.created_at}")
        print(f"  Updated At: {updated_paper.updated_at}\n")
    else:
        print("Failed to update paper.\n")

    # --------------------- Associate Block with Paper ---------------------
    print(">>> Associating Block with Paper...")
    # Create another block to associate
    try:
        another_block = await prisma.block.create(
            data={
                "name": "Another Test Block",
                "block_type": "dataset",
                "description": "This is another test block."
            }
        )
        another_block_id = UUID(another_block.block_id)
        print("Another Block Created Successfully:")
        print(f"  ID: {another_block.block_id}")
        print(f"  Name: {another_block.name}\n")
    except Exception as e:
        print(f"Failed to create another block: {e}\n")
        await prisma.disconnect()
        return

    # Associate the new block with the paper
    associated_paper = await paper_service.associate_block_with_paper(prisma, paper_id, another_block_id)
    if associated_paper:
        print("Block Associated with Paper Successfully:")
        print(f"  Paper ID: {associated_paper.paper_id}")
        print(f"  Associated Block ID: {associated_paper.block.block_id}\n")
    else:
        print("Failed to associate block with paper.\n")

    # --------------------- Disassociate Block from Paper ---------------------
    print(">>> Disassociating Block from Paper...")
    disassociated_paper = await paper_service.disassociate_block_from_paper(prisma, paper_id)
    if disassociated_paper:
        print("Block Disassociated from Paper Successfully:")
        print(f"  Paper ID: {disassociated_paper.paper_id}")
        print("  Associated Block: None\n")
    else:
        print("Failed to disassociate block from paper.\n")

    # --------------------- Delete Paper ---------------------
    print(">>> Deleting Paper...")
    deletion_success = await paper_service.delete_paper(prisma, paper_id)
    if deletion_success:
        print(f"Paper with ID {paper_id} deleted successfully.\n")
    else:
        print("Failed to delete paper.\n")

    # --------------------- Confirm Deletion ---------------------
    print(">>> Confirming Deletion by Retrieving Paper Again...")
    post_deletion_paper = await paper_service.get_paper(prisma, paper_id, include_block=True)
    if post_deletion_paper:
        print("Paper still exists after deletion attempt.")
    else:
        print("Paper confirmed deleted.\n")

    # --------------------- Final List of Papers ---------------------
    print(">>> Final List of All Papers...")
    final_papers = await paper_service.list_papers(prisma, include_block=True)
    if final_papers is not None:
        print(f"Total Papers Found: {len(final_papers)}")
        for idx, paper in enumerate(final_papers, start=1):
            print(f"\nPaper {idx}:")
            print(f"  ID: {paper.paper_id}")
            print(f"  PDF URL: {paper.pdf_url}")
            print(f"  Title: {paper.title}")
            print(f"  Abstract: {paper.abstract}")
            print(f"  Created At: {paper.created_at}")
            print(f"  Updated At: {paper.updated_at}")
            if paper.block:
                print("  Associated Block:")
                print(f"    ID: {paper.block.block_id}")
                print(f"    Name: {paper.block.name}")
                print(f"    Type: {paper.block.block_type}")
                print(f"    Description: {paper.block.description}")
    else:
        print("Failed to retrieve papers.\n")

    # --------------------- Cleanup: Delete Blocks ---------------------
    print("\n>>> Cleaning Up: Deleting Created Blocks...")
    try:
        await prisma.block.delete(
            where={"block_id": str(block_id)}
        )
        await prisma.block.delete(
            where={"block_id": str(another_block_id)}
        )
        print("Blocks deleted successfully.\n")
    except Exception as e:
        print(f"Failed to delete blocks: {e}\n")

    # Disconnect Prisma client
    await prisma.disconnect()
    print("Disconnected from the database.")
    print("===== PaperService Test Completed =====")

if __name__ == "__main__":
    asyncio.run(main())