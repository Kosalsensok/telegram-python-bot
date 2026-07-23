# Production Dockerfile for Telegram AI Math Solver Bot
FROM mcr.microsoft.com/playwright/node:20-jammy

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY prisma ./prisma/

# Install node dependencies
RUN npm ci

# Copy source files
COPY . .

# Generate Prisma Client and Build TypeScript
RUN npx prisma generate
RUN npm run build

# Expose Web Server Port
EXPOSE 3000

ENV NODE_ENV=production

# Start Application
CMD ["npm", "start"]
