import { Container } from "@cloudflare/containers";
import { env } from "cloudflare:workers";

export class Backend extends Container {
  defaultPort = 8000;
  sleepAfter = "20m";
  enableInternet = true;
  envVars = {
    DATABASE_URL: env.DATABASE_URL,
  };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/") {
      return new Response(
        JSON.stringify({
          service: "synthetic-experimentation-lab",
          backend: "FastAPI on Cloudflare Containers",
          database: "Neon PostgreSQL",
          status: "ok",
        }),
        { headers: { "content-type": "application/json" } },
      );
    }

    const backend = env.BACKEND.getByName("primary");
    return backend.fetch(request);
  },
};
