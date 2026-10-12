import Transaction from "../models/Transaction.js";

router.get("/revenue", checkAdmin, async (req, res) => {
  const revenue = await Transaction.aggregate([
    {
      $group: {
        _id: null,
        total: { $sum: "$amount" }
      }
    }
  ]);

  res.json({
    totalRevenue: revenue[0]?.total || 0
  });
});
