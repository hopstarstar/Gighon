# Telegram Webhook Bot for Render

This project runs a simple Telegram bot using webhooks and Flask. It's ready to deploy to Render.

## Steps to deploy

1. Create a GitHub repository and push these files.
2. On Render, create a new **Web Service** from your GitHub repo (or use `render.yaml` automatic deploy).
3. Set environment variables in Render:
   - `BOT_TOKEN` — your Telegram bot token (from @BotFather)
   - `WEBHOOK_URL` — (optional) full public URL for webhook, e.g. `https://your-service.onrender.com`
     If you don't set `WEBHOOK_URL`, the app will try to use Render's `RENDER_EXTERNAL_URL` env var automatically.
4. Deploy. Render will run the app with Gunicorn.
5. After deploy, the app will set the webhook automatically if `WEBHOOK_URL` or `RENDER_EXTERNAL_URL` is present.

## Notes

- The bot accepts a keyboard button "Написать код", checks five hardcoded codes and sends corresponding links.
- After a user sends a code (right or wrong), the bot schedules deletion of recent messages after 30 minutes.
- If webhook fails to set automatically, set `WEBHOOK_URL` manually in Render to `https://<your-service>.onrender.com` and redeploy.

