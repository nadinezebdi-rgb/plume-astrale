import mongoose from "mongoose";

const transactionSchema = new mongoose.Schema({
  email: String,
  amount: Number,
  credits: Number,
  createdAt: { type: Date, default: Date.now }
});

export default mongoose.model("Transaction", transactionSchema);
