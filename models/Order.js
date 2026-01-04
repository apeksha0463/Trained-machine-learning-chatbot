const mongoose = require("mongoose");

const OrderSchema = new mongoose.Schema({
  orderNumber: Number,
  status: String,
  items: [String],
  total: Number,
  customerName: String,
  address: String,
  orderDate: String
});

module.exports = mongoose.model("Order", OrderSchema);

