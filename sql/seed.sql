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

/*notification types*/
insert into notification_type (not_typ_cd, not_typ) values ('appt_st_u', '%s''s appointment starts at %s, check your email for video conference link.');
insert into notification_type (not_typ_cd, not_typ) values ('appt_st_p', 'Your appointment with %s starts at %s, check your email for video conference link.');
insert into notification_type (not_typ_cd, not_typ) values ('appt_req_u', 'Your request for %s''s appointment has been accepted, contact office staff for payment.');
insert into notification_type (not_typ_cd, not_typ) values ('appt_req_p', '%s has scheduled an appointment with you on %s for %s.');
insert into notification_type (not_typ_cd, not_typ) values ('appt_pment', 'Your payment of %s is due by %s for %s''s appointment.');
insert into notification_type (not_typ_cd, not_typ) values ('pment_u_a', 'The payment for %s''s appointment has been successfully processed.');
insert into notification_type (not_typ_cd, not_typ) values ('pment_u_d', 'The appointment for %s has been denied.');
insert into notification_type (not_typ_cd, not_typ) values ('pfile_comp', 'You need to complete your profile.');


