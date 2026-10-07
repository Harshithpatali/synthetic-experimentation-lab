import { DurableObject } from "cloudflare:workers";

const TIMEOUT_MS=10*60*1000;

export class Backend extends DurableObject {
  starting;

  constructor(ctx, env) {
    super(ctx, env);
    if (ctx.container?.running) {
      void ctx.blockConcurrencyWhile(() => ctx.container.setInactivityTimeout(TIMEOUT_MS));
    }
  }

  async start() {
    const container=this.ctx.container;
    if (!container) throw new Error("Container binding is not configured");

    if (!container.running) {
      container.start({
        image: container.images.base,
        enableInternet: true,
        env: { DATABASE_URL: this.env.DATABASE_URL }
      });
      await container.setInactivityTimeout(TIMEOUT_MS);
    }

    for (let attempt=0; attempt<60; attempt++) {
      try {
        const response=await container.getTcpPort(8000).fetch("http://container/health");
        if (response.ok) return;
      } catch (_) {}
      await new Promise(resolve=>setTimeout(resolve,500));
    }
    throw new Error("FastAPI container did not become ready");
  }

  async fetch(request) {
    this.starting ??= this.start().finally(()=>{ this.starting=undefined; });
    await this.starting;

    const url=new URL(request.url);
    url.protocol="http:";
    url.host="container";
    const forwarded=new Request(url,request);
    forwarded.headers.delete("host");
    return this.ctx.container.getTcpPort(8000).fetch(forwarded);
  }
}

export default {
  async fetch(request, env) {
    const id=env.BACKEND.idFromName("primary");
    return env.BACKEND.get(id).fetch(request);
  }
};
