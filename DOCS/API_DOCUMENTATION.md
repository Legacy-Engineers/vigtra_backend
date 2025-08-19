# Vigtra Backend API Documentation

## Overview

The Vigtra Backend provides a comprehensive GraphQL API for managing health insurance operations. This documentation covers all available queries, mutations, and data structures.

## Table of Contents

- [Authentication](#authentication)
- [GraphQL Endpoint](#graphql-endpoint)
- [Schema Overview](#schema-overview)
- [Queries](#queries)
- [Mutations](#mutations)
- [Subscriptions](#subscriptions)
- [Data Types](#data-types)
- [Error Handling](#error-handling)
- [Examples](#examples)

## Authentication

The API supports multiple authentication methods:

### JWT Authentication
```http
Authorization: Bearer <jwt-token>
```

### Session Authentication
Standard Django session authentication for web clients.

### API Key Authentication
```http
X-API-Key: <api-key>
```

## GraphQL Endpoint

- **URL**: `/graphql/`
- **Methods**: `POST`
- **Content-Type**: `application/json`

### GraphiQL IDE
For development, access the interactive GraphiQL IDE at:
- **URL**: `/graphiql/`
- **Available in**: Development environment only

## Schema Overview

The GraphQL schema is organized around the following main entities:

- **User**: Authentication and user management
- **Insuree**: Individual beneficiaries
- **Family**: Family units and relationships
- **Policy**: Insurance policies and coverage
- **Claim**: Claims processing and management
- **Location**: Geographic locations and administrative divisions

## Queries

### User Queries

#### Get Current User
```graphql
query GetCurrentUser {
  currentUser {
    id
    username
    email
    firstName
    lastName
    isActive
    isStaff
    dateJoined
    lastLogin
  }
}
```

#### Get Users (Admin only)
```graphql
query GetUsers($first: Int, $after: String, $filters: UserFilterInput) {
  users(first: $first, after: $after, filters: $filters) {
    edges {
      node {
        id
        username
        email
        firstName
        lastName
        isActive
        dateJoined
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}
```

### Insuree Queries

#### Get Insurees
```graphql
query GetInsurees($first: Int, $after: String, $filters: InsureeFilterInput) {
  insurees(first: $first, after: $after, filters: $filters) {
    edges {
      node {
        id
        uuid
        chfId
        lastName
        otherNames
        gender {
          code
          gender
        }
        dateOfBirth
        maritalStatus
        phone
        email
        status
        createdAt
        updatedAt
        family {
          id
          address
        }
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}
```

#### Get Insuree by ID
```graphql
query GetInsuree($id: ID!) {
  insuree(id: $id) {
    id
    uuid
    chfId
    lastName
    otherNames
    gender {
      code
      gender
    }
    dateOfBirth
    maritalStatus
    phone
    email
    passport
    profession {
      code
      profession
    }
    education {
      code
      education
    }
    status
    family {
      id
      address
      members {
        id
        insuree {
          id
          lastName
          otherNames
        }
        isHead
        relationship {
          code
          relation
        }
      }
    }
    policies {
      id
      enrollDate
      startDate
      effectiveDate
      status
      value
    }
    createdAt
    updatedAt
  }
}
```

### Family Queries

#### Get Families
```graphql
query GetFamilies($first: Int, $after: String, $filters: FamilyFilterInput) {
  families(first: $first, after: $after, filters: $filters) {
    edges {
      node {
        id
        uuid
        address
        ethnicity
        confirmationNo
        confirmationType
        memberCount
        headOfFamily {
          id
          lastName
          otherNames
        }
        members {
          id
          insuree {
            id
            lastName
            otherNames
          }
          isHead
          relationship {
            code
            relation
          }
          membershipStartDate
        }
        createdAt
        updatedAt
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}
```

### Policy Queries

#### Get Policies
```graphql
query GetPolicies($first: Int, $after: String, $filters: PolicyFilterInput) {
  policies(first: $first, after: $after, filters: $filters) {
    edges {
      node {
        id
        uuid
        productCode
        enrollDate
        startDate
        effectiveDate
        expiryDate
        status
        value
        family {
          id
          address
          headOfFamily {
            lastName
            otherNames
          }
        }
        beneficiaries {
          id
          insuree {
            id
            lastName
            otherNames
          }
        }
        createdAt
        updatedAt
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}
```

### Claim Queries

#### Get Claims
```graphql
query GetClaims($first: Int, $after: String, $filters: ClaimFilterInput) {
  claims(first: $first, after: $after, filters: $filters) {
    edges {
      node {
        id
        uuid
        code
        claimDate
        visitDate
        insuree {
          id
          lastName
          otherNames
        }
        healthFacility {
          id
          name
          code
        }
        status
        claimed
        approved
        rejected
        valuated
        reimbursed
        createdAt
        updatedAt
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}
```

## Mutations

### User Mutations

#### Create User
```graphql
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    success
    message
    user {
      id
      username
      email
      firstName
      lastName
    }
    errors {
      field
      message
    }
  }
}
```

**Input Type:**
```graphql
input CreateUserInput {
  username: String!
  email: String!
  password: String!
  firstName: String
  lastName: String
  isStaff: Boolean
  isActive: Boolean
}
```

#### Update User
```graphql
mutation UpdateUser($input: UpdateUserInput!) {
  updateUser(input: $input) {
    success
    message
    user {
      id
      username
      email
      firstName
      lastName
    }
    errors {
      field
      message
    }
  }
}
```

#### Login User
```graphql
mutation LoginUser($input: LoginInput!) {
  loginUser(input: $input) {
    success
    message
    token
    refreshToken
    user {
      id
      username
      email
    }
    errors {
      field
      message
    }
  }
}
```

### Insuree Mutations

#### Create Insuree
```graphql
mutation CreateInsuree($input: CreateInsureeInput!) {
  createInsuree(input: $input) {
    success
    message
    insuree {
      id
      uuid
      chfId
      lastName
      otherNames
      dateOfBirth
      gender {
        code
        gender
      }
    }
    errors {
      field
      message
    }
  }
}
```

**Input Type:**
```graphql
input CreateInsureeInput {
  chfId: String
  lastName: String!
  otherNames: String!
  genderCode: String
  dateOfBirth: Date
  maritalStatus: String
  phone: String
  email: String
  passport: String
  professionCode: String
  educationCode: String
  familyId: ID
  isHead: Boolean
  relationshipCode: String
}
```

#### Update Insuree
```graphql
mutation UpdateInsuree($input: UpdateInsureeInput!) {
  updateInsuree(input: $input) {
    success
    message
    insuree {
      id
      uuid
      chfId
      lastName
      otherNames
    }
    errors {
      field
      message
    }
  }
}
```

#### Delete Insuree
```graphql
mutation DeleteInsuree($input: DeleteInsureeInput!) {
  deleteInsuree(input: $input) {
    success
    message
    errors {
      field
      message
    }
  }
}
```

### Family Mutations

#### Create Family
```graphql
mutation CreateFamily($input: CreateFamilyInput!) {
  createFamily(input: $input) {
    success
    message
    family {
      id
      uuid
      address
      ethnicity
    }
    errors {
      field
      message
    }
  }
}
```

#### Add Family Member
```graphql
mutation AddFamilyMember($input: AddFamilyMemberInput!) {
  addFamilyMember(input: $input) {
    success
    message
    membership {
      id
      insuree {
        id
        lastName
        otherNames
      }
      isHead
      relationship {
        code
        relation
      }
    }
    errors {
      field
      message
    }
  }
}
```

#### Transfer Family Member
```graphql
mutation TransferFamilyMember($input: TransferFamilyMemberInput!) {
  transferFamilyMember(input: $input) {
    success
    message
    membership {
      id
      family {
        id
        address
      }
    }
    errors {
      field
      message
    }
  }
}
```

### Policy Mutations

#### Create Policy
```graphql
mutation CreatePolicy($input: CreatePolicyInput!) {
  createPolicy(input: $input) {
    success
    message
    policy {
      id
      uuid
      productCode
      enrollDate
      startDate
      effectiveDate
    }
    errors {
      field
      message
    }
  }
}
```

#### Renew Policy
```graphql
mutation RenewPolicy($input: RenewPolicyInput!) {
  renewPolicy(input: $input) {
    success
    message
    policy {
      id
      effectiveDate
      expiryDate
      status
    }
    errors {
      field
      message
    }
  }
}
```

### Claim Mutations

#### Submit Claim
```graphql
mutation SubmitClaim($input: SubmitClaimInput!) {
  submitClaim(input: $input) {
    success
    message
    claim {
      id
      uuid
      code
      claimDate
      status
    }
    errors {
      field
      message
    }
  }
}
```

#### Process Claim
```graphql
mutation ProcessClaim($input: ProcessClaimInput!) {
  processClaim(input: $input) {
    success
    message
    claim {
      id
      status
      approved
      rejected
      valuated
    }
    errors {
      field
      message
    }
  }
}
```

## Subscriptions

### Real-time Updates

#### Claim Status Updates
```graphql
subscription ClaimStatusUpdates($claimId: ID!) {
  claimStatusUpdate(claimId: $claimId) {
    claim {
      id
      status
      approved
      rejected
    }
    timestamp
  }
}
```

#### Policy Updates
```graphql
subscription PolicyUpdates($policyId: ID!) {
  policyUpdate(policyId: $policyId) {
    policy {
      id
      status
      effectiveDate
      expiryDate
    }
    timestamp
  }
}
```

## Data Types

### Scalar Types

- `ID`: Unique identifier
- `String`: Text data
- `Int`: Integer numbers
- `Float`: Floating-point numbers
- `Boolean`: True/false values
- `Date`: Date in YYYY-MM-DD format
- `DateTime`: ISO 8601 datetime format
- `UUID`: UUID string format

### Enums

#### InsureeStatus
```graphql
enum InsureeStatus {
  ACTIVE
  INACTIVE
  DECEASED
  SUSPENDED
  PENDING
}
```

#### MaritalStatus
```graphql
enum MaritalStatus {
  SINGLE
  MARRIED
  DIVORCED
  WIDOWED
}
```

#### PolicyStatus
```graphql
enum PolicyStatus {
  ACTIVE
  INACTIVE
  SUSPENDED
  EXPIRED
}
```

#### ClaimStatus
```graphql
enum ClaimStatus {
  ENTERED
  CHECKED
  PROCESSED
  VALUATED
  REJECTED
}
```

### Filter Input Types

#### InsureeFilterInput
```graphql
input InsureeFilterInput {
  chfId: String
  lastName: String
  otherNames: String
  genderCode: String
  status: InsureeStatus
  dateOfBirthFrom: Date
  dateOfBirthTo: Date
  familyId: ID
  search: String
}
```

#### FamilyFilterInput
```graphql
input FamilyFilterInput {
  address: String
  ethnicity: String
  confirmationType: String
  headOfFamilyId: ID
  memberCount: Int
  search: String
}
```

## Error Handling

### Error Response Format

All mutations return a standardized error format:

```graphql
type MutationResponse {
  success: Boolean!
  message: String
  errors: [FieldError!]
}

type FieldError {
  field: String!
  message: String!
  code: String
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Input validation failed
- `NOT_FOUND`: Resource not found
- `PERMISSION_DENIED`: Insufficient permissions
- `DUPLICATE_ENTRY`: Unique constraint violation
- `INVALID_STATE`: Operation not allowed in current state

### GraphQL Errors

GraphQL errors are returned in the standard format:

```json
{
  "errors": [
    {
      "message": "Error description",
      "locations": [{"line": 2, "column": 3}],
      "path": ["field", "subfield"],
      "extensions": {
        "code": "ERROR_CODE",
        "exception": {
          "stacktrace": ["..."]
        }
      }
    }
  ]
}
```

## Examples

### Complete Insuree Creation Flow

```graphql
# 1. Create Family
mutation CreateFamily {
  createFamily(input: {
    address: "123 Main Street, City"
    ethnicity: "Local"
    confirmationType: "P"
  }) {
    success
    message
    family {
      id
      uuid
    }
    errors {
      field
      message
    }
  }
}

# 2. Create Head of Family
mutation CreateHeadOfFamily {
  createInsuree(input: {
    chfId: "12345678"
    lastName: "Doe"
    otherNames: "John"
    genderCode: "M"
    dateOfBirth: "1985-06-15"
    maritalStatus: "M"
    phone: "+1234567890"
    email: "john.doe@email.com"
    familyId: "family-uuid-from-step-1"
    isHead: true
  }) {
    success
    message
    insuree {
      id
      uuid
      chfId
    }
    errors {
      field
      message
    }
  }
}

# 3. Add Spouse
mutation AddSpouse {
  createInsuree(input: {
    chfId: "12345679"
    lastName: "Doe"
    otherNames: "Jane"
    genderCode: "F"
    dateOfBirth: "1987-03-22"
    maritalStatus: "M"
    phone: "+1234567891"
    email: "jane.doe@email.com"
    familyId: "family-uuid-from-step-1"
    isHead: false
    relationshipCode: "SP"
  }) {
    success
    message
    insuree {
      id
      uuid
      chfId
    }
    errors {
      field
      message
    }
  }
}
```

### Query Family with All Members

```graphql
query GetFamilyDetails($familyId: ID!) {
  family(id: $familyId) {
    id
    uuid
    address
    ethnicity
    memberCount
    headOfFamily {
      id
      chfId
      lastName
      otherNames
      dateOfBirth
      gender {
        code
        gender
      }
    }
    members {
      id
      insuree {
        id
        chfId
        lastName
        otherNames
        dateOfBirth
        gender {
          code
          gender
        }
        phone
        email
      }
      isHead
      relationship {
        code
        relation
      }
      membershipStartDate
      status
    }
    policies {
      id
      productCode
      status
      effectiveDate
      expiryDate
      value
    }
  }
}
```

### Search Insurees with Pagination

```graphql
query SearchInsurees($search: String!, $first: Int!, $after: String) {
  insurees(
    first: $first
    after: $after
    filters: { search: $search }
  ) {
    edges {
      node {
        id
        chfId
        lastName
        otherNames
        dateOfBirth
        family {
          id
          address
        }
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}
```

### Variables:
```json
{
  "search": "John",
  "first": 10,
  "after": null
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Authenticated users**: 1000 requests per hour
- **Anonymous users**: 100 requests per hour
- **Admin users**: 5000 requests per hour

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets

## Versioning

The API uses schema evolution rather than versioning. Breaking changes are avoided through:

- Adding new fields instead of modifying existing ones
- Deprecating fields before removal
- Providing migration paths for deprecated features

Deprecated fields are marked in the schema and documentation.

## Support

For API support and questions:
- Documentation: This document
- GraphiQL IDE: `/graphiql/` (development only)
- Schema introspection: Available through GraphQL
- Issue tracking: [Project repository issues]