import type {
  LucideIcon,
} from "lucide-react";

import {
  Banknote,
  Boxes,
  Building2,
  ChartNoAxesCombined,
  ClipboardList,
  FileText,
  LayoutDashboard,
  Package,
  ReceiptText,
  Settings,
  ShieldCheck,
  ShoppingCart,
  Tags,
  Truck,
  Undo2,
  UserRoundCog,
  Users,
  Warehouse,
} from "lucide-react";

export interface NavigationItem {
  label: string;
  href: string;
  icon: LucideIcon;
  permission?: string;
}

export interface NavigationSection {
  label: string;
  items: NavigationItem[];
}

export const navigationSections:
  NavigationSection[] = [
    {
      label: "Overview",
      items: [
        {
          label: "Dashboard",
          href: "/dashboard",
          icon: LayoutDashboard,
        },
      ],
    },

    {
      label: "Inventory",
      items: [
        {
          label: "Products",
          href: "/products",
          icon: Package,
          permission: "products.read",
        },
        {
          label: "Warehouses",
          href: "/warehouses",
          icon: Warehouse,
          permission: "warehouses.read",
        },
        {
          label: "Stock",
          href: "/inventory",
          icon: Boxes,
          permission: "inventory.read",
        },
      ],
    },

    {
      label: "Sales",
      items: [
        {
          label: "Customers",
          href: "/customers",
          icon: Users,
          permission: "customers.read",
        },
        {
          label: "Sales Orders",
          href: "/sales-orders",
          icon: ShoppingCart,
          permission: "sales_orders.read",
        },
        {
          label: "Invoices",
          href: "/invoices",
          icon: ReceiptText,
          permission: "invoices.read",
        },
        {
          label: "Sales Returns",
          href: "/sales-returns",
          icon: Undo2,
          permission: "sales_returns.read",
        },
        {
          label: "Credit Notes",
          href: "/credit-notes",
          icon: FileText,
          permission: "credit_notes.read",
        },
      ],
    },

    {
      label: "Purchasing",
      items: [
        {
          label: "Suppliers",
          href: "/suppliers",
          icon: Truck,
          permission: "suppliers.read",
        },
        {
          label: "Purchase Orders",
          href: "/purchase-orders",
          icon: ClipboardList,
          permission: "purchase_orders.read",
        },
        {
          label: "Vendor Bills",
          href: "/vendor-bills",
          icon: FileText,
          permission: "vendor_bills.read",
        },
        {
          label: "Purchase Returns",
          href: "/purchase-returns",
          icon: Undo2,
          permission: "purchase_returns.read",
        },
      ],
    },

    {
      label: "Finance",
      items: [
        {
          label: "Accounting",
          href: "/accounting",
          icon: ChartNoAxesCombined,
          permission: "accounting_reports.read",
        },
        {
          label: "Banking",
          href: "/banking",
          icon: Banknote,
          permission: "bank_accounts.read",
        },
      ],
    },

    {
      label: "Administration",
      items: [
        {
          label: "Organization",
          href: "/settings/organization",
          icon: Building2,
          permission: "organizations.update",
        },
        {
          label: "Users",
          href: "/settings/users",
          icon: UserRoundCog,
          permission: "users.read",
        },
        {
          label: "Roles",
          href: "/settings/roles",
          icon: ShieldCheck,
          permission: "roles.read",
        },
        {
          label: "Permissions",
          href: "/settings/permissions",
          icon: Tags,
          permission: "permissions.read",
        },
        {
          label: "Settings",
          href: "/settings",
          icon: Settings,
        },
      ],
    },
  ];