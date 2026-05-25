FROM mes-frontend-base:latest

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_OPTIONS="--max-old-space-size=4096"

RUN npm run build

EXPOSE 3004
ENV PORT=3004

CMD ["npm", "run", "start"]
