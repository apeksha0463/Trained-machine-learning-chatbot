const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const axios = require("axios");
require("dotenv").config();

const Order = require("./models/Order");

const app = express();
app.use(cors());
app.use(express.json());

// MongoDB connection
mongoose
  .connect(process.env.MONGODB_URI)
  .then(() => console.log("MongoDB Connected"))
  .catch(err => console.log(err));

/* =========================
   CHAT ENDPOINT
========================= */
app.post("/chat", async (req, res) => {
  try {
    const userMessage = req.body.message;

    // Call ML service
    const mlResponse = await axios.post(
      "http://localhost:5001/predict",
      { message: userMessage }
    );

    const { intent, order_id } = mlResponse.data;

    // Greetings
    if (intent === "greeting") {
      return res.json({ reply: "Hello! How can I help you today?" });
    }

    if (intent === "thanks") {
      return res.json({ reply: "You're welcome!" });
    }

    if (intent === "goodbye") {
      return res.json({ reply: "Goodbye! Have a nice day." });
    }

    // Order lookup
    if (intent === "get_order") {
      if (!order_id) {
        return res.json({ reply: "Please provide an order number." });
      }

      const order = await Order.findOne({ orderNumber: order_id });

      if (!order) {
        return res.json({ reply: `No order found with number ${order_id}.` });
      }

      return res.json({
        reply: `Order ${order.orderNumber}
Status: ${order.status}
Items: ${order.items.join(", ")}
Total: $${order.total}
Customer: ${order.customerName}
Address: ${order.address}
Order Date: ${order.orderDate}`
      });
    }

    return res.json({ reply: "Sorry, I didn't understand that." });

  } catch (error) {
    console.error("BACKEND ERROR:", error.message);
    return res.status(500).json({ reply: "Backend error" });
  }
});

/* =========================
   SERVER START
========================= */
app.listen(3002, () => {
  console.log("Backend running on port 3002");
});

