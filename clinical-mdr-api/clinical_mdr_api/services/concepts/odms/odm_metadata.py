from neomodel import db

from common.utils import get_db_result_as_dict, validate_max_skip_clause


def _query(
    node_name: str,
    fields: list[str],
    page_size: int,
    page_number: int,
    search: str | None,
) -> tuple[list[dict[str, str]], int]:
    """
    Generic query function to get paginated results from a given node.

    :param node_name: Name of the node to query
    :param fields: List of fields to return
    :param page_size: Number of items per page
    :param page_number: Page number
    :param search: Search term to filter results
    :return: Tuple of list of results and total count
    """
    validate_max_skip_clause(page_number=page_number, page_size=page_size)

    params: dict[str, str | int] = {
        "skip": page_size * (page_number - 1),
        "limit": page_size,
    }

    where_stmt = ""

    for key in fields:
        if search is None:
            continue

        if where_stmt:
            where_stmt += f"OR toLower(n.{key}) CONTAINS ${key} "
            params[key] = search.casefold()
        else:
            where_stmt += f"WHERE toLower(n.{key}) CONTAINS ${key} "
            params[key] = search.casefold()

    results, columns = db.cypher_query(
        f"""
        MATCH (n:{node_name})
        {where_stmt}
        RETURN {', '.join([f'n.{field} AS {field}' for field in fields])}
        ORDER BY n.{fields[0]}
        SKIP $skip LIMIT $limit
        """,
        params=params,
    )

    total, _ = db.cypher_query(
        f"MATCH (n:{node_name}) {where_stmt} RETURN COUNT(n) as total", params=params
    )

    return [get_db_result_as_dict(result, columns) for result in results], total[0][0]


def get_odm_aliases(
    page_size: int, page_number: int, search: str | None
) -> tuple[list[dict[str, str]], int]:
    """
    Get all ODM Aliases.

    :param page_size: Number of items per page
    :param page_number: Page number
    :param search: Search term to filter results
    :return: List of ODM Aliases
    """

    return _query("OdmAlias", ["name", "context"], page_size, page_number, search)


def get_odm_descriptions(
    page_size: int, page_number: int, search: str | None
) -> tuple[list[dict[str, str]], int]:
    """
    Get all ODM Descriptions.

    :param page_size: Number of items per page
    :param page_number: Page number
    :param search: Search term to filter results
    :return: List of ODM Descriptions
    """

    return _query(
        "OdmDescription",
        ["name", "language", "description", "instruction", "sponsor_instruction"],
        page_size,
        page_number,
        search,
    )


def get_odm_formal_expressions(
    page_size: int, page_number: int, search: str | None
) -> tuple[list[dict[str, str]], int]:
    """
    Get all ODM Formal Expressions.

    :param page_size: Number of items per page
    :param page_number: Page number
    :param search: Search term to filter results
    :return: List of ODM Formal Expressions
    """

    return _query(
        "OdmFormalExpression",
        ["context", "expression"],
        page_size,
        page_number,
        search,
    )
