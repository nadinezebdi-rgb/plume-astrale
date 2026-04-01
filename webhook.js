import Transaction from "../models/Transaction.js";

if (event.type === "checkout.session.completed") {
  const session = event.data.object;

  const email = session.customer_email;
  const priceId = session.metadata.priceId;

  let creditsToAdd = 0;
  let amount = session.amount_total / 100;

  if (priceId === "price_20credits") creditsToAdd = 20;
  if (priceId === "price_100credits") creditsToAdd = 120;
  if (priceId === "price_300credits") creditsToAdd = 350;

  const user = await User.findOne({ email });

  if (user) {
    user.credits += creditsToAdd;
    await user.save();
  }

  // 📊 TRACK
  await Transaction.create({
    email,
    amount,
    credits: creditsToAdd
  });
}
