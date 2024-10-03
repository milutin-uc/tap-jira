"""Stream type classes for tap-jira."""

from __future__ import annotations

import functools
import operator
import typing as t
from http import HTTPStatus

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_jira.client import JiraStream

if t.TYPE_CHECKING:
    import requests
    from singer_sdk.helpers.types import Context, Record

PropertiesList = th.PropertiesList
Property = th.Property
ObjectType = th.ObjectType
DateTimeType = th.DateTimeType
DateType = th.DateType
StringType = th.StringType
ArrayType = th.ArrayType
BooleanType = th.BooleanType
IntegerType = th.IntegerType
NumberType = th.NumberType


ADFRootBlockNode = ObjectType(
    Property("type", StringType),
    Property("version", IntegerType),
    Property(
        "content",
        ArrayType(ObjectType(additional_properties=True)),
    ),
)


class UsersStream(JiraStream):
    """Users stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-users/#api-rest-api-3-user-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    name = "users"
    path = "/users/search"
    primary_keys = ("accountId",)
    replication_key = "accountId"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[*]"

    schema = PropertiesList(
        Property("self", StringType),
        Property("key", StringType),
        Property("accountId", StringType),
        Property("accountType", StringType),
        Property("emailAddress", StringType),
        Property("name", StringType),
        Property(
            "avatarUrls",
            ObjectType(
                Property("48x48", StringType),
                Property("24x24", StringType),
                Property("16x16", StringType),
                Property("32x32", StringType),
            ),
        ),
        Property("displayName", StringType),
        Property("active", BooleanType),
        Property("timeZone", StringType),
        Property("locale", StringType),
    ).to_dict()

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: t.Any | None,  # noqa: ANN401
    ) -> t.Any | None:  # noqa: ANN401
        """Return a token for identifying next page or None if no more pages."""
        # If pagination is required, return a token which can be used to get the
        #       next page. If this is the final page, return "None" to end the
        #       pagination loop.
        resp_json = response.json()
        if previous_token is None:
            previous_token = 0

        page = resp_json
        if len(page) == 0:
            return None

        return previous_token + len(page)


class FieldStream(JiraStream):
    """Field stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/#api-rest-api-3-field-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "fields"
    path = "/field"
    primary_keys = ("id",)
    replication_key = "id"
    replication_method = "INCREMENTAL"
    instance_name = ""

    schema = PropertiesList(
        Property("id", StringType),
        Property("key", StringType),
        Property("name", StringType),
        Property("untranslatedName", StringType),
        Property("custom", BooleanType),
        Property("orderable", BooleanType),
        Property("navigable", BooleanType),
        Property("searchable", BooleanType),
        Property("clauseNames", ArrayType(StringType)),
        Property(
            "scope",
            ObjectType(
                Property("type", StringType),
                Property(
                    "project",
                    ObjectType(
                        Property("id", StringType),
                    ),
                ),
            ),
        ),
        Property(
            "schema",
            ObjectType(
                Property("type", StringType),
                Property("system", StringType),
                Property("items", StringType),
                Property("custom", StringType),
                Property("customId", IntegerType),
                Property(
                    "configuration",
                    ObjectType(
                        Property("customRenderer", BooleanType),
                        Property("readOnly", BooleanType),
                        Property("environment", StringType),
                        Property("atlassian_team", BooleanType),
                    ),
                ),
            ),
        ),
    ).to_dict()


class ServerInfoStream(JiraStream):
    """Server info stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-server-info/#api-rest-api-3-serverinfo-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    name = "server_info"
    path = "/serverInfo"
    primary_keys = ("baseUrl",)
    replication_key = "serverTime"
    replication_method = "INCREMENTAL"
    instance_name = ""

    schema = PropertiesList(
        Property("baseUrl", StringType),
        Property("version", StringType),
        Property("versionNumbers", ArrayType(IntegerType)),
        Property("deploymentType", StringType),
        Property("buildNumber", IntegerType),
        Property("buildDate", StringType),
        Property("serverTime", StringType),
        Property("scmInfo", StringType),
        Property("serverTitle", StringType),
        Property(
            "defaultLocale",
            ObjectType(
                Property("locale", StringType),
            ),
        ),
    ).to_dict()


class IssueTypeStream(JiraStream):
    """Issue type stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-types/#api-rest-api-3-issuetype-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "issue_types"
    path = "/issuetype"
    primary_keys = ("id",)
    replication_key = "id"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[*]"  # Or override `parse_response`.
    instance_name = ""

    schema = PropertiesList(
        Property("self", StringType),
        Property("id", StringType),
        Property("description", StringType),
        Property("iconUrl", StringType),
        Property("name", StringType),
        Property("untranslatedName", StringType),
        Property("subtask", BooleanType),
        Property("avatarId", IntegerType),
        Property("hierarchyLevel", IntegerType),
        Property(
            "scope",
            ObjectType(
                Property("type", StringType),
                Property(
                    "project",
                    ObjectType(
                        Property("id", StringType),
                        Property("key", StringType),
                        Property("name", StringType),
                    ),
                ),
            ),
        ),
    ).to_dict()


class WorkflowStatusStream(JiraStream):
    """Workflow status stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-statuses/#api-rest-api-3-status-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    name = "workflow_statuses"
    path = "/status"
    primary_keys = ("id",)
    replication_key = "self"
    replication_method = "INCREMENTAL"
    instance_name = ""

    schema = PropertiesList(
        Property("self", StringType),
        Property("description", StringType),
        Property("iconUrl", StringType),
        Property("name", StringType),
        Property("untranslatedName", StringType),
        Property("id", StringType),
        Property(
            "statusCategory",
            ObjectType(
                Property("self", StringType),
                Property("id", IntegerType),
                Property("key", StringType),
                Property("colorName", StringType),
                Property("name", StringType),
            ),
        ),
        Property(
            "scope",
            ObjectType(
                Property("type", StringType),
                Property(
                    "project",
                    ObjectType(
                        Property("id", StringType),
                    ),
                ),
            ),
        ),
    ).to_dict()


class ProjectStream(JiraStream):
    """Project stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "projects"
    path = "/project/search"
    primary_keys = ("id",)
    replication_key = "id"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[values][*]"  # Or override `parse_response`.
    instance_name = "values"

    schema = PropertiesList(
        Property("expand", StringType),
        Property("self", StringType),
        Property("id", StringType),
        Property("key", StringType),
        Property("name", StringType),
        Property(
            "avatarUrls",
            ObjectType(
                Property("48x48", StringType),
                Property("24x24", StringType),
                Property("16x16", StringType),
                Property("32x32", StringType),
            ),
        ),
        Property("projectTypeKey", StringType),
        Property("simplified", BooleanType),
        Property("style", StringType),
        Property("isPrivate", BooleanType),
        Property(
            "properties",
            ObjectType(
                Property("propertyKey", StringType),
            ),
        ),
        Property("entityId", StringType),
        Property("uuid", StringType),
        Property(
            "projectCategory",
            ObjectType(
                Property("self", StringType),
                Property("id", StringType),
                Property("name", StringType),
                Property("description", StringType),
            ),
        ),
        Property(
            "insight",
            ObjectType(
                Property("totalIssueCount", IntegerType),
                Property("lastIssueUpdateTime", StringType),
            ),
        ),
    ).to_dict()


class IssueStream(JiraStream):
    """Issue stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "issues"
    path = "/search"
    primary_keys = ("id",)
    replication_key = "id"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[issues][*]"  # Or override `parse_response`.
    instance_name = "issues"

    __content_schema = ArrayType(
        ObjectType(
            Property("version", IntegerType),
            Property("text", StringType),
            Property("type", StringType),
            Property(
                "attrs",
                ObjectType(
                    Property("href", StringType),
                    Property("colspan", IntegerType),
                    Property("alt", StringType),
                    Property("timestamp", StringType),
                    Property(
                        "colwidth",
                        ArrayType(IntegerType),
                    ),
                    Property("language", StringType),
                    Property("background", StringType),
                    Property(
                        "isNumberColumnEnabled",
                        BooleanType,
                    ),
                    Property("localId", StringType),
                    Property("color", StringType),
                    Property("panelType", StringType),
                    Property("level", IntegerType),
                    Property("accessLevel", StringType),
                    Property("style", StringType),
                    Property("order", IntegerType),
                    Property("text", StringType),
                    Property("shortName", StringType),
                    Property("url", StringType),
                    Property("layout", StringType),
                    Property("id", StringType),
                    Property("type", StringType),
                    Property("collection", StringType),
                    Property("width", NumberType),
                    Property("height", NumberType),
                    Property("occurrenceKey", StringType),
                ),
            ),
            Property(
                "marks",
                ArrayType(
                    ObjectType(
                        Property("type", StringType),
                        Property(
                            "attrs",
                            ObjectType(
                                Property(
                                    "href",
                                    StringType,
                                ),
                                Property(
                                    "colspan",
                                    IntegerType,
                                ),
                                Property(
                                    "alt",
                                    StringType,
                                ),
                                Property(
                                    "timestamp",
                                    StringType,
                                ),
                                Property(
                                    "colwidth",
                                    ArrayType(IntegerType),
                                ),
                                Property(
                                    "language",
                                    StringType,
                                ),
                                Property(
                                    "background",
                                    StringType,
                                ),
                                Property(
                                    "isNumberColumnEnabled",
                                    BooleanType,
                                ),
                                Property(
                                    "localId",
                                    StringType,
                                ),
                                Property(
                                    "color",
                                    StringType,
                                ),
                                Property(
                                    "panelType",
                                    StringType,
                                ),
                                Property(
                                    "level",
                                    IntegerType,
                                ),
                                Property(
                                    "accessLevel",
                                    StringType,
                                ),
                                Property(
                                    "style",
                                    StringType,
                                ),
                                Property(
                                    "order",
                                    IntegerType,
                                ),
                                Property(
                                    "text",
                                    StringType,
                                ),
                                Property(
                                    "shortName",
                                    StringType,
                                ),
                                Property(
                                    "url",
                                    StringType,
                                ),
                                Property(
                                    "layout",
                                    StringType,
                                ),
                                Property("id", StringType),
                                Property(
                                    "type",
                                    StringType,
                                ),
                                Property(
                                    "collection",
                                    StringType,
                                ),
                                Property(
                                    "width",
                                    NumberType,
                                ),
                                Property(
                                    "height",
                                    NumberType,
                                ),
                                Property(
                                    "occurrenceKey",
                                    StringType,
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    schema = PropertiesList(
        Property("expand", StringType),
        Property("id", StringType),
        Property("self", StringType),
        Property("key", StringType),
        Property(
            "fields",
            ObjectType(
                Property("statuscategorychangedate", StringType),
                Property(
                    "issuetype",
                    ObjectType(
                        Property("self", StringType),
                        Property("id", StringType),
                        Property("description", StringType),
                        Property("iconUrl", StringType),
                        Property("name", StringType),
                        Property("subtask", BooleanType),
                        Property("avatarId", IntegerType),
                        Property("entityId", StringType),
                        Property("hierarchyLevel", IntegerType),
                    ),
                ),
                Property(
                    "parent",
                    ObjectType(
                        Property("id", StringType),
                        Property("key", StringType),
                        Property("self", StringType),
                        Property(
                            "fields",
                            ObjectType(
                                Property("summary", StringType),
                                Property(
                                    "status",
                                    ObjectType(
                                        Property("description", StringType),
                                        Property("iconUrl", StringType),
                                        Property("id", StringType),
                                        Property("name", StringType),
                                        Property("self", StringType),
                                        Property(
                                            "statusCategory",
                                            ObjectType(
                                                Property("colorName", StringType),
                                                Property("id", IntegerType),
                                                Property("key", StringType),
                                                Property("name", StringType),
                                                Property("self", StringType),
                                            ),
                                        ),
                                    ),
                                ),
                                Property(
                                    "priority",
                                    ObjectType(
                                        Property("self", StringType),
                                        Property("iconUrl", StringType),
                                        Property("name", StringType),
                                        Property("id", StringType),
                                    ),
                                ),
                                Property(
                                    "issuetype",
                                    ObjectType(
                                        Property("self", StringType),
                                        Property("id", StringType),
                                        Property("description", StringType),
                                        Property("iconUrl", StringType),
                                        Property("name", StringType),
                                        Property("subtask", BooleanType),
                                        Property("avatarId", IntegerType),
                                        Property("entityId", StringType),
                                        Property("hierarchyLevel", IntegerType),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                Property("timespent", IntegerType),
                Property(
                    "project",
                    ObjectType(
                        Property("self", StringType),
                        Property("id", StringType),
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("projectTypeKey", StringType),
                        Property("simplified", BooleanType),
                        Property(
                            "avatarUrls",
                            ObjectType(
                                Property("48x48", StringType),
                                Property("24x24", StringType),
                                Property("16x16", StringType),
                                Property("32x32", StringType),
                            ),
                        ),
                    ),
                ),
                Property(
                    "fixVersions",
                    ArrayType(
                        ObjectType(
                            Property("id", StringType),
                            Property("archived", BooleanType),
                            Property("name", StringType),
                            Property("released", BooleanType),
                            Property("self", StringType),
                        ),
                    ),
                ),
                Property("aggregatetimespent", IntegerType),
                Property(
                    "resolution",
                    ObjectType(
                        Property("description", StringType),
                        Property("id", StringType),
                        Property("name", StringType),
                        Property("self", StringType),
                    ),
                ),
                Property("resolutiondate", StringType),
                Property("workratio", IntegerType),
                Property(
                    "watches",
                    ObjectType(
                        Property("self", StringType),
                        Property("watchCount", IntegerType),
                        Property("isWatching", BooleanType),
                    ),
                ),
                Property("issuerestriction", StringType),
                Property("lastViewed", StringType),
                Property("created", StringType),
                Property(
                    "priority",
                    ObjectType(
                        Property("self", StringType),
                        Property("iconUrl", StringType),
                        Property("name", StringType),
                        Property("id", StringType),
                    ),
                ),
                Property("labels", ArrayType(StringType)),
                Property("timeestimate", IntegerType),
                Property("aggregatetimeoriginalestimate", IntegerType),
                Property("versions", ArrayType(StringType)),
                Property(
                    "issuelinks",
                    ArrayType(
                        ObjectType(
                            Property("id", StringType),
                            Property(
                                "outwardIssue",
                                ObjectType(
                                    Property(
                                        "fields",
                                        ObjectType(
                                            Property(
                                                "issuetype",
                                                ObjectType(
                                                    Property("avatarId", IntegerType),
                                                    Property("description", StringType),
                                                    Property("entityId", StringType),
                                                    Property(
                                                        "hierarchyLevel",
                                                        IntegerType,
                                                    ),
                                                    Property("iconUrl", StringType),
                                                    Property("id", StringType),
                                                    Property("name", StringType),
                                                    Property("self", StringType),
                                                    Property("subtask", BooleanType),
                                                ),
                                            ),
                                            Property(
                                                "priority",
                                                ObjectType(
                                                    Property("iconUrl", StringType),
                                                    Property("id", StringType),
                                                    Property("name", StringType),
                                                    Property("self", StringType),
                                                ),
                                            ),
                                            Property(
                                                "status",
                                                ObjectType(
                                                    Property("description", StringType),
                                                    Property("iconUrl", StringType),
                                                    Property("id", StringType),
                                                    Property("name", StringType),
                                                    Property("self", StringType),
                                                    Property(
                                                        "statusCategory",
                                                        ObjectType(
                                                            Property(
                                                                "colorName",
                                                                StringType,
                                                            ),
                                                            Property("id", IntegerType),
                                                            Property("key", StringType),
                                                            Property(
                                                                "name",
                                                                StringType,
                                                            ),
                                                            Property(
                                                                "self",
                                                                StringType,
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                            Property("summary", StringType),
                                        ),
                                    ),
                                    Property("id", StringType),
                                    Property("key", StringType),
                                    Property("self", StringType),
                                ),
                            ),
                            Property(
                                "inwardIssue",
                                ObjectType(
                                    Property(
                                        "fields",
                                        ObjectType(
                                            Property(
                                                "issuetype",
                                                ObjectType(
                                                    Property("avatarId", IntegerType),
                                                    Property("description", StringType),
                                                    Property("entityId", StringType),
                                                    Property(
                                                        "hierarchyLevel",
                                                        IntegerType,
                                                    ),
                                                    Property("iconUrl", StringType),
                                                    Property("id", StringType),
                                                    Property("name", StringType),
                                                    Property("self", StringType),
                                                    Property("subtask", BooleanType),
                                                ),
                                            ),
                                            Property(
                                                "priority",
                                                ObjectType(
                                                    Property("iconUrl", StringType),
                                                    Property("id", StringType),
                                                    Property("name", StringType),
                                                    Property("self", StringType),
                                                ),
                                            ),
                                            Property(
                                                "status",
                                                ObjectType(
                                                    Property("description", StringType),
                                                    Property("iconUrl", StringType),
                                                    Property("id", StringType),
                                                    Property("name", StringType),
                                                    Property("self", StringType),
                                                    Property(
                                                        "statusCategory",
                                                        ObjectType(
                                                            Property(
                                                                "colorName",
                                                                StringType,
                                                            ),
                                                            Property("id", IntegerType),
                                                            Property("key", StringType),
                                                            Property(
                                                                "name",
                                                                StringType,
                                                            ),
                                                            Property(
                                                                "self",
                                                                StringType,
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                            Property("summary", StringType),
                                        ),
                                    ),
                                    Property("id", StringType),
                                    Property("key", StringType),
                                    Property("self", StringType),
                                ),
                            ),
                            Property("self", StringType),
                            Property(
                                "type",
                                ObjectType(
                                    Property("id", StringType),
                                    Property("inward", StringType),
                                    Property("name", StringType),
                                    Property("outward", StringType),
                                    Property("self", StringType),
                                ),
                            ),
                        ),
                    ),
                ),
                Property(
                    "assignee",
                    ObjectType(
                        Property("self", StringType),
                        Property("accountId", StringType),
                        Property(
                            "avatarUrls",
                            ObjectType(
                                Property("48x48", StringType),
                                Property("24x24", StringType),
                                Property("16x16", StringType),
                                Property("32x32", StringType),
                            ),
                        ),
                        Property("displayName", StringType),
                        Property("active", BooleanType),
                        Property("timeZone", StringType),
                        Property("accountType", StringType),
                        Property("emailAddress", StringType),
                    ),
                ),
                Property("updated", StringType),
                Property(
                    "status",
                    ObjectType(
                        Property("self", StringType),
                        Property("description", StringType),
                        Property("iconUrl", StringType),
                        Property("name", StringType),
                        Property("id", StringType),
                        Property(
                            "statusCategory",
                            ObjectType(
                                Property("self", StringType),
                                Property("id", IntegerType),
                                Property("key", StringType),
                                Property("colorName", StringType),
                                Property("name", StringType),
                            ),
                        ),
                    ),
                ),
                Property(
                    "components",
                    ArrayType(
                        ObjectType(
                            Property("self", StringType),
                            Property("id", StringType),
                            Property("name", StringType),
                        ),
                    ),
                ),
                Property("timeoriginalestimate", IntegerType),
                Property(
                    "description",
                    ObjectType(
                        Property("version", IntegerType),
                        Property("text", StringType),
                        Property("type", StringType),
                        Property(
                            "content",
                            ArrayType(
                                ObjectType(
                                    Property("version", IntegerType),
                                    Property("text", StringType),
                                    Property("type", StringType),
                                    Property(
                                        "attrs",
                                        ObjectType(
                                            Property("href", StringType),
                                            Property("language", StringType),
                                            Property("timestamp", StringType),
                                            Property("colspan", IntegerType),
                                            Property("alt", StringType),
                                            Property(
                                                "colwidth",
                                                ArrayType(IntegerType),
                                            ),
                                            Property("background", StringType),
                                            Property("color", StringType),
                                            Property(
                                                "isNumberColumnEnabled",
                                                BooleanType,
                                            ),
                                            Property("localId", StringType),
                                            Property("panelType", StringType),
                                            Property("level", IntegerType),
                                            Property("accessLevel", StringType),
                                            Property("style", StringType),
                                            Property("text", StringType),
                                            Property("order", IntegerType),
                                            Property("shortName", StringType),
                                            Property("url", StringType),
                                            Property("layout", StringType),
                                            Property("id", StringType),
                                            Property("type", StringType),
                                            Property("collection", StringType),
                                            Property("width", NumberType),
                                            Property("height", NumberType),
                                            Property("occurrenceKey", StringType),
                                        ),
                                    ),
                                    Property(
                                        "marks",
                                        ArrayType(
                                            ObjectType(
                                                Property("type", StringType),
                                                Property(
                                                    "attrs",
                                                    ObjectType(
                                                        Property("href", StringType),
                                                        Property(
                                                            "colspan",
                                                            IntegerType,
                                                        ),
                                                        Property("alt", StringType),
                                                        Property(
                                                            "timestamp",
                                                            StringType,
                                                        ),
                                                        Property(
                                                            "language",
                                                            StringType,
                                                        ),
                                                        Property(
                                                            "colwidth",
                                                            ArrayType(IntegerType),
                                                        ),
                                                        Property(
                                                            "background",
                                                            StringType,
                                                        ),
                                                        Property(
                                                            "isNumberColumnEnabled",
                                                            BooleanType,
                                                        ),
                                                        Property("localId", StringType),
                                                        Property("color", StringType),
                                                        Property(
                                                            "panelType",
                                                            StringType,
                                                        ),
                                                        Property("level", IntegerType),
                                                        Property(
                                                            "accessLevel",
                                                            StringType,
                                                        ),
                                                        Property("style", StringType),
                                                        Property("order", IntegerType),
                                                        Property("text", StringType),
                                                        Property(
                                                            "shortName",
                                                            StringType,
                                                        ),
                                                        Property("url", StringType),
                                                        Property("layout", StringType),
                                                        Property("id", StringType),
                                                        Property("type", StringType),
                                                        Property(
                                                            "collection",
                                                            StringType,
                                                        ),
                                                        Property("width", NumberType),
                                                        Property("height", NumberType),
                                                        Property(
                                                            "occurrenceKey",
                                                            StringType,
                                                        ),
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                    Property(
                                        "content",
                                        ArrayType(
                                            ObjectType(
                                                Property("version", IntegerType),
                                                Property("text", StringType),
                                                Property("type", StringType),
                                                Property(
                                                    "attrs",
                                                    ObjectType(
                                                        Property("href", StringType),
                                                        Property(
                                                            "colspan",
                                                            IntegerType,
                                                        ),
                                                        Property("alt", StringType),
                                                        Property(
                                                            "timestamp",
                                                            StringType,
                                                        ),
                                                        Property(
                                                            "colwidth",
                                                            ArrayType(IntegerType),
                                                        ),
                                                        Property(
                                                            "language",
                                                            StringType,
                                                        ),
                                                        Property(
                                                            "background",
                                                            StringType,
                                                        ),
                                                        Property(
                                                            "isNumberColumnEnabled",
                                                            BooleanType,
                                                        ),
                                                        Property("localId", StringType),
                                                        Property("color", StringType),
                                                        Property(
                                                            "panelType",
                                                            StringType,
                                                        ),
                                                        Property("level", IntegerType),
                                                        Property(
                                                            "accessLevel",
                                                            StringType,
                                                        ),
                                                        Property("style", StringType),
                                                        Property("order", IntegerType),
                                                        Property("text", StringType),
                                                        Property(
                                                            "shortName",
                                                            StringType,
                                                        ),
                                                        Property("url", StringType),
                                                        Property("layout", StringType),
                                                        Property("id", StringType),
                                                        Property("type", StringType),
                                                        Property(
                                                            "collection",
                                                            StringType,
                                                        ),
                                                        Property("width", NumberType),
                                                        Property("height", NumberType),
                                                        Property(
                                                            "occurrenceKey",
                                                            StringType,
                                                        ),
                                                    ),
                                                ),
                                                Property(
                                                    "marks",
                                                    ArrayType(
                                                        ObjectType(
                                                            Property(
                                                                "type",
                                                                StringType,
                                                            ),
                                                            Property(
                                                                "attrs",
                                                                ObjectType(
                                                                    Property(
                                                                        "href",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "colspan",
                                                                        IntegerType,
                                                                    ),
                                                                    Property(
                                                                        "alt",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "timestamp",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "colwidth",
                                                                        ArrayType(
                                                                            IntegerType,
                                                                        ),
                                                                    ),
                                                                    Property(
                                                                        "language",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "background",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "isNumberColumnEnabled",
                                                                        BooleanType,
                                                                    ),
                                                                    Property(
                                                                        "localId",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "color",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "panelType",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "level",
                                                                        IntegerType,
                                                                    ),
                                                                    Property(
                                                                        "accessLevel",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "style",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "order",
                                                                        IntegerType,
                                                                    ),
                                                                    Property(
                                                                        "text",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "shortName",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "url",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "layout",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "id",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "type",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "collection",
                                                                        StringType,
                                                                    ),
                                                                    Property(
                                                                        "width",
                                                                        NumberType,
                                                                    ),
                                                                    Property(
                                                                        "height",
                                                                        NumberType,
                                                                    ),
                                                                    Property(
                                                                        "occurrenceKey",
                                                                        StringType,
                                                                    ),
                                                                ),
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                                Property(
                                                    "content",
                                                    ArrayType(
                                                        ObjectType(
                                                            Property(
                                                                "content",
                                                                ArrayType(
                                                                    ObjectType(
                                                                        Property(
                                                                            "version",
                                                                            IntegerType,
                                                                        ),
                                                                        Property(
                                                                            "text",
                                                                            StringType,
                                                                        ),
                                                                        Property(
                                                                            "type",
                                                                            StringType,
                                                                        ),
                                                                        Property(
                                                                            "content",
                                                                            __content_schema,
                                                                        ),
                                                                        Property(
                                                                            "attrs",
                                                                            ObjectType(
                                                                                Property(
                                                                                    "href",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "colspan",
                                                                                    IntegerType,
                                                                                ),
                                                                                Property(
                                                                                    "alt",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "timestamp",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "colwidth",
                                                                                    ArrayType(
                                                                                        IntegerType,
                                                                                    ),
                                                                                ),
                                                                                Property(
                                                                                    "language",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "background",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "isNumberColumnEnabled",
                                                                                    BooleanType,
                                                                                ),
                                                                                Property(
                                                                                    "localId",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "color",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "panelType",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "level",
                                                                                    IntegerType,
                                                                                ),
                                                                                Property(
                                                                                    "accessLevel",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "style",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "order",
                                                                                    IntegerType,
                                                                                ),
                                                                                Property(
                                                                                    "text",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "shortName",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "url",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "layout",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "id",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "type",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "collection",
                                                                                    StringType,
                                                                                ),
                                                                                Property(
                                                                                    "width",
                                                                                    NumberType,
                                                                                ),
                                                                                Property(
                                                                                    "height",
                                                                                    NumberType,
                                                                                ),
                                                                                Property(
                                                                                    "occurrenceKey",
                                                                                    StringType,
                                                                                ),
                                                                            ),
                                                                        ),
                                                                        Property(
                                                                            "marks",
                                                                            ArrayType(
                                                                                ObjectType(
                                                                                    Property(
                                                                                        "type",
                                                                                        StringType,
                                                                                    ),
                                                                                    Property(
                                                                                        "attrs",
                                                                                        ObjectType(
                                                                                            Property(
                                                                                                "href",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "colspan",
                                                                                                IntegerType,
                                                                                            ),
                                                                                            Property(
                                                                                                "alt",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "timestamp",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "colwidth",
                                                                                                ArrayType(
                                                                                                    IntegerType,
                                                                                                ),
                                                                                            ),
                                                                                            Property(
                                                                                                "language",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "background",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "isNumberColumnEnabled",
                                                                                                BooleanType,
                                                                                            ),
                                                                                            Property(
                                                                                                "localId",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "color",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "panelType",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "level",
                                                                                                IntegerType,
                                                                                            ),
                                                                                            Property(
                                                                                                "accessLevel",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "style",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "order",
                                                                                                IntegerType,
                                                                                            ),
                                                                                            Property(
                                                                                                "text",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "shortName",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "url",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "layout",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "id",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "type",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "collection",
                                                                                                StringType,
                                                                                            ),
                                                                                            Property(
                                                                                                "width",
                                                                                                NumberType,
                                                                                            ),
                                                                                            Property(
                                                                                                "height",
                                                                                                NumberType,
                                                                                            ),
                                                                                            Property(
                                                                                                "occurrenceKey",
                                                                                                StringType,
                                                                                            ),
                                                                                        ),
                                                                                    ),
                                                                                ),
                                                                            ),
                                                                        ),
                                                                    ),
                                                                ),
                                                            ),
                                                            Property(
                                                                "type",
                                                                StringType,
                                                            ),
                                                            Property(
                                                                "version",
                                                                IntegerType,
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                Property("timetracking", StringType),
                Property("security", StringType),
                Property("aggregatetimeestimate", IntegerType),
                Property("attachment", ArrayType(StringType)),
                Property("summary", StringType),
                Property(
                    "creator",
                    ObjectType(
                        Property("self", StringType),
                        Property("accountId", StringType),
                        Property("emailAddress", StringType),
                        Property(
                            "avatarUrls",
                            ObjectType(
                                Property("48x48", StringType),
                                Property("24x24", StringType),
                                Property("16x16", StringType),
                                Property("32x32", StringType),
                            ),
                        ),
                        Property("displayName", StringType),
                        Property("active", BooleanType),
                        Property("timeZone", StringType),
                        Property("accountType", StringType),
                    ),
                ),
                Property(
                    "subtasks",
                    ArrayType(
                        ObjectType(
                            Property("id", StringType),
                            Property("key", StringType),
                            Property("self", StringType),
                            Property(
                                "fields",
                                ObjectType(
                                    Property("summary", StringType),
                                    Property(
                                        "status",
                                        ObjectType(
                                            Property("self", StringType),
                                            Property("description", StringType),
                                            Property("iconUrl", StringType),
                                            Property("name", StringType),
                                            Property("id", StringType),
                                            Property(
                                                "statusCategory",
                                                ObjectType(
                                                    Property("self", StringType),
                                                    Property("id", IntegerType),
                                                    Property("key", StringType),
                                                    Property("colorName", StringType),
                                                    Property("name", StringType),
                                                ),
                                            ),
                                        ),
                                    ),
                                    Property(
                                        "priority",
                                        ObjectType(
                                            Property("self", StringType),
                                            Property("iconUrl", StringType),
                                            Property("name", StringType),
                                            Property("id", StringType),
                                        ),
                                    ),
                                    Property(
                                        "issuetype",
                                        ObjectType(
                                            Property("self", StringType),
                                            Property("id", StringType),
                                            Property("description", StringType),
                                            Property("iconUrl", StringType),
                                            Property("name", StringType),
                                            Property("subtask", BooleanType),
                                            Property("avatarId", IntegerType),
                                            Property("entityId", StringType),
                                            Property("hierarchyLevel", IntegerType),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                Property(
                    "reporter",
                    ObjectType(
                        Property("self", StringType),
                        Property("accountId", StringType),
                        Property("emailAddress", StringType),
                        Property(
                            "avatarUrls",
                            ObjectType(
                                Property("48x48", StringType),
                                Property("24x24", StringType),
                                Property("16x16", StringType),
                                Property("32x32", StringType),
                            ),
                        ),
                        Property("displayName", StringType),
                        Property("active", BooleanType),
                        Property("timeZone", StringType),
                        Property("accountType", StringType),
                    ),
                ),
                Property(
                    "aggregateprogress",
                    ObjectType(
                        Property("progress", IntegerType),
                        Property("total", IntegerType),
                        Property("percent", IntegerType),
                    ),
                ),
                Property(
                    "environment",
                    ObjectType(
                        Property("type", StringType),
                        Property(
                            "content",
                            ArrayType(
                                ObjectType(
                                    Property(
                                        "content",
                                        ArrayType(
                                            ObjectType(
                                                Property("text", StringType),
                                                Property("type", StringType),
                                            ),
                                        ),
                                    ),
                                    Property("type", StringType),
                                ),
                            ),
                        ),
                        Property("text", StringType),
                        Property("version", IntegerType),
                    ),
                ),
                Property("duedate", StringType),
                Property(
                    "progress",
                    ObjectType(
                        Property("progress", IntegerType),
                        Property("total", IntegerType),
                    ),
                ),
                Property("comment", StringType),
                Property(
                    "votes",
                    ObjectType(
                        Property("self", StringType),
                        Property("votes", IntegerType),
                        Property("hasVoted", BooleanType),
                    ),
                ),
                Property("worklog", StringType),
                Property("key", StringType),
                Property("id", IntegerType),
                Property("editmeta", StringType),
                Property("histories", StringType),
                Property("customfield_11394", StringType),
                Property("customfield_11395", StringType),
                Property("customfield_11397", StringType),
                Property("customfield_11396", base_item_schema),
                Property("customfield_11399", StringType),
                Property("customfield_11398", DateType),
                Property("customfield_11384", base_item_schema),
                Property("customfield_11385", StringType),
                Property("customfield_10600", base_item_schema),
                Property("customfield_11490", base_item_schema),
                Property("customfield_11492", StringType),
                Property(
                    "customfield_11371",
                    base_item_schema,
                ),
                Property(
                    "customfield_11370",
                    base_item_schema,
                ),
                Property("customfield_11491", base_item_schema),
                Property(
                    "customfield_11373",
                    base_item_schema,
                ),
                Property(
                    "customfield_11494",
                    base_item_schema,
                ),
                Property(
                    "customfield_11493",
                    base_item_schema,
                ),
                Property(
                    "customfield_11372",
                    base_item_schema,
                ),
                Property(
                    "customfield_11496",
                    base_item_schema,
                ),
                Property(
                    "customfield_11375",
                    base_item_schema,
                ),
                Property(
                    "customfield_11495",
                    base_item_schema,
                ),
                Property(
                    "customfield_11374",
                    base_item_schema,
                ),
                Property(
                    "customfield_11498",
                    base_item_schema,
                ),
                Property("customfield_11377", StringType),
                Property("customfield_11497", NumberType),
                Property("customfield_11376", StringType),
                Property("customfield_11379", ArrayType(base_item_schema)),
                Property("customfield_11378", ArrayType(base_item_schema)),
                Property(
                    "customfield_11369",
                    base_item_schema,
                ),
                Property("customfield_11481", ArrayType(base_item_schema)),
                Property("customfield_11482", base_item_schema),
                Property("customfield_11485", StringType),
                Property("customfield_11000", StringType),
                Property("customfield_11487", StringType),
                Property("customfield_11486", StringType),
                Property("customfield_11489", base_item_schema),
                Property("customfield_11368", DateType),
                Property("customfield_11488", StringType),
                Property("customfield_11359", DateType),
                Property("customfield_11358", StringType),
                Property("customfield_10701", StringType),
                Property("customfield_11470", NumberType),
                Property("customfield_11591", base_item_schema),
                Property("customfield_11472", NumberType),
                Property("customfield_11350", base_item_schema),
                Property("customfield_11353", base_item_schema),
                Property("customfield_11594", StringType),
                Property("customfield_11473", base_item_schema),
                Property("customfield_11355", base_item_schema),
                Property("customfield_11596", NumberType),
                Property("customfield_11354", base_item_schema),
                Property("customfield_11475", base_item_schema),
                Property("customfield_11357", StringType),
                Property("customfield_11356", StringType),
                Property("customfield_11598", StringType),
                Property("customfield_11469", base_item_schema),
                Property("customfield_11468", NumberType),
                Property("customfield_11347", StringType),
                Property("customfield_11582", base_item_schema),
                Property("customfield_11461", NumberType),
                Property("customfield_11340", StringType),
                Property("customfield_11460", StringType),
                # Property("customfield_11584", StringType),
                Property("customfield_11463", NumberType),
                Property("customfield_11341", base_item_schema),
                Property("customfield_11583", base_item_schema),
                Property(
                    "customfield_11100",
                    ArrayType(
                        ObjectType(
                            Property("_link", StringType),
                            Property("id", StringType),
                            Property("name", StringType),
                        )
                    ),
                ),
                Property("customfield_11586", StringType),
                Property("customfield_11344", NumberType),
                Property("customfield_11465", DateType),
                Property("customfield_11585", StringType),
                Property("customfield_11464", NumberType),
                Property("customfield_11346", StringType),
                Property("customfield_11467", base_item_schema),
                Property("customfield_11466", NumberType),
                Property("customfield_11345", StringType),
                Property("customfield_11587", StringType),
                # Property("customfield_11458", StringType),
                Property("customfield_11336", NumberType),
                Property("customfield_11457", base_item_schema),
                Property("customfield_11339", base_item_schema),
                Property("customfield_11459", NumberType),
                Property(
                    "customfield_10800",
                    ObjectType(
                        Property("hasEpicLinkFieldDependency", BooleanType),
                        Property(
                            "nonEditableReason",
                            ObjectType(
                                Property("message", StringType),
                                Property("reason", StringType),
                            ),
                            Property("showField", BooleanType),
                        ),
                        Property("showField", BooleanType),
                    ),
                ),
                Property("customfield_11338", base_item_schema),
                Property("customfield_11450", ArrayType(base_item_schema)),
                Property(
                    "customfield_11331",
                    ObjectType(
                        Property("displayName", StringType),
                        Property("languageCode", StringType),
                    ),
                ),
                Property("customfield_11452", base_item_schema),
                Property(
                    "customfield_11330",
                    ObjectType(Property("errorMessage", StringType)),
                ),
                Property("customfield_11451", StringType),
                Property("customfield_11454", base_item_schema),
                Property("customfield_11333", base_item_schema),
                Property("customfield_11575", base_item_schema),
                Property("customfield_11453", DateType),
                Property("customfield_11332", StringType),
                Property("customfield_11335", base_content_schema),
                Property("customfield_11576", StringType),
                Property(
                    "customfield_11334",
                    base_item_schema,
                ),
                Property("customfield_11342", base_item_schema),
                Property("customfield_11455", ArrayType(base_item_schema)),
                Property("customfield_11326", ArrayType(base_item_schema)),
                Property("customfield_11447", ArrayType(base_item_schema)),
                Property("customfield_11568", NumberType),
                Property("customfield_11567", NumberType),
                Property("customfield_11446", ArrayType(base_item_schema)),
                Property("customfield_11325", ArrayType(base_item_schema)),
                Property(
                    "customfield_11328",
                    ObjectType(Property("errorMessage", StringType)),
                ),
                Property("customfield_11449", ArrayType(base_item_schema)),
                Property(
                    "customfield_11327",
                    ObjectType(Property("errorMessage", StringType)),
                ),
                Property("customfield_11448", ArrayType(base_item_schema)),
                Property(
                    "customfield_11329",
                    ObjectType(Property("errorMessage", StringType)),
                ),
                Property("customfield_11560", StringType),
                Property("customfield_11441", StringType),
                Property(
                    "customfield_11562",
                    base_item_schema,
                ),
                Property("customfield_11320", base_item_schema),
                Property("customfield_11561", base_content_schema),
                Property("customfield_11443", StringType),
                Property("customfield_11200", base_item_schema),
                Property("customfield_11321", base_item_schema),
                Property("customfield_11564", base_content_schema),
                #
                # Custom definitions for UC Jira
                #
                Property(
                    "customfield_11442",
                    base_item_schema,
                ),
                Property(
                    "customfield_11476",
                    base_item_schema,
                ),
                Property(
                    "customfield_11364",
                    base_item_schema,
                ),
                Property(
                    "customfield_11581",
                    base_item_schema,
                ),
                Property(
                    "customfield_11535",
                    ArrayType(base_item_schema),
                ),
                Property(
                    "customfield_10116",
                    ObjectType(
                        Property("avatarUrl", StringType),
                        Property("id", StringType),
                        Property("isShared", BooleanType),
                        Property("isVisible", BooleanType),
                        Property("name", StringType),
                        Property("title", StringType)
                    ),
                ),
                Property(
                    "customfield_11537",
                    base_item_schema,
                ),
                # End custom definitions
                Property("customfield_11322", base_item_schema),
                Property("customfield_11563", base_content_schema),
                Property("customfield_11323", StringType),
                Property("customfield_11566", NumberType),
                Property("customfield_11445", StringType),
                Property("customfield_11324", StringType),
                Property("customfield_11565", NumberType),
                Property("customfield_11444", StringType),
                Property("customfield_11557", StringType),
                Property("customfield_11314", base_item_schema),
                Property("customfield_11436", StringType),
                Property("customfield_11435", StringType),
                Property("customfield_11556", StringType),
                Property("customfield_11315", DateTimeType),
                Property("customfield_11559", base_item_schema),
                Property("customfield_11316", DateTimeType),
                Property("customfield_11438", StringType),
                Property("customfield_11437", StringType),
                Property("customfield_11558", base_item_schema),
                Property("customfield_11317", base_item_schema),
                Property("customfield_11318", base_item_schema),
                Property("customfield_11319", base_item_schema),
                Property("customfield_11439", StringType),
                Property("customfield_11430", base_item_schema),
                Property("customfield_11310", ArrayType(base_item_schema)),
                Property("customfield_10100", StringType),
                Property("customfield_11431", ArrayType(base_item_schema)),
                Property("customfield_11311", base_item_schema),
                Property("customfield_11434", NumberType),
                Property("customfield_11312", base_item_schema),
                Property("customfield_11555", base_item_schema),
                Property("customfield_11433", StringType),
                Property("customfield_11313", base_item_schema),
                Property("customfield_11425", NumberType),
                Property("customfield_11303", DateType),
                Property("customfield_11667", StringType),
                Property("customfield_11666", ArrayType(base_item_schema)),
                Property("customfield_11545", base_content_schema),
                Property("customfield_11424", NumberType),
                Property(
                    "customfield_11305",
                    ObjectType(
                        Property(
                            "_links",
                            ObjectType(
                                Property("agent", StringType),
                                Property("jiraRest", StringType),
                                Property("self", StringType),
                                Property("web", StringType),
                            ),
                        ),
                        Property(
                            "currentStatus",
                            ObjectType(
                                Property("status", StringType),
                                Property("statusCategory", StringType),
                                Property(
                                    "statusDate",
                                    ObjectType(
                                        Property("epochMillis", IntegerType),
                                        Property("friendly", DateTimeType),
                                        Property("iso8601", DateTimeType),
                                        Property("jira", DateTimeType),
                                    ),
                                ),
                            ),
                        ),
                        Property(
                            "requestType",
                            ObjectType(
                                Property("_expands", ArrayType(StringType)),
                                Property(
                                    "_links", ObjectType(Property("self", StringType))
                                ),
                                Property("description", StringType),
                                Property("groupIds", ArrayType(StringType)),
                                Property("id", StringType),
                                Property("issueTypeId", StringType),
                                Property("name", StringType),
                                Property("portalId", StringType),
                                Property("serviceDeskId", StringType),
                            ),
                        ),
                    ),
                ),
                Property("customfield_11615", StringType),
                Property("customfield_11427", NumberType),
                Property("customfield_11548", base_item_schema),
                Property("customfield_11668", base_item_schema),
                Property("customfield_11306", ArrayType(base_item_schema)),
                Property("customfield_11307", NumberType),
                Property("customfield_11429", base_item_schema),
                Property("customfield_11308", base_item_schema),
                Property("customfield_11428", NumberType),
                Property("customfield_11549", StringType),
                Property("customfield_11309", DateTimeType),
                Property("customfield_11661", base_item_schema),
                Property("customfield_11660", base_content_schema),
                Property("customfield_11421", NumberType),
                Property("customfield_11663", NumberType),
                Property("customfield_11420", NumberType),
                Property("customfield_11300", StringType),
                Property("customfield_11665", StringType),
                Property("customfield_11301", DateType),
                Property("customfield_11423", NumberType),
                Property("customfield_11302", base_item_schema),
                Property("customfield_11422", NumberType),
                Property("customfield_11664", StringType),
                Property("customfield_11414", DateTimeType),
                Property("customfield_11656", StringType),
                Property("customfield_11413", base_item_schema),
                Property("customfield_11658", StringType),
                Property("customfield_11415", DateType),
                Property("customfield_11657", base_item_schema),
                Property("customfield_11418", DateType),
                Property("customfield_11659", StringType),
                Property("customfield_11652", base_item_schema),
                Property("customfield_11410", StringType),
                Property("customfield_11530", base_content_schema),
                Property("customfield_11411", StringType),
                Property("customfield_11524", base_item_schema),
                Property("customfield_11403", DateType),
                Property("customfield_11645", NumberType),
                Property("customfield_11402", ArrayType(base_item_schema)),
                Property("customfield_11644", NumberType),
                Property("customfield_11523", DateType),
                Property("customfield_11647", StringType),
                Property("customfield_11405", StringType),
                Property("customfield_11526", StringType),
                Property("customfield_11404", StringType),
                Property("customfield_11525", StringType),
                Property("customfield_11528", base_content_schema),
                Property("customfield_11649", StringType),
                Property("customfield_11648", ArrayType(base_item_schema)),
                Property("customfield_11527", StringType),
                Property("customfield_11529", StringType),
                Property("customfield_11641", StringType),
                Property("customfield_11520", base_item_schema),
                Property("customfield_11640", StringType),
                Property("customfield_11643", NumberType),
                Property("customfield_11522", DateType),
                Property("customfield_11401", StringType),
                Property("customfield_11400", StringType),
                Property("customfield_11642", NumberType),
                Property("customfield_11521", base_item_schema),
                Property("customfield_11513", DateType),
                Property("customfield_10302", DateTimeType),
                Property("customfield_11512", ArrayType(base_item_schema)),
                Property("customfield_11515", ArrayType(base_item_schema)),
                Property("customfield_11514", DateType),
                Property("customfield_11638", base_item_schema),
                Property("customfield_11517", ArrayType(StringType)),
                Property("customfield_11516", base_item_schema),
                Property("customfield_11637", base_item_schema),
                Property("customfield_11519", base_item_schema),
                Property("customfield_11639", base_item_schema),
                Property("customfield_11518", StringType),
                Property("customfield_10300", StringType),
                Property("customfield_11511", StringType),
                Property("customfield_10301", StringType),
                Property("customfield_11510", base_item_schema),
                Property("customfield_11502", NumberType),
                Property("customfield_11501", StringType),
                Property("customfield_11503", base_item_schema),
                Property("customfield_11505", base_item_schema),
                Property("customfield_11508", DateType),
                Property("customfield_11507", base_item_schema),
                Property("customfield_11509", StringType),
                Property("customfield_11618", base_item_schema),
                Property("customfield_11610", NumberType),
                Property("customfield_11600", base_item_schema),
                Property("customfield_11380", StringType),
                Property("customfield_11382", StringType),
                Property("customfield_11381", StringType),
                Property("customfield_11480", base_item_schema),
                Property("customfield_11479", StringType),
                Property("customfield_11590", NumberType),
                Property("customfield_11478", StringType),
                Property("customfield_11477", StringType),
                Property("customfield_11348", NumberType),
                Property("customfield_11349", base_item_schema),
                Property("customfield_11343", base_item_schema),
                Property("customfield_11571", base_item_schema),
                Property("customfield_11573", base_item_schema),
                Property("customfield_11572", NumberType),
                Property("customfield_11574", base_item_schema),
                Property("customfield_11577", base_item_schema),
                Property("customfield_11569", StringType),
                Property("customfield_11551", NumberType),
                Property("customfield_11550", StringType),
                Property("customfield_11553", NumberType),
                Property("customfield_11552", StringType),
                Property("customfield_11554", NumberType),
                Property("customfield_11540", base_item_schema),
                Property("customfield_11541", base_item_schema),
                Property("customfield_11543", StringType),
                Property("customfield_11617", StringType),
                Property("customfield_11504", base_item_schema),
                Property("customfield_11616", NumberType),
                additional_properties=True,
            ),
        ),
        Property("created", StringType),
        Property("updated", StringType),
    ).to_dict()

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ANN401
    ) -> dict[str, t.Any]:
        """Return a dictionary of query parameters."""
        params: dict = {}

        params["maxResults"] = self.config.get("page_size", {}).get("issues", 10)

        jql: list[str] = []

        if next_page_token:
            params["startAt"] = next_page_token

        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        if "start_date" in self.config:
            start_date = self.config["start_date"]
            jql.append(f"(created>='{start_date}' or updated>='{start_date}')")

        if "end_date" in self.config:
            end_date = self.config["end_date"]
            jql.append(f"(created<'{end_date}' or updated<'{end_date}')")

        if (
            base_jql := self.config.get("stream_options", {})
            .get("issues", {})
            .get("jql")
        ):
            jql.append(f"({base_jql})")

        if jql:
            params["jql"] = " and ".join(jql)

        return params

    def post_process(self, row: Record, context: Context | None = None) -> Record:  # noqa: ARG002
        """Post-process the record.

        - Add top-level `created` field.
        """
        created = row.get("fields", {}).pop("created", None)
        row["created"] = created
        return row

    def get_child_context(self, record: dict, context: dict | None) -> dict:  # noqa: ARG002
        """Return a context dictionary for child streams."""
        return {"issue_id": record["id"]}


class PermissionStream(JiraStream):
    """Permission stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permissions/#api-rest-api-3-permissions-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    """

    name = "permissions"
    path = "/permissions"
    instance_name = ""

    schema = PropertiesList(
        Property(
            "permissions",
            ObjectType(
                Property(
                    "ADD_COMMENTS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "ADMINISTER_PROJECTS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "DELETE_ALL_WORKLOGS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "ADMINISTER",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "ADMINISTER_PROJECT",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "ASSIGNABLE_USER",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "ASSIGN_ISSUES",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "BROWSE_PROJECTS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "BULK_CHANGE",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "CLOSE_ISSUES",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "CREATE_ATTACHMENTS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "CREATE_ISSUES",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "CREATE_PROJECT",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "CREATE_SHARED_OBJECTS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "DELETE_ALL_ATTACHMENTS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "DELETE_ALL_COMMENTS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "DELETE_ALL_WORKLOG",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "DELETE_ISSUES",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "DELETE_OWN_ATTACHMENTS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "DELETE_OWN_COMMENTS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "DELETE_OWN_WORKLOGS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "EDIT_ALL_COMMENTS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "EDIT_ALL_WORKLOGS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "EDIT_ISSUES",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "EDIT_OWN_COMMENTS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "EDIT_OWN_WORKLOGS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "LINK_ISSUES",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "MANAGE_GROUP_FILTER_SUBSCRIPTIONS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "MANAGE_SPRINTS_PERMISSION",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "MANAGE_WATCHERS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "MODIFY_REPORTER",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "MOVE_ISSUES",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "RESOLVE_ISSUES",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "SCHEDULE_ISSUES",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "SET_ISSUE_SECURITY",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "SYSTEM_ADMIN",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "TRANSITION_ISSUES",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "USER_PICKER",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "VIEW_AGGREGATED_DATA",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "VIEW_DEV_TOOLS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "VIEW_READONLY_WORKFLOW",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "VIEW_VOTERS_AND_WATCHERS",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "WORK_ON_ISSUES",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
                Property(
                    "com.atlassian.atlas.jira__jira-townsquare-link-unconnected-issue-glance-view-permission",
                    ObjectType(
                        Property("key", StringType),
                        Property("name", StringType),
                        Property("type", StringType),
                        Property("description", StringType),
                    ),
                ),
            ),
        ),
    ).to_dict()


class ProjectRoleStream(JiraStream):
    """Project role stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-roles/#api-rest-api-3-role-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    name = "project_roles"
    path = "/role"
    primary_keys = ("id",)
    replication_key = "id"
    replication_method = "INCREMENTAL"
    instance_name = ""

    schema = PropertiesList(
        Property("self", StringType),
        Property("name", StringType),
        Property("id", IntegerType),
        Property("description", StringType),
        Property(
            "scope",
            ObjectType(
                Property("type", StringType),
                Property(
                    "project",
                    ObjectType(
                        Property("id", StringType),
                    ),
                ),
            ),
        ),
        Property(
            "actors",
            ArrayType(
                ObjectType(
                    Property("id", IntegerType),
                    Property("displayName", StringType),
                    Property("type", StringType),
                    Property("name", StringType),
                    Property(
                        "actorUser",
                        ObjectType(
                            Property("accountId", StringType),
                        ),
                    ),
                    Property(
                        "actorGroup",
                        ObjectType(
                            Property("name", StringType),
                            Property("displayName", StringType),
                            Property("groupId", StringType),
                        ),
                    ),
                ),
            ),
        ),
    ).to_dict()


class PriorityStream(JiraStream):
    """Priority stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-priorities/#api-rest-api-3-priority-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    name = "priorities"
    path = "/priority"
    primary_keys = ("id",)
    replication_key = "id"
    replication_method = "INCREMENTAL"
    instance_name = ""

    schema = PropertiesList(
        Property("self", StringType),
        Property("statusColor", StringType),
        Property("description", StringType),
        Property("iconUrl", StringType),
        Property("name", StringType),
        Property("id", StringType),
    ).to_dict()


class PermissionHolderStream(JiraStream):
    """Permission holder stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permission-schemes/#api-rest-api-3-permissionscheme-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "permission_holders"
    path = "/permissionscheme"
    primary_keys = ("id",)
    replication_key = "id"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[permissionSchemes][*]"  # Or override `parse_response`.
    instance_name = "permissionSchemes"

    schema = PropertiesList(
        Property("expand", StringType),
        Property("id", IntegerType),
        Property("self", StringType),
        Property("name", StringType),
        Property(
            "scope",
            ObjectType(
                Property("type", StringType),
                Property(
                    "project",
                    ObjectType(
                        Property("id", StringType),
                    ),
                ),
            ),
        ),
        Property("description", StringType),
        Property(
            "permissions",
            ArrayType(
                ObjectType(
                    Property("id", IntegerType),
                    Property("self", StringType),
                    Property(
                        "holder",
                        ObjectType(
                            Property("type", StringType),
                            Property("parameter", StringType),
                            Property("value", StringType),
                            Property("expand", StringType),
                        ),
                    ),
                    Property("permission", StringType),
                ),
            ),
        ),
    ).to_dict()


class BoardStream(JiraStream):
    """Board stream.

    https://developer.atlassian.com/cloud/jira/platform/jira-expressions-type-reference/#sprint
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "boards"
    path = "/board"
    primary_keys = ("id",)
    replication_key = "id"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[values][*]"  # Or override `parse_response`.
    instance_name = "values"

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("self", StringType),
        Property("name", StringType),
        Property("type", StringType),
        Property(
            "location",
            ObjectType(
                Property("projectId", IntegerType),
                Property("displayName", StringType),
                Property("projectName", StringType),
                Property("projectKey", StringType),
                Property("projectTypeKey", StringType),
                Property("name", StringType),
            ),
        ),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Return the base URL for the API requests."""
        domain = self.config["domain"]
        return f"https://{domain}:443/rest/agile/1.0"

    def get_child_context(self, record: dict, context: dict | None) -> dict:  # noqa: ARG002
        """Return a context dictionary for child streams."""
        return {"board_id": record["id"]}


class SprintStream(JiraStream):
    """Sprint stream.

    * https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/#api-rest-agile-1-0-board-boardid-sprint-get
    * https://developer.atlassian.com/cloud/jira/platform/jira-expressions-type-reference/#sprint
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "sprints"
    primary_keys = ("id",)
    parent_stream_type = BoardStream
    path = "/board/{board_id}/sprint?maxResults=100"
    replication_method = "INCREMENTAL"
    replication_key = "id"
    records_jsonpath = "$[values][*]"  # Or override `parse_response`.
    instance_name = "values"

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("self", StringType),
        Property("state", StringType),
        Property("name", StringType),
        Property("startDate", DateTimeType),
        Property("endDate", DateTimeType),
        Property("completeDate", DateTimeType),
        Property("originBoardId", IntegerType),
        Property("goal", StringType),
        Property("boardId", IntegerType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        """Return the base URL for the API requests."""
        domain = self.config["domain"]
        return f"https://{domain}:443/rest/agile/1.0"

    def post_process(self, row: dict, context: dict | None) -> dict:
        """Post-process the record before it is returned."""
        if context:
            row["boardId"] = context["board_id"]
        return row

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """Get records from the API response."""
        for record in self.request_records(context):
            transformed_record = self.post_process(record, context)
            if transformed_record is None:
                continue
            yield transformed_record

    def validate_response(self, response: requests.Response) -> None:
        """Validate the API response.

        Allow for a 400 response if the board does not support sprints.
        Do raise an error for other 400 responses.
        """
        if (
            response.status_code == HTTPStatus.BAD_REQUEST
            and "The board does not support sprints"
            in response.json().get("errorMessages", [])
        ):
            return
        super().validate_response(response)


class ProjectRoleActorStream(JiraStream):
    """Project role actor stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-role-actors/#api-rest-api-3-role-id-actors-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    name = "project_role_actors"
    path = "/role"

    primary_keys = ("id",)
    replication_key = "id"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[*]"  # Or override `parse_response`.

    schema = PropertiesList(
        Property("self", StringType),
        Property("name", StringType),
        Property("id", IntegerType),
        Property("description", StringType),
        Property(
            "actors",
            ArrayType(
                ObjectType(
                    Property("id", IntegerType),
                    Property("displayName", StringType),
                    Property("type", StringType),
                    Property(
                        "actorUser",
                        ObjectType(
                            Property("accountId", StringType),
                        ),
                    ),
                ),
            ),
        ),
        Property(
            "scope",
            ObjectType(
                Property("type", StringType),
                Property(
                    "project",
                    ObjectType(
                        Property("id", StringType),
                    ),
                ),
            ),
        ),
    ).to_dict()

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """Get records from the API response.

        Takes each of the role ID's gathered above and adds to a list, then loops
        through the list and gets data from the project role actor endpoint for each of
        the role ID's in the list.
        """
        role_actor_records = []
        project = ProjectStream(self._tap, schema={"properties": {}})

        role_id = [
            record.get("id")
            for record in list(ProjectRoleStream(self._tap).get_records(context))
        ]

        project_id = [record.get("id") for record in list(project.get_records(context))]

        for pid in project_id:
            for role in role_id:
                try:

                    class ProjectRoleActor(JiraStream):
                        role_id = role
                        project_id = pid
                        name = "project_role_actor"
                        path = f"/project/{project_id}/role/{role_id}"
                        instance_name = ""

                    project_role_actor = ProjectRoleActor(
                        self._tap,
                        schema={"properties": {}},
                    )

                    role_actor_records.append(
                        list(project_role_actor.get_records(context)),
                    )

                except:  # noqa: E722, PERF203, S110
                    pass

        return functools.reduce(
            operator.iadd,
            role_actor_records,
            [],
        )


class AuditingStream(JiraStream):
    """Auditing stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-audit-records/#api-rest-api-3-auditing-record-get

    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "audit_records"
    path = "/auditing/record"
    primary_keys = ("id",)
    replication_key = "created"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[records][*]"  # Or override `parse_response`.
    instance_name = "records"

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("summary", StringType),
        Property("created", StringType),
        Property("category", StringType),
        Property("eventSource", StringType),
        Property("remoteAddress", StringType),
        Property("authorKey", StringType),
        Property("authorAccountId", StringType),
        Property(
            "objectItem",
            ObjectType(
                Property("id", StringType),
                Property("name", StringType),
                Property("typeName", StringType),
                Property("parentId", StringType),
                Property("parentName", StringType),
            ),
        ),
        Property(
            "changedValues",
            ArrayType(
                ObjectType(
                    Property("fieldName", StringType),
                    Property("changedFrom", StringType),
                    Property("changedTo", StringType),
                ),
            ),
        ),
        Property(
            "associatedItems",
            ArrayType(
                ObjectType(
                    Property("id", StringType),
                    Property("name", StringType),
                    Property("typeName", StringType),
                    Property("parentId", StringType),
                    Property("parentName", StringType),
                ),
            ),
        ),
    ).to_dict()


class DashboardStream(JiraStream):
    """Dashboard stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-dashboards/#api-rest-api-3-dashboard-get

    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "dashboards"
    path = "/dashboard"
    primary_keys = ("id",)
    replication_key = "id"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[dashboards][*]"  # Or override `parse_response`.
    instance_name = "dashboards"

    schema = PropertiesList(
        Property("id", StringType),
        Property("isFavourite", BooleanType),
        Property("name", StringType),
        Property("popularity", IntegerType),
        Property("self", StringType),
        Property(
            "sharePermissions",
            ArrayType(
                ObjectType(
                    Property("id", IntegerType),
                    Property("type", StringType),
                ),
            ),
        ),
        Property(
            "editPermissions",
            ArrayType(
                ObjectType(Property("id", IntegerType), Property("type", StringType)),
            ),
        ),
        Property("view", StringType),
        Property("isWritable", BooleanType),
        Property("systemDashboard", BooleanType),
    ).to_dict()


class FilterSearchStream(JiraStream):
    """Filter search stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filters/#api-rest-api-3-filter-search-get

    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "filter_searches"
    path = "/filter/search"
    primary_keys = ("id",)
    replication_key = "id"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[values][*]"  # Or override `parse_response`.
    instance_name = "values"

    schema = PropertiesList(
        Property("expand", StringType),
        Property("self", StringType),
        Property("id", StringType),
        Property("name", StringType),
    ).to_dict()


class FilterDefaultShareScopeStream(JiraStream):
    """Filter default share scope stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filter-sharing/#api-rest-api-3-filter-defaultsharescope-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    name = "filter_default_share_scopes"
    path = "/filter/defaultShareScope"
    primary_keys = ("scope",)
    replication_key = "scope"
    replication_method = "INCREMENTAL"
    instance_name = ""

    schema = PropertiesList(
        Property("scope", StringType),
    ).to_dict()


class GroupsPickerStream(JiraStream):
    """Groups picker stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/#api-rest-api-3-groups-picker-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath: json response body
    """

    name = "groups_pickers"
    path = "/groups/picker"
    primary_keys = ("groupId",)
    replication_key = "groupId"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[groups][*]"  # Or override `parse_response`.
    instance_name = "groups"

    schema = PropertiesList(
        Property("name", StringType),
        Property("html", StringType),
        Property(
            "labels",
            ArrayType(
                ObjectType(
                    Property("text", StringType),
                    Property("title", StringType),
                    Property("type", StringType),
                ),
            ),
        ),
        Property("groupId", StringType),
    ).to_dict()


class LicenseStream(JiraStream):
    """License stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-license-metrics/#api-rest-api-3-instance-license-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "licenses"
    path = "/instance/license"
    primary_keys = ("id",)
    replication_key = "id"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[applications][*]"  # Or override `parse_response`.
    instance_name = "applications"

    schema = PropertiesList(
        Property("id", StringType),
        Property("plan", StringType),
    ).to_dict()


class ScreensStream(JiraStream):
    """Screens stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screens/#api-rest-api-3-screens-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "screens"
    path = "/screens"
    primary_keys = ("id",)
    replication_key = "id"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[values][*]"  # Or override `parse_response`.
    instance_name = "values"

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("name", StringType),
        Property("description", StringType),
        Property(
            "scope",
            ObjectType(
                Property("type", StringType),
                Property(
                    "project",
                    ObjectType(
                        Property("id", StringType),
                    ),
                ),
            ),
        ),
    ).to_dict()


class ScreenSchemesStream(JiraStream):
    """Screen schemes stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tab-fields/#api-rest-api-3-screens-screenid-tabs-tabid-fields-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "screen_schemes"
    path = "/screenscheme"
    primary_keys = ("id",)
    replication_key = "id"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[values][*]"  # Or override `parse_response`.
    instance_name = "values"

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("name", StringType),
        Property("description", StringType),
        Property(
            "screens",
            ObjectType(
                Property("default", IntegerType),
                Property("create", IntegerType),
            ),
        ),
    ).to_dict()


class StatusesSearchStream(JiraStream):
    """Statuses search stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tab-fields/#api-rest-api-3-screens-screenid-tabs-tabid-fields-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "statuses_searches"
    path = "/statuses/search"
    primary_keys = ("id",)
    replication_key = "id"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[values][*]"  # Or override `parse_response`.
    instance_name = "values"

    schema = PropertiesList(
        Property("id", StringType),
        Property("name", StringType),
        Property("statusCategory", StringType),
        Property(
            "scope",
            ObjectType(Property("type", StringType)),
        ),
        Property("description", StringType),
        Property("usages", ArrayType(StringType)),
        Property("workflowUsages", ArrayType(StringType)),
    ).to_dict()


class WorkflowStream(JiraStream):
    """Workflow stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflows/#api-rest-api-3-workflow-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    """

    name = "workflows"
    path = "/workflow"
    primary_keys = ("name",)
    replication_key = "name"
    replication_method = "INCREMENTAL"
    instance_name = ""

    schema = PropertiesList(
        Property("name", StringType),
        Property("description", StringType),
        Property("steps", IntegerType),
        Property("default", BooleanType),
        Property("lastModifiedDate", StringType),
        Property("lastModifiedUser", StringType),
        Property("lastModifiedUserAccountId", StringType),
        Property(
            "scope",
            ObjectType(
                Property("type", StringType),
                Property(
                    "project",
                    ObjectType(
                        Property("id", StringType),
                    ),
                ),
            ),
        ),
    ).to_dict()


class Resolutions(JiraStream):
    """Resolution stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-resolutions/#api-rest-api-3-resolution-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "resolutions"

    path = "/resolution/search"

    records_jsonpath = "$[values][*]"

    primary_keys = ("id",)

    instance_name = "values"

    schema = PropertiesList(
        Property("id", StringType),
        Property("description", StringType),
        Property("name", StringType),
        Property("isDefault", BooleanType),
    ).to_dict()


class WorkflowSearchStream(JiraStream):
    """Workflow search stream.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflows/#api-rest-api-3-workflow-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "workflow_searches"
    path = "/workflow/search"
    primary_keys = ("name", "entityId")
    replication_key = "updated"
    replication_method = "INCREMENTAL"
    records_jsonpath = "$[values][*]"  # Or override `parse_response`.
    instance_name = "values"

    schema = PropertiesList(
        Property("name", StringType),
        Property("entityId", StringType),
        Property("description", StringType),
        Property("created", StringType),
        Property("updated", StringType),
    ).to_dict()

    def post_process(self, row: dict, context: dict | None) -> dict:  # noqa: ARG002
        """Post-process the record before it is returned.

        Flattens the id object into separate name and entityId fields.
        """
        if "id" in row:
            # Extract values from the id object
            id_obj = row.pop("id")
            row["name"] = id_obj.get("name")
            row["entityId"] = id_obj.get("entityId")
        return row


# Child Streams


class IssueWatchersStream(JiraStream):
    """Issue Watchers.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflows/#api-rest-api-3-workflow-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "issue_watchers"
    path = "/issue/{issue_id}/watchers"
    parent_stream_type = IssueStream
    ignore_parent_replication_keys = True
    primary_keys = ("accountId",)
    records_jsonpath = "$[watchers][*]"
    instance_name = ""

    schema = PropertiesList(
        Property("accountId", StringType),
        Property("accountType", StringType),
        Property("active", BooleanType),
        Property("displayName", StringType),
        Property("issueId", StringType),
    ).to_dict()

    def post_process(self, row: dict, context: dict) -> dict:
        """Post-process the record before it is returned."""
        row["issueId"] = context["issue_id"]
        return row


class IssueChangeLogStream(JiraStream):
    """Issue Change Log.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflows/#api-rest-api-3-workflow-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "issue_changelog"

    parent_stream_type = IssueStream

    ignore_parent_replication_keys = True

    path = "/issue/{issue_id}/changelog"

    replication_key = "created"

    primary_keys = ("id",)

    records_jsonpath = "$[values][*]"

    instance_name = "values"

    next_page_token_jsonpath = None  # type: ignore[assignment]

    schema = PropertiesList(
        Property("id", StringType),
        Property("issueId", StringType),
        Property("author", ObjectType(Property("accountId", StringType))),
        Property("created", DateTimeType),
        Property(
            "items",
            ArrayType(
                ObjectType(
                    Property("field", StringType),
                    Property("fieldtype", StringType),
                    Property("fieldId", StringType),
                    Property("from", StringType),
                    Property("fromString", StringType),
                    Property("to", StringType),
                    Property("toString", StringType),
                ),
            ),
        ),
    ).to_dict()

    def post_process(self, row: dict, context: dict) -> dict:
        """Post-process the record before it is returned."""
        row["issueId"] = context["issue_id"]
        return row


class IssueComments(JiraStream):
    """Issue Comments.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "issue_comments"

    parent_stream_type = IssueStream

    ignore_parent_replication_keys = True

    path = "/issue/{issue_id}/comment"

    primary_keys = ("id",)

    records_jsonpath = "$[comments][*]"

    instance_name = "comments"

    next_page_token_jsonpath = None  # type: ignore[assignment]

    schema = PropertiesList(
        Property("id", StringType),
        Property("issueId", StringType),
        Property("self", StringType),
        Property(
            "author",
            ObjectType(
                Property("accountId", StringType),
                Property("self", StringType),
                Property("displayName", StringType),
                Property("active", BooleanType),
            ),
        ),
        Property("created", DateTimeType),
        Property("updated", DateTimeType),
        Property("body", ADFRootBlockNode),
        Property(
            "updateAuthor",
            ObjectType(
                Property("accountId", StringType),
                Property("self", StringType),
                Property("displayName", StringType),
                Property("active", BooleanType),
            ),
        ),
    ).to_dict()

    def post_process(self, row: dict, context: dict) -> dict:
        """Post-process the record before it is returned."""
        row["issueId"] = context["issue_id"]
        return row


class IssueWorklogs(JiraStream):
    """Issue Worklogs.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-get
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "issue_worklogs"

    parent_stream_type = IssueStream

    ignore_parent_replication_keys = True

    path = "/issue/{issue_id}/worklog"

    primary_keys = ("id",)

    records_jsonpath = "$[worklogs][*]"

    instance_name = "worklogs"

    next_page_token_jsonpath = None  # type: ignore[assignment]

    schema = PropertiesList(
        Property("id", StringType),
        Property("self", StringType),
        Property(
            "author",
            ObjectType(
                Property("accountId", StringType),
                Property("self", StringType),
                Property("displayName", StringType),
                Property("active", BooleanType),
            ),
        ),
        Property(
            "updateAuthor",
            ObjectType(
                Property("accountId", StringType),
                Property("self", StringType),
                Property("displayName", StringType),
                Property("active", BooleanType),
            ),
        ),
        Property("updated", DateTimeType),
        Property("started", DateTimeType),
        Property("timeSpentSeconds", IntegerType),
        Property("issueId", StringType),
    ).to_dict()
