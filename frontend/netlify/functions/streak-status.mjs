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
  let payload;
  try {
    payload = extractUser(req);
  } catch (err) {
    return errorResponse(err.message, 401);
  }

  const streaks = getStore({ name: 'streaks', consistency: 'strong' });
  const streak = await streaks.get(payload.user_id, { type: 'json' });

  if (!streak) {
    return jsonResponse({
      streak_count: 0,
      checked_in_today: false,
      last_checkin: null,
      longest_streak: 0,
      total_checkins: 0,
      next_milestone: nextMilestone(0),
    });
  }

  const now = new Date();
  const todayStr = now.toISOString().slice(0, 10);
  const last = streak.last_checkin ? new Date(streak.last_checkin) : null;
  const checkedToday = last && last.toISOString().slice(0, 10) === todayStr;

  let currentCount = streak.streak_count || 0;
  if (last && !checkedToday) {
    const yesterday = new Date(now);
    yesterday.setUTCDate(yesterday.getUTCDate() - 1);
    if (last.toISOString().slice(0, 10) < yesterday.toISOString().slice(0, 10)) {
      currentCount = 0; // Streak broken
    }
  }

  return jsonResponse({
    streak_count: currentCount,
    checked_in_today: checkedToday,
    last_checkin: streak.last_checkin,
    longest_streak: streak.longest_streak || 0,
    total_checkins: streak.total_checkins || 0,
    next_milestone: nextMilestone(currentCount),
  });
};

export const config = {
  path: '/api/streak/status',
  method: 'GET',
};
