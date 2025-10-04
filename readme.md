# BeAuthy 🚀

BeAuthy is a Python script designed to interact with an [Authentik](https://github.com/goauthentik/authentik/) server and make it prettier (beauty-authentik). It started because I'm lazy and didn't want to manually setup every icon for every app in authentik (my homelab has 23 apps and counting), so I wanted a more sustainable and cleaner way to do it. 

It automates the process of fetching applications, setting icons, updating metadata, and leveraging AI to generate descriptions and publisher information.

__NOTE__: this is really rough so far, use with caution.

## Features 🌟

- **Fetch Applications** 📋 Retrieve all applications from the Authentik server.
- **Set Icons** 🎨 Upload or set icon URLs for applications.
- **Update Icons Metadata** 🔄 Fetch and store icons metadata from [homarr-labs/dashboard-icons](https://github.com/homarr-labs/dashboard-icons) repository.
- **Generate Descriptions and Publishers** 🤖 Use AI (Ollama) to generate descriptions and publisher information for applications.

## Prerequisites 🛠️

- Python 3.13.3
- `requests`, `pickle`, `json`, `re`, `fire`, `dotenv`, `github`, `ollama` libraries
- GitHub token with access to the [homarr-labs/dashboard-icons](https://github.com/homarr-labs/dashboard-icons) repository
- Authentik server credentials (hostname and API token)

## Installation 🛠️

1. Clone the repository:
   ```bash
   git clone https://github.com/mangobiche/beauthy
   cd beauthy
   ```

2. Sync the required packages using `uv`, the project's package manager:
   ```bash
   uv sync
   ```

3. Set up environment variables in a `.env` file:
   ```
   GITHUB_TOKEN=<your-github-token>
   AUTHENTIK_HOST=<your-authentik-host>
   AUTHENTIK_TOKEN=<your-authentik-token>
   ```

## Usage 🚀
Working on this, for now, you can edit the main [beauthy.py](./beauthy.py) to call the functions you might need.

1. **Update Icons Metadata** 🔃
    This updates the metadata for icons. Run this prio to other operations.
   ```bash
   uv run beauthy.py update_icons
   ```

2. **Get and Set Icons** 🎨
    This will search the meta database for icons and apply them to all Authentik apps. The search method is based on the app __slug__, so keep it as simple and in kebab case as possible (see helper function ``to_kebab_case()``). The only tested method for now is url. Adding file upload soon.
    
    > **💡 Note:**
   > apps icon would take some time to show on Authentik's dashboard but will reflect the change almost inmediately on the ``Admin Interface > Applications menu``.
   ```bash
   uv run beauthy.py get_icons
   uv run beauthy.py get_icons "single_app_slug"
   ```

3. **Reset a single app or all apps Icons** 🔄
    Sometimes (haven't identify the reason) the app would show a big Application Icon msg on authentik instead of the actual icon. Just reset the app icon.
   ```bash
   uv run beauthy.py reset_icons
   uv run beauthy.py reset_icons "single_app_slug"
   ```

4. **Generate Descriptions and Publishers** 🤖
   ```bash
   uv run beauthy.py generate_info
   uv run beauthy.py generate_info "single_app_slug"   
   ```
5. **Full run!**
   This will execute all the above commands, reset icons, get meta for icons, update icons urls and then generate the description and publisher with Ollama. This is mainly for testing purposes 
   ```bash
   uv run beauthy.py full_run
   ```

## Contributing 👥

Feel free to contribute to this project by opening issues or submitting pull requests.

## License 🔒

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- **AI Model**: The script uses the Ollama model `qwen3:14b` for generating descriptions and publisher information.
- **GitHub Repository**: Icons metadata are fetched from the [homarr-labs/dashboard-icons](https://github.com/homarr-labs/dashboard-icons) repository.

---

**readme file (mostly) Generated with love by qwen served by Ollama.**
(Imagine if I'm too lazy for setting icons urls manually...where does it leaves me to writing a full readme.md)
