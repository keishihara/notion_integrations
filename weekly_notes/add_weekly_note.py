import copy
import datetime
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from jpholiday import is_holiday_name
from notion_client import Client

load_dotenv()

INTEGRATION_TOKEN = os.getenv('WEEKLY_NOTES_INTEGRATION_TOKEN')
DATABASE_ID = os.getenv('WEEKLY_DATABASE_ID')
WEEKLY_TEMPLATE_PAGE_ID = os.getenv('WEEKLY_TEMPLATE_PAGE_ID')
NOTION_BASE_URL = 'https://api.notion.com/v1/'
HEADERS = {
    'Authorization': f'Bearer {INTEGRATION_TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28',
}


@dataclass
class DateHolidayPair:
    date: datetime.date
    holiday: str | None


def get_dates() -> list[DateHolidayPair]:
    """Return a list of DateHolidayPair objects, starting with Monday of this week."""
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    dates = []
    for i in range(7):
        date: datetime.date = monday + datetime.timedelta(days=i)
        holiday: str = get_japanese_holiday(date)
        dates.append(DateHolidayPair(date=date, holiday=holiday))
    return dates


def get_japanese_holiday(date: datetime.date) -> str:
    """Convert a date object into Japanese holiday name."""
    return is_holiday_name(date)


def get_block_children(client: Client, block_id: str) -> list:
    """Get blocks recursively from a page. """
    blocks = []
    start_cursor = None
    while True:
        response = client.blocks.children.list(block_id=block_id, start_cursor=start_cursor)
        blocks.extend(response['results'])
        if not response['has_more']:
            break
        start_cursor = response['next_cursor']
    for block in blocks:
        if block['has_children']:
            block['children'] = get_block_children(client, block['id'])
    return blocks


def replace_date_placeholders(blocks: list, dates: list[DateHolidayPair]):
    # Replace a date placeholder into actual dates: eg, 2024.MM.DD(Mon) -> 2024.09.16(Mon, 敬老の日)
    for block in blocks:
        block_type = block['type']
        if block_type in [
            'heading_1', 'heading_2', 'heading_3', 'paragraph', 'bulleted_list_item',
            'numbered_list_item',
        ]:
            rich_texts = block[block_type].get('rich_text', [])
            for rich_text in rich_texts:
                if '2024.MM.DD' in rich_text['text']['content']:
                    date = dates.pop(0)
                    if date.holiday:
                        new_date = date.date.strftime(f'%Y.%m.%d(%a, {date.holiday})')
                        new_color = 'pink'
                    else:
                        new_date = date.date.strftime('%Y.%m.%d(%a)')
                        new_color = rich_text['annotations']['color']
                    rich_text['text']['content'] = new_date
                    rich_text['annotations']['color'] = new_color

        # Recursively handle if there is any child blocks
        if 'children' in block:
            replace_date_placeholders(block['children'], dates)


def clean_blocks_for_creation(blocks: list) -> list:
    """ Cleanup a block so it can be used to create a new page in the DB. """
    allowed_children_blocks = [
        'toggle', 'to_do', 'synced_block', 'template', 'column_list', 'column',
        'callout', 'quote', 'bulleted_list_item', 'numbered_list_item', 'paragraph'
    ]

    clean_blocks = []
    for block in blocks:
        block_type = block['type']
        new_block = {
            'type': block_type,
            block_type: {},
        }

        # Copy contents of the block, and remove unnecessary fields
        content = block.get(block_type, {}).copy()
        content_keys_to_remove = [
            'children', 'id', 'created_time', 'last_edited_time', 'has_children',
            'archived', 'object'
        ]
        for key in content_keys_to_remove:
            content.pop(key, None)

        # If allowed block type and 'children' exists
        if block_type in allowed_children_blocks and 'children' in block:
            # Cleanup the children block
            cleaned_children = clean_blocks_for_creation(block['children'])
            content['children'] = cleaned_children

        new_block[block_type] = content
        clean_blocks.append(new_block)
    return clean_blocks


def main():
    notion = Client(auth=INTEGRATION_TOKEN)

    dates = get_dates()
    monday = dates[0].date

    # Get blocks from the template page
    template_blocks = get_block_children(notion, WEEKLY_TEMPLATE_PAGE_ID)
    blocks = copy.deepcopy(template_blocks)
    dates_copy = copy.deepcopy(dates)

    # Replace dates
    replace_date_placeholders(blocks, dates_copy)

    # Cleanup blocks
    cleaned_blocks = clean_blocks_for_creation(blocks)

    # Set the new page title
    week_number = datetime.date.today().isocalendar().week
    title_str = f'Weekly {week_number} | {monday.strftime("%Y.%m.%d")}'

    # Create a new page in the database
    new_page = notion.pages.create(
        parent={'database_id': DATABASE_ID},
        properties={
            'Name': {
                'title': [
                    {
                        'type': 'text',
                        'text': {'content': title_str}
                    }
                ]
            }
        },
        children=cleaned_blocks,
    )

    print(f"New Weekly Note is created: {new_page['url']}")


if __name__ == '__main__':
    main()
