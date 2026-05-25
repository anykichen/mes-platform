FROM node:22-alpine

WORKDIR /app

RUN apk add --no-cache libc6-compat

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV PORT=3004

RUN npm run build 2>&1 | tee /tmp/build.log; exit_code=$?; if [ $exit_code -ne 0 ]; then echo "=== BUILD FAILED ==="; cat /tmp/build.log; exit 1; fi

EXPOSE 3004

CMD ["npm", "run", "start"]
