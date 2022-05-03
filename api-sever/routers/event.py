from fastapi import APIRouter,status, Response
from variables import *
import datetime

from schemas import GetEventDetailsRequest

event_router = APIRouter()

''' API - 10 : /get-event-details '''
@event_router.post("/get-event-details", tags=["event"] )
async def get_event_details(request: GetEventDetailsRequest, res:Response):
    ddb_table = dynamodb_resource.Table(AWS_DB_TABLE2)
    fullname = request.fullname
    name1 = fullname.split()
    name = ''
    for i in name1:
        name = name + i
    print(name)
    try:
        response = ddb_table.scan(
            FilterExpression=Attr('external_image_id').eq(name))
        print(response)
        if(response['Count'] == 0):
            res.status_code = 404
            return {"response_code": res.status_code,
                    "details": "Item not Found"}
        data = {"notification": []}
        temp = data['notification']
        for i in range(len(response['Items'])):
            data1 = response['Items'][i]['notification']
            print(response['Items'][i]['notification'])
            timestamp =  response['Items'][i]['approx_capture_timestamp']
            time1 = datetime.datetime.fromtimestamp(int(timestamp))
            #time = time1.strftime("%m-%d-%Y  %H:%M %P")
            time = time1.strftime("%m-%d-%Y  %H:%M:%S")
            print("time:",time)
            #video = 'https://rpidemo.s3.amazonaws.com/video/'+response['Items'][i]['s3_video_key']
            y = {
                "title":data1,
                "time": time
            }
            temp.append(y)
            res_msg = {
                'statusCode': status.HTTP_200_OK,
                'Data': data
                }
            return res_msg
    except ClientError as e:
         print(e.response['Error']['Message'])
         return e.response['Error']['Message']
