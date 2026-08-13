FROM node:24.18-alpine AS base

WORKDIR /app

RUN chown node:node /app
USER node

COPY --chown=node:node package.json package-lock.json ./
RUN npm ci

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM base AS test

COPY . .

CMD ["npm", "run", "test"]

FROM base AS production

COPY . .

RUN npm run build

EXPOSE 3000

CMD [ "serve", "-s", "dist" ]
