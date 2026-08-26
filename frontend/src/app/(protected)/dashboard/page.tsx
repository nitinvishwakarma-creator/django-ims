"use client";

import {
  useRouter,
} from "next/navigation";

import RequireAuth from "@/features/auth/components/require-auth";

import {
  useAuth,
} from "@/features/auth/auth-context";

function DashboardContent() {
  const router = useRouter();

  const {
    authentication,
    signOut,
  } = useAuth();

  if (!authentication) {
    return null;
  }

  async function handleSignOut():
    Promise<void> {
    await signOut();

    router.replace("/login");
    router.refresh();
  }

  return (
    <main
      className="
        min-h-screen bg-slate-50 p-8
      "
    >
      <div
        className="
          mx-auto max-w-5xl rounded-2xl
          border border-slate-200
          bg-white p-8 shadow-sm
        "
      >
        <p
          className="
            text-sm font-semibold
            text-blue-600
          "
        >
          {
            authentication
              .organization
              .name
          }
        </p>

        <h1
          className="
            mt-2 text-3xl font-bold
            text-slate-900
          "
        >
          Welcome,{" "}
          {
            authentication
              .user
              .first_name
          }
        </h1>

        <p className="mt-2 text-slate-600">
          Role:{" "}
          {
            authentication
              .role
              .name
          }
        </p>

        <button
          type="button"
          onClick={() => {
            void handleSignOut();
          }}
          className="
            mt-6 rounded-lg
            bg-slate-900 px-4 py-2
            text-sm font-semibold
            text-white hover:bg-slate-700
          "
        >
          Sign out
        </button>
      </div>
    </main>
  );
}

export default function DashboardPage() {
  return (
    <RequireAuth>
      <DashboardContent />
    </RequireAuth>
  );
}