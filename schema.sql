drop table if exists deadline;
create table deadline (
    id integer primary key autoincrement,
    name string not null,
    deadline datetime not null,
    created datetime not null
);
