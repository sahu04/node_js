import os
import requests
import json

def get_pull_requests_between_releases(owner, repo, release_versions, github_token):
    url = f'https://api.github.com/repos/{owner}/{repo}/pulls'
    headers = {'Authorization': f'token {github_token}'}
    pull_requests = []

    page = 1
    per_page = 100 

    while True:
        response = requests.get(url, headers=headers, params={'page': page, 'per_page': per_page, 'state': 'all'})

        if response.status_code == 200:     
            page_pull_requests = response.json()
            if not page_pull_requests:
                break  

            for pr in page_pull_requests:
                pr_labels = [label['name'] for label in pr.get('labels', [])]
                if any(label in release_versions for label in pr_labels):
                    pr_details_response = requests.get(pr['url'], headers=headers)
                    if pr_details_response.status_code == 200:
                        pr_details = pr_details_response.json()
                        pr_details['labels'] = pr_labels
                        pull_requests.append(pr_details)
            page += 1
        else:
            print(f'Failed to fetch pull requests. Status code: {response.status_code}')
            return None

    return pull_requests

if __name__ == "__main__":
    with open('config.json') as config_file:
        config = json.load(config_file)

    owner = config.get('owner')
    repo = config.get('repo')
    release_versions = config.get('release_versions', [])
    github_token = os.getenv('MY_GITHUB_TOKEN')

    pull_requests = get_pull_requests_between_releases(owner, repo, release_versions, github_token)
    
    if pull_requests is not None:
        version_msg = f'release versions {", ".join(release_versions)}'
        total_pull_requests_msg = f'Total pull requests for {version_msg}: {len(pull_requests)}'
        print(total_pull_requests_msg)
        output_file = 'pull_requests.txt'
        with open(output_file, 'w') as f:
            f.write(f'Total pull requests for {version_msg}: {len(pull_requests)}\n')
            f.write("Pull Requests:\n")
            if len(pull_requests) == 0:
                f.write("No pull requests found for the specified versions.\n")
            else:
                for pr in pull_requests:
                    pr_info = f'- #{pr["number"]}: {pr["title"]} by {pr["user"]["login"]}'
                    if pr.get("labels"):
                        labels_info = f' {pr["labels"]}'
                    else:
                        labels_info = ''
                    f.write(f'{pr_info}{labels_info}\n')
                    f.write(f'  URL: {pr["html_url"]}\n')
                    f.write(f'  State: {pr["state"]}\n')
                    f.write(f'  Description: {pr["body"]}\n\n' if pr.get("body") else '\n')
        print(f'Pull requests details are saved in {output_file}')
    else:
        print('Failed to retrieve pull requests.')
