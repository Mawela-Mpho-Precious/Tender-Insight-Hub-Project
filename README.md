# Tender Insight Hub

**Tender Insight Hub** is a cloud-native SaaS platform designed to assist South African SMEs in navigating public procurement opportunities. The platform simplifies tender documents, enables meaningful analysis, and helps SMEs assess their readiness to apply for tenders.

---

## 🚀 Features

### 1. Keyword Search, Filtering & Match Ranking
- Search tenders using free-text keywords (e.g., “road construction”, “security services”).
- Backend retrieves tenders from the [OCDS eTenders API](https://www.tenders.gov.za).
- Results are ranked based on relevance.
- Filter search results by:
  - Province  
  - Submission deadline  
  - Buyer (organ of state)  
  - Budget range  
- Filters are applied dynamically after initial search results.

### 2. Company Profile Management
- **Team Registration Requirement**: Every team must create a company profile upon registering.  
- **Profile Fields**:  
  - Industry sector  
  - Services provided  
  - Certifications (e.g., CIDB, BBBEE)  
  - Geographic coverage  
  - Years of experience  
  - Contact information  
- **Updateable Profiles**: Companies can update their profile at any time.  
- **Purpose**: Profiles are used to enhance tender **readiness scoring** and enable **advanced filtering** of tenders relevant to the company.

### 3. Team-Based SaaS Functionality
- Multiple user tiers with seat-based access.
- Collaborative tools for teams to analyze and share tender opportunities.

### 4. Data Management
- **SQL Database**: Stores structured data such as user accounts, teams, and tender metadata (MySQL).  
- **NoSQL Database**: Handles flexible or high-speed data like search indices, caching, or trending tenders (MongoDB).  

### 5. AI & Insights
- Simplifies complex tender documents for SMEs.
- Provides analytics to assess readiness for application.

---

## 🛠 Technology Stack
- **Backend:** FastAPI (Python)  
- **Databases:** SQL (PostgreSQL/MySQL), NoSQL (MongoDB/Redis)  
- **API Integration:** OCDS eTenders API  
- **Authentication & Authorization:** Team-based, tiered access  

---


