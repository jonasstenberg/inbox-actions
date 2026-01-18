"""Terminal output formatting."""


def truncate(text, length=40):
    """Truncate text with ellipsis."""
    text = text.replace("\n", " ").strip()
    return text[:length] + "..." if len(text) > length else text


def print_results(results):
    """Print classification results as a table."""
    if not results:
        print("No emails to display.")
        return

    # Separate action items from others
    action_items = [r for r in results if r.get("needs_action")]
    no_action = [r for r in results if not r.get("needs_action")]

    # Sort action items by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    action_items.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))

    if action_items:
        print()
        print("=== ACTION REQUIRED ===")
        print(f"{'PRI':<6} {'DATE':<18} {'FROM':<25} {'SUBJECT':<40} {'REASON'}")
        print("-" * 120)

        for r in action_items:
            sender = truncate(r["sender"].split("<")[0].strip(' "'), 23)
            subject = truncate(r["subject"], 38)
            priority = r.get("priority", "low").upper()
            reason = truncate(r["reason"], 35)

            print(f"{priority:<6} {r['date']:<18} {sender:<25} {subject:<40} {reason}")

    if no_action:
        print()
        print("=== NO ACTION NEEDED ===")
        print(f"{'DATE':<18} {'FROM':<25} {'SUBJECT':<40} {'REASON'}")
        print("-" * 120)

        for r in no_action:
            sender = truncate(r["sender"].split("<")[0].strip(' "'), 23)
            subject = truncate(r["subject"], 38)
            reason = truncate(r["reason"], 35)

            print(f"{r['date']:<18} {sender:<25} {subject:<40} {reason}")

    print()
    print(f"Total: {len(results)} emails ({len(action_items)} need action, {len(no_action)} informational)")
