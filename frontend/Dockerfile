FROM node:18-alpine

WORKDIR /app

# Cache node modules
COPY package.json .
RUN npm install

# Copy source code
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
