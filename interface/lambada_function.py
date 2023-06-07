import json
import base64
import boto3

# base64 字符串转换后的图片
image_filename = '/tmp/inputimage.jpg'
# 存放图片的 S3 存储桶 
output_bucket = 'detectsotre'
# 存放在 S3 存储桶中的档案名称
s3_key_value = 'apigateway2S3.jpg'

s3_client = boto3.client('s3')

def lambda_handler(event, context):
  requestMethod = event['httpMethod']
  # HTTP 请求方式为 POST 才做后续处理
  if requestMethod=='POST':
    # 将上传的 JSON 字符串转换成字典
    requestBody = json.loads(event['body'])
    # 将上传的 base64 字符串转换成字组，再转换成 binary 格式
    image_64_decode = base64.decodebytes(requestBody['key'].encode())
    # 暂存在 Lambda 的文件系统中
    image_result = open(image_filename, 'wb')
    image_result.write(image_64_decode)
    image_result.close()
    # 上传到 S3 存储桶
    s3_client.upload_file(image_filename, output_bucket, s3_key_value,ExtraArgs={'ACL': 'public-read','ContentType':'image/jpeg'})
    s3_url = 'https://' + output_bucket + '.s3.amazonaws.com/' + s3_key_value
    return {
        'statusCode': 200,
        'body': s3_url
    }
  else:
  # HTTP 请求方式非 POST 回传错误
    return {
        'statusCode': 200,
        'body': 'method error'
    }

