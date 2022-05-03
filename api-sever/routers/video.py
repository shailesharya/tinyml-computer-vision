from fastapi import APIRouter, HTTPException
from variables import *
import datetime

video_router = APIRouter()


# ''' API - 12 : get-all-video-details '''

@video_router.get("/get-all-video-details", tags=["video"])
async def get_all_video_details():
    try:
        response = dynamodb_client.scan(TableName = AWS_DB_TABLE2,
                   AttributesToGet=['notification','approx_capture_timestamp','s3_video_key'])
        print(response['ResponseMetadata']['HTTPStatusCode'])
        data = {"notification": []}
        temp = data['notification']
        for i in range(len(response['Items'])):
           data1 = response['Items'][i]['notification']['S']
           timestamp = response['Items'][i]['approx_capture_timestamp']['N']
           time = datetime.datetime.fromtimestamp(int(timestamp))
           time1 = time.strftime("%d, %b %Y :  %H:%M:%S")
           url = S3_VIDEO_URL
           video = response['Items'][i]['s3_video_key']['S']
           video = url + video
           y = {
               "title":data1,
               "time": time1,
               "video": video
           }
           temp.append(y)
        return data

    except ClientError as e:
        print("Error: " + e.response['Error']['Message'])
        response = e.response['Error']['Message']
        return response
    # except:
    #     raise HTTPException(status_code=404, detail="Table not found!!")




    # return {
    #    'statusCode': 200,
    #    'Data': data
    # }
