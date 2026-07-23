# Production Dockerfile for Telegram AI Math Solver Bot
FROM mcr.microsoft.com/playwright/node:20-jammy

WORKDIR /app

# Install Khmer Unicode and Math Fonts
RUN apt-get update && apt-get install -y \
    fonts-noto-core \
    fonts-noto-extra \
    fonts-noto-ui-core \
    fonts-khmeros \
    fonts-lmodern \
    chromium \
    && rm -rf /var/lib/apt/lists/*

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
