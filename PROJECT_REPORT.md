# Sado Music Bot Project Documentation

## Overview
Sado Music Bot is a Telegram bot built with Aiogram v3 and SQLite (via aiosqlite) for managing artist profiles, track submissions, donations, and admin review workflows. The project is modular, with clear separation between music, donations, and admin logic.

---

## Project Structure

```
SadoMusicBot/
├── main.py                  # (Legacy) Main entry point, handlers, and command setup
├── run_bot.py               # (Optional) Script to run the bot
├── requirements.txt         # Python dependencies
├── sado_music_bot/
│   ├── __init__.py
│   ├── app.py               # Modern main entry point (async, aiogram v3)
│   ├── config.py            # Configuration loading and management
│   ├── db.py                # Database access and models
│   ├── keyboards.py         # Inline and reply keyboard definitions
│   ├── texts.py             # Text templates for messages
│   ├── admin/
│   │   ├── __init__.py
│   │   └── handlers.py      # Admin review/approval logic
│   ├── donations/
│   │   ├── __init__.py
│   │   ├── handlers.py      # Donation flow logic
│   │   └── states.py        # FSM states for donations
│   └── music/
│       ├── __init__.py
│       └── handlers.py      # User-facing music/artist/profile logic
├── bot_output.log           # Log file
├── bot.db / sado.db         # SQLite database files
├── start_bot.bat            # Windows batch file to start the bot
└── __pycache__/             # Python bytecode cache
```

---

## Main Components

### 1. Entry Points
- **main.py**: Contains legacy synchronous bot logic and command setup. New development should use `sado_music_bot/app.py`.
- **sado_music_bot/app.py**: Modern async entry point using Aiogram v3. Loads config, initializes DB, sets up routers, and starts polling.

### 2. Configuration
- **sado_music_bot/config.py**: Loads environment variables and config (token, DB path, admin ID, etc). Use `load_config()` to get a `Config` object.
- **.env**: Store sensitive data (bot token, DB path, etc). Copy `.env.example` and fill in your values.

### 3. Database
- **sado_music_bot/db.py**: Handles all SQLite operations (artists, tracks, users, donations). Use the `DB` class for async DB access.
- **bot.db / sado.db**: SQLite database files. Do not edit manually.

### 4. Handlers & Routers
- **music/handlers.py**: User commands (`/start`, `/profile`, track submission, artist profile deep links, etc).
- **donations/handlers.py**: Donation flows, payment links, and related FSM states.
- **admin/handlers.py**: Admin review, approval, and posting to channels.

### 5. Keyboards & Texts
- **keyboards.py**: Inline and reply keyboard markup for all flows.
- **texts.py**: Message templates for tracks, profiles, donations, etc.

---

## How to Add or Edit Features

### Adding a New Command
1. Define a handler function in the appropriate module (e.g., `music/handlers.py`).
2. Register the handler with the router (e.g., `@router.message(Command("newcommand"))`).
3. Add the command to the bot menu in `main.py` or `app.py` (see `setup_bot_commands`).

### Editing Database Models
- Update the schema in `db.py` and add migration logic if needed.
- Update related handler logic to use new/changed fields.
- Be careful: Changing DB schema may break existing data. Always back up the DB first.

### Adding a New Keyboard
- Define a new function in `keyboards.py` returning the desired markup.
- Import and use it in your handler.

### Adding/Editing Text Templates
- Edit or add functions in `texts.py`.
- Use these functions in handlers to keep text consistent and translatable.

### Adding a New FSM State
- Define a new `StatesGroup` in the relevant module (e.g., `donations/states.py`).
- Use it in handlers with Aiogram's FSMContext.

---

## Best Practices & Things to Be Careful With
- **Bot Token**: Never commit your real bot token. Use `.env` and `.gitignore`.
- **Database**: Always back up before making schema changes.
- **Async**: Use async/await everywhere in new code (see `app.py`).
- **Routers**: Register routers in the correct order (admin > donations > music) to avoid handler conflicts.
- **Deep Links**: When generating links to profiles or tracks, use `/profile @artist_title` or `/profile artist_<id>` as needed.
- **Testing**: Test all endpoints after changes. Use a test group/channel for posting.
- **Error Handling**: Always handle exceptions in handlers to avoid bot crashes.
- **Dependencies**: Update `requirements.txt` if you add new packages.

---

## How to Run the Bot
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in your values.
3. Run the bot:
   - For legacy: `python main.py`
   - For modern/async: `python -m sado_music_bot.app`
   - Or use `start_bot.bat` on Windows

---

## How to Test Endpoints
- Use Telegram to interact with the bot for all commands and flows.
- For channel posting, ensure the bot is admin in the target channels.
- Check logs in `bot_output.log` for errors.

---

## Adding a New Module
1. Create a new folder under `sado_music_bot/` (e.g., `events/`).
2. Add `__init__.py` and your handler files.
3. Register the new router in `app.py`.

---

## Common Pitfalls
- Forgetting to register new handlers/routers.
- Not updating the command menu after adding commands.
- Breaking DB schema without migration.
- Hardcoding sensitive data (always use `.env`).
- Not handling exceptions in async handlers.

---

## Contact & Support
For questions, contact the original author or check the code comments for guidance.

---

*Last updated: January 19, 2026*

