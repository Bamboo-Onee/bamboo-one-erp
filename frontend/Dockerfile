# ==============================================================================
# FRONTEND DOCKERFILE - REACT + TYPESCRIPT + VITE
# ==============================================================================
FROM node:20-alpine AS development

WORKDIR /app

COPY package*.json ./
RUN npm install --no-audit --no-fund --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
