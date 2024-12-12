# https://github.com/mirumee/ariadne/issues/287#issuecomment-1424088938

from collections.abc import Iterable

from graphql import GraphQLResolveInfo
from graphql.language import (FieldNode, FragmentSpreadNode,
                              InlineFragmentNode, SelectionNode)
from sqlalchemy.orm.attributes import InstrumentedAttribute


def selected_fields(info: GraphQLResolveInfo, model) -> list[InstrumentedAttribute]:
    """
    Extracts selected fields from a GraphQL query and maps them to the attributes of the given SQLAlchemy model.

    Args:
        info (GraphQLResolveInfo): The GraphQL query resolution information.
        model: The SQLAlchemy model to map the fields to.

    Returns:
        list[InstrumentedAttribute]: A list of SQLAlchemy model attributes corresponding to the selected fields.
    """
    names: set[str] = set()
    for node in info.field_nodes:
        if node.selection_set is None: continue
        names.update(_fields_from_selections(info, node.selection_set.selections))
    return [getattr(model, field) for field in names]


def _fields_from_selections(
    info: GraphQLResolveInfo, selections: Iterable[SelectionNode]
) -> list[str]:
    """
    Recursively extracts field names from GraphQL selections.

    Args:
        info (GraphQLResolveInfo): The GraphQL query resolution information.
        selections (Iterable[SelectionNode]): The selection nodes from the GraphQL query.

    Returns:
        list[str]: A list of field names extracted from the selections.

    Raises:
        NotImplementedError: If an unsupported selection type is encountered.
    """
    names: list[str] = []
    for selection in selections:
        match selection:
            case FieldNode():
                names.append(selection.name.value)
                if selection.selection_set is not None:
                    names.extend(
                        _fields_from_selections(
                            info, selection.selection_set.selections
                        )
                    )
            case InlineFragmentNode():
                names.extend(
                    _fields_from_selections(info, selection.selection_set.selections)
                )
            case FragmentSpreadNode():
                fragment = info.fragments[selection.name.value]
                names.extend(
                    _fields_from_selections(info, fragment.selection_set.selections)
                )
            case _:
                raise NotImplementedError(f"field type {type(selection)} not supported")
    return names