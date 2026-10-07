import { env } from "cloudflare:workers";
import { Container, getContainer } from "@cloudflare/containers";

export class ApiContainer extends Container {
  defaultPort = 8000;
  sleepAfter = "15m";
  pingEndpoint = "/health";
  enableInternet = true;

  envVars = {
    APP_ENV: "production",
    DATABASE_URL: env.DATABASE_URL,
    CORS_ORIGINS: env.CORS_ORIGINS || "*",
    DB_POOL_SIZE: "1",
    DB_MAX_OVERFLOW: "1",
  };
}

export default {
  async fetch(request, workerEnv) {
    const container = getContainer(workerEnv.API_CONTAINER, "synthetic-api");
    return container.fetch(request);
  },
};
