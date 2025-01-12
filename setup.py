from setuptools import setup, find_packages

setup(
    name="recipe_level_predictor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.95.2",
        "uvicorn==0.15.0",
        "sqlalchemy==1.4.54",
        "mysql-connector-python==8.0.33",
        "python-dotenv==0.19.2",
        "pydantic==1.10.13",
        "pytest==6.2.5",
        "httpx==0.24.1",
    ],
)
