from fastapi import APIRouter, status, Response
from variables import *
from schemas import UserUpdateDetailRequest, EditContactDetailsRequest, GetUserFromGroupRequest

contact_router = APIRouter()


'''
API - 11 : /edit-contact //Sample got problem
'''
@contact_router.post("/edit-contact", tags=["contact"])
async def edit_contact(request: EditContactDetailsRequest, resp:Response):
    previous_name = request.previous_name
    fullname = request.fullname
    p_name1 = previous_name.split()
    p_name = ''
    name1 = fullname.split()
    name = ''
    for i in p_name1:
        p_name = p_name + i
    for i in name1:
        name = name + i
    p_email = request.emailId
    p_phone = request.phone
    p_group = request.group
    face = request.face
    try:
        response = ddb_table.get_item(Key={'fullname': previous_name})
        print(response)
        if "Item" in response.keys() :
            ddb_table.delete_item(Key={'fullname': previous_name})
            item = {}
            item['fullname'] = fullname
            item['phone'] = p_phone
            item['group'] = p_group
            item['emailId'] = p_email
            ddb_table.put_item(Item = item)
            res = bytes(face, 'utf-8')
            image_64_decode = base64.decodebytes(res)
            file_name = name +'.jpeg'
            print(file_name)
            try:
                #Deleting S3 item
                del_item = s3.delete_object(Bucket=S3_BUCKET_NAME, Key=p_name + '.jpeg')
                #s3.Object(bucket_name, file_name).delete()
                #inserting new Image
                obj = s3_resource.Object(S3_BUCKET_NAME,file_name)
                obj.put(Body=base64.b64decode(res))
                resp.status_code = 200
                res_msg =  {
                        "statusCode": resp.status_code,
                        "Message" : "User details updated successfully"
                    }
                return res_msg
            except ClientError as e:
                 print(e.response['Error']['Message'])
                 return e.response['Error']['Message']
        else:
            resp.status_code = 404
            return {"response_code": resp.status_code,
                    "details": "Item not Found"}

    except ClientError as e:
         print(e.response['Error']['Message'])
         return e.response['Error']['Message']

'''
API - 4 : /update-details - change/update group (i.e. friend, family, visitor)
'''
@contact_router.post("/update-details", tags=["contact"])
async def update_details(request: UserUpdateDetailRequest, res:Response):
  fullname = request.fullname
  updated_group = request.group
  res_msg = {}
  item = {}
  try:
      #DB operation
      response = ddb_table.get_item(Key={'fullname': fullname})
      print(response.keys())
      if "Item" in response.keys() :
          email = response['Item']['emailId']
          phone = response['Item']['phone']
          item['fullname'] = fullname
          item['phone'] = phone
          item['group'] = updated_group
          item['emailId'] = email
          #DB operation
          ddb_table.put_item(Item = item)
          res_msg = {
           'statusCode': status.HTTP_200_OK,
           'body': {
              'Response':'Data Updated Successfully',
              'data': item
              }
          }
          return res_msg
      else:
        resp.status_code = 404
        res_msg = {
            "response_code": resp.status_code,
            "details": "Item not Found"
        }
        return res_msg
  except ClientError as e:
       print("Error")
       print(e.response['Error']['Message'])
       #return "e.response['Error']['Message']"
       raise e

# '''
# API - 3 : /get-data-on-group
# '''
@contact_router.post("/get-data-on-group", tags=["contact"])
async def get_data_on_group(request: GetUserFromGroupRequest, res:Response):
    group = request.group
    res_msg = {}
    try:
        response = ddb_table.scan(
            FilterExpression=Attr('group').eq(group)
        )
        print("raw_responce",response)
        if(int(response['Count']) == 0):
            res.status_code = 404
            res_msg = {
                    "status_code": res.status_code,
                    "Details": "No such Group Found"
            }
            return res_msg
        else:
            for i in range(0,len(response['Items'])):
                print(response['Items'][i])
                fullname = response['Items'][i]['fullname']
                name1 = fullname.split()
                name = ''
                for j in name1:
                    name = name + j
                print("name:" ,name)
                image = S3_FACE_URL + name +'.jpeg'
                print(image)
                response['Items'][i]['img'] = image
            res_msg = {
                "Details": "Data Retrieved Successfully"
            }
            return res_msg
    except botocore.exceptions.ClientError as error:
        raise error
