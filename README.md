# E-commerce Chatbot

A full-stack React-based chatbot for handling e-commerce order inquiries with a REST API backend.

## Features

- Real-time chat interface for order inquiries
- REST API backend for order data management
- Natural language processing using compromise library
- Fallback to demo data if API is unavailable
- Responsive UI with modern chat styling
- Support for greetings, order status queries, and help

## Tech Stack

- **Frontend**: React, CSS
- **Backend**: Node.js, Express, MongoDB, Mongoose
- **NLP**: Compromise library
- **API**: RESTful endpoints for order management

## Getting Started

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

### Prerequisites

- Node.js
- npm

### Installation

1. Clone the repository
2. Run `npm install` to install dependencies

### Running the App

First, start the backend API server:

```bash
npm run server
```

This will start the order API on http://localhost:3002.

Then, in a separate terminal, start the React frontend:

```bash
npm start
```

Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

## Full ML Integration Setup

This project now includes machine learning for intent classification!

### Additional Prerequisites
- Python 3.x
- MongoDB (local or Atlas)

### ML Setup Steps

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Train the ML model:**
   ```bash
   cd ml
   python train.py
   cd ..
   ```

3. **Start MongoDB:**
   - Local: Run `mongod`
   - Atlas: Update `MONGODB_URI` in `.env`

4. **Seed database (optional):**
   ```bash
   curl -X POST http://localhost:3002/api/seed
   ```

### Running All Services

**Terminal 1: ML Service**
```bash
python app.py
```
Port: 5001

**Terminal 2: Backend API**
```bash
npm run server
```
Port: 3002

**Terminal 3: Frontend**
```bash
npm start
```
Port: 3000/3001

### Test ML Chatbot
Try these messages:
- "hello" → Greeting response
- "order 70" → Order details from MongoDB
- "thank you" → Thanks response
- "bye" → Goodbye response

The ML model classifies intents and the backend fetches data from MongoDB!

### API Endpoints

The backend provides the following REST API endpoints:

- `GET /api/orders` - Get all orders
- `GET /api/orders/:id` - Get a specific order by ID
- `PUT /api/orders/:id` - Update an order's status

If the API is unavailable, the app falls back to demo data.

## Database Setup

This app uses MongoDB for data persistence.

### Option 1: Local MongoDB
1. Install MongoDB locally from [mongodb.com](https://www.mongodb.com/try/download/community)
2. Start MongoDB service: `mongod` (in a separate terminal)
3. The app will connect to `mongodb://localhost:27017/chatbot` (default in `.env`)

### Option 2: MongoDB Atlas (Cloud)
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a cluster and database
3. Get your connection string (replace `<password>` and `<dbname>`)
4. Update the `MONGODB_URI` in `.env` file: `MONGODB_URI=your_connection_string`

### Seeding Data
After starting the server and connecting to MongoDB, seed initial data:

```bash
curl -X POST http://localhost:3002/api/seed
```

Or use Postman/Insomnia to POST to `http://localhost:3002/api/seed`

## Database Setup

This app uses MongoDB for data persistence.

### Option 1: Local MongoDB
1. Install MongoDB locally from [mongodb.com](https://www.mongodb.com/try/download/community)
2. Start MongoDB service: `mongod`
3. The app will connect to `mongodb://localhost:27017/chatbot`

### Option 2: MongoDB Atlas (Cloud)
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a cluster and database
3. Get your connection string (replace `<password>` and `<dbname>`)
4. Set the environment variable: `MONGODB_URI=your_connection_string`
5. Or edit `server.js` and change the `MONGODB_URI` variable

### Seeding Data
After starting the server and connecting to MongoDB, seed initial data:

```bash
curl -X POST http://localhost:3002/api/seed
```

Or use Postman/Insomnia to POST to `http://localhost:3002/api/seed`

### Available Scripts

- `npm start` - Runs the app in development mode
- `npm test` - Launches the test runner
- `npm run build` - Builds the app for production
- `npm run eject` - Ejects from Create React App (irreversible)

## Usage

Type messages like:
- "Hello"
- "What's the status of order 70?"
- "Hi, check order 71"

The bot will respond accordingly using mock order data.

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
