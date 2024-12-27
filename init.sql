-- Таблица mentors
create table mentors (
    id uuid primary key,
    telegram_id text not null unique
    name text not null,
);

-- Таблица mentor_time
create table mentor_time (
    id uuid primary key,
    day integer not null,
    time_start time not null,
    time_end time not null,
    foreign key (mentor_id) references mentors(id) on delete cascade
);

-- Таблица requests
create table requests (
    id uuid primary key,
    call_type boolean not null,
    time_sended timestamp not null default current_timestamp,
    foreign key (mentor_id) references mentors(id) on delete cascade,
    guest_id uuid not null,
    description text not null,
    call_time timestamp,
    response integer not null default 0
);

