APP_NAME = "Creative Test Agent"
APP_VERSION = "0.1.0-rc1"
APP_STAGE = "pilot"
BUILD_CHANNEL = "local"


def get_version_info() -> dict:
    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "stage": APP_STAGE,
        "build_channel": BUILD_CHANNEL,
    }
