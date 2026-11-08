# Phase 1: AWS Terraform Native Synthesis

Quando avvii la generazione dell'infrastruttura da 'infra-intent.md':

1. NON utilizzare moduli Terraform monolitici preesistenti. Genera esclusivamente 
   risorse primitive del provider AWS (~> 5.0).
2. Per ogni componente dichiarato nell'intent, rispetta questi PATTERN CONSTRAINTS:
   - S3: Crea 'aws_s3_bucket', 'aws_s3_bucket_public_access_block' (tutti i flag a true) 
     e 'aws_s3_bucket_server_side_encryption_configuration' (usando il KMS token aziendale).
   - DynamoDB: Usa 'billing_mode = "PAY_PER_REQUEST"' e imposta 'server_side_encryption' abilitata.
   - ECS Fargate: Crea 'aws_ecs_cluster', 'aws_ecs_task_definition' e 'aws_ecs_service'. 
     Il service DEVE essere associato alle sole subnet 'private_app' e avere 'assign_public_ip = false'.
   - API Gateway: Crea 'aws_apigatewayv2_api' di tipo HTTP, 'aws_apigatewayv2_vpc_link' 
     verso le subnet private e le relative route dichiarate nell'intent.
3. Naming Convention:
   - Rispetta la formula: acme-{environment}-{service_name}-{resource_suffix}