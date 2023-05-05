#  Copyright (c) 2015-2021 Condugo bvba
import os
import string
from random import choice
from typing import List, Optional

import sendgrid
from flask import request, current_app
from pydantic import EmailStr, ValidationError, StrictStr, SecretStr, BaseModel
from sendgrid.helpers.mail import *

from api.logger import logger
from api.status import HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR
from api.v2 import blueprint, make_response
from cdg_service.errors import InvalidParameter
from cdg_service.service.auth import UserService
from cdg_service.service.cluster import ClusterService
from cdg_service.service.email import EmailService
from cdglib import scoped_general_session

MARKETING_APIKEY = "a*BT36gXzHZ!XCQay84dKadNQXGq$fvjZ$D8#*RATFa3sSb78Q%&49f2w2b5D%446WyAccGT5DWMcFg4eqc!uXw4HXCQbNSmc69fEBdtJWNudv4TmV&cH!2sx$Ny^3Zb"
TEST_API_KEY = "GWGrJeQeTUkRXjYFbuMP^hPM2bDC6TfE@HFaMX%DV65u@hqMHqAUEA@vVSERqFfe2*pPzmNjj2J!Nx3wJGw3*5#vBT8&$M!2dkWp@97H&hSjDJQ*z3UGQh^!Mzj2h#ks"
DEMO_DOMAIN_ID = 231
SENDGRID_API_KEY =  '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' # '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'
CDG_MARKETING_EMAIL = "info@condugo.com"


class DemoUserIn(BaseModel):
    first_name: StrictStr
    last_name: StrictStr
    email: EmailStr
    apikey: StrictStr


class DemoUserOut(BaseModel):
    email: StrictStr
    password: SecretStr


@blueprint.route('/marketing/register_demo_user', methods=["POST"])
def register_demo_user():
    json_data = request.get_json(silent=True)
    provided_apikey: Optional[str] = json_data.get("apikey")
    if not MARKETING_APIKEY or not provided_apikey:
        message = f"APIKEY is not correct!"
        logger.error(f"{request.url}: {message}: {provided_apikey} - {request.args}")
        return make_response({}, error_msg=message, status_code=HTTP_403_FORBIDDEN)
    if provided_apikey != MARKETING_APIKEY and provided_apikey != TEST_API_KEY:
        message = f"APIKEY is not correct"
        logger.error(f"{request.url}: {message}: {provided_apikey} - {request.args}")
        return make_response({}, error_msg=message, status_code=HTTP_403_FORBIDDEN)
    try:
        schema = DemoUserIn(**json_data)
    except ValidationError as e:
        message = str(e)
        logger.error(f"{request.url}: Validation error: {message} - {request.args}")
        return make_response({}, error_msg=message, status_code=HTTP_400_BAD_REQUEST)
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            user_service = UserService(session)
            generated_password = generate_password( string.ascii_letters+string.digits, 10)
            full_name = f"{schema.first_name} {schema.last_name}"
            user = {
                "name": full_name,
                "title": "Demo User",
                "active": True,
                "email": schema.email,
                "department": "Demo Users",
                "password": generated_password,
                "roles": [
                    {
                        "role_id": 22,
                        "domain_id": DEMO_DOMAIN_ID
                    }
                ]
            }
            try:
                user_service.create(user)
                session.commit()
            except InvalidParameter as e:
                # Check if user exists.
                if e.message.startswith("Email address already in use:"):
                    # Reset password for user and reset creation date
                    user = user_service.reset_password_for_demo_or_cluster_user(schema.email, generated_password)
                    session.commit()
            email_service = EmailService(session)
            # Create user email
            user_email_response = email_service.send(
                from_email=CDG_MARKETING_EMAIL,
                to_emails=[schema.email],
                subject="Demo account information",
                content=f"""Thank you for your interest in our Energy Management Platform.\n\nPlease find your login information below. Your login will be valid for 15 days. \n\nWebsite: https://races.condugo.com\nUsername: {schema.email}\nPassword: {generated_password}\n\nIf you have questions or need more information, feel free to contact us on\ninfo@condugo.com\n\nThe Condugo Team\nwww.condugo.com"""
            )
            # Create condugo email
            cdg_email_response = email_service.send(
                from_email=CDG_MARKETING_EMAIL,
                to_emails=[CDG_MARKETING_EMAIL],
                subject="Demo account information",
                content=f"""The following user has registered himself for a R-Aces demo account\n\nUser: {full_name}\nUsername: {schema.email}\n"""
            )
            user_out = DemoUserOut(email=schema.email, password=generated_password)
            response = make_response(user_out, 'User created', status_code=HTTP_201_CREATED)
    except Exception as e:
        print(e)
        response = make_response({}, error_msg='Generic error', status_code=HTTP_500_INTERNAL_SERVER_ERROR)

    return response

class ClusterUserIn(BaseModel):
    first_name: StrictStr
    last_name: StrictStr
    email: EmailStr
    apikey: StrictStr
    cluster_name: str


class ClusterUserOut(BaseModel):
    email: StrictStr
    password: SecretStr


def setup_cluster(cluster_name: str, cluster_service) -> None:
    """ Setup an new cluster for a user """
    cluster = {
        "name": cluster_name,
        "active": True,
    }
    cluster = cluster_service.create(json_data=cluster)
    return cluster



@blueprint.route('/marketing/register_cluster_user', methods=["POST"])
def register_cluster_user():
    json_data = request.get_json(silent=True)
    provided_apikey: Optional[str] = json_data.get("apikey")
    print(f"Marketing key: {MARKETING_APIKEY}, provided_apikey: {provided_apikey}")
    if not MARKETING_APIKEY or not provided_apikey:
        message = f"APIKEY is not correct!"
        logger.error(f"{request.url}: {message}: {provided_apikey} - {request.args}")
        return make_response({}, error_msg=message, status_code=HTTP_403_FORBIDDEN)
    if provided_apikey != MARKETING_APIKEY and provided_apikey != TEST_API_KEY:
        message = f"APIKEY is not correct"
        logger.error(f"{request.url}: {message}: {provided_apikey} - {request.args}")
        return make_response({}, error_msg=message, status_code=HTTP_403_FORBIDDEN)
    try:
        from pprint import pprint
        pprint(json_data)
        schema = ClusterUserIn(**json_data)
    except ValidationError as e:
        message = str(e)
        logger.error(f"{request.url}: Validation error: {message} - {request.args}")
        return make_response({}, error_msg=message, status_code=HTTP_400_BAD_REQUEST)
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:


            # Setup the cluster
            cluster_service = ClusterService(session=session, config=current_app.config)
            clusters = cluster_service.read()
            cluster_names = [cluster.name for cluster in clusters]
            # print(f"Cluster names: {cluster_names}")
            if schema.cluster_name in cluster_names:
                message = f"Cluster name {schema.cluster_name} already exists"
                # cluster = None
                # for clus in clusters:
                #     if clus.name == schema.cluster_name:
                #         cluster = clus
                logger.error(f"{request.url}: {message}: {provided_apikey} - {request.args}")
                return make_response({}, error_msg=message, status_code=HTTP_400_BAD_REQUEST)
            else:
                cluster = setup_cluster(schema.cluster_name, cluster_service)

                        # Setup the user
            generated_password = generate_password( string.ascii_letters+string.digits, 10)
            full_name = f"{schema.first_name} {schema.last_name}"
            user_schema = {
                "name": full_name,
                "title": "Cluster User",
                "active": True,
                "email": schema.email,
                "department": "Cluster Users",
                "password": generated_password,
                "roles": [                    
                    {
                        "role_id": 21,
                        "domain_id": cluster.id
                    },
                    {
                        "role_id": 22,
                        "domain_id": cluster.id
                    }
                ]
            }

            user_service = UserService(session)
            try:
                user_service.create(user_schema.copy())

            except InvalidParameter as e:
                # Check if user exists.
                if e.message.startswith("Email address already in use:"):
                    # print(f"User already exists: {schema.email} - new generared password: '{generated_password}' !")
                    # Reset password for user and reset creation date
                    existing_user = user_service.reset_password_for_demo_or_cluster_user(schema.email, generated_password)
                    # print(f"Existing user: {existing_user}")
                    # print(user_schema)
                    # Add new cluster roles to user
                    if existing_user:
                        # print(f"Existing user id: {existing_user.id} - roles: {user_schema['roles']}")
                        user_service.add_roles_to_user(existing_user, user_schema["roles"])
                    session.commit()

            email_service = EmailService(session)
            # Create user email
            user_email_response = email_service.send(
                from_email=CDG_MARKETING_EMAIL,
                to_emails=[schema.email],
                subject="Cluster account information",
                content=f"""Thank you for your interest in our Energy Management Platform.\n\nPlease find your login information below. \n\nWebsite: https://races.condugo.com\nUsername: {schema.email}\nPassword: {generated_password}\n\nIf you have questions or need more information, feel free to contact us on\ninfo@condugo.com\n\nThe Condugo Team\nwww.condugo.com"""
            )
            # Create condugo email
            cdg_email_response = email_service.send(
                from_email=CDG_MARKETING_EMAIL,
                to_emails=[CDG_MARKETING_EMAIL],
                subject="Cluster account information",
                content=f"""The following user has registered himself for a R-Aces cluster account\n\nUser: {full_name}\nUsername: {schema.email}"""
            )
            user_out = ClusterUserOut(email=schema.email, password=generated_password)
            response = make_response(user_out, 'User created', status_code=HTTP_201_CREATED)
    except Exception as e:
        print(e)
        response = make_response({}, error_msg='Generic error', status_code=HTTP_500_INTERNAL_SERVER_ERROR)

    return response


def clean_demo_accounts():
    """ Clean demo accounts older than 15 days """
    with scoped_general_session(call_back=current_app.register_session) as session:
        user_service = UserService(session)
        user_service.read()


def send_email(from_email: str, to_emails: List[str], subject: str, content: str, content_type: str="text/plain"):
    """ Send an email using sendgrid """
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email(from_email)
    to_email = To(to_emails)
    content_obj = Content(content_type, content)
    mail = Mail(from_email, to_email, subject, content_obj)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.message)
    return response


def generate_password(alphabet:str, length:int):
    """ Generate a password with length: int with characters alphabet """
    return ''.join(choice(alphabet) for _ in range(length))

