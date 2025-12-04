# LienOS Frontend

React + Vite frontend for the LienOS tax lien portfolio management system.

## Development

```bash
# Install dependencies
npm install

# Run development server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

### Development
In development mode, the app uses Vite's proxy to forward `/api` requests to `http://localhost:8000`.

No environment variables are needed for local development.

### Production
Create `.env.production` to point to your production API:

```bash
VITE_API_URL=https://lien-os-402756129398.us-central1.run.app
```

## Configuration

### API Client (`src/api/client.js`)

The API client automatically switches between:
- **Development:** Uses mock data and local API proxy
- **Production:** Connects to real API specified in `VITE_API_URL`

### Mock Data

Mock data is enabled by default in development for easier testing. To disable:

```javascript
// src/api/client.js
const USE_MOCK_DATA = false;
```

## Deployment to Render

### Option 1: Blueprint Deployment (Recommended)

1. Push code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Blueprint"
4. Connect your repository
5. Render will automatically detect `render.yaml` and deploy

### Option 2: Manual Deployment

1. Create new Static Site on Render
2. Connect GitHub repository
3. Configure:
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Publish Directory:** `frontend/dist`
   - **Environment Variable:** `VITE_API_URL=https://lien-os-402756129398.us-central1.run.app`

## Tech Stack

- **Framework:** React 18
- **Build Tool:** Vite 5
- **Routing:** React Router 6
- **Styling:** Tailwind CSS
- **UI Components:** Custom components with shadcn/ui inspiration
- **Charts:** Recharts
- **Icons:** Lucide React
- **Date Handling:** date-fns

## Project Structure

```
frontend/
├── public/
│   └── _redirects          # Render routing config
├── src/
│   ├── api/
│   │   └── client.js       # API client with auto-switching
│   ├── components/         # Reusable UI components
│   ├── pages/              # Page components
│   ├── App.jsx             # Main app component
│   └── main.jsx            # Entry point
├── .env.example            # Example environment variables
├── .env.production         # Production environment variables
├── index.html              # HTML template
├── package.json            # Dependencies
├── vite.config.js          # Vite configuration
└── README.md               # This file
```

## Features

- 📊 **Portfolio Dashboard** - Overview of all tax liens
- 📝 **Lien Management** - CRUD operations for liens
- 💰 **Interest Calculator** - Real-time interest calculations
- ⏰ **Deadline Tracker** - Monitor redemption deadlines
- 📄 **Document Generator** - Create legal documents
- 📱 **Responsive Design** - Works on all devices
- 🔄 **Mock Data Mode** - Test without backend

## Contributing

See the main [LienOS README](../README.md) for contribution guidelines.
