import graphene
from django.core.exceptions import ValidationError

from saleor.core.tracing import traced_atomic_transaction

from ....core.permissions import ProductPermissions
from ....product import models
from ....product.error_codes import ProductErrorCode
from ...core.mutations import ModelDeleteMutation, ModelMutation
from ...core.types import ProductError
from ...core.utils import validate_slug_and_generate_if_needed
from ..types import ProductTag


class ProductTagInput(graphene.InputObjectType):
    name = graphene.String(description="Name of the product name.")
    slug = graphene.String(description="Product name slug.")
    is_active = graphene.Boolean(description="Determines if the product tag is active")
    has_variants = graphene.Boolean(
        description=(
            "Determines if product of this tag has multiple variants. This option "
            "mainly simplifies product management in the dashboard. There is always at "
            "least one variant created under the hood."
        )
    )


class ProductTagCreate(ModelMutation):
    class Arguments:
        input = ProductTagInput(
            required=True, description="Fields required to create a product tag."
        )

    class Meta:
        description = "Creates a new product tag."
        model = models.ProductTag
        object_type = ProductTag
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = ProductError
        error_type_field = "product_errors"

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)

        try:
            cleaned_input = validate_slug_and_generate_if_needed(
                instance, "name", cleaned_input
            )
        except ValidationError as error:
            error.code = ProductErrorCode.REQUIRED.value
            raise ValidationError({"slug": error})

        return cleaned_input


class ProductTagUpdate(ProductTagCreate):
    class Arguments:
        id = graphene.ID(required=True, description="ID of a product tag to update.")
        input = ProductTagInput(
            required=True, description="Fields required to update a product tag."
        )

    class Meta:
        description = "Updates an existing product tag."
        model = models.ProductTag
        object_type = ProductTag
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = ProductError
        error_type_field = "product_errors"


class ProductTagDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of a product tag to delete.")

    class Meta:
        description = "Deletes a product tag."
        model = models.ProductTag
        object_type = ProductTag
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = ProductError
        error_type_field = "product_errors"
