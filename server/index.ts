import express from 'express';
import session from 'express-session';
import connectPgSimple from 'connect-pg-simple';
import { db } from '@db';
import routes from './routes';
import { createServer } from 'vite';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

// Environment variables
const isProduction = process.env.NODE_ENV === 'production';
const PORT = Number(process.env.PORT || 5000);
const SESSION_SECRET = process.env.SESSION_SECRET || 'fantasy-rpg-secret';

// Initialize Express
const app = express();

// Session store setup with PostgreSQL
const PgSession = connectPgSimple(session);
const sessionStore = new PgSession({
  conString: process.env.DATABASE_URL,
  createTableIfMissing: true,
});

// Session middleware
app.use(
  session({
    store: sessionStore,
    secret: SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    cookie: {
      maxAge: 30 * 24 * 60 * 60 * 1000, // 30 days
      secure: isProduction,
    },
  })
);

// Parse JSON body
app.use(express.json());

// Use our API routes
app.use(routes);

// Integrate Vite in development, serve static files in production
if (!isProduction) {
  // Create a development server for frontend with HMR
  (async () => {
    try {
      const vite = await createServer({
        server: { middlewareMode: true },
        appType: 'spa',
      });
      
      app.use(vite.middlewares);
      console.log('Vite middleware attached');
    } catch (e) {
      console.error('Error setting up Vite middleware:', e);
    }
  })();
} else {
  // For production, serve static files from the dist directory
  app.use(express.static('dist/client'));
  
  // Handle client-side routing by serving the index.html for all non-API routes
  app.get('*', (req, res, next) => {
    if (req.path.startsWith('/api')) {
      return next();
    }
    res.sendFile('dist/client/index.html', { root: '.' });
  });
}

// Error handling middleware
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});

export default app;