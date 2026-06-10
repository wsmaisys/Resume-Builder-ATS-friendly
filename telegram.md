# Telegram Job Post Access Guide

This note explains how to read job posts from Telegram groups or channels that you can already access as a normal Telegram user.

## Key Point

If you are only a regular member of a Telegram group, a normal Telegram Bot API token is usually not enough. Bots cannot read group messages unless the bot is added to the group and has the required permissions.

For groups or channels that you personally can read, use the Telegram Client API through a user session. This is often called a userbot approach.

## Recommended Library

Use one of these Python libraries:

- `Telethon`: mature and widely used for Telegram Client API automation.
- `Pyrogram`: another popular Telegram Client API framework.

For this project, `Telethon` is the simplest starting point.

## Setup Steps

1. Open Telegram API tools:

   ```text
   https://my.telegram.org/
   ```

2. Log in with your Telegram phone number.

3. Open `API development tools`.

4. Create a new application.

5. Copy the generated credentials:

   ```text
   api_id
   api_hash
   ```

   Keep both secret. Do not commit them to Git.

6. Install Telethon:

   ```powershell
   pip install telethon
   ```

7. Identify the group or channel.

   You can use either:

   ```python
   group_identifier = "@public_group_username"
   ```

   or a numeric chat ID if the group is private.

## Minimal Example

```python
from telethon import TelegramClient

api_id = 123456
api_hash = "your_api_hash_here"
group_identifier = "@example_job_group"

client = TelegramClient("job_scraper_session", api_id, api_hash)


async def main():
    async for message in client.iter_messages(group_identifier, limit=10):
        if message.text:
            print(f"Post Date: {message.date}")
            print(f"Job Details:\n{message.text}")
            print("-" * 40)


with client:
    client.loop.run_until_complete(main())
```

The first run will ask you to log in. Telethon creates a local session file, so later runs can reuse the authenticated session.

## Safer Usage Pattern

Avoid scraping in tight loops. Telegram can rate-limit accounts or temporarily restrict suspicious activity.

Prefer event-based processing:

```python
from telethon import TelegramClient, events

api_id = 123456
api_hash = "your_api_hash_here"
group_identifier = "@example_job_group"

client = TelegramClient("job_scraper_session", api_id, api_hash)


@client.on(events.NewMessage(chats=group_identifier))
async def handler(event):
    text = event.message.message
    if text and any(word.lower() in text.lower() for word in ["python", "ai", "remote"]):
        print(text)


client.start()
client.run_until_disconnected()
```

## Security Notes

- Keep `api_id`, `api_hash`, phone login codes, and session files private.
- Add session files to `.gitignore` before building anything around Telegram.
- Do not scrape faster than a human-like workflow.
- Respect group rules, Telegram terms, and local laws.

## Possible Integration With This App

Telegram job posts could later become a job-source ingestion module:

1. Read new job posts from allowed Telegram groups.
2. Filter posts by keywords such as `AI Engineer`, `FastAPI`, `RAG`, `Remote`, or `UAE`.
3. Extract the job description text.
4. Send the JD into this resume builder's `/api/generate` endpoint.
5. Save the generated resume and cover letter using the company-specific filename convention.
