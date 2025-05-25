import express from 'express';
import routes from './api/routes';
import http from 'http';

export async function registerRoutes(app: express.Express): Promise<http.Server> {
  // Set up API routes
  app.use('/', routes);
  
  // Create and return the HTTP server
  return http.createServer(app);
}