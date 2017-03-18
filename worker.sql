/*
Navicat MySQL Data Transfer

Source Server         : local
Source Server Version : 50630
Source Host           : 192.168.25.131:3306
Source Database       : worker

Target Server Type    : MYSQL
Target Server Version : 50630
File Encoding         : 65001

Date: 2017-03-17 16:54:28
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for alembic_version
-- ----------------------------
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- ----------------------------
-- Records of alembic_version
-- ----------------------------
INSERT INTO `alembic_version` VALUES ('b9e258bbdf3d');

-- ----------------------------
-- Table structure for role
-- ----------------------------
DROP TABLE IF EXISTS `role`;
CREATE TABLE `role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  `description` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `description` (`description`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of role
-- ----------------------------
INSERT INTO `role` VALUES ('1', 'admin', '管理员');
INSERT INTO `role` VALUES ('2', 'teacher', '老师');
INSERT INTO `role` VALUES ('3', 'student', '学生');

-- ----------------------------
-- Table structure for role_user_relationship
-- ----------------------------
DROP TABLE IF EXISTS `role_user_relationship`;
CREATE TABLE `role_user_relationship` (
  `user_id` int(11) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  KEY `role_id` (`role_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `role_user_relationship_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`),
  CONSTRAINT `role_user_relationship_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- ----------------------------
-- Records of role_user_relationship
-- ----------------------------
INSERT INTO `role_user_relationship` VALUES ('1000', '1');

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varbinary(255) DEFAULT NULL,
  `phone` varchar(16) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `last_login_time` datetime DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `photo_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `phone` (`phone`)
) ENGINE=InnoDB AUTO_INCREMENT=1003 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES ('1000', 0x737570657261646D696E4071712E636F6D, '13800138000', 'superadmin', 'E10ADC3949BA59ABBE56E057F20F883E', '2017-03-17 11:12:41', '2017-03-17 10:25:32', 'profile_photo\\1000-f43d079e0add11e79215005056c00008.jpg');
