import { redirect } from "next/navigation";
export default function ProjectsRedirect() {
  redirect("/my-path?tab=projects");
}
