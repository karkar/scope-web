import string

import boto3
import copy
import pymongo.database
import random
from typing import List

import scope.config


def _generate_temporary_password() -> str:
    """
    Generate a temporary password with requirements:
    - 8 characters long
    - Includes at least 1 lowercase, uppercase, number, and symbol

    Allowable Cognito symbols are:
      ^$*.[]{}()?!@#%&/\,><'":;|_~`=+-

    For readability of generated passwords that are emailed to people, we use:
      !@#$%^&*
    """

    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    numbers = string.digits
    symbols = "!@#$%^&*"
    combined_not_symbols = lowercase + uppercase + numbers

    # List to build up a sequence of password characters
    characters = []

    # Include 1 of each class of character
    characters.extend(
        [
            random.choice(lowercase),
            random.choice(uppercase),
            random.choice(numbers),
            random.choice(symbols),
        ]
    )

    # Include 3 characters that are not symbols
    characters.extend(random.sample(combined_not_symbols, 3))
    random.shuffle(characters)

    # Prefix with a character that is not a symbol
    characters = [random.choice(combined_not_symbols)] + characters

    # Convert the list into a string
    temporary_password = "".join(characters)

    return temporary_password


def _get_cognito_users_existing(
    *,
    boto_userpool,
    cognito_config: scope.config.CognitoClientConfig,
) -> List[dict]:
    """
    Obtain a complete list of existing Cognito users.
    """

    user_paginator = boto_userpool.get_paginator("list_users")
    user_pages = user_paginator.paginate(UserPoolId=cognito_config.poolid)

    users = []
    for user_page_current in user_pages:
        users.extend(user_page_current.get("Users", []))

    return users


def populate_account_from_config(
    *,
    database: pymongo.database.Database,
    cognito_config: scope.config.CognitoClientConfig,
    populate_config_account: dict,
) -> dict:
    populate_config_account = copy.deepcopy(populate_config_account)

    if "create" in populate_config_account:
        # Obtain an authorization token.
        # boto will obtain AWS context from environment variables, but will have obtained those at an unknown time.
        # Creating a boto session ensures it uses the current value of AWS configuration environment variables.
        boto_session = boto3.Session()
        boto_userpool = boto_session.client("cognito-idp")

        # Account and email address we intend to create
        create_account_name = populate_config_account["create"]["accountName"]
        create_email = populate_config_account["create"]["email"]
        create_temporary_password = _generate_temporary_password()

        # Raise if an account with the same name already exists
        cognito_users_existing = _get_cognito_users_existing(
            boto_userpool=boto_userpool,
            cognito_config=cognito_config,
        )
        for cognito_user_current in cognito_users_existing:
            if cognito_user_current["Username"] == create_account_name:
                raise ValueError(
                    'Cognito "Username" of "{}" already exists.'.format(
                        create_account_name
                    )
                )

        # Create an account
        response = boto_userpool.admin_create_user(
            UserPoolId=cognito_config.poolid,
            Username=create_account_name,
            TemporaryPassword=create_temporary_password,
            MessageAction="SUPPRESS",
            UserAttributes=[
                {
                    "Name": "email",
                    "Value": create_email,
                },
                {
                    "Name": "email_verified",
                    "Value": "True",
                },
            ],
        )

        # If no exception was raised, the account was created.
        # Recover the "sub" user attribute as the associated unique id.
        created_attributes = {
            attribute["Name"]: attribute["Value"]
            for attribute in response["User"]["Attributes"]
        }
        cognito_id = created_attributes["sub"]

        populate_config_account["existing"] = {
            "cognitoId": cognito_id,
            "accountName": create_account_name,
            "email": create_email,
            "temporaryPassword": create_temporary_password,
        }
        del populate_config_account["create"]

    return populate_config_account
