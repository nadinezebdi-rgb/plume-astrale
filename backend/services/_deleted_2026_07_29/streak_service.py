"""Streak service - daily check-in streak management with milestone bonuses"""
import uuid
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase

# Streak milestone bonuses (streak_day → bonus_credits)
STREAK_MILESTONES = {
    7: 3,
    14: 5,
    30: 10,
    60: 15,
    100: 25,
}

DAILY_CHECKIN_CREDIT = 1


async def get_streak(db: AsyncIOMotorDatabase, user_id: str) -> dict:
    """Get current streak status without modifying it."""
    streak = await db.streaks.find_one({"user_id": user_id}, {"_id": 0})
    if not streak:
        return {
            "streak_count": 0,
            "checked_in_today": False,
            "last_checkin": None,
            "longest_streak": 0,
            "total_checkins": 0,
            "next_milestone": _next_milestone(0),
        }

    now = datetime.now(timezone.utc)
    last = datetime.fromisoformat(streak["last_checkin"]) if streak.get("last_checkin") else None
    checked_today = last and last.date() == now.date()

    # Check if streak is still alive (last checkin was today or yesterday)
    current_count = streak.get("streak_count", 0)
    if last and not checked_today:
        yesterday = (now - timedelta(days=1)).date()
        if last.date() < yesterday:
            current_count = 0  # Streak broken

    return {
        "streak_count": current_count,
        "checked_in_today": checked_today,
        "last_checkin": streak.get("last_checkin"),
        "longest_streak": streak.get("longest_streak", 0),
        "total_checkins": streak.get("total_checkins", 0),
        "next_milestone": _next_milestone(current_count),
    }


async def do_checkin(db: AsyncIOMotorDatabase, user_id: str) -> dict:
    """Perform daily check-in. Returns streak info + credits earned."""
    now = datetime.now(timezone.utc)
    streak = await db.streaks.find_one({"user_id": user_id}, {"_id": 0})

    if not streak:
        # First ever check-in
        streak = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "streak_count": 0,
            "longest_streak": 0,
            "total_checkins": 0,
            "last_checkin": None,
            "created_at": now.isoformat(),
        }
        await db.streaks.insert_one(streak)

    last = datetime.fromisoformat(streak["last_checkin"]) if streak.get("last_checkin") else None

    # Already checked in today
    if last and last.date() == now.date():
        return {
            "already_checked_in": True,
            "streak_count": streak["streak_count"],
            "credits_earned": 0,
            "milestone_bonus": 0,
            "milestone_name": None,
            "longest_streak": streak.get("longest_streak", 0),
            "total_checkins": streak.get("total_checkins", 0),
            "next_milestone": _next_milestone(streak["streak_count"]),
        }

    # Determine if streak continues or resets
    yesterday = (now - timedelta(days=1)).date()
    if last and last.date() == yesterday:
        new_count = streak["streak_count"] + 1
    else:
        new_count = 1  # Reset or first check-in

    total = streak.get("total_checkins", 0) + 1
    longest = max(streak.get("longest_streak", 0), new_count)

    # Calculate credits
    credits = DAILY_CHECKIN_CREDIT
    milestone_bonus = 0
    milestone_name = None

    if new_count in STREAK_MILESTONES:
        milestone_bonus = STREAK_MILESTONES[new_count]
        credits += milestone_bonus
        milestone_name = f"Streak {new_count} jours"

    # Update streak record
    await db.streaks.update_one(
        {"user_id": user_id},
        {"$set": {
            "streak_count": new_count,
            "longest_streak": longest,
            "total_checkins": total,
            "last_checkin": now.isoformat(),
        }},
    )

    return {
        "already_checked_in": False,
        "streak_count": new_count,
        "credits_earned": credits,
        "milestone_bonus": milestone_bonus,
        "milestone_name": milestone_name,
        "longest_streak": longest,
        "total_checkins": total,
        "next_milestone": _next_milestone(new_count),
    }


def _next_milestone(current_count: int) -> dict:
    """Find the next streak milestone."""
    for day, bonus in sorted(STREAK_MILESTONES.items()):
        if day > current_count:
            return {"days": day, "bonus": bonus, "remaining": day - current_count}
    return {"days": None, "bonus": 0, "remaining": 0}
