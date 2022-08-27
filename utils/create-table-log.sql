create table public."Log" (
	"uuid" text primary key,
	"url" text not null,
	"title" text,
	"startedAt" timestamp not null,
	"finishedAt" timestamp,
	"downloadStatus" text not null
)