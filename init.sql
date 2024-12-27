-- Таблица mentors
create table mentors (
    id uuid primary key,
    telegram_id varchar not null,
    name varchar not null,
    info varchar not null
);

-- Таблица mentor_time
create table mentor_time (
    id uuid primary key,
    day integer not null,
    time_start time not null,
    time_end time not null,
    mentor_id UUID references mentors(id),
    foreign key (mentor_id) references mentors(id) on delete cascade
);

-- Таблица requests
create table requests (
    id uuid primary key,
    call_type boolean not null,
    time_sended timestamp not null default current_timestamp,
    mentor_id UUID references mentors(id),
    foreign key (mentor_id) references mentors(id) on delete cascade,
    guest_id uuid not null,
    description varchar not null,
    call_time timestamp,
    response integer not null default 0
);

