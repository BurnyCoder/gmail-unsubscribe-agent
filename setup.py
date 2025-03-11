from setuptools import setup, find_packages

setup(
    name="gmail-unsubscribe",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-api-python-client",
        "google-auth-oauthlib",
        "google-auth",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "gmail-unsubscribe=gmail.cli:main",
        ],
    },
    author="Gmail Unsubscribe Agent",
    description="An agent that unsubscribes from Gmail messages containing 'unsubscribe'",
    keywords="gmail, unsubscribe, agent",
    python_requires=">=3.6",
)
