app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Save with **Ctrl+S** — backend will auto-reload.

---

## Now test the form fully:

Scroll up and fill these fields:
- **HCP Name**: `Dr. Smith`
- **Interaction Type**: `Meeting`
- **Date**: today's date
- **Time**: current time
- **Attendees**: `mansa` (already filled)
- **Topics Discussed**: `healthcheckup` (already filled)
- **Sentiment**: select `Positive`
- **Outcomes**: `Patient agreed to follow-up`
- **Follow-up Actions**: `Schedule call next week`

Then scroll down and click **Log Interaction** button.

---

## Test the chat:

In the chat box type:
```
Met Dr. Smith today, discussed Product X efficacy, positive sentiment, shared brochure