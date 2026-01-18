"""Email classification using Mistral API."""

import json
import os
import sys
import time

from mistralai import Mistral


def load_prompt():
    """Load prompt template from prompt.md file."""
    prompt_path = os.path.join(os.path.dirname(__file__), "prompt.md")
    try:
        with open(prompt_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: prompt.md not found at {prompt_path}")
        sys.exit(1)


def classify_email(client, email_data, prompt_template):
    """Classify a single email using Mistral API."""
    prompt = prompt_template.format(
        sender=email_data["sender"],
        subject=email_data["subject"],
        date=email_data["date"],
        body=email_data["body"],
    )

    try:
        response = client.chat.complete(
            model="mistral-medium-latest",
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content.strip()

        # Extract JSON from response (handle markdown code blocks)
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        return json.loads(content)

    except json.JSONDecodeError:
        return {"needs_action": False, "priority": "low", "reason": "Failed to parse response"}
    except Exception as e:
        return {"needs_action": False, "priority": "low", "reason": str(e)[:50]}


def classify_emails(config, emails):
    """Classify all emails using Mistral API."""
    client = Mistral(api_key=config["mistral_api_key"])
    prompt_template = load_prompt()
    results = []

    for i, email_data in enumerate(emails):
        result = classify_email(client, email_data, prompt_template)
        results.append({
            **email_data,
            "needs_action": result.get("needs_action", False),
            "priority": result.get("priority", "low"),
            "reason": result.get("reason", ""),
        })

        # Simple rate limiting
        if i < len(emails) - 1:
            time.sleep(0.5)

    return results
