import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "BBA — Elektron milliy sertifikat platformasi" },
      { name: "description", content: "Bilimni baholash agentligi elektron test platformasi: tizimga kirish, imtihon va natijalar." },
      { property: "og:title", content: "BBA — Elektron milliy sertifikat platformasi" },
      { property: "og:description", content: "Milliy sertifikat imtihoni uchun elektron test platformasi." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <iframe
      className="platform-frame"
      title="BBA — Milliy sertifikat test platformasi"
      src="/bba-platform.html?v=31"
      allow="camera; fullscreen"
    />
  );
}
