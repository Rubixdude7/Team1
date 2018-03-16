/*role inserts*/
insert into role values (1, 'admin');
insert into role values (2, 'staff');
insert into role values (3, 'psyc');
insert into role values (4, 'user');

/*day inserts*/
insert into day_typ_cd values ('m', 'Monday');
insert into day_typ_cd values ('t', 'Tuesday');
insert into day_typ_cd values ('w', 'Wednesday');
insert into day_typ_cd values ('th', 'Thursday');
insert into day_typ_cd values ('f', 'Friday');
insert into day_typ_cd values ('s', 'Saturday');
insert into day_typ_cd values ('su', 'Sunday');

/*fees*/
insert into consultation_fee (fee) values (500);

/*lengths*/
insert into consultation_length (length, cnslt_fee_id) values (1, 1);
insert into consultation_length (length, cnslt_fee_id) values (1.5, 1);
insert into consultation_length (length, cnslt_fee_id) values (2, 1);


