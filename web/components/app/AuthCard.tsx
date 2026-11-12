import { NetworkIcon } from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

interface AuthCardProps {
  title: string;
  description: string;
  footer: React.ReactNode;
  children: React.ReactNode;
}

export function AuthCard({ title, description, footer, children }: AuthCardProps) {
  return (
    <div className="relative isolate flex min-h-[calc(100dvh-4rem)] items-center justify-center px-4 py-12">
      <div className="hero-mesh absolute inset-0 -z-10" aria-hidden />
      <div className="dot-grid absolute inset-0 -z-10" aria-hidden />
      <Card className="w-full max-w-md shadow-xl shadow-black/5">
        <CardHeader className="items-center text-center">
          <span className="bg-primary text-primary-foreground mx-auto mb-2 flex size-11 items-center justify-center rounded-xl shadow-sm">
            <NetworkIcon className="size-5" aria-hidden />
          </span>
          <CardTitle className="text-2xl font-semibold tracking-tight">{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent className="[&_button[type=submit]]:h-10 [&_button[type=submit]]:w-full">{children}</CardContent>
        <CardFooter className="text-muted-foreground justify-center text-sm">{footer}</CardFooter>
      </Card>
    </div>
  );
}
