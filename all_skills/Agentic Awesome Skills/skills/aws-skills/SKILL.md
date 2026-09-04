---
name: aws-skills
description: "Design and automate AWS cloud architectures, serverless functions, and infrastructure as code. Use when configuring AWS Lambda, API Gateway, S3, DynamoDB, IAM least-privilege policies, CDK, or Terraform deployments."
risk: safe
source: community
---
# AWS Cloud Architecture & Infrastructure Automation

## When to Use
- Designing serverless, microservices, or containerized architectures on AWS.
- Authoring infrastructure as code with AWS CDK (TypeScript/Python) or Terraform.
- Implementing least-privilege IAM security policies and resource-based policies.
- Configuring event-driven pipelines with SQS, SNS, EventBridge, and Lambda.

## Core Architecture Patterns

### 1. Serverless Lambda com TypeScript (ESM)
```typescript
import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';

export const handler = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    const body = event.body ? JSON.parse(event.body) : {};
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'Success', data: body }),
    };
  } catch (error) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Invalid JSON payload' }),
    };
  }
};
```

### 2. Política IAM de Privilégio Mínimo (S3 Bucket Scope)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAppBucketReadWrite",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::app-production-assets/*"
    }
  ]
}
```

### 3. Comandos Úteis do AWS CLI
```bash
# Verificar credenciais e identidade ativa
aws sts get-caller-identity

# Listar buckets S3 com formato tabular
aws s3 ls

# Invocar função Lambda e ler payload de resposta
aws lambda invoke --function-name MyFunction --payload '{"key": "value"}' out.json && cat out.json
```
