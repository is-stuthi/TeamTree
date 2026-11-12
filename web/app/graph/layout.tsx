import { SectionTitle } from "@/components/app/SectionTitle";

export default function GraphLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <SectionTitle />
      {children}
    </div>
  );
}
