ROLE_CATALOG = {

    "admin": {
        "name": "Admin",
        "description": "Full access to the organization.",
        "permissions": [
            "products.read",
            "products.create",
            "products.update",
            "products.delete",
        ],
    },

    "warehouse_manager": {
        "name": "Warehouse Manager",
        "description": "Manages warehouse and inventory operations.",
        "permissions": [
            "products.read",
        ],
    },

    "sales_manager": {
        "name": "Sales Manager",
        "description": "Manages customers and sales operations.",
        "permissions": [
            "products.read",
        ],
    },

    "purchase_manager": {
        "name": "Purchase Manager",
        "description": "Manages suppliers and purchase operations.",
        "permissions": [
            "products.read",
        ],
    },

}