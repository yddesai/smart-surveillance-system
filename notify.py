import boto3

from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os

SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')



def send_notification(message):
    sns_client = boto3.client('sns', region_name='us-east-1')
    try:
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject='Intruder Alert'
        )
        print("Notification sent!")
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Error in sending notification: {e}")
    # os.system(f"sshpass -p '3141' ssh ydesai@10.0.0.231 -p 22 'python notify.py'")
    # os.system


send_notification("Intruder detected!")