from prisma import Prisma
from prisma.models import (
    Block,
    Edge,
    Pipeline,
    PipelineBlock,
    PipelineEdge,
    BlockVector,
    Paper,
)

Block.create_partial("BlockBasicInfo", include=["name", "block_type", "description"])
Block.create_partial(
    "BlockBasicInfoWithID", include=["block_id", "name", "block_type", "description"]
)
Block.create_partial(
    "BlockUpdateInfo",
    include=["name", "block_type", "description"],
    optional=["name", "block_type", "description"],
)

Edge.create_partial("EdgeBasicInfo", include=["source_block_id", "target_block_id"])
Edge.create_partial(
    "EdgeUpdate",
    include=["source_block_id", "target_block_id"],
    optional=["source_block_id", "target_block_id"],
)
Edge.create_partial(
    "EdgeBasicInfoWithID", include=["edge_id", "source_block_id", "target_block_id"]
)

Pipeline.create_partial("PipelineBasicInfo", include=["name", "description", "user_id"])
Pipeline.create_partial(
    "PipelineBasicInfoWithID",
    include=[
        "pipeline_id",
        "name",
        "description",
        "user_id",
        "PipelineBlock",
        "PipelineEdge",
    ],
)

PipelineBlock.create_partial(
    "PipelineBlockBasicInfo", include=["pipeline_id", "block_id", "order"]
)
PipelineEdge.create_partial(
    "PipelineEdgeBasicInfo", include=["pipeline_id", "edge_id", "order"]
)

BlockVector.create_partial("BlockVectorContent", include=["content"])

Paper.create_partial("PaperBasicInfo", include=["pdf_url", "title", "abstract"])
