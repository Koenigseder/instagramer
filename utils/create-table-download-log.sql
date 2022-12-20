CREATE TABLE public."DownloadLog" (
	"uuid" TEXT PRIMARY KEY,
	"url" TEXT NOT NULL,
	"title" TEXT,
	"startedAt" TIMESTAMP NOT NULL,
	"finishedAt" TIMESTAMP,
	"downloadStatus" TEXT NOT NULL
);