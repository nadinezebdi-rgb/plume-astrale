import { getStore } from '@netlify/blobs';
import { extractUser, jsonResponse, errorResponse } from '../lib/auth-helpers.mjs';

const STREAK_MILESTONES = { 7: 3, 14: 5, 30: 10, 60: 15, 100: 25 };
const DAILY_CHECKIN_CREDIT = 1;

function nextMilestone(currentCount) {
  for (const [day, bonus] of Object.entries(STREAK_MILESTONES).sort((a, b) => a[0] - b[0])) {
    const d = parseInt(day);
    if (d > currentCount) {
      return { days: d, bonus, remaining: d - currentCount };
    }
  }
  return { days: null, bonus: 0, remaining: 0 };
}

export default async (req) => {
  if (req.method !== 'POST') {
    return errorResponse('Method not allowed', 405);
  }

  let payload;
  try {
    payload = extractUser(req);
  } catch (err) {
    return errorResponse(err.message, 401);
  }

  const streaks = getStore({ name: 'streaks', consistency: 'strong' });
  const wallets = getStore({ name: 'wallets', consistency: 'strong' });

  let streak = await streaks.get(payload.user_id, { type: 'json' });
  const now = new Date();
  const todayStr = now.toISOString().slice(0, 10);

  if (!streak) {
    streak = {
      user_id: payload.user_id,
      streak_count: 0,
      longest_streak: 0,
      total_checkins: 0,
      last_checkin: null,
      created_at: now.toISOString(),
    };
  }

  const last = streak.last_checkin ? new Date(streak.last_checkin) : null;

  // Already checked in today
  if (last && last.toISOString().slice(0, 10) === todayStr) {
    return jsonResponse({
      already_checked_in: true,
      streak_count: streak.streak_count,
      credits_earned: 0,
      milestone_bonus: 0,
      milestone_name: null,
      longest_streak: streak.longest_streak || 0,
      total_checkins: streak.total_checkins || 0,
      next_milestone: nextMilestone(streak.streak_count),
    });
  }

  // Determine if streak continues or resets
  const yesterday = new Date(now);
  yesterday.setUTCDate(yesterday.getUTCDate() - 1);
  const yesterdayStr = yesterday.toISOString().slice(0, 10);

  let newCount;
  if (last && last.toISOString().slice(0, 10) === yesterdayStr) {
    newCount = (streak.streak_count || 0) + 1;
  } else {
    newCount = 1;
  }

  const total = (streak.total_checkins || 0) + 1;
  const longest = Math.max(streak.longest_streak || 0, newCount);

  // Calculate credits
  let credits = DAILY_CHECKIN_CREDIT;
  let milestoneBonus = 0;
  let milestoneName = null;

  if (newCount in STREAK_MILESTONES) {
    milestoneBonus = STREAK_MILESTONES[newCount];
    credits += milestoneBonus;
    milestoneName = `Streak ${newCount} jours`;
  }

  // Update streak
  streak.streak_count = newCount;
  streak.longest_streak = longest;
  streak.total_checkins = total;
  streak.last_checkin = now.toISOString();
  await streaks.setJSON(payload.user_id, streak);

  // Add credits to wallet
  if (credits > 0) {
    const wallet = await wallets.get(payload.user_id, { type: 'json' });
    if (wallet) {
      wallet.credit_balance += credits;
      wallet.updated_at = now.toISOString();
      await wallets.setJSON(payload.user_id, wallet);
    }
  }

  const wallet = await wallets.get(payload.user_id, { type: 'json' });

  return jsonResponse({
    already_checked_in: false,
    streak_count: newCount,
    credits_earned: credits,
    milestone_bonus: milestoneBonus,
    milestone_name: milestoneName,
    longest_streak: longest,
    total_checkins: total,
    next_milestone: nextMilestone(newCount),
    credit_balance: wallet ? wallet.credit_balance : 0,
  });
};

export const config = {
  path: '/api/streak/checkin',
  method: 'POST',
};
