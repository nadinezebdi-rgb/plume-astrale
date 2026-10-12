import { useEffect, useState } from "react";

export default function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);

  const headers = {
    "admin": "SECRET123" // ⚠️ à sécuriser après
  };

  useEffect(() => {
    fetch("/api/admin/users", { headers })
      .then(res => res.json())
      .then(setUsers);

    fetch("/api/admin/stats", { headers })
      .then(res => res.json())
      .then(setStats);
  }, []);

  return (
    <div style={{ padding: 40, color: "white" }}>
      <h1>📊 Admin Dashboard</h1>

      {stats && (
        <div style={{ marginBottom: 30 }}>
          <p>👥 Users: {stats.totalUsers}</p>
          <p>💎 Premium: {stats.premiumUsers}</p>
          <p>💰 Total Credits: {stats.totalCredits}</p>
        </div>
      )}

      {users.map(user => (
        <div key={user._id} style={{ marginBottom: 20 }}>
          <p>{user.email}</p>
          <p>Credits: {user.credits}</p>
        </div>
      ))}
    </div>
  );
}
