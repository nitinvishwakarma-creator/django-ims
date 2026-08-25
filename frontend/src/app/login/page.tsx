import type {
  Metadata,
} from "next";

import LoginForm from "@/features/auth/components/login-form";

export const metadata: Metadata = {
  title: "Sign in | Django IMS",
  description:
    "Sign in to the Django IMS workspace.",
};

export default function LoginPage() {
  return (
    <main
      className="
        flex min-h-screen items-center
        justify-center bg-slate-50
        px-4 py-12
      "
    >
      <div className="w-full max-w-md">
        <LoginForm />
      </div>
    </main>
  );
}