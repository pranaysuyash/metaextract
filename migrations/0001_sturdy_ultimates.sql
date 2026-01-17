CREATE TABLE "images_mvp_quotes" (
	"id" varchar PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"session_id" text NOT NULL,
	"user_id" varchar,
	"files" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"ops" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"credits_total" integer DEFAULT 0 NOT NULL,
	"per_file_credits" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"per_file" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"schedule" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"expires_at" timestamp NOT NULL,
	"used_at" timestamp,
	"status" varchar(20) DEFAULT 'active' NOT NULL
);
--> statement-breakpoint
ALTER TABLE "images_mvp_quotes" ADD CONSTRAINT "images_mvp_quotes_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;