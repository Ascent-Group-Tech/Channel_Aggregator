# Channel Aggregator

A Telegram userbot that monitors a source channel for product listings, extracts pricing information, applies markup, and republishes to a target channel while maintaining synchronization across edits and deletions.

## Project Overview

Channel Aggregator automates the aggregation of product listings from Telegram channels. It captures messages from a donor channel, validates them as products using regex pattern matching for pricing, applies a configurable markup percentage, and forwards the modified listings to a target channel. All message relationships are tracked in a local SQLite database to handle real-time synchronization of edits and deletions.

## Stack

- **Telegram Client**: [Hydrogram](https://github.com/hydrogram/hydrogram) (async Pyrogram fork)
- **Database**: SQLAlchemy ORM with SQLite
- **Runtime**: Python 3.8+
- **Utilities**: python-dotenv for environment configuration

## Project Structure

```
Channel_Aggregator/
├── config.py                 # Environment variable loader
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Configuration template
├── .gitignore               # Git exclusions (*.session, .env, *.db)
│
├── core/
│   └── client.py            # Telegram userbot client wrapper
│
├── database/
│   ├── database.py          # SQLAlchemy engine, session factory, Base model
│   ├── models.py            # ORM models (Pairs table)
│   └── db_handler.py        # Database operations (CRUD functions)
│
├── logic/
│   └── parser.py            # Message parsing and pricing extraction
│
└── handlers/
    └── sync_handlers.py     # Event handlers for message lifecycle
```

## Core Components

### Configuration (`config.py`)

Loads environment variables from `.env` using `python-dotenv`. Validates required keys:
- `API_ID`, `API_HASH` - Telegram API credentials (obtain from [my.telegram.org](https://my.telegram.org))
- `SOURCE_CHANNEL` - Donor channel ID or username
- `TARGET_CHANNEL` - Target channel ID or username

All variables are accessible globally throughout the application.

### Entry Point (`main.py`)

1. Initializes SQLite database schema using SQLAlchemy
2. Starts the userbot and connects to Telegram
3. Calls `catch_up_history()` to process historical messages from the source channel
4. Enters idle state, listening for real-time events via event handlers
5. Handles graceful shutdown with error logging

### Telegram Client (`core/client.py`)

Wrapper class `UserBot` encapsulating Hydrogram's `Client`. Key methods:

- **`start()`** - Authenticates with Telegram API
- **`stop()`** - Gracefully disconnects
- **`safe_send(chat_id, text, **kwargs)`** - Sends messages with automatic retry on FloodWait errors
- **`safe_send_album(chat_id, messages, caption)`** - Sends grouped media (photos/videos) with new caption
- **`safe_edit(chat_id, msg_id, text)`** - Edits message text
- **`safe_delete(chat_id, msg_id)`** - Deletes message

All methods implement error handling for:
- `FloodWait` - Telegram rate limiting (auto-retry with exponential backoff)
- `PeerIdInvalid` - Invalid chat/channel IDs
- `MessageIdInvalid` - Non-existent messages
- `Unauthorized` - Session expiration

### Parser (`logic/parser.py`)

Extracts and validates product pricing using regex patterns.

**Supported currencies**:
- 💲, 💵 → USD
- ₴ → UAH

**Price pattern**: `[emoji]\s*[number with optional spaces/decimals]`

**Validation rules**:
- Must contain exactly one price (rejects no price or price ranges like "💲100-200")
- Price must be positive
- Message length must exceed minimum threshold (default: 1 character)
- Markup applied: `final_price = price × (1 + markup_percent / 100)`

**Returns** `ParsedMessage` dataclass with:
- `is_product` - Boolean validity
- `price` - Extracted price
- `currency` - Currency code
- `final_price` - Price with markup, rounded to 2 decimals
- `emoji` - Original currency emoji
- `original_substring` - Matched price string (e.g., "₴ 100")

### Database

#### Schema (`database/models.py`)

Single table `Pairs` tracking message relationships:
```sql
CREATE TABLE pairs (
  id INTEGER PRIMARY KEY,
  source_msg_id INTEGER UNIQUE,      -- Message ID in source channel
  target_msg_id INTEGER UNIQUE,      -- Message ID in target channel
  last_updated DATETIME DEFAULT now,
  is_deleted BOOLEAN DEFAULT false
);
```

#### Engine Setup (`database/database.py`)

- **Database**: SQLite at project root (`app.db`)
- **Session management**: Context manager `get_db()` for automatic connection pooling and error handling
- **ORM**: SQLAlchemy declarative base for model definitions

#### Operations (`database/db_handler.py`)

- **`save_pair(source_id, target_id)`** - Records new message mapping
- **`get_my_id_by_original(source_id)`** - Retrieves target message ID by source message ID
- **`delete_pair(source_id)`** - Marks/removes message relationship
- **`get_last_seen_source_id()`** - Returns highest source message ID for catch-up logic

### Event Handlers (`handlers/sync_handlers.py`)

Three async handlers listening to source channel events:

#### 1. `handle_new_post()` - `@app.on_message()`

- Parses message text/caption
- Validates as product using `parse_message()`
- Updates caption with new price
- Forwards to target channel
- Records source→target message IDs in database

#### 2. `handle_edit_post()` - `@app.on_edited_message()`

- Looks up target message ID via source message ID
- Re-parses edited text
- Updates target message caption if still valid product
- Keeps database mappings intact

#### 3. `handle_delete_post()` - `@app.on_deleted_messages()`

- Retrieves target message ID for each deleted source message
- Deletes corresponding target message
- Removes database pair record

## Getting Started

### Prerequisites

- Python 3.8+
- Telegram account with API credentials from [my.telegram.org](https://my.telegram.org)
- Access to at least two Telegram channels (source and target)

### Setup

1. **Clone and navigate**:
   ```bash
   git clone https://github.com/Ascent-Group-Tech/Channel_Aggregator.git
   cd Channel_Aggregator
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Activate
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials:
   # - API_ID and API_HASH from my.telegram.org
   # - SOURCE_CHANNEL and TARGET_CHANNEL usernames or IDs
   # - PERCENT_MARKUP (optional, default: 15%)
   ```

5. **Run**:
   ```bash
   python main.py
   ```

   First run generates `sessions/userbot.session` and authenticates. On subsequent runs, it reuses the session.

## How It Works

### Message Flow

```
SOURCE CHANNEL
    ↓
Parser validates pricing (regex)
    ↓
Apply markup to price
    ↓
Forward to TARGET CHANNEL
    ↓
Save source_msg_id → target_msg_id mapping in database
    ↓
Listen for edits/deletes on SOURCE
    ↓
Update/delete corresponding TARGET message
    ↓
Keep database in sync
```

### Example

**Source message**: "Brand new laptop 💵 800.50"

**Parsing**: Extracts `💵 800.50` → USD 800.50 (valid, text length > 1)

**Markup** (15%): `800.50 × 1.15 = 920.58`

**Target message**: "Brand new laptop 💵 920.58"

**Database**: `Pairs(source_msg_id=123, target_msg_id=456)`

If source is edited to remove price → target is deleted. If source is deleted → target is deleted and database pair removed.

## Important Notes

- **Session files** (`*.session`, `*.session-journal`) are gitignored for security
- **Environment variables** (`.env`) are gitignored; use `.env.example` as template
- **Database** (`app.db`) is local-only and gitignored
- **Rate limiting**: Automatic backoff on Telegram FloodWait errors; random delays between requests prevent API bans
- **Catch-up logic**: On startup, `catch_up_history()` processes all existing messages in source channel, essential for syncing after downtime

## Development

To add dependencies:
```bash
pip install package_name
pip freeze > requirements.txt  # Or manually add to requirements.txt
```

When creating new modules, follow the folder structure:
- Database operations → `database/`
- Business logic → `logic/`
- Event handlers → `handlers/`
- Configuration → root `config.py`
- Telegram client methods → `core/`

## Contributors

<a href="https://github.com/Ascent-Group-Tech/Channel_Aggregator/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Ascent-Group-Tech/Channel_Aggregator" />
</a>

See the [full contributors list](https://github.com/Ascent-Group-Tech/Channel_Aggregator/graphs/contributors).
