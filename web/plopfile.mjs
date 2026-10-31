// Boilerplate generators (see .claude/skills/scaffold).
//   npx plop router <name>        FastAPI router + models + queries, registered in main.py
//   npx plop component <Name>     components/app/<Name>.tsx + test
//   npx plop page <route/path>    app/<route/path>/page.tsx + loading.tsx
const API = "../api/app";

export default function plopfile(plop) {
  plop.setHelper("routeTitle", (route) =>
    route.split("/").filter((s) => s && !s.startsWith("(") && !s.startsWith("["))
      .map((s) => s[0].toUpperCase() + s.slice(1)).join(" ") || "Home");

  plop.setGenerator("router", {
    description: "FastAPI router (+ models, queries) registered in main.py",
    prompts: [{ type: "input", name: "name", message: "router name (snake_case)" }],
    actions: [
      { type: "add", path: `${API}/routers/{{snakeCase name}}.py`, templateFile: "plop-templates/router.py.hbs", skipIfExists: true },
      { type: "add", path: `${API}/models/{{snakeCase name}}.py`, templateFile: "plop-templates/models.py.hbs", skipIfExists: true },
      { type: "add", path: `${API}/queries/{{snakeCase name}}.py`, templateFile: "plop-templates/queries.py.hbs", skipIfExists: true },
      { type: "modify", path: `${API}/main.py`, pattern: /(# plop: router imports)/,
        template: "from app.routers import {{snakeCase name}}\n$1" },
      { type: "modify", path: `${API}/main.py`, pattern: /(# plop: include routers)/,
        template: "app.include_router({{snakeCase name}}.router)\n$1" },
    ],
  });

  plop.setGenerator("component", {
    description: "App component (server by default) + test",
    prompts: [
      { type: "input", name: "name", message: "component name (PascalCase)" },
      { type: "confirm", name: "client", message: "client component?", default: false },
    ],
    actions: [
      { type: "add", path: "components/app/{{pascalCase name}}.tsx", templateFile: "plop-templates/component.tsx.hbs" },
      { type: "add", path: "components/app/{{pascalCase name}}.test.tsx", templateFile: "plop-templates/component.test.tsx.hbs" },
    ],
  });

  plop.setGenerator("page", {
    description: "App Router page + loading skeleton",
    prompts: [{ type: "input", name: "route", message: "route path, e.g. (dashboard)/dashboard/skills" }],
    actions: [
      { type: "add", path: "app/{{route}}/page.tsx", templateFile: "plop-templates/page.tsx.hbs" },
      { type: "add", path: "app/{{route}}/loading.tsx", templateFile: "plop-templates/loading.tsx.hbs" },
    ],
  });
}
