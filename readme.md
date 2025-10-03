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
- `requests`, `pickle`, `json`, `re` libraries
- `dotenv`, `github` libraries
- `ollama` library
- GitHub token with access to the [homarr-labs/dashboard-icons](https://github.com/homarr-labs/dashboard-icons) repository
- Authentik server credentials (hostname and API token)

## Installation 🛠️

1. Clone the repository:
   ```bash
   git clone https://github.com/mangobiche/beauthy
   cd beauthy
   ```

2. Install the required packages using `uv`, the project's package manager:
   ```bash
   uv add requests ollama github python-dotenv
   ```

3. Set up environment variables in a `.env` file:
   ```
   GITHUB_TOKEN=<your-github-token>
   AUTHENTIK_HOST=<your-authentik-host>
   AUTHENTIK_TOKEN=<your-authentik-token>
   ```

## Usage 🚀

1. **Update Icons Metadata** 🔃
   ```bash
   python beauthy.py --update-icons
   ```

2. **Get and Set Icons** 🎨
   ```bash
   python beauthy.py --get-icons --method url
   ```

3. **Reset All Icons** 🔄
   ```bash
   python beauthy.py --reset-icons
   ```

4. **Generate Descriptions and Publishers** 🤖
   ```bash
   python beauthy.py --generate-info
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
