AWS_PROFILE=brightthread
AWS_REGION=us-west-2
AWS_ACCOUNT_ID=233569452394

deploy-infrastructure:
	# cdk deploy InfrastructureStack --profile $(AWS_PROFILE) --region $(AWS_REGION)
	# cdk deploy CDNStack --profile $(AWS_PROFILE) --region $(AWS_REGION)
	# cdk deploy OidcStack --profile $(AWS_PROFILE) --region $(AWS_REGION)
	# cdk deploy Route53Stack --profile $(AWS_PROFILE) --region $(AWS_REGION)
	# cdk deploy CertificateStackPrimary --profile $(AWS_PROFILE) --region $(AWS_REGION)
	# cdk deploy CertificateStackUsEast1 --profile $(AWS_PROFILE) --region $(AWS_REGION)
	# cdk deploy RDSStack --profile $(AWS_PROFILE) --region $(AWS_REGION)
	cdk deploy DynamoDBStack --profile $(AWS_PROFILE) --region $(AWS_REGION)
	cdk deploy IAMStack --profile $(AWS_PROFILE) --region $(AWS_REGION)

diff-infrastructure:
	# cdk diff InfrastructureStack --profile $(AWS_PROFILE) --region $(AWS_REGION)
	# cdk diff CDNStack --profile $(AWS_PROFILE) --region $(AWS_REGION)
	# cdk diff OidcStack --profile $(AWS_PROFILE) --region $(AWS_REGION)
	# cdk diff Route53Stack --profile $(AWS_PROFILE) --region $(AWS_REGION)
	# cdk diff CertificateStackPrimary --profile $(AWS_PROFILE) --region $(AWS_REGION)
	# cdk diff CertificateStackUsEast1 --profile $(AWS_PROFILE) --region $(AWS_REGION)
	# cdk diff RDSStack --profile $(AWS_PROFILE) --region $(AWS_REGION)
	cdk diff DynamoDBStack --profile $(AWS_PROFILE) --region $(AWS_REGION)
	cdk diff IAMStack --profile $(AWS_PROFILE) --region $(AWS_REGION)
	

deploy-backend:
	cdk deploy BackendServiceStack --profile $(AWS_PROFILE) --region $(AWS_REGION)

diff-backend:
	cdk diff BackendServiceStack --profile $(AWS_PROFILE) --region $(AWS_REGION)

diff-all:
	cdk diff --all --profile $(AWS_PROFILE) --region $(AWS_REGION)

create-api-gateway-role:
	aws apigateway put-account \
    --cloudwatch-role-arn arn:aws:iam::$(AWS_ACCOUNT_ID):role/APIGatewayCloudWatchRole \
    --region $(AWS_REGION)