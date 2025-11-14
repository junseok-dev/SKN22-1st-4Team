-- ---------------------------------------------------
-- Lemon Scanner DB 테이블 생성 스크립트
-- ---------------------------------------------------

-- ---------------------------------------------------
-- 1. Brand (브랜드) 테이블
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS Brand (
    brand_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '브랜드ID (기본키)',
    brand_name VARCHAR(100) NOT NULL UNIQUE COMMENT '브랜드명 (예: 현대, 기아)'
) ENGINE=InnoDB COMMENT='브랜드 마스터 테이블';


-- ---------------------------------------------------
-- 2. Model (차종) 테이블
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS Model (
    model_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '차종ID (기본키)',
    brand_id INT NOT NULL COMMENT '브랜드ID (외래키)',
    model_name VARCHAR(100) NOT NULL COMMENT '차종명 (예: 소나타, K5)',
    
    FOREIGN KEY (brand_id) REFERENCES Brand(brand_id),
    UNIQUE KEY uk_brand_model (brand_id, model_name)
) ENGINE=InnoDB COMMENT='차종 마스터 테이블';


-- ---------------------------------------------------
-- 3. Keyword (키워드) 테이블 
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS Keyword (
    keyword_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '키워드ID (기본키)',
    keyword_text VARCHAR(100) NOT NULL UNIQUE COMMENT '키워드 (예: 엔진, 화재, 브레이크)',
    

    keyword_desc TEXT COMMENT '키워드 상세 설명'
    
) ENGINE=InnoDB COMMENT='리콜 사유 핵심 키워드';


-- ---------------------------------------------------
-- 4. Recall (리콜 내역) 테이블 (***원본***)
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS Recall (
    recall_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '리콜ID (기본키)',
    model_id INT NOT NULL COMMENT '차종ID (외래키)',
    
    reason TEXT COMMENT '리콜 사유 (원문)',
    prod_from DATE COMMENT '생산기간(부터)',
    prod_to DATE COMMENT '생산기간(까지)',
    recall_date DATE COMMENT '리콜 날짜 (개시일)',
    recall_count INT COMMENT '리콜 대수',
    correction_count INT COMMENT '시정 대수',
    correction_rate FLOAT COMMENT '시정률',
    
    FOREIGN KEY (model_id) REFERENCES Model(model_id)
) ENGINE=InnoDB COMMENT='리콜 상세 내역 (원본 데이터)';


-- ---------------------------------------------------
-- 5. Recall_Keyword_Junction (N:M 연결) 테이블
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS Recall_Keyword_Junction (
    recall_id INT NOT NULL COMMENT '리콜ID (외래키)',
    keyword_id INT NOT NULL COMMENT '키워드ID (외래키)',
    
    PRIMARY KEY (recall_id, keyword_id),
    FOREIGN KEY (recall_id) REFERENCES Recall(recall_id),
    FOREIGN KEY (keyword_id) REFERENCES Keyword(keyword_id)
) ENGINE=InnoDB COMMENT='리콜과 키워드 N:M 연결 테이블';
