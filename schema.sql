drop table if exists ideas;
drop table if exists votes;
create table ideas (
  id integer primary key autoincrement,
  description text not null,
  fullname text not null,
  email text not null,
  department text not null,
  votes integer
);
create table votes(
  id integer primary key autoincrement,
  ipaddress text not null
  idea integer not null
);
