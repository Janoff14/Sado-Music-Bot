import os
import psycopg2

def init_db():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")
    conn = psycopg2.connect(db_url)
    with conn.cursor() as cur:
        cur.execute("""
        BEGIN;
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id BIGINT PRIMARY KEY,
            lang TEXT DEFAULT 'uz',
            anonymous_default INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS artists (
            artist_id TEXT PRIMARY KEY,
            tg_user_id BIGINT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            payment_link TEXT,
            profile_url TEXT,
            default_genre TEXT,
            bio TEXT,
            created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS submissions (
            submission_id TEXT PRIMARY KEY,
            artist_id TEXT NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
            submitter_user_id BIGINT NOT NULL,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            caption TEXT,
            telegram_file_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING',
            admin_message_id BIGINT,
            created_at INTEGER NOT NULL,
            reviewed_at INTEGER
        );
        CREATE TABLE IF NOT EXISTS tracks (
            track_id TEXT PRIMARY KEY,
            artist_id TEXT NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            caption TEXT,
            telegram_file_id TEXT,
            channel_message_id BIGINT NOT NULL,
            discussion_anchor_message_id BIGINT DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS donation_events (
            donation_id TEXT PRIMARY KEY,
            track_id TEXT NOT NULL REFERENCES tracks(track_id) ON DELETE CASCADE,
            artist_id TEXT NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
            donor_user_id BIGINT,
            donor_name TEXT,
            donor_username TEXT,
            amount INTEGER NOT NULL,
            note TEXT,
            is_anonymous INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            confirmed_at INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_submissions_artist_id ON submissions(artist_id);
        CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
        CREATE INDEX IF NOT EXISTS idx_tracks_artist_id ON tracks(artist_id);
        CREATE INDEX IF NOT EXISTS idx_tracks_status ON tracks(status);
        CREATE INDEX IF NOT EXISTS idx_donations_track_id ON donation_events(track_id);
        CREATE INDEX IF NOT EXISTS idx_donations_artist_id ON donation_events(artist_id);
        CREATE INDEX IF NOT EXISTS idx_donations_status ON donation_events(status);
        COMMIT;
        """)
        conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("✅ Database tables initialized with foreign keys and indexes.")
