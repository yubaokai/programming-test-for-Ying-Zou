from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

"""
https://github.com/google/guava/pulls?page=2&q=is%3Apr+is%3Aopen
https://github.com/google/guava/pulls?q=is%3Apr+is%3Aclosed
"""

# set the headers of request
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36",
    # "Host": 'github.com',
    'Accept': "application/json, text/plain, */*",
}

requests.DEFAULT_RETRIES = 5  # increase the number of connection retries
s = requests.session()
s.keep_alive = False  # close redundant links


def get_max_page(url):
    """
    get the max_page of the outer url
    for example open is 3 , closed is 32
    """
    print("request", url)
    resp = s.get(url, headers=headers, timeout=300)
    print('resp:', resp)
    html = resp.text
    soup = BeautifulSoup(html, 'lxml')
    paginate_container = soup.find_all('div', class_="paginate-container d-none d-sm-flex flex-sm-justify-center")[0]
    pages = int(paginate_container.find_all('a')[-2].text)
    return pages


def get_detail_url_list(t='open'):
    """
    get the url_list
        [
            "https://github.com/google/guava/pull/5425",
            "https://github.com/google/guava/pull/5398",
            ...
        ]
    :param t: open or closed
    :return: get detail_url_list
    """
    url_list = []
    # https://github.com/google/guava/pulls?page=2&q=is%3Apr+is%3Aclosed
    url = f"https://github.com/google/guava/pulls?page=1&q=is%3Apr+is%3A{t}"
    p = get_max_page(url)
    print('max_page:', p)
    # go through every page
    for i in range(p):
        print('page of outer:', i+1, "page")
        url = f"https://github.com/google/guava/pulls?page={i+1}&q=is%3Apr+is%3A{t}"
        print('request:', url)
        resp = s.get(url, headers=headers, timeout=300)
        html = resp.text
        soup = BeautifulSoup(html, 'lxml')
        pull_list_container = soup.find('div', class_="js-navigation-container js-active-navigation-container")
        pull_list_list = pull_list_container.find_all('a', class_="Link--primary")
        for i in pull_list_list:
            url = "https://github.com" + i.attrs['href']
            print(url)
            url_list.append(url)
    return url_list


def get_html_text(detail_url):
    """
    get the information of the text through url request
    """
    resp = s.get(
        detail_url,
        headers=headers,
        timeout=300
    )
    resp.encoding = 'utf-8'
    return resp.text


def parse_detail_data(html):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.find('span', class_="js-issue-title").text.strip()
    print('title', title)
    # 1: Reviewers
    # 2: Assignees
    # 3: Labels
    right_sidebar = soup.find(
        'div',
        id="partial-discussion-sidebar"
    )
    right_div_list = right_sidebar.find_all(
        'div',
        recursive=False  # only find direct child node
    )
    # Reviewers
    reviewers_list = right_div_list[0].find_all(
        'span',
        class_="css-truncate-target")
    reviewers_list = [reviewer.text for reviewer in reviewers_list]
    reviewers = ','.join(reviewers_list)
    print('reviewers', reviewers)
    # for reviewer in reviewers_list:
    #     print(reviewer.text)
    # Assignees
    assignees_list = right_div_list[1].find_all(
        'span',
        class_="css-truncate-target")
    assignees_list = [assignees.text for assignees in assignees_list]
    assignees = ','.join(assignees_list)
    print('assignees', assignees)
    # for assignees in assignees_list:
    #     print(assignees.text)
    # Labels
    labels_list = right_div_list[2].find_all(
        'span',
        class_="css-truncate-target")
    labels_list = [labels.text for labels in labels_list]
    labels = ' '.join(labels_list)
    print('labels', labels)
    # for labels in labels_list:
    #     print(labels.text)
    # Comments
    comments_list = soup.find_all(
        'div',
        class_="timeline-comment-group"
    )
    comments_text_list = []
    for comments in comments_list:
        try:
            comments_user = comments.find(
                'a',
                class_="author Link--primary css-truncate-target width-fit"
            ).text.strip()
        except:
            comments_user = "None"
        # print(comments_user)

        try:
            comments_content = comments.find(
                'table'
            ).text.strip()
        except:
            comments_content = "None"

        # print(comments_content)
        comments_text_list.append(f"{comments_user}: {comments_content}")
    comments = '.'.join(comments_text_list)
    print('comments', comments)

    # Opened time
    opened_time = comments_list[0].find('relative-time').attrs['datetime']
    print('opened_time', opened_time)

    # Closed time regular expression
    closed_time = re.findall(
        r'</a>.*?closed this.*?datetime="(.*?Z)"',
        html, flags=re.DOTALL)
    if len(closed_time) > 0:
        closed_time = closed_time[0]
    else:
        closed_time = 'None'
    print('closed_time', closed_time)
    # Number of commits
    try:
        number_of_commits = soup.find('span', id="commits_tab_counter").text
    except:
        number_of_commits = '0'
    print('number_of_commits', number_of_commits)
    # Number of changed files
    try:
        number_of_changed_files = soup.find('span', id="files_tab_counter").text
    except:
        number_of_changed_files = '0'
    print('number_of_changed_files', number_of_changed_files)
    # Number of participants
    try:
        number_of_participants = soup.find('div', id="partial-users-participants").text.strip().split()[0]
    except:
        number_of_participants = "0"
    print('number_of_participants', number_of_participants)

    df = pd.DataFrame([
        [title, labels, reviewers, assignees, comments,
         opened_time, closed_time, number_of_commits,
         number_of_changed_files, number_of_participants]
    ], columns=[
        "Title", "Labels", "Reviewers", "Assignees", "Comments",
        "Opened time", "Closed time", "Number of commits",
        "Number of changed files", "Number of participants"
    ])

    return df


if __name__ == '__main__':


    # DataFrame
    df_list = []

    # get 800+ pages of detail_url_list
    open_url_list = get_detail_url_list(t='open')
    closed_url_list = get_detail_url_list(t='closed')
    url_all = open_url_list + closed_url_list

    pd.DataFrame({'detail_urls': open_url_list + closed_url_list}).to_excel(
        "detail_urls.xlsx", index=False
    )

    # url_all = list(pd.read_excel('detail_urls.xlsx')['detail_urls'])

    # go through every detail_page
    for url in url_all:
        try:
            detail_txt = get_html_text(url)
            # parse the text
            df = parse_detail_data(detail_txt)
            df_list.append(df)
        except:
            continue

    # combine all DataFrame
    df_all = pd.concat(df_list)

    # export csv file
    df_all.to_csv('github_guava.csv', index=False)
    df_all.to_excel('github_guava.xlsx', index=False)

    # df.to_excel('1.xlsx')

