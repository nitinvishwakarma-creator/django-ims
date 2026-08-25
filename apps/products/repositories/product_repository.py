from mongoengine.queryset.visitor import Q

from apps.products.models import Product


class ProductRepository:

    @staticmethod
    def get_by_id(*, organization, product_id):
        """
        Retrieve a product by ID within an organization.
        """

        return Product.objects(
            organization=organization,
            id=product_id,
        ).first()

    @staticmethod
    def get_by_sku(*, organization, sku):
        """
        Retrieve a product by SKU within an organization.
        """

        return Product.objects(
            organization=organization,
            sku=sku,
        ).first()

    @staticmethod
    def list_by_organization(*, organization):
        """
        Return all products belonging to an organization.
        """

        return Product.objects(
            organization=organization,
        ).order_by("-created_at")

    @staticmethod
    def list_active(*, organization):
        """
        Return active products belonging to an organization.
        """

        return Product.objects(
            organization=organization,
            is_active=True,
        ).order_by("-created_at")

    @staticmethod
    def search_by_name(*, organization, search_term):
        """
        Search products by name within an organization.
        """

        return Product.objects(
            organization=organization,
            name__icontains=search_term,
        ).order_by("-created_at")

    @staticmethod
    def search(*, organization, search_term):
        """
        Search products by SKU or product name
        within an organization.
        """

        return Product.objects(
            Q(
                organization=organization
            )
            & (
                Q(sku__icontains=search_term)
                | Q(name__icontains=search_term)
            )
        ).order_by("-created_at")