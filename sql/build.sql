CREATE TABLE `user` (
	`user_id` bigint NOT NULL AUTO_INCREMENT,
	`username` varchar(50) NOT NULL UNIQUE,
	`password` varchar(255) NOT NULL,
	`email` varchar(255) NOT NULL UNIQUE,
	`confirmed_at` DATETIME,
	`active` bool NOT NULL,
	`first_name` varchar(100) NOT NULL,
	`last_name` varchar(100),
	PRIMARY KEY (`user_id`)
);

CREATE TABLE `user_roles` (
	`user_role_id` bigint NOT NULL AUTO_INCREMENT,
	`user_id` bigint NOT NULL,
	`role_id` bigint NOT NULL,
	PRIMARY KEY (`user_role_id`)
);

CREATE TABLE `role` (
	`role_id` bigint NOT NULL,
	`role_nm` varchar(10) NOT NULL UNIQUE,
	PRIMARY KEY (`role_id`)
);

CREATE TABLE `child` (
	`child_id` bigint NOT NULL AUTO_INCREMENT,
	`user_id` bigint NOT NULL,
	`child_nm_fst` varchar(20) NOT NULL,
	`child_nm_lst` varchar(20),
	`child_dob` DATETIME NOT NULL,
	`q_comp_dtm` DATETIME,
	PRIMARY KEY (`child_id`)
);

CREATE TABLE `consultation` (
	`cnslt_id` bigint NOT NULL AUTO_INCREMENT,
	`child_id` bigint NOT NULL,
	`fee` double NOT NULL,
	`paid` varchar(1) NOT NULL DEFAULT 'n',
	`length` double NOT NULL,
	`link` varchar(2000),
	`finished` varchar(1) NOT NULL DEFAULT 'n',
	PRIMARY KEY (`cnslt_id`)
);

CREATE TABLE `consultation_fee` (
	`cnslt_fee_id` bigint NOT NULL AUTO_INCREMENT,
	`fee` double NOT NULL,
	`void_ind` varchar(1) NOT NULL DEFAULT 'n',
	PRIMARY KEY (`cnslt_fee_id`)
);

CREATE TABLE `consultation_length` (
	`cnslt_len_id` bigint NOT NULL AUTO_INCREMENT,
	`length` double NOT NULL UNIQUE,
	`void_ind` varchar(1) NOT NULL DEFAULT 'n',
	`cnslt_fee_id` bigint NOT NULL,
	PRIMARY KEY (`cnslt_len_id`)
);

CREATE TABLE `psychologist` (
	`psyc_id` bigint NOT NULL AUTO_INCREMENT,
	`user_id` bigint NOT NULL,
	`photo` varchar(1000) NOT NULL,
	`qualifications` varchar(1000) NOT NULL,
	PRIMARY KEY (`psyc_id`)
);

CREATE TABLE `calendar` (
	`cal_id` bigint NOT NULL AUTO_INCREMENT,
	`psyc_id` bigint NOT NULL,
	`time_st` TIME NOT NULL,
	`time_end` TIME NOT NULL,
	`day_typ_cd` varchar(2) NOT NULL,
	`void_ind` varchar(1) NOT NULL DEFAULT 'n',
	PRIMARY KEY (`cal_id`)
);

CREATE TABLE `consult_time` (
	`cnslt_tm_id` bigint NOT NULL AUTO_INCREMENT,
	`cnslt_id` bigint NOT NULL,
	`psyc_id` bigint NOT NULL,
	`time_st` DATETIME NOT NULL,
	`time_end` DATETIME NOT NULL,
	`approved` varchar(1),
	PRIMARY KEY (`cnslt_tm_id`)
);

CREATE TABLE `notes` (
	`note_id` bigint NOT NULL AUTO_INCREMENT,
	`cnslt_id` bigint NOT NULL,
	`note` varchar(400) NOT NULL,
	`user_id_crea` bigint NOT NULL,
	`crea_dtm` DATETIME NOT NULL,
	`user_id_upd` bigint,
	`updt_dtm` DATETIME,
	`void_ind` varchar(1) NOT NULL DEFAULT 'n',
	PRIMARY KEY (`note_id`)
);

CREATE TABLE `review` (
	`rev_id` bigint NOT NULL AUTO_INCREMENT,
	`cnslt_id` bigint NOT NULL,
	`review` varchar(2000) NOT NULL,
	`stars` double NOT NULL,
	`approved` varchar(1) NOT NULL DEFAULT 'n',
	`crea_dtm` DATETIME NOT NULL,
	`void_ind` varchar(1) NOT NULL DEFAULT 'n',
	PRIMARY KEY (`rev_id`)
);

CREATE TABLE `psychologist_child_xref` (
	`pcx_id` bigint NOT NULL AUTO_INCREMENT,
	`psyc_id` bigint NOT NULL,
	`child_id` bigint NOT NULL,
	PRIMARY KEY (`pcx_id`)
);

CREATE TABLE `blog` (
	`blog_id` bigint NOT NULL AUTO_INCREMENT,
	`psyc_id` bigint NOT NULL,
	`subject` varchar(100) NOT NULL,
	`text` varchar(2000) NOT NULL,
	`img_id` varchar(20),
	`img_ver` varchar(20),
	`crea_dtm` DATETIME NOT NULL,
	`user_id_upd` bigint,
	`updt_dtm` DATETIME,
	`void_ind` varchar(1) NOT NULL DEFAULT 'n',
	PRIMARY KEY (`blog_id`)
);

CREATE TABLE `day_typ_cd` (
	`day_tp_cd` char(2) NOT NULL,
	`day` varchar(12) NOT NULL,
	PRIMARY KEY (`day_tp_cd`)
);

CREATE TABLE `questions` (
	`q_id` bigint NOT NULL AUTO_INCREMENT,
	`question` varchar(2000) NOT NULL,
	`user_id_crea` bigint NOT NULL,
	`crea_dtm` DATETIME NOT NULL,
	`user_id_upd` bigint,
	`upd_dtm` DATETIME,
	`active` varchar(1) NOT NULL DEFAULT 'y',
	`void_ind` varchar(1) NOT NULL DEFAULT 'n',
	PRIMARY KEY (`q_id`)
);

CREATE TABLE `question_answers` (
	`qa_id` bigint NOT NULL AUTO_INCREMENT,
	`child_id` bigint NOT NULL,
	`q_id` bigint NOT NULL,
	`answer` varchar(2000) NOT NULL,
	`qa_crea_dtm` DATETIME NOT NULL,
	`qa_upt_dtm` DATETIME,
	`void_ind` varchar(1) NOT NULL DEFAULT 'n',
	PRIMARY KEY (`qa_id`)
);

CREATE TABLE `contact` (
	`contact_id` bigint NOT NULL AUTO_INCREMENT,
	`user_id` bigint NOT NULL,
	`phone_no` varchar(20) NOT NULL,
	`address_1` varchar(100) NOT NULL,
	`address_2` varchar(100),
	`city` varchar(100) NOT NULL,
	`providence` varchar(100),
	`zip` varchar(100),
	PRIMARY KEY (`contact_id`)
);

CREATE TABLE `vacation` (
	`vac_id` bigint NOT NULL AUTO_INCREMENT,
	`psyc_id` bigint NOT NULL,
	`vac_st` DATETIME NOT NULL,
	`vac_end` DATETIME NOT NULL,
	`annual` bool NOT NULL,
	PRIMARY KEY (`vac_id`)
);

CREATE TABLE `notification` (
	`not_id` bigint NOT NULL AUTO_INCREMENT,
	`user_id` bigint NOT NULL,
	`not_typ_cd` varchar(10) NOT NULL,
	`not_vars` varchar(2000),
	`not_st_dtm` DATETIME NOT NULL,
	`not_end_dtm` DATETIME NOT NULL,
	`dismissed` varchar(1) NOT NULL DEFAULT 'n',
	PRIMARY KEY (`not_id`)
);

CREATE TABLE `notification_type` (
	`not_typ_cd` varchar(10) NOT NULL,
	`not_typ` varchar(2000) NOT NULL,
	PRIMARY KEY (`not_typ_cd`)
);

ALTER TABLE `user_roles` ADD CONSTRAINT `user_roles_fk0` FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`);

ALTER TABLE `user_roles` ADD CONSTRAINT `user_roles_fk1` FOREIGN KEY (`role_id`) REFERENCES `role`(`role_id`);

ALTER TABLE `child` ADD CONSTRAINT `child_fk0` FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`);

ALTER TABLE `consultation` ADD CONSTRAINT `consultation_fk0` FOREIGN KEY (`child_id`) REFERENCES `child`(`child_id`);

ALTER TABLE `consultation_length` ADD CONSTRAINT `consultation_length_fk0` FOREIGN KEY (`cnslt_fee_id`) REFERENCES `consultation_fee`(`cnslt_fee_id`);

ALTER TABLE `psychologist` ADD CONSTRAINT `psychologist_fk0` FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`);

ALTER TABLE `calendar` ADD CONSTRAINT `calendar_fk0` FOREIGN KEY (`psyc_id`) REFERENCES `psychologist`(`psyc_id`);

ALTER TABLE `calendar` ADD CONSTRAINT `calendar_fk1` FOREIGN KEY (`day_typ_cd`) REFERENCES `day_typ_cd`(`day_tp_cd`);

ALTER TABLE `consult_time` ADD CONSTRAINT `consult_time_fk0` FOREIGN KEY (`cnslt_id`) REFERENCES `consultation`(`cnslt_id`);

ALTER TABLE `consult_time` ADD CONSTRAINT `consult_time_fk1` FOREIGN KEY (`psyc_id`) REFERENCES `psychologist`(`psyc_id`);

ALTER TABLE `notes` ADD CONSTRAINT `notes_fk0` FOREIGN KEY (`cnslt_id`) REFERENCES `consultation`(`cnslt_id`);

ALTER TABLE `review` ADD CONSTRAINT `review_fk0` FOREIGN KEY (`cnslt_id`) REFERENCES `consultation`(`cnslt_id`);

ALTER TABLE `psychologist_child_xref` ADD CONSTRAINT `psychologist_child_xref_fk0` FOREIGN KEY (`psyc_id`) REFERENCES `psychologist`(`psyc_id`);

ALTER TABLE `psychologist_child_xref` ADD CONSTRAINT `psychologist_child_xref_fk1` FOREIGN KEY (`child_id`) REFERENCES `child`(`child_id`);

ALTER TABLE `blog` ADD CONSTRAINT `blog_fk0` FOREIGN KEY (`psyc_id`) REFERENCES `psychologist`(`psyc_id`);

ALTER TABLE `question_answers` ADD CONSTRAINT `question_answers_fk0` FOREIGN KEY (`child_id`) REFERENCES `child`(`child_id`);

ALTER TABLE `question_answers` ADD CONSTRAINT `question_answers_fk1` FOREIGN KEY (`q_id`) REFERENCES `questions`(`q_id`);

ALTER TABLE `contact` ADD CONSTRAINT `contact_fk0` FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`);

ALTER TABLE `vacation` ADD CONSTRAINT `vacation_fk0` FOREIGN KEY (`psyc_id`) REFERENCES `psychologist`(`psyc_id`);

ALTER TABLE `notification` ADD CONSTRAINT `notification_fk0` FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`);

ALTER TABLE `notification` ADD CONSTRAINT `notification_fk1` FOREIGN KEY (`not_typ_cd`) REFERENCES `notification_type`(`not_typ_cd`);
