import { redirect } from "next/navigation";
export default function RoadmapRedirect() {
  redirect("/my-path?tab=roadmap");
}
