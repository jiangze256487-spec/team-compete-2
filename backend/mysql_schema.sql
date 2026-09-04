-- =============================================================
-- 竞赛组队系统 · MySQL 表结构
-- 与后端 SQLAlchemy ORM（backend/app/models/*.py）严格一致
-- 字符集 utf8mb4，引擎 InnoDB
-- 执行前会先 DROP 同名旧表，请确认无重要数据后再执行
-- =============================================================
SET NAMES utf8mb4;

DROP TABLE IF EXISTS team_applications;
DROP TABLE IF EXISTS team_members;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS event_categories;
DROP TABLE IF EXISTS users;

-- 用户
CREATE TABLE users (
    id            INT           NOT NULL AUTO_INCREMENT,
    student_id    VARCHAR(32)   NOT NULL,
    name          VARCHAR(64)   NOT NULL,
    school        VARCHAR(128)  NOT NULL DEFAULT '',
    major         VARCHAR(128)  NOT NULL DEFAULT '',
    grade         VARCHAR(16)   NOT NULL DEFAULT '',
    password_hash VARCHAR(256)  NOT NULL,
    skills        VARCHAR(1024) NOT NULL DEFAULT '[]',
    attrs         VARCHAR(1024) NOT NULL DEFAULT '[]',
    phone         VARCHAR(32)   NOT NULL DEFAULT '',
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_student_id (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 赛事分类
CREATE TABLE event_categories (
    id   INT         NOT NULL AUTO_INCREMENT,
    name VARCHAR(64) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_event_categories_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 赛事
CREATE TABLE events (
    id         INT           NOT NULL AUTO_INCREMENT,
    name       VARCHAR(128)  NOT NULL,
    category   VARCHAR(64)   NOT NULL,
    org        VARCHAR(128)  NOT NULL DEFAULT '',
    `desc`     VARCHAR(2000) NOT NULL DEFAULT '',
    deadline   VARCHAR(64)   NOT NULL DEFAULT '',
    created_at DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_events_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 队伍
CREATE TABLE teams (
    id          INT           NOT NULL AUTO_INCREMENT,
    name        VARCHAR(128)  NOT NULL,
    leader_id   INT           NOT NULL,
    event_name  VARCHAR(64)   NOT NULL DEFAULT '',
    school      VARCHAR(128)  NOT NULL DEFAULT '',
    `desc`      VARCHAR(2000) NOT NULL DEFAULT '',
    status      VARCHAR(16)   NOT NULL DEFAULT '招募中',
    max_members INT           NOT NULL DEFAULT 4,
    tags        VARCHAR(1024) NOT NULL DEFAULT '[]',
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_teams_leader_id (leader_id),
    CONSTRAINT fk_teams_leader FOREIGN KEY (leader_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 队伍成员
CREATE TABLE team_members (
    id        INT        NOT NULL AUTO_INCREMENT,
    team_id   INT        NOT NULL,
    user_id   INT        NOT NULL,
    is_leader TINYINT(1) NOT NULL DEFAULT 0,
    joined_at DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_team_members_team_id (team_id),
    KEY idx_team_members_user_id (user_id),
    CONSTRAINT fk_team_members_team FOREIGN KEY (team_id) REFERENCES teams (id),
    CONSTRAINT fk_team_members_user FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 入队申请
CREATE TABLE team_applications (
    id         INT         NOT NULL AUTO_INCREMENT,
    team_id    INT         NOT NULL,
    user_id    INT         NOT NULL,
    status     VARCHAR(16) NOT NULL DEFAULT 'pending',
    created_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_team_applications_team_id (team_id),
    KEY idx_team_applications_user_id (user_id),
    CONSTRAINT fk_team_applications_team FOREIGN KEY (team_id) REFERENCES teams (id),
    CONSTRAINT fk_team_applications_user FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 通知
CREATE TABLE notifications (
    id          INT          NOT NULL AUTO_INCREMENT,
    user_id     INT          NOT NULL,
    type        VARCHAR(16)  NOT NULL DEFAULT 'team',
    title       VARCHAR(128) NOT NULL,
    content     VARCHAR(512) NOT NULL DEFAULT '',
    is_read     TINYINT(1)   NOT NULL DEFAULT 0,
    action_type VARCHAR(16)  NOT NULL DEFAULT '',
    related_id  INT          NOT NULL DEFAULT 0,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_notifications_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
