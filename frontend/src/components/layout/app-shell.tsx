"use client";

import {
  useState,
  type ReactNode,
} from "react";

import RequireAuth from "@/features/auth/components/require-auth";

import AppHeader from "@/components/layout/app-header";
import AppSidebar from "@/components/layout/app-sidebar";

export default function AppShell({
  children,
}: {
  children: ReactNode;
}) {
  const [
    mobileOpen,
    setMobileOpen,
  ] = useState(false);

  const [
    collapsed,
    setCollapsed,
  ] = useState(false);

  return (
    <RequireAuth>
      <div
        className="
          flex min-h-screen
          bg-slate-50
        "
      >
        <AppSidebar
          mobileOpen={mobileOpen}
          collapsed={collapsed}
          onCloseMobile={() => {
            setMobileOpen(false);
          }}
          onToggleCollapsed={() => {
            setCollapsed(
              (current) => !current,
            );
          }}
        />

        <div
          className="
            min-w-0 flex-1
          "
        >
          <AppHeader
            onOpenMobile={() => {
              setMobileOpen(true);
            }}
          />

          <main className="p-4 sm:p-6">
            {children}
          </main>
        </div>
      </div>
    </RequireAuth>
  );
}