# Stage 1: Build the application
FROM node:18 AS builder

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve the application
FROM node:18-alpine AS runner

# Set working directory
WORKDIR /app

# Copy the built application from the builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package*.json ./

# Copy assets
COPY --from=builder /app/public ./public

# Copy .env file
COPY --from=builder /app/.env.local ./.env.local

# Install only production dependencies
RUN npm install --production

# Expose the port the app runs on
EXPOSE 3005

# Start the application
CMD ["npm", "start", "--", "--port", "3005"]
