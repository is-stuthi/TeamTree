import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

/** Shown wherever a Neo4j-backed read failed (API 503 GRAPH_UNAVAILABLE). MySQL features keep working. */
export function GraphUnavailable({ what = "Graph features" }: { what?: string }) {
  return (
    <Alert>
      <AlertTitle>{what} are unavailable right now</AlertTitle>
      <AlertDescription>
        The graph database isn&apos;t responding. Projects, applications, teams and tasks still work. Try again shortly.
      </AlertDescription>
    </Alert>
  );
}
