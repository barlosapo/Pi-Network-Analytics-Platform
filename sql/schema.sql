--blocklists storing the blocklist data, including the domain name and the reason
--created first to reference in the dns_queries table
create table blocklists(
	id serial primary key, 
	domain_name varchar(255) not null unique,
	reason varchar(255) not null,
	created_at timestamp default current_timestamp
);

--clients storing the device infomration, including the device name and IP address
create table clients(
	id serial primary key,
	device_name varchar(255) not null,
	ip_address inet not null unique,
	created_at timestamp default current_timestamp
);

--dns_queries storing the DNS query data, including the domain name, query type, and timestamp
create table dns_queries (
	id serial primary key,
	client_id integer references clients(id),
	domain_name varchar(255) not null,
	query_type varchar(10) not null,
	timestamp timestamp default current_timestamp,
	status varchar(20) not null default 'allowed',
	blocklist_id integer references blocklists(id)
);
