# Brightthread Infrastructure - Python CDK Project

## Overview

Production-grade AWS CDK infrastructure as code for Brightthread, a full-stack application. This project follows AWS CDK best practices with clear separation of concerns, reusable constructs, and environment-specific configuration.

## Architecture Layers

The infrastructure consists of these integrated components:

- **DNS & Edge**: Route53 for DNS, CloudFront for global content delivery
- **API Gateway**: REST API entry point with request/response transformation
- **Compute**: Lambda functions for serverless backend logic
- **Load Balancing**: Application Load Balancer for internal service routing (if needed)
- **Data**: RDS (PostgreSQL/MySQL) for persistent data storage
- **Security**: IAM roles, policies, security groups, and encryption
- **Observability**: CloudWatch logs, metrics, and alarms (integrated per stack)

## Project Structure

```
infrastructure/
├── stacks/
│   ├── __init__.py
│   ├── oidc_stack.py              # GitHub Actions OIDC authentication
│   ├── cdn_stack.py               # S3 website bucket + CloudFront distribution
│   ├── infrastructure_stack.py     # Core infrastructure (RDS, databases, etc.)
│   ├── vpc_stack.py               # Networking foundation (VPC, subnets, security groups)
│   ├── database_stack.py          # RDS, parameter store for credentials
│   ├── api_stack.py               # API Gateway, REST configuration
│   ├── lambda_stack.py            # Lambda functions and layers
│   ├── iam_stack.py               # Cross-stack IAM roles and policies
│   └── monitoring_stack.py         # CloudWatch alarms, dashboards
│
├── constructs/
│   ├── __init__.py
│   ├── lambda_construct.py         # Reusable Lambda function with env vars, VPC config
│   ├── rds_construct.py            # RDS instance with rotation, encryption, backups
│   ├── api_construct.py            # API Gateway with CORS, stages, request validation
│   ├── cdn_construct.py            # CloudFront distribution with origins and caching
│   └── security_construct.py       # Shared security patterns (IAM, encryption)
│
├── config.py                       # Environment configuration
├── lib/
│   ├── __init__.py
│   └── utils.py                    # Helper functions (ARN building, tag management, etc.)
│
├── main.py                         # CDK App entry point
├── pyproject.toml                  # Dependencies
└── cdk.json                        # CDK configuration (context values, outputs)
```

## Design Philosophy

### 1. Stack Organization
Each stack represents a logical domain with clear dependencies:
- **VPC Stack** (foundation) → **Database Stack** (needs VPC) → **Lambda Stack** (needs VPC, security groups)
- Cross-stack references use CDK `Fn.importValue()` or stack properties
- Stacks are instantiated once in `main.py` with explicit dependencies

### 2. Reusable Constructs
- **Constructs (L3)** encapsulate common patterns (Lambda + IAM + VPC setup)
- Accept configuration parameters for flexibility
- Output relevant references (ARNs, names, security groups) for cross-stack use
- No business logic—purely infrastructure patterns

### 3. Configuration Management
- **Single config file**: `config.py` for all demo settings
- Store secrets in AWS Secrets Manager (not config files)
- Lambda environment variables loaded from config at deploy time

### 4. IAM & Security
- Least-privilege principle: specific actions, specific resources
- Lambda execution roles created per function (or per service group)
- Database credentials stored in Secrets Manager with automatic rotation
- VPC security groups defined in `VPCStack`, referenced by other stacks
- All inter-service communication happens within VPC or through API Gateway

### 5. Lambda Deployment
- Lambda construct handles: code packaging, environment variables, VPC config, IAM role
- Layers for shared dependencies (avoid code duplication)
- API Gateway integrations defined in `APIStack` (not in Lambda construct)
- CloudWatch log groups created per function with retention policy

### 6. Data Layer
- RDS instance in private subnet (no public access)
- Multi-AZ for production
- Automated backups, encryption at rest
- Credentials managed by Secrets Manager with Lambda execution role access
- Connection pooling via RDS proxy (optional, recommended for high Lambda concurrency)

### 7. API Gateway
- Single REST API with configuration stage
- Request validation, CORS configuration
- Lambda integrations use proxy integration for full request control
- CloudWatch logs enabled for debugging

### 8. CDN & Global Distribution
- CloudFront distribution with API Gateway as origin
- Route53 alias records pointing to CloudFront
- SSL/TLS managed by ACM (auto-renewed)
- Static asset caching policies
- Origin request/response Lambda@Edge functions (if needed)

### 9. Monitoring & Observability
- CloudWatch log groups created with retention policies
- Custom metrics from Lambda (via CloudWatch SDK)
- Alarms for Lambda errors, throttling, duration
- Alarms for database CPU, connections, replication lag
- Dashboard consolidating key metrics

### 10. Environment Configuration
- Single environment configuration in `config.py`
- Secrets and sensitive values NEVER in code—loaded at runtime from AWS Secrets Manager

## Deployment Flow

1. **CDK Synth**: Generate CloudFormation templates from config
2. **CDK Deploy**: Deploy stacks in order (dependencies handled automatically)
3. **Outputs**: Stack outputs written to `cdk.json` for reference

## Key Files to Implement

- `main.py`: App instantiation and stack ordering
- `config.py`: Demo configuration and settings
- `stacks/*.py`: Domain-specific resource grouping
- `constructs/*.py`: Reusable component patterns
- `cdk.json`: CDK context and stack outputs

## Environment Variables & Secrets

- **Configuration**: Store in `config.py`
- **Secrets**: Store in AWS Secrets Manager, reference via IAM-enabled Lambda execution role
- **Lambda env vars**: Set via construct properties, pulled from config
- **Database credentials**: Managed by Secrets Manager

## OIDC Setup for GitHub Actions

The infrastructure includes an OIDC (OpenID Connect) stack that enables GitHub Actions to authenticate to AWS without storing static credentials.

### Components
- **OidcStack**: Creates an OIDC identity provider and IAM role for GitHub Actions
- **config.py**: Stores GitHub repository owner, name, and role configuration
- **`.github/workflows/infrastructure-deploy.yaml`**: Automated deployment workflow

### AWS Account Details
- **Account ID**: `233569452394`
- **GitHub Actions Role**: `arn:aws:iam::233569452394:role/brightthread-github-actions-role`
- **Region**: `us-west-2`

### GitHub Actions Workflow
The workflow (`.github/workflows/infrastructure-deploy.yaml`) automatically:
- Triggers on changes to the `infrastructure/` folder on the `main` branch
- Uses OIDC to assume the GitHub Actions role
- Runs `cdk synth` to validate infrastructure code
- Runs `cdk deploy --require-approval never` for automated deployment

### Setup Steps
1. Ensure `config.py` has correct GitHub repository details
2. Deploy the OIDC stack: `cdk deploy OidcStack`
3. The workflow file is already configured and will trigger on infrastructure changes
4. Push changes to `main` branch to trigger automatic deployment

## Website & CDN Stack

The CDN stack provides website hosting infrastructure:

### S3 Bucket
- **Name**: `brightthread-web-233569452394`
- **Purpose**: Static website hosting for single-page application
- **Features**:
  - Public read access via bucket policy
  - Auto-deletion of objects on stack destruction (for development)
  - Blocks to prevent accidental public access misconfiguration

### CloudFront Distribution
- **Origin**: S3 website bucket
- **Protocol**: HTTPS only (redirects HTTP to HTTPS)
- **Caching**: Optimized for SPA with long-lived asset cache
- **SPA Routing**: Custom error responses redirect 403/404 to `index.html` for client-side routing
- **Price Class**: PriceClass 100 (edge locations in US, Canada, Europe, Asia)

### SPA Configuration
- **Index Document**: `index.html`
- **Error Handling**: All 404/403 errors serve `index.html` to enable React Router / Vue Router / Angular routing
- **Cache TTL**: 5 minutes for error responses, optimized cache for assets

### Outputs
- `website-bucket-name`: S3 bucket name
- `website-distribution-domain`: CloudFront domain (e.g., `d123456.cloudfront.net`)
- `website-distribution-id`: For cache invalidation

## DNS & Route53 Configuration

The Route53Stack automatically creates a hosted zone and DNS records for your domain.

### What Gets Created
- **Route53 Hosted Zone** for `brightthread.design`
- **Apex record (`brightthread.design`)**: A alias record → CloudFront distribution (website)
- **API subdomain (`api.brightthread.design`)**: A alias record → API Gateway (backend API)

### Setup Steps

1. **Deploy infrastructure** (includes Route53Stack):
   ```bash
   cdk deploy --all
   ```

2. **Note the nameservers**:
   - After deployment, go to Route53 console
   - Find the hosted zone for `brightthread.design`
   - Copy the 4 nameservers

3. **Update domain registrar**:
   - Log in to your domain registrar (GoDaddy, Namecheap, etc.)
   - Update nameservers to point to the Route53 nameservers
   - DNS propagation typically takes 5-30 minutes

4. **Verify DNS**:
   ```bash
   nslookup brightthread.design
   nslookup api.brightthread.design
   ```

### Stack Outputs
- `HostedZoneId`: Route53 Hosted Zone ID
- `WebsiteUrl`: `https://brightthread.design`
- `ApiUrl`: `https://api.brightthread.design`

## Next Steps

1. **Deploy All Infrastructure**:
   ```bash
   cdk deploy --all
   ```
   - Creates S3 bucket and CloudFront distribution
   - Creates Route53 hosted zone and DNS records
   - Creates OIDC provider for GitHub Actions
   - Creates API Gateway infrastructure

2. **Configure Domain Registrar**:
   - Get nameservers from Route53 console
   - Update domain registrar to use Route53 nameservers
   - Wait for DNS propagation (5-30 minutes)

3. **Deploy Frontend**:
   - Push frontend code to `main` branch
   - GitHub Actions workflow automatically builds and deploys to S3
   - Accesses website at `https://brightthread.design`

4. **Backend Services**:
   - Implement VPC stack as foundation
   - Build reusable constructs for Lambda, RDS, API Gateway
   - Add stacks in dependency order: VPC → Database → API → Lambda
