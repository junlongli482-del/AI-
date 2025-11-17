-- MySQL dump 10.13  Distrib 8.4.7, for Win64 (x86_64)
--
-- Host: localhost    Database: user_system
-- ------------------------------------------------------
-- Server version	8.4.7

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `us_ai_optimizations`
--

DROP TABLE IF EXISTS `us_ai_optimizations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_ai_optimizations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `user_id` int NOT NULL,
  `original_content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `optimized_content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `optimization_prompt` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `ai_provider` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'default',
  `status` enum('pending','completed','failed') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'completed',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `us_ai_optimizations_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `us_editor_sessions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `us_ai_optimizations_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `us_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `us_ai_review_logs`
--

DROP TABLE IF EXISTS `us_ai_review_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_ai_review_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `document_id` int NOT NULL,
  `user_id` int NOT NULL,
  `review_type` enum('content_quality','content_safety','format_check','length_check') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ai_provider` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'default',
  `file_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `review_prompt` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ai_response` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `review_result` enum('pending','passed','failed','error') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'pending',
  `failure_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `confidence_score` decimal(3,2) DEFAULT NULL,
  `review_duration` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_document_id` (`document_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_review_result` (`review_result`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `us_ai_review_logs_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `us_documents` (`id`) ON DELETE CASCADE,
  CONSTRAINT `us_ai_review_logs_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `us_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=138 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `us_document_comments`
--

DROP TABLE IF EXISTS `us_document_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_document_comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `document_id` int NOT NULL,
  `user_id` int NOT NULL,
  `parent_id` int DEFAULT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_deleted` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_document_id` (`document_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `us_document_comments_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `us_documents` (`id`) ON DELETE CASCADE,
  CONSTRAINT `us_document_comments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `us_users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `us_document_comments_ibfk_3` FOREIGN KEY (`parent_id`) REFERENCES `us_document_comments` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `us_document_favorites`
--

DROP TABLE IF EXISTS `us_document_favorites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_document_favorites` (
  `id` int NOT NULL AUTO_INCREMENT,
  `document_id` int NOT NULL,
  `user_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_document_favorite` (`user_id`,`document_id`),
  KEY `idx_document_id` (`document_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `us_document_favorites_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `us_documents` (`id`) ON DELETE CASCADE,
  CONSTRAINT `us_document_favorites_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `us_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `us_document_interaction_stats`
--

DROP TABLE IF EXISTS `us_document_interaction_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_document_interaction_stats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `document_id` int NOT NULL,
  `like_count` int DEFAULT '0',
  `favorite_count` int DEFAULT '0',
  `comment_count` int DEFAULT '0',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `document_id` (`document_id`),
  KEY `idx_document_id` (`document_id`),
  CONSTRAINT `us_document_interaction_stats_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `us_documents` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `us_document_likes`
--

DROP TABLE IF EXISTS `us_document_likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_document_likes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `document_id` int NOT NULL,
  `user_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_document_like` (`user_id`,`document_id`),
  KEY `idx_document_id` (`document_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `us_document_likes_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `us_documents` (`id`) ON DELETE CASCADE,
  CONSTRAINT `us_document_likes_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `us_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `us_document_shares`
--

DROP TABLE IF EXISTS `us_document_shares`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_document_shares` (
  `id` int NOT NULL AUTO_INCREMENT,
  `document_id` int NOT NULL,
  `user_id` int NOT NULL,
  `share_code` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `share_type` enum('public','private','password') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'public',
  `share_password` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `allow_download` tinyint(1) DEFAULT '1',
  `allow_comment` tinyint(1) DEFAULT '1',
  `status` enum('active','expired','disabled') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `expire_time` datetime DEFAULT NULL,
  `view_count` int DEFAULT '0',
  `download_count` int DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `share_code` (`share_code`),
  KEY `idx_document_id` (`document_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_share_code` (`share_code`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `us_document_shares_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `us_documents` (`id`) ON DELETE CASCADE,
  CONSTRAINT `us_document_shares_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `us_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `us_documents`
--

DROP TABLE IF EXISTS `us_documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文档标题',
  `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '文档内容（MD格式）',
  `file_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '上传文件路径（如果是上传的文件）',
  `file_type` enum('md','pdf') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'md' COMMENT '文件类型',
  `file_size` int DEFAULT '0' COMMENT '文件大小（字节）',
  `summary` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '用户填写的简短摘要',
  `status` enum('draft','published','review_failed') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'draft' COMMENT '状态：草稿/已发布/审核失败',
  `publish_time` timestamp NULL DEFAULT NULL COMMENT '发布时间',
  `review_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT 'AI审核失败原因',
  `folder_id` int DEFAULT NULL COMMENT '所属文件夹ID',
  `user_id` int NOT NULL COMMENT '作者ID',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `pending_title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '待审核标题',
  `pending_content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '待审核内容',
  `pending_summary` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '待审核摘要',
  `has_pending_update` tinyint(1) DEFAULT '0' COMMENT '是否有待审核更新',
  `has_published_version` tinyint(1) DEFAULT '0' COMMENT '是否曾经发布过',
  PRIMARY KEY (`id`),
  KEY `folder_id` (`folder_id`),
  KEY `idx_user_folder` (`user_id`,`folder_id`),
  KEY `idx_status` (`status`),
  KEY `idx_publish_time` (`publish_time`),
  KEY `idx_documents_title_content` (`title`,`content`(100)),
  KEY `idx_documents_status_publish_time` (`status`,`publish_time` DESC),
  CONSTRAINT `us_documents_ibfk_1` FOREIGN KEY (`folder_id`) REFERENCES `us_folders` (`id`) ON DELETE SET NULL,
  CONSTRAINT `us_documents_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `us_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=110 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `us_editor_sessions`
--

DROP TABLE IF EXISTS `us_editor_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_editor_sessions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `document_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `is_draft` tinyint(1) DEFAULT '1',
  `session_type` enum('new_document','edit_document') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'new_document',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_document_id` (`document_id`),
  KEY `idx_session_type` (`session_type`),
  CONSTRAINT `us_editor_sessions_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `us_documents` (`id`) ON DELETE CASCADE,
  CONSTRAINT `us_editor_sessions_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `us_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=153 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `us_folders`
--

DROP TABLE IF EXISTS `us_folders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_folders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文件夹名称',
  `parent_id` int DEFAULT NULL COMMENT '父文件夹ID，NULL表示根目录',
  `user_id` int NOT NULL COMMENT '所属用户ID',
  `level` tinyint DEFAULT '1' COMMENT '层级：1-根目录，2-一级，3-二级',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  KEY `idx_user_parent` (`user_id`,`parent_id`),
  KEY `idx_level` (`level`),
  CONSTRAINT `us_folders_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `us_folders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `us_folders_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `us_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `us_publish_history`
--

DROP TABLE IF EXISTS `us_publish_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_publish_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `publish_record_id` int NOT NULL,
  `document_id` int NOT NULL,
  `user_id` int NOT NULL,
  `action_type` enum('submit','approve','reject','publish','unpublish','edit') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `old_status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `new_status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `operator_id` int DEFAULT NULL,
  `action_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `operator_id` (`operator_id`),
  KEY `idx_publish_record_id` (`publish_record_id`),
  KEY `idx_document_id` (`document_id`),
  KEY `idx_action_time` (`action_time`),
  CONSTRAINT `us_publish_history_ibfk_1` FOREIGN KEY (`publish_record_id`) REFERENCES `us_publish_records` (`id`) ON DELETE CASCADE,
  CONSTRAINT `us_publish_history_ibfk_2` FOREIGN KEY (`document_id`) REFERENCES `us_documents` (`id`) ON DELETE CASCADE,
  CONSTRAINT `us_publish_history_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `us_users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `us_publish_history_ibfk_4` FOREIGN KEY (`operator_id`) REFERENCES `us_users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=238 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `us_publish_records`
--

DROP TABLE IF EXISTS `us_publish_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_publish_records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `document_id` int NOT NULL,
  `user_id` int NOT NULL,
  `publish_version` int DEFAULT '1',
  `publish_status` enum('draft','pending_review','review_passed','review_failed','published','unpublished') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'draft',
  `publish_time` timestamp NULL DEFAULT NULL,
  `unpublish_time` timestamp NULL DEFAULT NULL,
  `publish_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `unpublish_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `review_id` int DEFAULT NULL,
  `view_count` int DEFAULT '0',
  `is_featured` tinyint(1) DEFAULT '0',
  `publish_config` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_document_id` (`document_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_publish_status` (`publish_status`),
  KEY `idx_publish_time` (`publish_time`),
  KEY `idx_publish_records_status_time` (`publish_status`,`publish_time` DESC),
  KEY `idx_publish_records_view_count` (`view_count` DESC),
  CONSTRAINT `us_publish_records_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `us_documents` (`id`) ON DELETE CASCADE,
  CONSTRAINT `us_publish_records_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `us_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `us_review_rules`
--

DROP TABLE IF EXISTS `us_review_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_review_rules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rule_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `rule_type` enum('length_limit','format_check','content_policy','quality_standard') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `rule_config` json NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `priority` int DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rule_name` (`rule_name`),
  KEY `idx_rule_type` (`rule_type`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `us_share_access_logs`
--

DROP TABLE IF EXISTS `us_share_access_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_share_access_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `share_id` int NOT NULL,
  `visitor_ip` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `visitor_user_agent` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `visitor_user_id` int DEFAULT NULL,
  `access_type` enum('VIEW','DOWNLOAD','COMMENT') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `access_result` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'success',
  `accessed_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_share_id` (`share_id`),
  KEY `idx_visitor_user_id` (`visitor_user_id`),
  KEY `idx_access_type` (`access_type`),
  KEY `idx_accessed_at` (`accessed_at`),
  CONSTRAINT `us_share_access_logs_ibfk_1` FOREIGN KEY (`share_id`) REFERENCES `us_document_shares` (`id`) ON DELETE CASCADE,
  CONSTRAINT `us_share_access_logs_ibfk_2` FOREIGN KEY (`visitor_user_id`) REFERENCES `us_users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `us_upload_records`
--

DROP TABLE IF EXISTS `us_upload_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_upload_records` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '上传记录ID',
  `original_filename` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '原始文件名',
  `stored_filename` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '存储文件名',
  `file_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文件存储路径',
  `file_size` int NOT NULL COMMENT '文件大小(字节)',
  `file_type` enum('md','pdf') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文件类型',
  `mime_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'MIME类型',
  `status` enum('uploading','uploaded','validated','failed','deleted') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'uploading' COMMENT '文件状态',
  `validation_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '验证结果信息',
  `user_id` int NOT NULL COMMENT '上传用户ID',
  `document_id` int DEFAULT NULL COMMENT '关联文档ID',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `document_id` (`document_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_file_type` (`file_type`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `us_upload_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `us_users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `us_upload_records_ibfk_2` FOREIGN KEY (`document_id`) REFERENCES `us_documents` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件上传记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `us_users`
--

DROP TABLE IF EXISTS `us_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `us_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '用户昵称',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_us_users_username` (`username`),
  UNIQUE KEY `ix_us_users_email` (`email`),
  UNIQUE KEY `idx_nickname` (`nickname`),
  KEY `ix_us_users_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'user_system'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-14  8:54:42
