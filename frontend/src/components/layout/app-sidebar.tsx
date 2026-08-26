"use client";

import Link from "next/link";

import {
  usePathname,
} from "next/navigation";

import {
  Boxes,
  PanelLeftClose,
  PanelLeftOpen,
  X,
} from "lucide-react";

import {
  navigationSections,
} from "@/config/navigation";

import {
  useAuth,
} from "@/features/auth/auth-context";

import {
  hasPermission,
} from "@/lib/authorization/permissions";

interface AppSidebarProps {
  mobileOpen: boolean;
  collapsed: boolean;
  onCloseMobile: () => void;
  onToggleCollapsed: () => void;
}

export default function AppSidebar({
  mobileOpen,
  collapsed,
  onCloseMobile,
  onToggleCollapsed,
}: AppSidebarProps) {
  const pathname = usePathname();

  const {
    authentication,
  } = useAuth();

  const permissions =
    authentication
      ?.role
      .permissions
    ??
    [];

  const visibleSections =
    navigationSections
      .map((section) => ({
        ...section,

        items: section.items.filter(
          (item) =>
            hasPermission(
              permissions,
              item.permission,
            ),
        ),
      }))
      .filter(
        (section) =>
          section.items.length > 0,
      );

  return (
    <>
      {mobileOpen && (
        <button
          type="button"
          aria-label="Close navigation"
          onClick={onCloseMobile}
          className="
            fixed inset-0 z-40
            bg-slate-950/40 backdrop-blur-sm
            lg:hidden
          "
        />
      )}

      <aside
        className={`
          fixed inset-y-0 left-0 z-50
          flex w-72 flex-col
          border-r border-slate-200
          bg-white transition-all duration-200
          lg:static lg:z-auto
          ${
            mobileOpen
              ? "translate-x-0"
              : "-translate-x-full lg:translate-x-0"
          }
          ${
            collapsed
              ? "lg:w-20"
              : "lg:w-72"
          }
        `}
      >
        <div
          className="
            flex h-16 items-center
            border-b border-slate-200
            px-4
          "
        >
          <div
            className="
              flex min-w-0 flex-1
              items-center gap-3
            "
          >
            <div
              className="
                flex size-10 shrink-0
                items-center justify-center
                rounded-xl bg-blue-600
                text-white
              "
            >
              <Boxes size={22} />
            </div>

            {!collapsed && (
              <div className="min-w-0">
                <p
                  className="
                    truncate font-bold
                    text-slate-900
                  "
                >
                  Django IMS
                </p>

                <p
                  className="
                    truncate text-xs
                    text-slate-500
                  "
                >
                  Inventory Management
                </p>
              </div>
            )}
          </div>

          <button
            type="button"
            aria-label="Close navigation"
            onClick={onCloseMobile}
            className="
              rounded-lg p-2 text-slate-500
              hover:bg-slate-100
              lg:hidden
            "
          >
            <X size={20} />
          </button>
        </div>

        <nav
          className="
            flex-1 overflow-y-auto
            px-3 py-4
          "
        >
          {visibleSections.map(
            (section) => (
              <div
                key={section.label}
                className="mb-6"
              >
                {!collapsed && (
                  <p
                    className="
                      mb-2 px-3 text-xs
                      font-semibold uppercase
                      tracking-wider
                      text-slate-400
                    "
                  >
                    {section.label}
                  </p>
                )}

                <div className="space-y-1">
                  {section.items.map(
                    (item) => {
                      const active =
                        pathname
                          ===
                          item.href
                        ||
                        pathname.startsWith(
                          `${item.href}/`,
                        );

                      const Icon =
                        item.icon;

                      return (
                        <Link
                          key={item.href}
                          href={item.href}
                          title={
                            collapsed
                              ? item.label
                              : undefined
                          }
                          onClick={
                            onCloseMobile
                          }
                          className={`
                            flex items-center
                            rounded-lg px-3 py-2.5
                            text-sm font-medium
                            transition
                            ${
                              collapsed
                                ? "lg:justify-center"
                                : "gap-3"
                            }
                            ${
                              active
                                ? "bg-blue-50 text-blue-700"
                                : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                            }
                          `}
                        >
                          <Icon
                            size={19}
                            className="shrink-0"
                          />

                          {!collapsed && (
                            <span>
                              {item.label}
                            </span>
                          )}
                        </Link>
                      );
                    },
                  )}
                </div>
              </div>
            ),
          )}
        </nav>

        <div
          className="
            hidden border-t
            border-slate-200 p-3
            lg:block
          "
        >
          <button
            type="button"
            onClick={onToggleCollapsed}
            className="
              flex w-full items-center
              justify-center gap-2
              rounded-lg px-3 py-2
              text-sm font-medium
              text-slate-600
              hover:bg-slate-100
            "
          >
            {collapsed ? (
              <PanelLeftOpen size={19} />
            ) : (
              <>
                <PanelLeftClose size={19} />
                <span>Collapse sidebar</span>
              </>
            )}
          </button>
        </div>
      </aside>
    </>
  );
}