import openreview

# 适用于 API V2 的客户端实例
client = openreview.api.OpenReviewClient(
    baseurl='https://api2.openreview.net',
    username='<your-username>',
    password='<your-password>'
)

get_venues = lambda client: client.get_group(id='venues').members
venues = get_venues(client)
print(len(venues)) # 1841

# [ven for ven in venues if 'ICLR.cc/2025' in ven]
['ICLR.cc/2025/Conference',
 'ICLR.cc/2025/Workshop_Proposals',
 'ICLR.cc/2025/BlogPosts'
]


def get_submissions(client, venue_id, status='all'):
    # Retrieve the venue group information
    venue_group = client.get_group(venue_id)
    
    # Define the mapping of status to the respective content field
    status_mapping = {
        "all": venue_group.content['submission_name']['value'],
        "accepted": venue_group.id,  # Assuming 'accepted' status doesn't have a direct field
        "under_review": venue_group.content['submission_venue_id']['value'],
        "withdrawn": venue_group.content['withdrawn_venue_id']['value'],
        "desk_rejected": venue_group.content['desk_rejected_venue_id']['value']
    }

    # Fetch the corresponding submission invitation or venue ID
    if status in status_mapping:
        if status == "all":
            # Return all submissions regardless of their status
            return client.get_all_notes(invitation=f'{venue_id}/-/{status_mapping[status]}')
        
        # For all other statuses, use the content field 'venueid'
        return client.get_all_notes(content={'venueid': status_mapping[status]})
    
    raise ValueError(f"Invalid status: {status}. Valid options are: {list(status_mapping.keys())}")

get_submissions(client, 'ICLR.cc/2024/Workshop/AGI') # 共 40 篇，接收 34 篇

venue_id = 'ICLR.cc/2025/Conference'
submissions = get_submissions(client, venue_id, 'under_review')
print(len(submissions))

from datetime import datetime

def extract_submission_info(submission):
    # Helper function to convert timestamps to datetime
    def convert_timestamp_to_date(timestamp):
        return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d') if timestamp else None

    # Extract the required information
    submission_info = {
        'id': submission.id,
        'title': submission.content['title']['value'],
        'abstract': submission.content['abstract']['value'],
        'keywords': submission.content['keywords']['value'],
        'primary_area': submission.content['primary_area']['value'],
        'TLDR': submission.content['TLDR']['value'] if 'TLDR' in submission.content else "",
        'creation_date': convert_timestamp_to_date(submission.cdate),
        'original_date': convert_timestamp_to_date(submission.odate),
        'modification_date': convert_timestamp_to_date(submission.mdate),
        'forum_link': f"https://openreview.net/forum?id={submission.id}",
        'pdf_link': f"https://openreview.net/pdf?id={submission.id}"
    }
    return submission_info

submission = submissions[0]
print(extract_submission_info(submission))



import re
from typing import Union, List

def contains_text(submission: dict, target_text: str, fields: Union[str, List[str]] = ['title', 'abstract'], is_regex: bool = False) -> bool:
    # If 'all', consider all available keys in the submission for matching
    if fields == 'all':
        fields = ['title', 'abstract', 'keywords', 'primary_area', 'TLDR']

    # Convert string input for fields into a list
    if isinstance(fields, str):
        fields = [fields]
    
    # Iterate over the specified fields
    for field in fields:
        content = submission.get(field, "")
        
        # Join lists into a single string (e.g., keywords)
        if isinstance(content, list):
            content = " ".join(content)
        
        # Check if the target_text is found in the content of the field
        if is_regex:
            if re.search(target_text, content):
                return True
        else:
            if target_text in content:
                return True
    
    # If no matches were found, return False
    return False



def search_submissions(submissions: List[Dict], target_text: str, fields: Union[str, List[str]] = ['title', 'abstract'], is_regex: bool = False) -> List[Dict]:
    """
    Search through the list of submissions and return those that match the target text.
    
    :param submissions: List of submission dictionaries to search through.
    :param target_text: The text to search for in each submission.
    :param fields: The fields to search within for matching. Default is ['title', 'abstract'].
    :param is_regex: Boolean flag indicating whether to use regex for matching. Default is False.
    :return: List of submissions matching the target text.
    """
    # List to hold matching submissions
    matching_submissions = []
    
    for submission in submissions:
        if contains_text(submission, target_text, fields, is_regex):
            matching_submissions.append(submission)
    
    return matching_submissions
