-- CreateExtension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";

-- CreateExtension
CREATE EXTENSION IF NOT EXISTS "vector" WITH SCHEMA "extensions";

-- CreateEnum
CREATE TYPE "action_type_enum" AS ENUM ('CREATE', 'READ', 'UPDATE', 'DELETE');

-- CreateEnum
CREATE TYPE "audit_entity_type_enum" AS ENUM ('block', 'edge', 'pipeline', 'taxonomy', 'metadata', 'user', 'api_key', 'code_repo', 'docker_image', 'verification');

-- CreateEnum
CREATE TYPE "block_type_enum" AS ENUM ('dataset', 'model');

-- CreateEnum
CREATE TYPE "build_status_enum" AS ENUM ('pending', 'success', 'failed');

-- CreateEnum
CREATE TYPE "dependency_type_enum" AS ENUM ('internal', 'external');

-- CreateEnum
CREATE TYPE "entity_type_enum" AS ENUM ('block', 'edge');

-- CreateEnum
CREATE TYPE "verification_status_enum" AS ENUM ('pending', 'passed', 'failed');

-- CreateTable
CREATE TABLE "alembic_version" (
    "version_num" VARCHAR(32) NOT NULL,

    CONSTRAINT "alembic_version_pkc" PRIMARY KEY ("version_num")
);

-- CreateTable
CREATE TABLE "api_keys" (
    "api_key_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "user_id" UUID NOT NULL,
    "encrypted_api_key" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "expires_at" TIMESTAMPTZ(6) NOT NULL,
    "is_active" BOOLEAN DEFAULT true,

    CONSTRAINT "api_keys_pkey" PRIMARY KEY ("api_key_id")
);

-- CreateTable
CREATE TABLE "audit_logs" (
    "log_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "user_id" UUID NOT NULL,
    "action_type" "action_type_enum" NOT NULL,
    "entity_type" "audit_entity_type_enum" NOT NULL,
    "entity_id" UUID NOT NULL,
    "timestamp" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "details" JSONB,

    CONSTRAINT "audit_logs_pkey" PRIMARY KEY ("log_id")
);

-- CreateTable
CREATE TABLE "block_categories" (
    "block_category_id" UUID NOT NULL,
    "block_id" UUID,
    "category_id" UUID,
    "created_at" TIMESTAMP(6) DEFAULT (now() AT TIME ZONE 'UTC'::text),

    CONSTRAINT "block_categories_pkey" PRIMARY KEY ("block_category_id")
);

-- CreateTable
CREATE TABLE "block_taxonomies" (
    "block_taxonomy_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "block_id" UUID NOT NULL,
    "category_id" UUID NOT NULL,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "block_taxonomies_pkey" PRIMARY KEY ("block_taxonomy_id")
);

-- CreateTable
CREATE TABLE "block_vector_representations" (
    "vector_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "block_id" UUID NOT NULL,
    "taxonomy_filter" JSONB,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "vector" vector,

    CONSTRAINT "block_vector_representations_pkey" PRIMARY KEY ("vector_id")
);

-- CreateTable
CREATE TABLE "block_versions" (
    "version_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "block_id" UUID NOT NULL,
    "version_number" INTEGER NOT NULL,
    "metadata" JSONB,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "is_active" BOOLEAN DEFAULT true,

    CONSTRAINT "block_versions_pkey" PRIMARY KEY ("version_id")
);

-- CreateTable
CREATE TABLE "blocks" (
    "block_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR(255) NOT NULL,
    "block_type" "block_type_enum" NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "current_version_id" UUID,

    CONSTRAINT "blocks_pkey" PRIMARY KEY ("block_id")
);

-- CreateTable
CREATE TABLE "categories" (
    "category_id" UUID NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "parent_id" UUID,
    "created_at" TIMESTAMP(6) DEFAULT (now() AT TIME ZONE 'UTC'::text),
    "updated_at" TIMESTAMP(6) DEFAULT (now() AT TIME ZONE 'UTC'::text),

    CONSTRAINT "categories_pkey" PRIMARY KEY ("category_id")
);

-- CreateTable
CREATE TABLE "code_repos" (
    "repo_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "entity_type" "entity_type_enum" NOT NULL,
    "entity_id" UUID NOT NULL,
    "repo_url" VARCHAR(255) NOT NULL,
    "branch" VARCHAR(100) DEFAULT 'main',
    "last_updated" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "code_repos_pkey" PRIMARY KEY ("repo_id")
);

-- CreateTable
CREATE TABLE "dependencies" (
    "dependency_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "entity_type" "entity_type_enum" NOT NULL,
    "entity_id" UUID NOT NULL,
    "dependency_type" "dependency_type_enum" NOT NULL,
    "dependency_detail" TEXT NOT NULL,

    CONSTRAINT "dependencies_pkey" PRIMARY KEY ("dependency_id")
);

-- CreateTable
CREATE TABLE "docker_images" (
    "image_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "entity_type" "entity_type_enum" NOT NULL,
    "entity_id" UUID NOT NULL,
    "image_tag" VARCHAR(100) NOT NULL,
    "registry_url" VARCHAR(255) NOT NULL,
    "build_status" "build_status_enum" DEFAULT 'pending',
    "build_logs" TEXT,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "docker_images_pkey" PRIMARY KEY ("image_id")
);

-- CreateTable
CREATE TABLE "documents_v1" (
    "id" VARCHAR(128) NOT NULL,
    "embedding" vector,
    "content" TEXT,
    "dataframe" JSONB,
    "blob_data" BYTEA,
    "blob_meta" JSONB,
    "blob_mime_type" VARCHAR(255),
    "meta" JSONB,

    CONSTRAINT "documents_v1_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "documents_v2" (
    "internal_id" BIGSERIAL NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "paper_id" TEXT,
    "data" JSONB,

    CONSTRAINT "documents_v2_pkey" PRIMARY KEY ("internal_id")
);

-- CreateTable
CREATE TABLE "edge_vector_representations" (
    "vector_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "edge_id" UUID NOT NULL,
    "vector_db" VARCHAR(100) NOT NULL,
    "vector_key" VARCHAR(255) NOT NULL,
    "taxonomy_filter" JSONB,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "edge_vector_representations_pkey" PRIMARY KEY ("vector_id")
);

-- CreateTable
CREATE TABLE "edge_verifications" (
    "verification_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "edge_version_id" UUID NOT NULL,
    "verification_status" "verification_status_enum" DEFAULT 'pending',
    "verification_logs" TEXT,
    "verified_at" TIMESTAMPTZ(6),
    "verified_by" UUID,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "edge_verifications_pkey" PRIMARY KEY ("verification_id")
);

-- CreateTable
CREATE TABLE "edge_versions" (
    "version_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "edge_id" UUID NOT NULL,
    "version_number" INTEGER NOT NULL,
    "metadata" JSONB,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "is_active" BOOLEAN DEFAULT true,

    CONSTRAINT "edge_versions_pkey" PRIMARY KEY ("version_id")
);

-- CreateTable
CREATE TABLE "edges" (
    "edge_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "current_version_id" UUID,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "edge_type" VARCHAR(50) NOT NULL DEFAULT 'primary',
    "source_block_id" BIGINT,
    "target_block_id" BIGINT,

    CONSTRAINT "edges_pkey" PRIMARY KEY ("edge_id")
);

-- CreateTable
CREATE TABLE "pipeline_blocks" (
    "pipeline_block_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "pipeline_id" UUID NOT NULL,
    "block_id" UUID NOT NULL,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pipeline_blocks_pkey" PRIMARY KEY ("pipeline_block_id")
);

-- CreateTable
CREATE TABLE "pipeline_edges" (
    "pipeline_edge_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "pipeline_id" UUID NOT NULL,
    "edge_id" UUID NOT NULL,
    "source_block_id" UUID NOT NULL,
    "target_block_id" UUID NOT NULL,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pipeline_edges_pkey" PRIMARY KEY ("pipeline_edge_id")
);

-- CreateTable
CREATE TABLE "pipelines" (
    "pipeline_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "dagster_pipeline_config" JSONB,
    "created_by" UUID NOT NULL,
    "times_run" INTEGER DEFAULT 0,
    "average_runtime" DOUBLE PRECISION DEFAULT 0.0,

    CONSTRAINT "pipelines_pkey" PRIMARY KEY ("pipeline_id")
);

-- CreateTable
CREATE TABLE "taxonomy_categories" (
    "category_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "name" VARCHAR(255) NOT NULL,
    "parent_id" UUID,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "taxonomy_categories_pkey" PRIMARY KEY ("category_id")
);

-- CreateTable
CREATE TABLE "users" (
    "user_id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "username" VARCHAR(150) NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "password_hash" VARCHAR(255) NOT NULL,
    "role" VARCHAR(50) NOT NULL,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "users_pkey" PRIMARY KEY ("user_id")
);

-- CreateTable
CREATE TABLE "vector_representations" (
    "vector_id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "entity_type" TEXT NOT NULL,
    "entity_id" UUID NOT NULL,
    "vector" vector NOT NULL,
    "taxonomy_filter" JSONB,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "vector_representations_pkey" PRIMARY KEY ("vector_id")
);

-- CreateIndex
CREATE INDEX "idx_block_categories_block_id" ON "block_categories"("block_id");

-- CreateIndex
CREATE INDEX "idx_block_categories_category_id" ON "block_categories"("category_id");

-- CreateIndex
CREATE UNIQUE INDEX "block_taxonomies_block_id_category_id_key" ON "block_taxonomies"("block_id", "category_id");

-- CreateIndex
CREATE INDEX "idx_block_vectors_vector" ON "block_vector_representations"("vector");

-- CreateIndex
CREATE UNIQUE INDEX "block_versions_block_id_version_number_key" ON "block_versions"("block_id", "version_number");

-- CreateIndex
CREATE UNIQUE INDEX "blocks_name_key" ON "blocks"("name");

-- CreateIndex
CREATE INDEX "idx_categories_name" ON "categories"("name");

-- CreateIndex
CREATE UNIQUE INDEX "docker_images_entity_id_image_tag_key" ON "docker_images"("entity_id", "image_tag");

-- CreateIndex
CREATE INDEX "haystack_hnsw_index" ON "documents_v1"("embedding");

-- CreateIndex
CREATE UNIQUE INDEX "edge_versions_edge_id_version_number_key" ON "edge_versions"("edge_id", "version_number");

-- CreateIndex
CREATE UNIQUE INDEX "edges_name_key" ON "edges"("name");

-- CreateIndex
CREATE INDEX "idx_edges_edge_id" ON "edges"("edge_id");

-- CreateIndex
CREATE INDEX "idx_edges_source" ON "edges"("source_block_id");

-- CreateIndex
CREATE INDEX "idx_edges_target" ON "edges"("target_block_id");

-- CreateIndex
CREATE UNIQUE INDEX "pipeline_blocks_pipeline_id_block_id_key" ON "pipeline_blocks"("pipeline_id", "block_id");

-- CreateIndex
CREATE UNIQUE INDEX "pipeline_edges_pipeline_id_edge_id_key" ON "pipeline_edges"("pipeline_id", "edge_id");

-- CreateIndex
CREATE UNIQUE INDEX "pipelines_name_key" ON "pipelines"("name");

-- CreateIndex
CREATE UNIQUE INDEX "users_username_key" ON "users"("username");

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE INDEX "idx_vector_representations_vector" ON "vector_representations"("vector");

-- AddForeignKey
ALTER TABLE "api_keys" ADD CONSTRAINT "api_keys_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("user_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "audit_logs" ADD CONSTRAINT "audit_logs_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("user_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "block_categories" ADD CONSTRAINT "block_categories_block_id_fkey" FOREIGN KEY ("block_id") REFERENCES "blocks"("block_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "block_categories" ADD CONSTRAINT "block_categories_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "categories"("category_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "block_taxonomies" ADD CONSTRAINT "block_taxonomies_block_id_fkey" FOREIGN KEY ("block_id") REFERENCES "blocks"("block_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "block_taxonomies" ADD CONSTRAINT "block_taxonomies_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "taxonomy_categories"("category_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "block_vector_representations" ADD CONSTRAINT "block_vector_representations_block_id_fkey" FOREIGN KEY ("block_id") REFERENCES "blocks"("block_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "block_versions" ADD CONSTRAINT "block_versions_block_id_fkey" FOREIGN KEY ("block_id") REFERENCES "blocks"("block_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "block_versions" ADD CONSTRAINT "block_versions_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "users"("user_id") ON DELETE SET NULL ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "blocks" ADD CONSTRAINT "fk_blocks_current_version" FOREIGN KEY ("current_version_id") REFERENCES "block_versions"("version_id") ON DELETE SET NULL ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "categories" ADD CONSTRAINT "categories_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "categories"("category_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "edge_vector_representations" ADD CONSTRAINT "edge_vector_representations_edge_id_fkey" FOREIGN KEY ("edge_id") REFERENCES "edges"("edge_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "edge_verifications" ADD CONSTRAINT "edge_verifications_edge_version_id_fkey" FOREIGN KEY ("edge_version_id") REFERENCES "edge_versions"("version_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "edge_verifications" ADD CONSTRAINT "edge_verifications_verified_by_fkey" FOREIGN KEY ("verified_by") REFERENCES "users"("user_id") ON DELETE SET NULL ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "edge_versions" ADD CONSTRAINT "edge_versions_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "users"("user_id") ON DELETE SET NULL ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "edge_versions" ADD CONSTRAINT "edge_versions_edge_id_fkey" FOREIGN KEY ("edge_id") REFERENCES "edges"("edge_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "edges" ADD CONSTRAINT "fk_edges_current_version" FOREIGN KEY ("current_version_id") REFERENCES "edge_versions"("version_id") ON DELETE SET NULL ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "pipeline_blocks" ADD CONSTRAINT "pipeline_blocks_block_id_fkey" FOREIGN KEY ("block_id") REFERENCES "blocks"("block_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "pipeline_blocks" ADD CONSTRAINT "pipeline_blocks_pipeline_id_fkey" FOREIGN KEY ("pipeline_id") REFERENCES "pipelines"("pipeline_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "pipeline_edges" ADD CONSTRAINT "pipeline_edges_edge_id_fkey" FOREIGN KEY ("edge_id") REFERENCES "edges"("edge_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "pipeline_edges" ADD CONSTRAINT "pipeline_edges_pipeline_id_fkey" FOREIGN KEY ("pipeline_id") REFERENCES "pipelines"("pipeline_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "pipeline_edges" ADD CONSTRAINT "pipeline_edges_source_block_id_fkey" FOREIGN KEY ("source_block_id") REFERENCES "blocks"("block_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "pipeline_edges" ADD CONSTRAINT "pipeline_edges_target_block_id_fkey" FOREIGN KEY ("target_block_id") REFERENCES "blocks"("block_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "pipelines" ADD CONSTRAINT "pipelines_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "users"("user_id") ON DELETE SET NULL ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "taxonomy_categories" ADD CONSTRAINT "taxonomy_categories_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "taxonomy_categories"("category_id") ON DELETE SET NULL ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "vector_representations" ADD CONSTRAINT "fk_entity" FOREIGN KEY ("entity_id") REFERENCES "blocks"("block_id") ON DELETE CASCADE ON UPDATE NO ACTION;
