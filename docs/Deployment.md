# Deployment Guide

## Production Checklist
- [ ] Set `DEBUG=False` in your environment configuration.
- [ ] Change the default `JWT_SECRET_KEY` to a strong, randomly generated key.
- [ ] Configure database backups for PostgreSQL.
- [ ] Install SSL certificates on Nginx.
- [ ] Secure access to storage folders (evidence and uploads).

## Docker Production Deployment

1. Set up production environment configuration:
   ```bash
   cp .env.example .env
   # Update variables for production
   ```

2. Build and start services using the production compose file:
   ```bash
   docker-compose -f docker-compose.yml up -d --build
   ```

3. Verify service health and container status:
   ```bash
   docker-compose ps
   ```

4. Monitor application logs:
   ```bash
   docker-compose logs -f backend
   ```
