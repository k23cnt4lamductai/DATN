-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: banhngot
-- ------------------------------------------------------
-- Server version	8.0.35

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add Danh mục',7,'add_category'),(26,'Can change Danh mục',7,'change_category'),(27,'Can delete Danh mục',7,'delete_category'),(28,'Can view Danh mục',7,'view_category'),(29,'Can add Sản phẩm',8,'add_product'),(30,'Can change Sản phẩm',8,'change_product'),(31,'Can delete Sản phẩm',8,'delete_product'),(32,'Can view Sản phẩm',8,'view_product'),(33,'Can add Đơn hàng',9,'add_order'),(34,'Can change Đơn hàng',9,'change_order'),(35,'Can delete Đơn hàng',9,'delete_order'),(36,'Can view Đơn hàng',9,'view_order'),(37,'Can add Chi tiết đơn hàng',10,'add_orderitem'),(38,'Can change Chi tiết đơn hàng',10,'change_orderitem'),(39,'Can delete Chi tiết đơn hàng',10,'delete_orderitem'),(40,'Can view Chi tiết đơn hàng',10,'view_orderitem'),(41,'Can add Đánh giá',11,'add_review'),(42,'Can change Đánh giá',11,'change_review'),(43,'Can delete Đánh giá',11,'delete_review'),(44,'Can view Đánh giá',11,'view_review');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$1000000$EKNPWYtDIiahLEvkUKvKgB$M0VM+Q9yEK+MdCQo5pAxkAN2/QXriCUMJ/Zk3pfDCL0=','2026-11-12 06:50:15.611535',1,'Admin','','','',1,1,'2026-10-13 09:31:03.000000'),(2,'pbkdf2_sha256$1000000$vIu9L4ntOrPUcQuDjHLtAK$/tugDUBYw7yepHXMf9AadkrtOG5UOKc/M0tuGdvpaXw=','2026-11-14 06:19:37.680349',0,'TàiTZ','Lâm Đức Tài','','lamductai2005@gmail.com',0,1,'2026-11-09 06:41:46.141217');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2026-11-09 06:46:11.296941','11','bánh cupcake',1,'[{\"added\": {}}]',8,1),(2,'2026-11-09 06:46:46.111896','11','bánh cupcake',2,'[{\"changed\": {\"fields\": [\"H\\u00ecnh \\u1ea3nh\"]}}]',8,1),(3,'2026-11-09 06:48:51.307963','11','bánh cupcake',2,'[{\"changed\": {\"fields\": [\"S\\u1ed1 l\\u01b0\\u1ee3ng t\\u1ed3n\"]}}]',8,1),(4,'2026-11-09 06:49:11.063825','11','bánh cupcake',2,'[{\"changed\": {\"fields\": [\"Gi\\u00e1 (VN\\u0110)\"]}}]',8,1),(5,'2026-11-09 06:50:53.901712','1','Bánh trái cây',2,'[{\"changed\": {\"fields\": [\"T\\u00ean danh m\\u1ee5c\"]}}]',7,1),(6,'2026-11-12 06:30:55.065629','1','Admin',2,'[{\"changed\": {\"fields\": [\"Username\"]}}]',4,1),(7,'2026-11-12 06:50:39.343532','1','Đơn #1 - Tuấn',2,'[{\"changed\": {\"fields\": [\"Tr\\u1ea1ng th\\u00e1i\"]}}]',9,1),(8,'2026-11-12 06:51:32.289952','1','Đơn #1 - Tuấn',3,'',9,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(9,'orders','order'),(10,'orders','orderitem'),(7,'products','category'),(8,'products','product'),(11,'products','review'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-11-04 04:52:24.700898'),(2,'auth','0001_initial','2026-11-04 04:52:25.930087'),(3,'admin','0001_initial','2026-11-04 04:52:26.460821'),(4,'admin','0002_logentry_remove_auto_add','2026-11-04 04:52:26.477553'),(5,'admin','0003_logentry_add_action_flag_choices','2026-11-04 04:52:26.499097'),(6,'contenttypes','0002_remove_content_type_name','2026-11-04 04:52:26.674990'),(7,'auth','0002_alter_permission_name_max_length','2026-11-04 04:52:26.788591'),(8,'auth','0003_alter_user_email_max_length','2026-11-04 04:52:26.941913'),(9,'auth','0004_alter_user_username_opts','2026-11-04 04:52:26.960052'),(10,'auth','0005_alter_user_last_login_null','2026-11-04 04:52:27.078621'),(11,'auth','0006_require_contenttypes_0002','2026-11-04 04:52:27.083795'),(12,'auth','0007_alter_validators_add_error_messages','2026-11-04 04:52:27.191184'),(13,'auth','0008_alter_user_username_max_length','2026-11-04 04:52:27.310240'),(14,'auth','0009_alter_user_last_name_max_length','2026-11-04 04:52:27.418115'),(15,'auth','0010_alter_group_name_max_length','2026-11-04 04:52:27.444088'),(16,'auth','0011_update_proxy_permissions','2026-11-04 04:52:27.456564'),(17,'auth','0012_alter_user_first_name_max_length','2026-11-04 04:52:27.657773'),(18,'products','0001_initial','2026-11-04 04:52:27.954188'),(19,'products','0002_alter_category_id_alter_product_id','2026-11-04 04:52:28.889215'),(20,'orders','0001_initial','2026-11-04 04:52:29.435232'),(21,'sessions','0001_initial','2026-11-04 04:52:29.496774'),(22,'products','0003_review','2026-11-09 06:54:20.095260');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('ijtw9x7y3lg85jsxqqxzsuu5wkbrcrr2','.eJxVjjsOwyAQRO9CHSEDyy9lep8BLQvETiwjGbuKcvfEEkXSzpt5mhcLeOxTOFrewpzYlUl2-c0i0jOvJ0gPXO-VU133bY78rPBOGx9rysutd_8EE7bpuwavByBF0mpjDemkCGLSYJx1AK6UrLyQgy_kDRgpJAoSwlnjlRgintIF2x7qlvpT9f4AwyY8yA:1xS77E:HVu6GeWjlOCBeMJhmQUbk8o2UZYjIR0i_Ed3u4Kqreo','2026-11-28 06:19:56.187913');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders_order`
--

DROP TABLE IF EXISTS `orders_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders_order` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `full_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `address` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `note` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `delivery_date` date DEFAULT NULL,
  `payment_method` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(12) COLLATE utf8mb4_unicode_ci NOT NULL,
  `total` decimal(12,0) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `orders_order_user_id_e9b59eb1_fk_auth_user_id` (`user_id`),
  CONSTRAINT `orders_order_user_id_e9b59eb1_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders_order`
--

LOCK TABLES `orders_order` WRITE;
/*!40000 ALTER TABLE `orders_order` DISABLE KEYS */;
INSERT INTO `orders_order` VALUES (2,'Lâm Đức Tài','0338962005','lamductai2005@gmail.com','36 hà tĩnh','','2026-11-10','cod','pending',135000,'2026-11-09 06:42:32.205514','2026-11-09 06:42:32.223005',2),(3,'Lâm Đức Tài','0338962005','lamductai2005@gmail.com','36 hà tĩnh','',NULL,'cod','pending',18,'2026-11-14 06:19:56.156579','2026-11-14 06:19:56.178343',2);
/*!40000 ALTER TABLE `orders_order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders_orderitem`
--

DROP TABLE IF EXISTS `orders_orderitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders_orderitem` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `product_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `price` decimal(10,0) NOT NULL,
  `quantity` int unsigned NOT NULL,
  `order_id` bigint NOT NULL,
  `product_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `orders_orderitem_order_id_fe61a34d_fk_orders_order_id` (`order_id`),
  KEY `orders_orderitem_product_id_afe4254a_fk_products_product_id` (`product_id`),
  CONSTRAINT `orders_orderitem_order_id_fe61a34d_fk_orders_order_id` FOREIGN KEY (`order_id`) REFERENCES `orders_order` (`id`),
  CONSTRAINT `orders_orderitem_product_id_afe4254a_fk_products_product_id` FOREIGN KEY (`product_id`) REFERENCES `products_product` (`id`),
  CONSTRAINT `orders_orderitem_chk_1` CHECK ((`quantity` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders_orderitem`
--

LOCK TABLES `orders_orderitem` WRITE;
/*!40000 ALTER TABLE `orders_orderitem` DISABLE KEYS */;
INSERT INTO `orders_orderitem` VALUES (2,'Macaron hộp 6 cái',120000,1,2,10),(3,'Cookie socola chip',15000,1,2,9),(4,'bánh cam',18,1,3,1);
/*!40000 ALTER TABLE `orders_orderitem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products_category`
--

DROP TABLE IF EXISTS `products_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products_category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products_category`
--

LOCK TABLES `products_category` WRITE;
/*!40000 ALTER TABLE `products_category` DISABLE KEYS */;
INSERT INTO `products_category` VALUES (1,'Bánh trái cây','banh-trai-cay'),(2,'Bánh kem','banh-kem'),(3,'Bánh mì ngọt','banh-mi-ngot'),(4,'Bánh cupcake','banh-cupcake'),(5,'Bánh quy','banh-quy');
/*!40000 ALTER TABLE `products_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products_product`
--

DROP TABLE IF EXISTS `products_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products_product` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(220) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `price` decimal(10,0) NOT NULL,
  `image` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `stock` int unsigned NOT NULL,
  `is_available` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `category_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `products_product_category_id_9b594869_fk` (`category_id`),
  CONSTRAINT `products_product_category_id_9b594869_fk` FOREIGN KEY (`category_id`) REFERENCES `products_category` (`id`),
  CONSTRAINT `products_product_chk_1` CHECK ((`stock` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products_product`
--

LOCK TABLES `products_product` WRITE;
/*!40000 ALTER TABLE `products_product` DISABLE KEYS */;
INSERT INTO `products_product` VALUES (1,'bánh cam','banh-cam','',18,'',49,1,'2026-10-13 09:51:49.338527','2026-11-14 06:19:56.175994',1),(2,'Bánh kem dâu tây','banh-kem-dau-tay','Bánh bông lan mềm, kem tươi và dâu tây Đà Lạt.',350000,'',10,1,'2026-11-04 04:52:54.454715','2026-11-04 04:52:54.454785',2),(3,'Bánh kem socola','banh-kem-socola','Socola đen đậm vị, phủ ganache mịn.',380000,'',8,1,'2026-11-04 04:52:54.462594','2026-11-04 04:52:54.462631',2),(4,'Bánh kem trà xanh','banh-kem-tra-xanh','Vị matcha thanh nhẹ, ít ngọt.',360000,'',6,1,'2026-11-04 04:52:54.470294','2026-11-04 04:52:54.470333',2),(5,'Bánh mì bơ sữa','banh-mi-bo-sua','Mềm xốp, thơm mùi bơ sữa.',25000,'',40,1,'2026-11-04 04:52:54.486520','2026-11-04 04:52:54.486560',3),(6,'Bánh mì sữa tươi','banh-mi-sua-tuoi','Nhân kem sữa béo ngậy.',22000,'',40,1,'2026-11-04 04:52:54.492969','2026-11-04 04:52:54.492988',3),(7,'Cupcake vani','cupcake-vani','Cupcake vani phủ kem bơ.',30000,'',30,1,'2026-11-04 04:52:54.505238','2026-11-04 04:52:54.505264',4),(8,'Cupcake red velvet','cupcake-red-velvet','Red velvet với kem phô mai.',35000,'',25,1,'2026-11-04 04:52:54.512547','2026-11-04 04:52:54.512583',4),(9,'Cookie socola chip','cookie-socola-chip','Giòn rụm, nhiều socola chip.',15000,'',58,1,'2026-11-04 04:52:54.527167','2026-11-09 06:42:32.220547',5),(10,'Macaron hộp 6 cái','macaron-hop-6-cai','Macaron nhiều vị, đóng hộp quà.',120000,'',14,1,'2026-11-04 04:52:54.534472','2026-11-09 06:42:32.213371',5),(11,'bánh cupcake','banh-cupcake','',50001,'products/Screenshot_2026-08-23_195543.png',6,1,'2026-11-09 06:46:11.294406','2026-11-09 06:49:11.061772',4);
/*!40000 ALTER TABLE `products_product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products_review`
--

DROP TABLE IF EXISTS `products_review`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products_review` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rating` smallint unsigned NOT NULL,
  `comment` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_visible` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `product_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_review_per_user_product` (`product_id`,`user_id`),
  KEY `products_review_user_id_2e53b831_fk_auth_user_id` (`user_id`),
  CONSTRAINT `products_review_product_id_d933ffa7_fk_products_product_id` FOREIGN KEY (`product_id`) REFERENCES `products_product` (`id`),
  CONSTRAINT `products_review_user_id_2e53b831_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `products_review_chk_1` CHECK ((`rating` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products_review`
--

LOCK TABLES `products_review` WRITE;
/*!40000 ALTER TABLE `products_review` DISABLE KEYS */;
INSERT INTO `products_review` VALUES (1,4,'ngon',1,'2026-11-09 06:55:26.787255','2026-11-09 06:55:26.787297',10,2),(2,4,'ngon - rẻ',1,'2026-11-14 06:20:11.467132','2026-11-14 06:20:11.467168',1,2);
/*!40000 ALTER TABLE `products_review` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-14 13:52:56
