# Google Play Publisher

This script automates the process of uploading Android App Bundles (AAB) to the Google Play Store and managing releases using the Google Play Developer API.

## Prerequisites

- Python 3.x installed
- A Google Play Developer account
- A service account with access to the Google Play API
- A `key.p12` file for authentication
- A `requirements.txt` file with necessary dependencies

## Installation

1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Create a `.env` file and add the following:
   ```ini
   SERVICE_ACCOUNT_EMAIL=<your-service-account-email>
   ```

## Usage

### Listing Bundles
To list existing app bundles for a package:
```sh
python main.py <package_name>
```
Example:
```sh
python main.py com.example.app
```

### Uploading an AAB
To upload an Android App Bundle to a specific track:
```sh
python main.py <package_name> --aab <path_to_aab> --track <track>
```
Example:
```sh
python main.py com.example.app --aab my_app.aab --track internal --release-notes '{"en-US": "Initial release"}'
```

### Available Tracks
- `internal`
- `alpha`
- `beta`
- `production`

## Notes
- Ensure your service account has the necessary permissions to manage app releases.
- The `key.p12` file should be placed in the project root.
- The `--track` parameter is required when uploading an AAB.

## License
MIT License

