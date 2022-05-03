from fastapi import APIRouter, HTTPException, status, Response

from variables import *
import base64
from schemas import AddUserDetailsRequest, DeleteUserDetailsRequest, GetUserDetailsRequest

face_router = APIRouter()
# API - 1 : Add user's "fullname", "phone", "group","emailId" & "Face" '''
@face_router.post('/add-face', tags=["face"], status_code=201)
async def add_face(request: AddUserDetailsRequest):
    fullname = request.fullname
    face = request.face
    phone = request.phone
    group = request.group
    emailId = request.emailId

    response = {}
    response['fullname'] = fullname
    response['phone'] = phone
    response['group'] = group
    response['emailId'] = emailId

    try:
        ddb_table.put_item(Item = response)
    except ClientError as e:
         print(e.response['Error']['Message'])
         return e.response['Error']['Message']
    #print("fullname", fullname)
    name1 = fullname.split()
    name = ''
    for i in name1:
        name = name + i
    res = bytes(face, 'utf-8')
    image_64_decode = base64.decodebytes(res)
    file_name = name +'.jpeg'
    obj = s3_resource.Object(S3_BUCKET_NAME,file_name)
    try:
        obj.put(Body=base64.b64decode(res),ACL = 'public-read')
    except ClientError as e:
         print(e.response['Error']['Message'])
         return e.response['Error']['Message']
    #collectionId = 'addFace'

    #rekog_client_response=rekog_client.create_collection(CollectionId=AWS_RECK_COLLECTION_ID)

    try:
        index_response = rekog_client.index_faces(
                              CollectionId=AWS_RECK_COLLECTION_ID,
                              Image={'S3Object':{'Bucket':S3_BUCKET_NAME,'Name':file_name}},
                              ExternalImageId=name,
                              MaxFaces=1,
                              QualityFilter="AUTO",
                              DetectionAttributes=['ALL']
                              )
    except ClientError as e:
         print(e.response['Error']['Message'])
         return e.response['Error']['Message']

    res_msg =  {
            'statusCode': status.HTTP_201_CREATED,
            'body': response,
            'message': 'Data Stored Successfully!!!'
        }
    return res_msg


''' API - 2 : /delete-face '''
@face_router.post("/delete-face", tags=["face"])
async def delete_face(request: DeleteUserDetailsRequest, res:Response):
    fullname = request.fullname
    name1 = fullname.split()
    name = ''
    for i in name1:
        name = name + i
    try:
        response = ddb_table.get_item(Key={'fullname': fullname})
        if "Item" in response.keys():
            ddb_table.delete_item(
            Key={
                'fullname': fullname
            })
            obj = s3_resource.Object(S3_BUCKET_NAME, name + '.jpeg').delete()
            res.status_code = 200
            res_msg = {
                'statusCode': res.status_code,
                'body': {'Response':'Data deleted successfully!!!'
                        }
            }
            return res_msg
        else:
            res.status_code = 404
            return {"response_code": res.status_code,
                    "details": "Item not Found"}
    except ClientError as e:
         print(e.response['Error']['Message'])
         return e.response['Error']['Message']



''' API - 9 : /get-face-details '''
@face_router.post("/get-face-details", tags=["face"])
async def get_face_details(request: GetUserDetailsRequest, res:Response):
    fullname = request.fullname
    name1 = fullname.split()
    name = ''
    for i in name1:
        name = name + i
    try:
        response = ddb_table.get_item(Key={'fullname': fullname})
        if "Item" in response.keys():
            #bucket_name = 'registered-faces'
            data = s3.get_object(Bucket=S3_BUCKET_NAME, Key=name +'.jpeg')
            contents = data['Body'].read()
            img = S3_FACE_URL + name +'.jpeg';
            response_code = data['ResponseMetadata']['HTTPStatusCode']
            res_msg = {
            'statusCode': response_code,
            'Response':'Data Retrieved Successfully',
            'body': {
                'fullname':fullname,
                'emailId': response['Item']['emailId'],
                'group': response['Item']['group'],
                'phone': response['Item']['phone'],
                'img': img
                }
            }
            return res_msg
        else:
            res.status_code = 404
            return {"response_code": res.status_code,
                    "details": "Item not Found"}
    except ClientError as e:
         print(e.response['Error']['Message'])
         return e.response['Error']['Message']
    # except:
    #     raise HTTPException(status_code=404, detail="Item not found")
