---
name: preview
description: Preview today's morning and evening push content locally without sending to Bark. Use when you want to see what the notification will look like.
---

Generate and display today's push content by running the scripts locally.

Run these two commands from the project root:

```bash
python -m scripts.generate_task
python -m scripts.check_evening
```

Print the output as formatted JSON, then render the `title` and `body` fields in a readable way so the user can see exactly what the notification will look like on their phone.

If either command fails, show the error and explain what's wrong (missing state.json, bad start_date, import error, etc.).
