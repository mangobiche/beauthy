import requests
import os
import ollama
import re
import pickle
import json
from dotenv import load_dotenv
from github import Github

load_dotenv()  # Load variables from .env file

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
AUTHENTIK_HOST = os.getenv("AUTHENTIK_HOST")
AUTHENTIK_TOKEN = os.getenv("AUTHENTIK_TOKEN")

class BeAuthy(object):
    """
    Class to interact with the BeAuthy application.
    Handles authentication, fetching applications, setting icons, and updating metadata.
    """
    def __init__(self, hostname, token):
        """
        Initialize the BeAuthy client.

        :param hostname: The hostname of the Authentik server.
        :param token: The API token for authentication.
        """
        self.hostname = hostname
        self.token = token
        self.apps = []
        self.icons_meta = []
        self.get_apps()

        # Load or create icons metadata file
        if os.path.isfile('./icons_meta.pkl'):
           with open('./icons_meta.pkl', 'rb') as file:
               self.icons_meta = pickle.load(file)
        else:
           self.icons_meta = self.update_icons()

    def request(self, method, category, headers=None, params=None, payload=None):
        """
        Make a generic HTTP request to the Authentik API.

        :param method: The HTTP method to use (GET, POST, PUT, DELETE, PATCH).
        :param category: The API category endpoint.
        :param headers: Optional dictionary of custom headers.
        :param params: Optional list of parameters for the URL.
        :param payload: Optional JSON payload for POST or PATCH requests.
        :return: Response data if successful, otherwise None.
        """
        if headers is None:
            headers =  { 'Content-Type': 'application/json',
                         'Authorization': f'Bearer {self.token}' }
        if payload is None:
            payload = {}
        if params is None:
            url = f"https://{self.hostname}/api/v3/{category}/"
        else:
            params_parsed = '/'.join([param for param in params])
            url = f"https://{self.hostname}/api/v3/{category}/{params_parsed}/"

        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=payload)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=payload)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, json=payload)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=payload)
            else:
                raise ValueError("Unsupported method: %s" % method)

            if not response.ok:
                response.raise_for_status()
            else:
                if method == "GET":
                    return response.json()['results']
                else:
                    return True

        except Exception as e:
            print(repr(e))

    def get_apps(self):
        """
        Fetch all applications from the Authentik server.
        """
        response = self.request('GET', 'core/applications')
        self.apps = [app for app in response]

    def core_applications_set_icon_create(self, slug, full_path):
        """
        Set an icon for a specific application by uploading a file.

        :param slug: The slug of the application.
        :param full_path: The path to the icon file.
        """
        if not os.path.isfile(full_path):
            print("File '%s' not found. Exiting" %full_path)

        url = f"https://{self.hostname}/api/v3/core/applications/{slug}/set_icon/"

        payload = {}
        files = { 'file': ('file', open(full_path,'rb'), 'image/svg+xml') }
        headers = { 'Content-Type': 'multipart/form-data',
                    'Authorization': 'Bearer %s' % self.token }

        try:
            # TODO: can be merged into general requests
            response = requests.request("POST", url, headers=headers, data=payload, files=files) #, verify=True)

            if not response.ok :
                response.raise_for_status()

            print(f'Icon updated for %s!', slug)
            return response.json()

        except Exception as e:
            print(repr(e))
        return None

    def core_applications_set_icon_url_create(self, slug, icon_url):
        """
        Set an icon URL for a specific application.

        :param slug: The slug of the application.
        :param icon_url: The URL of the icon.

        NOTE: It takes quite a while to update after loading the urls
        """
        self.request("POST", 'core/applications',
                     params=[slug, 'set_icon_url'],
                     payload={ 'url' : icon_url })

    def update_icons(self):
        """
        Update the icons metadata from the GitHub repository.

        :return: List of icons metadata.
        """
        # Get all icons from the repo
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo("homarr-labs/dashboard-icons")
        tree = repo.get_git_tree('main', recursive=True)
        g.close()

        # Search for items in meta folder
        icons_meta = [icon for icon in tree.tree if icon.path.startswith('meta/') and icon.path.endswith('.json')]

        # Save file
        with open('icons_meta.pkl', 'wb') as file:
            pickle.dump(icons_meta, file, protocol=pickle.HIGHEST_PROTOCOL)

        return icons_meta

    def get_icons(self, icon_format='default', theme='dark', save_path='./icons', method='file'):
        """
        Get and set icons for all applications.

        :param icon_format: The format of the icon (e.g., 'svg', 'png').
        :param theme: The color theme of the icon ('light' or 'dark').
        :param save_path: The directory to save the icons.
        :param method: The method to set the icon ('file' or 'url').
        """
        # the name is host? nah
        icons_host = "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/"

        # Evaluate meta for each icon requested
        counter = 0
        for app in self.apps:
            # search for app on icons meta, prioritize full match
            icon_found = False
            icon_meta_path = ''
            print(f"Evaluating {app['slug']}...{counter}")

            for icon in self.icons_meta:
                if icon.path == f"meta/{app['slug']}.json":
                    icon_meta_path = icon.path
                    icon_found = True
                    break

            if not icon_found:
                for icon in self.icons_meta:
                    # go after starts with
                    if icon.path.startswith(f"meta/{app['slug']}"):
                        icon_meta_path = icon.path
                        icon_found = True
                        break

            if not icon_found:
                for icon in self.icons_meta:
                    # ate least is somewhere in!
                    if app['slug'] in icon.path:
                        icon_meta_path = icon.path
                        icon_found = True
                        break

            # no icon found for slug
            if icon_found:
                print(f"Found icon for {app['slug']} in path: {icon_meta_path}")
                icon_filename = icon_meta_path.replace("meta/", "")
                icon_filename = icon_filename.replace(".json", "")

                # evaluate icon format
                # TODO: you need to get the actual json file, not the tree id
                # Get icon meta
                g = Github(GITHUB_TOKEN)
                repo = g.get_repo("homarr-labs/dashboard-icons")
                meta_file = json.loads(repo.get_contents(icon_meta_path).decoded_content)
                g.close()

                if icon_format == 'default':
                    icon_format = meta_file['base']

                # evaluate icon theme
                if hasattr(meta_file, 'colors'):
                    if theme == 'light':
                        icon_url = f"{icons_host}{icon_format}/{icon_filename}-{theme}.{icon_format}"
                else:
                    icon_url = f"{icons_host}{icon_format}/{icon_filename}.{icon_format}"

                if method == 'file':
                    # TODO: its only used here, move it to add_icon
                    # self.download_file(url, filename, save_path)
                    self.core_applications_set_icon_create(app['slug'],
                                                           f"{save_path}/{icon_filename}.{icon_format}")
                elif method == "url":
                    self.core_applications_set_icon_url_create(app['slug'], icon_url)

            else:
                print(f"No icon found for {app['slug']}! Check slug and try again.")

            counter += 1


    ## This could be replicated for every API call required
    # maybe parsing the name of the function so its more generic
    def core_applications_partial_update(self, slug, payload):
        """
        Partially update an application.

        :param slug: The slug of the application.
        :param payload: The JSON payload with fields to update.
        """
        response = self.request('PATCH', 'core/applications', params=slug, payload=payload)


    ## TODO: is it necessary the self?
    def to_kebab_case(self, text):
        """
        Convert a string to kebab-case.

        :param text: The input string.
        :return: The string in kebab-case.
        """
        # Replace spaces and underscores with hyphens
        text = re.sub(r'[\s_]+', '-', text)
        # Insert hyphen before uppercase letters (if not already preceded by a hyphen)
        text = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', text)
        return text.lower()

    # TODO:
    def download_file(self, url, filename, save_path):
        """
        Download a file from a given URL and save it to a specified path.

        :param url: The base URL of the file.
        :param filename: The name of the file to download.
        :param save_path: The directory where the file should be saved.
        :return: True if successful, False otherwise.

        NOTE: haven't chek this fully
        """
        # Downloads a file from a given URL and saves it to a specified path.
        try:
            # Send a GET request to the URL, streaming the response
            composed_url = url + filename
            response = requests.get(composed_url)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Ensure the directory for saving exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path + filename, 'wb') as f:
                f.write(response.content)
            print(f"File downloaded successfully to: {save_path}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error downloading file: {e}")
        except IOError as e:
            print(f"Error saving file: {e}")

    def reset_icons(self):
        """
        Reset all application icons.
        """
        for app in self.apps:
            #self.request("POST", "core/applications", params=app['slug'], payload={'clear':'True'})
            url = f"https://{self.hostname}/api/v3/core/applications/{app['slug']}/set_icon/"
            headers = { 'Authorization': f'Bearer {self.token}' }
            form_data = { "clear": (None, "true") }

            response = requests.post(url, headers=headers, files=form_data)


    def batch_request(self):
        """
        Batch process a request for all applications.

        :param function_to_batch: The function to apply to each application.
        """
        # TODO: everything
        for app in self.apps:
            #
            print('get away from this, for now')

    def get_apps_info(self, model='qwen3:14b'):
        """
        Use AI (Ollama) to generate descriptions and other possible tags for applications.

        :param model: The AI model to use.
        """
        for app in self.apps:
            # Generate description
            print(f'Generating {app["slug"]}...')
            brief = ollama.generate(model=model,
                                    prompt=f'No introductions, plain answer.'
                                           f'A brief description, no more than 2 lines for this app: {app['name']}.'
                                           f'Cocky tone, funny, daring, you''re talking about a homelab',
                                    think=False)
            print(f'Generated description (by {model}): {brief.response}')

            # Generate publisher
            print(f'Generating {app["slug"]}...')
            publisher = ollama.generate(model=model,
                                        prompt=f'No introductions, plain answer.' 
                                               f'Name of {app['name']} publisher.'
                                               f'If the app can be tracked back to github, reply just the repo link',
                                        think=False)
            print(f'Generated description (by {model}): {publisher.response}')

            # Patch both values to authentik
            ba.request('PATCH', 'core/applications',
                       params=[app['slug']],
                       payload={'meta_publisher': publisher.response,
                                'meta_description': brief.response})

if __name__ == '__main__':
    # Initialize the BeAuthy client with environment variables
    # NOTE: must include .env file on the main folder
    ba = BeAuthy(AUTHENTIK_HOST, AUTHENTIK_TOKEN)

    # Update icons metadata from GitHub
    # Needs the .env variable for the GitHub access
    ba.update_icons()

    # Search the homarr-labs/dashboard-icons repo to get all icons available
    # (just the meta, not the actual icons, they are only pointed when requested)
    # ba.get_icons(method='url')

    # Reset all application icons
    # ba.reset_icons()

    # Use Ollama to generate descriptions and publisher information for applications
    ba.get_apps_info()
