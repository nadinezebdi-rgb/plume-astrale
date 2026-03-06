"""Wallet service - credit balance management and transaction logging"""
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase

REGISTRATION_BONUS = 20
DAILY_BONUS = 1


async def create_wallet(db: AsyncIOMotorDatabase, user_id: str) -> dict:
    """Create a new wallet with registration bonus."""
    wallet = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "credit_balance": REGISTRATION_BONUS,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "last_daily_bonus": None,
    }
    await db.user_wallets.insert_one(wallet)

    # Log the registration bonus transaction
    await log_transaction(
        db,
        user_id=user_id,
        tx_type="bonus",
        amount=REGISTRATION_BONUS,
        description="Bonus d'inscription",
    )
    return wallet


async def get_wallet(db: AsyncIOMotorDatabase, user_id: str) -> dict:
    """Get user wallet, applying daily bonus if eligible."""
    wallet = await db.user_wallets.find_one({"user_id": user_id}, {"_id": 0})
    if not wallet:
        return None

    # Check daily bonus eligibility
    now = datetime.now(timezone.utc)
    last_bonus = wallet.get("last_daily_bonus")

    if last_bonus:
        last_bonus_dt = datetime.fromisoformat(last_bonus) if isinstance(last_bonus, str) else last_bonus
        # Give bonus if last bonus was before today (UTC)
        if last_bonus_dt.date() < now.date():
            wallet["credit_balance"] += DAILY_BONUS
            wallet["last_daily_bonus"] = now.isoformat()
            wallet["updated_at"] = now.isoformat()
            await db.user_wallets.update_one(
                {"user_id": user_id},
                {"$set": {
                    "credit_balance": wallet["credit_balance"],
                    "last_daily_bonus": wallet["last_daily_bonus"],
                    "updated_at": wallet["updated_at"],
                }},
            )
            await log_transaction(db, user_id, "bonus", DAILY_BONUS, "Bonus quotidien")
    else:
        # First day after registration — give daily bonus if account was created before today
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if user:
            created = datetime.fromisoformat(user["created_at"]) if isinstance(user.get("created_at"), str) else user.get("created_at")
            if created and created.date() < now.date():
                wallet["credit_balance"] += DAILY_BONUS
                wallet["last_daily_bonus"] = now.isoformat()
                wallet["updated_at"] = now.isoformat()
                await db.user_wallets.update_one(
                    {"user_id": user_id},
                    {"$set": {
                        "credit_balance": wallet["credit_balance"],
                        "last_daily_bonus": wallet["last_daily_bonus"],
                        "updated_at": wallet["updated_at"],
                    }},
                )
                await log_transaction(db, user_id, "bonus", DAILY_BONUS, "Bonus quotidien")

    return wallet


async def deduct_credits(db: AsyncIOMotorDatabase, user_id: str, amount: int, description: str) -> dict:
    """Deduct credits from user wallet. Raises if insufficient."""
    wallet = await get_wallet(db, user_id)
    if not wallet:
        raise ValueError("Portefeuille introuvable")
    if wallet["credit_balance"] < amount:
        raise ValueError("Crédits insuffisants")

    new_balance = wallet["credit_balance"] - amount
    now = datetime.now(timezone.utc).isoformat()
    await db.user_wallets.update_one(
        {"user_id": user_id},
        {"$set": {"credit_balance": new_balance, "updated_at": now}},
    )
    await log_transaction(db, user_id, "usage", -amount, description)
    return {"credit_balance": new_balance}


async def add_credits(db: AsyncIOMotorDatabase, user_id: str, amount: int, description: str) -> dict:
    """Add credits to user wallet."""
    wallet = await get_wallet(db, user_id)
    if not wallet:
        raise ValueError("Portefeuille introuvable")

    new_balance = wallet["credit_balance"] + amount
    now = datetime.now(timezone.utc).isoformat()
    await db.user_wallets.update_one(
        {"user_id": user_id},
        {"$set": {"credit_balance": new_balance, "updated_at": now}},
    )
    await log_transaction(db, user_id, "purchase", amount, description)
    return {"credit_balance": new_balance}


async def log_transaction(db: AsyncIOMotorDatabase, user_id: str, tx_type: str, amount: int, description: str):
    """Log a credit transaction."""
    tx = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "type": tx_type,
        "credits_amount": amount,
        "description": description,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await db.credit_transactions.insert_one(tx)


async def get_transactions(db: AsyncIOMotorDatabase, user_id: str, limit: int = 50) -> list:
    """Get credit transaction history."""
    txs = await db.credit_transactions.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("timestamp", -1).to_list(limit)
    return txs


async def check_free_tarot_used(db: AsyncIOMotorDatabase, user_id: str) -> bool:
    """Check if user has already used their free Tarot Oui/Non draw."""
    tx = await db.credit_transactions.find_one(
        {"user_id": user_id, "description": "Tarot Oui/Non (tirage gratuit)"},
        {"_id": 0},
    )
    return tx is not None


async def mark_free_tarot_used(db: AsyncIOMotorDatabase, user_id: str):
    """Mark the free Tarot Oui/Non as used (0-credit transaction)."""
    await log_transaction(db, user_id, "usage", 0, "Tarot Oui/Non (tirage gratuit)")
