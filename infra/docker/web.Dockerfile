# Web (Next.js) image. Build context = ./web (see docker-compose.yml).
FROM node:20-alpine

WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .

EXPOSE 3000
# Dev by default; production deploy overrides with `npm run build && npm start`.
CMD ["npm", "run", "dev"]
