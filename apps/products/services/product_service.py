from decimal import Decimal

from mongoengine.errors import NotUniqueError

from apps.products.models import Product, Category


class ProductService:

    @staticmethod
    def create_product(
        *,
        organization,
        sku,
        name,
        category,
        unit,
        cost_price=0,
        selling_price=0,
        description="",
        brand="",
        barcode="",
    ):
        """
        Create a new product for an organization.
        """

        if not organization:
            raise ValueError("Organization is required.")

        if not sku:
            raise ValueError("SKU is required.")

        if not name:
            raise ValueError("Product name is required.")

        if not category:
            raise ValueError("Category is required.")

        if category.organization.id != organization.id:
            raise ValueError(
                "Category does not belong to this organization."
            )

        cost_price = Decimal(str(cost_price))
        selling_price = Decimal(str(selling_price))

        if cost_price < 0:
            raise ValueError(
                "Cost price cannot be negative."
            )

        if selling_price < 0:
            raise ValueError(
                "Selling price cannot be negative."
            )

        product = Product(
            organization=organization,
            sku=sku,
            name=name,
            description=description,
            category=category,
            brand=brand,
            unit=unit,
            cost_price=cost_price,
            selling_price=selling_price,
            barcode=barcode,
        )

        try:
            product.save()
        except NotUniqueError:
            raise ValueError(
                f"Product with SKU '{sku}' already exists "
                "in this organization."
            )

        return product