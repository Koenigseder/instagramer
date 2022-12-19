CREATE TABLE public."PostLog" (
	"uuid" TEXT PRIMARY KEY,
	"startedAt" TIMESTAMP NOT NULL,
	"finishedAt" TIMESTAMP,
	"postStatus" TEXT NOT NULL,
	"errorMsg" TEXT
);