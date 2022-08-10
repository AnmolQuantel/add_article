import json
import tenjin_utility as pg
import re


def lambda_handler(event, context):
    if isinstance(event['body'], (str)):
        input_json = json.loads(event['body'])
    else:
        input_json = event["body"]

    print(input_json)
    if "x-api-key" in event["headers"]:
        api_key = event["headers"]["x-api-key"]

        id_sql = f"Select * from tenjin_common.get_tenant_info_json('{api_key}')"
        columns = ('id_json')
        print('SQL:', id_sql)

        id_json = json.loads(pg.run(id_sql, columns))

        if not (id_json):
            return {"body": "Access to API forbidden", "statusCode": 403, "headers": {
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
                }}
        else:
            schema = id_json[0]['i']['schema']
            tenant = id_json[0]['i']['tenant']
            if ("clientUserId" in input_json):
                user_name = input_json["clientUserId"]
            elif input_json["clientUserId"].strip() == '':
                return {"body": "clientUserId attribute is mising", "statusCode": 400, "headers": {
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
                    }}
            else:
                return {"body": "Client User Id is required", "statusCode": 400, "headers": {
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
                    }}
    else:
        try:
            user_name = event['requestContext']['authorizer']['claims']['cognito:username']
            tenant = 'Tenjin'
        except KeyError:
            return {"body": "Access to API forbidden. Authorization information not provided.", "statusCode": 403,
                    "headers": {
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
                        }}

    article_data = json.dumps(input_json["articleData"])
    article_author = input_json["articleAuthor"]
    article_hashtags = input_json["articleHashtags"]
    article_expiry_time = input_json["articleExpiryTime"]

    if not ("category" in article_data):
        return {"body": "ERROR: category field is missing, add category field in article", "statusCode": 400, "headers": {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
            }}

    if not ("title" in article_data):
        return {"body": "ERROR: title field is missing, add title field in article", "statusCode": 400, "headers": {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
            }}

    if not ("subtitle" in article_data):
        return {"body": "ERROR: subtitle field is missing, add subtitle field in article", "statusCode": 400, "headers": {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
            }}

    if not ("summarytext" in article_data):
        return {"body": "ERROR: summarytext field is missing, add summarytext field in article", "statusCode": 400, "headers": {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
            }}

    if not ("ctatext" in article_data):
        return {"body": "ERROR: ctatext field is missing, add ctatext field in article", "statusCode": 400, "headers": {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
            }}

    if not ("webctalink" in article_data) and not ('appctalink' in article_data):
        return {"body": "ERROR: ctalink field is missing, either webctalink or appctalink should be there", "statusCode": 400, "headers": {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
            }}

    if not article_author:
        return {"body": "ERROR: article author is missing, add article author in body",
                "statusCode": 400, "headers": {
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
            }}

    if not article_hashtags:
        return {"body": "ERROR: article hashtags is missing, add article hashtags in body",
                "statusCode": 400, "headers": {
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
            }}

    sql_string = f"select * from tenjin_common.add_article('{article_data}','{article_author}','{article_hashtags}'," \
                 f"{article_expiry_time});"
    pg.debug_print('SQL statement', sql_string)

    try:
        #return_columns = ('article_json')
        created_record = json.loads(pg.run(sql_string))
        article_id = created_record[0]['g']
        return {"body": json.dumps({"articleId": article_id}), "statusCode": 200, "headers": {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
        }}
    except Exception as error:
        print(error)
        return {"body": f"Internal error! Error adding article", "statusCode": 500, "headers": {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
            }}

