from metagpt.actions.action_node import ActionNode

LANGUAGE = ActionNode(
    key="Language",
    expected_type=str,
    instruction="Provide the language used in the project, typically matching the user's requirement language.",
    example="en_us",
)


CRON_EXPRESSION = ActionNode(
    key="Cron Expression",
    expected_type=str,
    instruction="If the user requires scheduled triggering, please provide the corresponding 5-field cron expression. "
    "Otherwise, leave it blank.",
    example="",
)


CRAWLER_URL_LIST = ActionNode(
    key="Crawler URL List",
    expected_type=list[str],
    instruction="List the URLs user want to crawl. Leave it blank if not provided in the User Requirement.",
    example=["https://example1.com", "https://example2.com"],
)


PAGE_CONTENT_EXTRACTION = ActionNode(
    key="Page Content Extraction",
    expected_type=str,
    instruction="Specify the requirements and tips to extract from the crawled web pages based on User Requirement.",
    example="Retrieve the titles and content of articles published today.",
)


CRAWL_POST_PROCESSING = ActionNode(
    key="Crawl Post Processing",
    expected_type=str,
    instruction="Specify the processing to be applied to the crawled content, such as summarizing today's news.",
    example="Generate a summary of today's news articles.",
)


INFORMATION_SUPPLEMENT = ActionNode(
    key="Information Supplement",
    expected_type=str,
    instruction="If unable to obtain the Cron Expression, prompt the user to provide the time to receive subscription "
    "messages. If unable to obtain the URL List Crawler, prompt the user to provide the URLs they want to crawl. Keep it "
    "blank if everything is clear",
    example="",
)


NODES = [
    LANGUAGE,
    CRON_EXPRESSION,
    CRAWLER_URL_LIST,
    PAGE_CONTENT_EXTRACTION,
    CRAWL_POST_PROCESSING,
    INFORMATION_SUPPLEMENT,
]


PARSE_SUB_REQUIREMENTS_NODE = ActionNode.from_children("ParseSubscriptionReq", NODES)
