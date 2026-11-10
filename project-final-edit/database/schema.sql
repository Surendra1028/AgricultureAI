CREATE DATABASE IF NOT EXISTS smart_agriculture CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_agriculture;
CREATE TABLE IF NOT EXISTS users (
 id BIGINT PRIMARY KEY AUTO_INCREMENT,
 full_name VARCHAR(120) NOT NULL,
 email VARCHAR(190) NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS predictions (
 id BIGINT PRIMARY KEY AUTO_INCREMENT,
 user_id BIGINT NULL,
 module VARCHAR(60) NOT NULL,
 input_json JSON NOT NULL,
 result_json JSON NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 INDEX idx_predictions_user_created(user_id, created_at),
 CONSTRAINT fk_predictions_user FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);
