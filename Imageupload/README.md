置触发器为当S3:detectsotre中上传图片时，Lambda函数应该读取上传的图像，检测图像中的对象，并将检测到的对象列表(称为标签)与该图像的S3 URL一起保存在AWS的Dynamodb中 ，以备将来查询。注意，YOLO配置文件存储在S3：detectconfig中，并在lambda_function的layer中添加运行yolo所需的环境包

S3：detectsotre
![6e44be534678044eced2703a84ccdf9](https://github.com/cuixh0/aws-cognito-tutorial-complete/assets/75778123/00334273-9448-43c9-a19d-4cfd9b3a9fb5)
S3:detectconfig
![f357db1b5822a234464d995282cfd25](https://github.com/cuixh0/aws-cognito-tutorial-complete/assets/75778123/f0cdf9d2-d21a-43d1-99b6-5a69c55f4eef)
labda_function and layer
![157ba9b0ccbf970ee7f784deea265be](https://github.com/cuixh0/aws-cognito-tutorial-complete/assets/75778123/1d9e4760-4ba6-4843-84e2-c2dc7014d450)
Dynamodb
![abeb93179d89580dcce2dba06868279](https://github.com/cuixh0/aws-cognito-tutorial-complete/assets/75778123/865c6014-45a9-433e-8344-e3332a09b6b7)
