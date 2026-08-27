---
name: core-salesforce
description: >
  Frontiers Media SA Salesforce CRM skill. Use when the user needs to query, explore, analyze,
  or report on Salesforce data — including articles, journals, research topics, contacts,
  accounts, opportunities, campaigns, cases, leads, invoices, editorial board members, AIRA
  indicators, discount codes, board invitations, campaign members, workflow delays, call logs,
  or any other Salesforce object at frontiers.my.salesforce.com.
  This skill covers the Salesforce REST API, SOQL query patterns, object schemas, picklist
  values, record types, and domain knowledge about how Frontiers uses its CRM.
---

# Frontiers Salesforce

## When to Use What

| Need | Use |
|------|-----|
| **Analytics / reporting** (aggregations, trends, dashboards) | **BigQuery mirror** at `ocean-breeze-tier-2.salesforce` — faster, no API limits, supports JOINs and GROUP BY |
| **Live data** (create/update records, real-time lookup) | **Salesforce REST API** (SOQL) — see Connection section below |
| **Bulk data exports** | **BigQuery mirror** — full tables already materialized |

**For most analytical questions, use BigQuery.** The Salesforce REST API is rate-limited, can't do
complex JOINs, and times out on large result sets. The BigQuery mirror at `ocean-breeze-tier-2.salesforce`
has all 51 core objects pre-loaded and is refreshed regularly.

```python
# BigQuery path (preferred for analytics)
from google.cloud import bigquery
client = bigquery.Client(project="gcp-innovation-hub")

rows = list(client.query("""
    SELECT Name, Status__c, ISSN__c
    FROM `ocean-breeze-tier-2.salesforce.Journal__c`
    WHERE Status__c = 'Active'
    ORDER BY Name
""").result())
```

### BigQuery Mirror Tables

The full Salesforce mirror lives at `ocean-breeze-tier-2.salesforce` (51 tables):

| Table | Salesforce Object |
|-------|------------------|
| `Article__c` | Articles |
| `ArticleAuthor__c` | Article-Author junction |
| `ArticleEditor__c` | Article-Editor junction |
| `ArticleReviewer__c` | Article-Reviewer junction |
| `Contact` | People/researchers |
| `Account` | Institutions |
| `Journal__c` | Journals |
| `JournalSection__c` | Journal sections |
| `EditorialBoardMember__c` | Board membership |
| `ResearchTopic__c` | Research Topics |
| `ResearchTopicContributor__c` | RT contributors |
| `ResearchTopicEditor__c` | RT editors |
| `Opportunity` | Sales pipeline / APCs |
| `Campaign` | Marketing campaigns |
| `CampaignMember` | Campaign membership |
| `Case` | Support cases |
| `Lead` | Prospective contacts |
| `Discount_Code__c` | Discount codes |
| `EmailMessage` | Email messages |
| `Domain` | Email domains |
| `Taxonomy__c` | Journal taxonomy |
| `Field__c` / `Specialty__c` / `Space__c` | Taxonomy hierarchy |
| `User` / `UserRole` | Salesforce users |

For full column schemas, see `core-analytics/references/bigquery-schemas.json`.



## Connection

The Salesforce instance is **frontiers.my.salesforce.com**, accessible via REST API using pre-configured environment variables.

```python
import os, requests

headers = {
    "Authorization": f'Bearer {os.environ["SALESFORCE_ACCESS_TOKEN"]}',
}
base = os.environ["SALESFORCE_INSTANCE_URL"]  # https://frontiers.my.salesforce.com

# SOQL query
resp = requests.get(
    f"{base}/services/data/v59.0/query",
    params={"q": "SELECT Id, Name FROM Account LIMIT 5"},
    headers=headers,
)
data = resp.json()
```

### Useful API endpoints

| Endpoint | Purpose |
|----------|---------|
| `/services/data/v59.0/query?q=SOQL` | Run SOQL queries |
| `/services/data/v59.0/sobjects` | List all objects |
| `/services/data/v59.0/sobjects/{Object}/describe` | Get object metadata (fields, picklists, record types) |
| `/services/data/v59.0/sobjects/{Object}/{Id}` | Get/update a specific record |
| `/services/data/v59.0/queryAll?q=SOQL` | Query including deleted/archived records |

### Pagination

SOQL queries return a maximum of 2,000 records per response. For larger result sets, use the `nextRecordsUrl` field to fetch subsequent batches:

```python
all_records = []
resp = requests.get(f"{base}/services/data/v59.0/query", params={"q": soql}, headers=headers)
data = resp.json()
all_records.extend(data["records"])

while not data["done"]:
    resp = requests.get(f"{base}{data['nextRecordsUrl']}", headers=headers)
    data = resp.json()
    all_records.extend(data["records"])
```

## Instance Overview

| Object | Approx Records | Description |
|--------|---------------|-------------|
| `ResearchTopicContributor__c` | ~15M | RT contributor invitations and confirmations |
| `Case` | ~13.3M | Support cases across editorial, accounting, CRM |
| `AIRAIndicator__c` | ~8.9M | AI Review Assistant quality indicators |
| `ArticleAuthor__c` | ~8.3M | Article-author relationships |
| `Lead` | ~7.0M | Prospective researchers and partners |
| `Contact` | ~5.6M | Researchers, authors, editors, reviewers |
| `ArticleReviewer__c` | ~2.4M | Article-reviewer assignments |
| `Article__c` | ~1.4M | Research articles through lifecycle |
| `Invoice__c` | ~1.3M | Article processing charge invoices |
| `ArticleEditor__c` | ~1.1M | Article-editor assignments |
| `BoardInvitation__c` | ~943K | Editorial board invitations |
| `EditorialBoardMember__c` | ~647K | Editorial board memberships |
| `Opportunity` | ~567K | RT proposals, editor recruitment, partnerships |
| `Discount_Code__c` | ~432K | Fee waivers and discount codes |
| `ResearchTopicEditor__c` | ~258K | RT editor assignments |
| `Campaign` | ~163K | Outreach campaigns (RT, EBG, events) |
| `ResearchTopic__c` | ~80K | Research topics |
| `Journal__c` | ~345 | Frontiers journals |
| `Space__c` | 6 | Frontiers publishing spaces |

## Taxonomy & Hierarchy

Frontiers organizes knowledge into a hierarchical taxonomy:

```
Space__c (6 spaces)
  └── Domain__c
       └── Field__c
            └── Specialty__c
                 └── Journal__c
                      └── JournalSection__c
```

`Taxonomy__c` is a reference table that unifies references across the hierarchy.

### Space__c (6 records)

| Name | SpaceID | Long Name | URL |
|------|---------|-----------|-----|
| Frontiers | 1 | Frontiers | frontiersin.org |
| GSL | 2 | The Geological Society of London | escubed.org |
| FSHIP | 3 | Frontiers Publishing Partnerships | frontierspartnerships.org |
| ALF | 4 | Arányi Lajos Foundation | por-journal.com |
| SSPH | 5 | Swiss School of Public Health | ssph-journal.org |
| SEBM | 7 | Society for Experimental Biology and Medicine | ebm-journal.org |

## Core Objects

### Article__c — Research Articles (~1.4M)

The central object tracking manuscripts from submission through publication. 153 fields.

**Key fields:**

| Field | Type | Description |
|-------|------|-------------|
| `ArticleId__c` | string | External article ID |
| `Title__c` | textarea | Article title |
| `DOI__c` | string | Digital Object Identifier |
| `Stage__c` | picklist | Current review stage |
| `ArticleStatus__c` | picklist | On Time / Delayed |
| `Type__c` | picklist | Article type (Original Research, Review, etc.) |
| `Source__c` | picklist | Submission source: RT-CC, RT-IC, RT-SP, Other |
| `Journal__c` | reference → Journal__c | Parent journal |
| `ResearchTopic__c` | reference → ResearchTopic__c | Associated research topic |
| `Section__c` | reference → JournalSection__c | Journal section |
| `Field__c` | reference → Field__c | Academic field |
| `Specialty__c` | reference → Specialty__c | Academic specialty |
| `Creator__c` | reference → Contact | Submitting author |
| `CreateDate__c` | datetime | Submission date |
| `Submitted_on__c` | date | Formal submission date |
| `AcceptedOn__c` | date | Acceptance date |
| `Published_on__c` | date | Publication date |
| `Rejected_on__c` | date | Rejection date |
| `DecisionDate__c` | date | Decision date |
| `ReceivedOn__c` | date | Received date |
| `DaysInReview__c` | double | Days spent in review |
| `ReviewStageDuration__c` | double | Duration in current stage |
| `ServiceLevel__c` | picklist | Service level: 0–5 |
| `ServiceLevelScore__c` | double | Numeric service level score |
| `ServiceLevelScoreAIRA__c` | double | Service level score (SF calculated) |
| `NoOfReviewers__c` | double | Number of assigned reviewers |
| `NoOfCases__c` | double | Related support cases |
| `NoOfOpenCases__c` | double | Open support cases |
| `WordCount__c` | double | Manuscript word count |
| `Views__c` | double | Total article views |
| `Downloads__c` | double | Total downloads |
| `ArticleCitations__c` | double | Citation count |
| `ReviewType__c` | picklist | Short Review / Full Review |
| `FastTrack__c` | boolean | Fast-tracked article |
| `InvoicePaid__c` | boolean | All invoices paid |
| `NoOfInvoices__c` | double | Total invoice count |
| `NoOfOpenInvoice__c` | double | Open invoice count |
| `LanguageQualityIndicator__c` | picklist | Blocked / Checked / Warning |
| `TextOverlapIndicator__c` | picklist | Blocked / Checked / Warning |
| `QualityAuditOutcome__c` | picklist | Quality audit result |
| `QualityAuditStatus__c` | picklist | Quality audit status |
| `ScopeOutcome__c` | picklist | Scope audit result |
| `QualityFunnelStatus__c` | picklist | Initial author checks: Passed / Blocked / Warning / Skipped |
| `CurrentQualityFunnelStatus__c` | picklist | RI author checks status |
| `RIProcessingStatus__c` | picklist | checkedByRI / pendingByRI / Unchecked |
| `InvestigationStatus__c` | picklist | Ongoing / Completed / Flagged |
| `ArticleUnderInvestigation__c` | boolean | Under RI investigation |
| `LatestAssignedEditor__c` | reference → Contact | Current handling editor |
| `PrimaryArticleAuthor__c` | reference → ArticleAuthor__c | Primary author record |
| `HighestInfluencerAuthor__c` | reference → Contact | Highest-influence author |
| `AIRASLHighestHIndex__c` | double | Highest author h-index |
| `RIOwner__c` | reference → User | Research Integrity owner |
| `RIAuditorOwner__c` | reference → User | RI Auditor owner |
| `ArticleOpportunityOwner__c` | reference → User | Opportunity owner |
| `Program__c` | string | Journal program |
| `Market__c` | string | Market |
| `PriorityRegion__c` | string | Priority region |
| `IsFromACP__c` | boolean | Part of an Article Collection Package |
| `DirectCommission__c` | boolean | Direct commission |
| `InReview__c` | boolean | Currently in review |
| `NoOfEndorsements__c` | double | Number of endorsements |

**Stage__c picklist values (article lifecycle):**

```
Initial Validation → Editorial Assignment → In Independent Review →
In Interactive Review → Review Finalized → Final Validation →
Accepted → In Copy-Editing → Copy-Edited → Copy Approved →
In Production → Author's Proof → Authors' Proof Approved →
Publishers' Proof → Publishers' Proof Approved → Published → Deposited
```

Also: `Rejected`, `Rejection Recommended`, `Recommendation for Rejection Revoked`, `Reviewed`, `Deleted`, `Paper Pending Published`

**Type__c picklist values (60 values, most common):**

`Original Research`, `Review`, `Mini Review`, `Systematic Review`, `Hypothesis & Theory`, `Methods`, `Perspective`, `Opinion`, `Editorial`, `Case Report`, `Data Report`, `General Commentary`, `Correction`, `Corrigendum`, `Erratum`, `Retraction`, `Brief Research Report`, `Technology Report`, `Policy Brief`, `Clinical Trial`, `Protocols`, `Code`, `Conceptual Analysis`, `FAIR² Data Article`, `Field Grand Challenge`, `Specialty Grand Challenge`, `Core Concept`, `Focused Review`, `Clinical Case Study`, `Community Case Study`

### Journal__c — Journals (~345)

Frontiers journals with editorial, financial, and operational data. 99 fields.

**Record types:** `Frontiers Account`, `Society Account` (on related Account)

**Key fields:**

| Field | Type | Description |
|-------|------|-------------|
| `JournalId__c` | string | External taxonomy ID |
| `Name__c` | textarea | Full journal name |
| `Abbreviation__c` | string | Short name |
| `ISSNElectronic__c` | string | Electronic ISSN |
| `IsOnline__c` | boolean | Currently live |
| `IsOpenForSubmission__c` | boolean | Accepting submissions |
| `ImpactFactor__c` | double | Journal Impact Factor |
| `FiveYearImpactFactor__c` | double | 5-year IF |
| `ImpactFactorWOSelfCits__c` | double | IF without self-citations |
| `PreviousJournalImpactFactor__c` | double | Previous year IF |
| `ChangeInJournalImpactFactor__c` | percent | % change in IF |
| `CiteScore__c` | double | CiteScore |
| `ArticleProcessingCharge__c` | currency | APC amount |
| `Program__c` | picklist | Journal program |
| `Indexing__c` | picklist | Indexing status |
| `PublishingModel__c` | picklist | Publishing model |
| `Type__c` | picklist | Journal type |
| `Field__c` | reference → Field__c | Academic field |
| `Specialty__c` | reference → Specialty__c | Specialty |
| `Domain__c` | reference → Domain__c | Domain |
| `EditorInChief__c` | reference → Contact | Editor-in-Chief |
| `Manager__c` | reference → User | Journal Manager |
| `SocietyAccount__c` | reference → Account | Society partner |
| `SocietyPartnershipManager__c` | reference → User | Society partnership manager |
| `SpaceId__c` | reference → Space__c | Publishing space |
| `LaunchDate__c` | datetime | Journal launch date |
| `MinimumHIndex__c` | double | Min h-index for board eligibility |
| `MiniumAEHIndex__c` | double | Min h-index for AE |
| `ContractRenewalDate__c` | date | Contract renewal date |
| `Description__c` | textarea | Journal description |
| `Languages__c` | multipicklist | Supported languages |

**Program__c values:** `FaaS`, `BioSci`, `Brain`, `Data`, `HealthandBiomed`, `HSS`, `Life`, `PSE`, `Sustainability`, `Launch`, `Hidden`

**Indexing__c values:** `SCIE`, `SSCI`, `AHCI`, `ESCI`

**PublishingModel__c values:** `Open Access`, `Hybrid`, `Subscription`, `Diamond Open Access`

**Type__c values:** `Specialty Journal`, `Field Journal`, `Specialty Section`, `Field Section`, `Society Journal`

**Budget fields** (by year — current, previous, two years previous):
- `CurrentYearlyWaiverBudget__c`, `CurrentYearPubDevBudget__c`, `CurrentYearChinaBudget__c`, `CurrentYearUSABudget__c`, `CurrentYearOKRBudget__c`, `CurrentYearSubmissionsBudget__c`, `CurrentYearSocietyContractsBudget__c`, `CurrentYearLaunchBudget__c`
- Corresponding `PreviousYear*` and `TwoYearsPrevious*` fields

**RT target fields:** `CurrentYearRTPostedTarget__c`, `CurrentYearRTMSSubmissionsTarget__c`

### ResearchTopic__c — Research Topics (~80K)

Collaborative article collections curated by topic editors. 165 fields.

**Key fields:**

| Field | Type | Description |
|-------|------|-------------|
| `ResearchTopicId__c` | string | External RT ID |
| `Title__c` | textarea | Topic title |
| `Journal__c` | reference → Journal__c | Host journal |
| `Section__c` | reference → Section__c | Host section |
| `Field__c` | reference → Field__c | Academic field |
| `Specialty__c` | reference → Specialty__c | Specialty |
| `Region__c` | reference → Region__c | Region |
| `Stage__c` | picklist | RT lifecycle stage |
| `Step__c` | picklist | Operational step within lifecycle |
| `OnlineDate__c` | date | When it went live |
| `SubmissionDeadline__c` | datetime | MS submission deadline |
| `ExtendedSubmissionDeadline__c` | datetime | Extended close date |
| `IsClosed__c` | boolean | Closed for submissions |
| `IsPublished__c` | boolean | Published/completed |
| `IsRejected__c` | boolean | Rejected |
| `IsSuggested__c` | boolean | Suggested (not yet accepted) |
| `NoOfPCs__c` | double | All contributors |
| `Invited_Contributors__c` | double | Invited Contributors (RT-IC) |
| `NoContributorsConfirmed__c` | double | Confirmed contributors (IC-CCs) |
| `allConfirmedContributors__c` | double | All confirmed contributors |
| `Submitted_Manuscripts__c` | double | Total submissions (all sources) |
| `RTtoICSubmissionsNew__c` | double | RT-IC Submissions |
| `RTtoCCSubmissions__c` | double | RT-CC Submissions |
| `NoPublishedArticles__c` | double | Published articles (all sources) |
| `NoOfAcceptances__c` | double | Total acceptances |
| `AcceptedArticles__c` | double | Accepted articles |
| `NoOfRejections__c` | double | Rejections (all sources) |
| `AcceptanceRate__c` | percent | Acceptance rate |
| `RejectionRate__c` | percent | Rejection rate |
| `RTHealthStatus__c` | picklist | Red / Amber / Green |
| `RTHealthStatusIndicator__c` | string | Health status indicator text |
| `RTSL_Score__c` | double | RT service level score |
| `TETeamEngagement__c` | picklist | TE Team Engaged / Disengaged |
| `Connectivity__c` | double | Connectivity metric |
| `ArticlesViews__c` | double | Article views |
| `ArticlesDownloads__c` | double | Downloads |
| `ArticleCitations__c` | double | Citations |
| `TopicEditors__c` | double | Number of Topic Editors |
| `AllRTEditorsNames__c` | textarea | All editor names |
| `HighPriority__c` | boolean | High priority flag |
| `SignatureType__c` | picklist | Global / China |
| `RTUnderInvestigation__c` | boolean | Under investigation |
| `InvestigationStatus__c` | picklist | Ongoing / Completed / Flagged |
| `NoSubmittedSummaries__c` | double | Submitted MS summaries |
| `Days_Since_Launch__c` | double | Days since launch |
| `Days_Since_Deadline__c` | double | Days since deadline |
| `Opportunity_Turn_Around__c` | double | Opportunity turnaround |
| `Window__c` | double | Window period |
| `Market__c` | string | Market |
| `PriorityRegion__c` | string | Priority region |
| `IsFromACP__c` | boolean | Part of an ACP |
| `ArticlesWithTEAsAuthor__c` | double | Articles with TE as author |
| `ArticlesWithTEAsEditor__c` | double | Articles with TE as editor |
| `AcceptanceToTERatio__c` | double | Acceptance-to-TE ratio |
| `RTQualityFlag__c` | double | TE quality flags count |

**Stage__c values:** `In Preparation`, `Suggested`, `Online`, `Closed`, `Completed`, `Rejected`, `Deleted`, `Lost`, `In-discussion`

**Step__c values (operational progression):** `RT Kickoff` → `Contributor Confirmation` → `Summary Submission` → `Manuscript Submission` → `Late Submissions` → `Closed For Submissions` → `Final Validation` → `Completed`

**RTHealthStatus__c values:** `Red`, `Amber`, `Green`

**RTSL_Score__c** is a composite metric combining multiple sub-scores:
- `RTSL_Days_since_Deadline_response__c`, `RTSL_Days_since_Launch_Response__c`, `RTSL_MS_vs_CC_response__c`, `RTSL_number_of_PCs_Response__c`, `RTSL_Opp_Turnaround_Time_Response__c`, `RTSL_Strategic_Discounts_Response__c`, `RTSL_TE_Connectivity_Response__c`, `RTSL_CC_to_PC_Response__c`, `RTSL_Total_CCs_Response__c`
- Window priorities: `RTSL_Window_1_Priority__c`, `RTSL_Window_2_Priority__c`, `RTSL_Window_3_Priority__c`

### Contact — Researchers (~5.6M)

People in the Frontiers ecosystem: authors, editors, reviewers, board members. 275 fields.

**Record types:** `Registered User`, `SPP Contact`

**Key fields:**

| Field | Type | Description |
|-------|------|-------------|
| `ContactId__c` | string | Loop ID |
| `FirstName` / `LastName` | string | Name |
| `Email` | email | Primary email |
| `Affiliation__c` | string | Institution |
| `BillingCountry__c` | picklist | Country |
| `Country__c` | string | Country (text) |
| `HIndex__c` | double | h-index |
| `No_of_Citations__c` | double | Citation count |
| `NumberOfPublications__c` | double | Publication count |
| `Coauthorships__c` | double | Co-author count |
| `Seniority__c` | picklist | Junior / Early Career / Senior |
| `IsActivated__c` | boolean | Activated account |
| `Status__c` | picklist | Contact status |
| `EditorialBoardMemberRoles__c` | multipicklist | EB roles held |
| `HighestEBR_Text__c` | string | Highest EB role text |
| `HighestEBRRoleNumber__c` | double | Highest EB role number |
| `ActiveEBMRoles__c` | double | Active board roles |
| `VIP__c` | boolean | VIP flag |
| `Blacklisted__c` | boolean | Temporarily suppressed |
| `BlacklistReason__c` | picklist | Suppression reason |
| `Watchlisted__c` | boolean | Watchlisted |
| `GloballyUnsubscribed__c` | boolean | Email unsubscribed |
| `ContributorsOptOut__c` | boolean | Contributors opt-out |
| `Field__c` | picklist | Research field |
| `PhD__c` | picklist | Yes / No |
| `YearPhDObtained__c` | string | PhD year |
| `YearsSincePhD__c` | double | Years since PhD |
| `NoArticlesAuthored__c` | double | Articles authored |
| `NoArticlesEdited__c` | double | Articles edited |
| `NoArticlesReviewed__c` | double | Articles reviewed |
| `NoRTsEdited__c` | double | RTs edited |
| `TotalWonOpportunities__c` | double | Won opportunities total |
| `TotalRTWonOpportunities__c` | double | Won RT opportunities |
| `TotalRTOpenOpportunities__c` | double | Open RT opportunities |
| `TotalEBWonOpportunities__c` | double | Won EB opportunities |
| `LatestArticle__c` | reference → Article__c | Latest article authored |
| `LatestArticleSubmitted_F__c` | date | Latest article submission date |
| `LatestPublishedArticleDate__c` | date | Latest published article date |
| `LatestReviewReportDate__c` | date | Latest review report date |
| `LatestEditorAssignedDate__c` | date | Latest editor assignment |
| `EBAppointmentDate__c` | date | Latest EB appointment |
| `HighestEBRoleAppointmentDate__c` | date | Highest EB role appointment |
| `SFClosestFrontiersJournal__c` | reference → Journal__c | Best-matching journal |
| `Segment__c` | picklist | Global / USA / China |
| `Market__c` | string | Market |
| `PriorityRegion__c` | string | Priority region |
| `LoopProfile__c` | string | Loop profile URL |
| `ApprovalStatus__c` | picklist | Not Started / In Progress |
| `Influence_Percentile__c` | double | Influence percentile |
| `Connectivity_Percentile__c` | double | Connectivity percentile |
| `Productivity_Percentile__c` | double | Productivity percentile |
| `Trendiness_Percentile__c` | double | Trendiness percentile |
| `Activity_Percentile__c` | double | Activity percentile |
| `SR_Score__c` | double | SR score |
| `EmailIsSafeToSend__c` | boolean | Email validated for sending |
| `EmailValidationStatus__c` | picklist | Email validation status |
| `CoTEEligible__c` | boolean | Co-TE eligible |
| `LastEngagementActivity__c` | picklist | Last engagement type |
| `LastEngagementDate__c` | date | Last engagement date |

**Status__c values:** `Prospect`, `Registered Account`, `Lead Account`, `Blacklist`, `Flagged`, `Deactivated`

**BlacklistReason__c values:** `CO-TE pending`, `CO-TE invited Busy`, `Health Issues`, `Junior`, `On Leave`, `Other Contact Request > 6 months`, `Technical Issue`, `Application Support - Incorrect AIRA Data`

**EditorialBoardMemberRoles__c values:** `Review Editor`, `Associate Editor`, `Specialty Chief Editor`, `Field Chief Editor`, `Assistant Field Chief Editor`, `Assistant Specialty Chief Editor`, `Guest Associate Editor`, `Managing Editor`, `Editor-in-Chief`, `Reviewer`, `Assistant Chief Editor`

### Opportunity — Sales Pipeline (~567K)

Tracks research topic proposals, editor recruitment, journal partnerships, and more. 172 fields.

**Record types (active):**

`Research Topic`, `Editor Recruitment`, `Article`, `Journal Launch`, `Section Launch Pre-IF`, `Section Launch Post-IF`, `Section Pre-Launch`, `Community Partnership`, `Institutional and Consortia Partnership`, `Partnership`, `FYM Collections`, `FYM Commissioned Articles`, `FYM Partnerships`, `Frontiers in Science Lead Article`, `Policy Labs`, `Strategic Projects`

**Key fields:**

| Field | Type | Description |
|-------|------|-------------|
| `Name` | string | Opportunity name |
| `StageName` | picklist | Current stage |
| `Amount` | currency | Revenue amount |
| `CloseDate` | date | Expected close date |
| `Probability` | percent | Win probability |
| `Type` | picklist | Opportunity type |
| `IsClosed` / `IsWon` | boolean | Outcome flags |
| `AccountId` | reference → Account | Related account |
| `Contact__c` | reference → Contact | Primary contact |
| `ResearchTopic__c` | reference → ResearchTopic__c | Related RT |
| `Journal__c` | reference → Journal__c | Related journal |
| `Journal_Section__c` | reference → JournalSection__c | Related section |
| `Loss_Reason__c` | picklist | Why lost |
| `BlockedReason__c` | picklist | Why blocked |
| `Priority_Score__c` | double | Priority score |
| `Priority_Level__c` | double | Priority level |
| `Conversion_Likelihood__c` | double | Conversion likelihood |
| `Opportunity_Turn_Around__c` | double | Turnaround time |
| `NoOfTEs__c` | double | Number of topic editors |
| `LeadTeHIndex__c` | double | Lead TE h-index |
| `NoOfPcs__c` | double | Number of PCs |
| `VettingStatus__c` | picklist | Vetting status |
| `SignatureType__c` | picklist | Global / China |
| `PaymentTerm__c` | picklist | Payment model |
| `AgreementType__c` | picklist | Agreement type |
| `BoardInvitation__c` | reference → BoardInvitation__c | Related board invitation |
| `RecruitmentInvitationRole__c` | picklist | Recruitment role |
| `RecruitmentType__c` | picklist | Recruitment type |
| `ParentOpportunity__c` | reference → Opportunity | Parent opportunity |
| `StageDuration__c` | double | Time in current stage |
| `Article__c` | reference → Article__c | Related article |
| `Discount_Code__c` | reference → Discount_Code__c | Related discount code |
| `Region__c` | reference → Region__c | Region |

**StageName values (vary by record type — common for RT):**

`Qualification → First Contact → First Reply → SQL → Discussion → Scoping → Commitment → Final Stage → In DEO → Closed Won / Closed - Cancelled`

Also: `Postponed`, `Replied`, `Interested`, `Proposal Presented`, `Meeting`, `Proposal`, `Contract`

**Type values:** `New Business`, `Existing Business`, `FaaS Journal Launch`, `FaaS Journal Transfer`, `Frontiers Journal Partnership`, `Frontiers Section Partnership`

**VettingStatus__c values:** `No Ongoing Vetting`, `Ongoing Vetting`, `Approved by SCE`, `Rejected by SCE Scope`, `Rejected by SCE Other`, `Automatically sent`

**AgreementType__c values:** `Institutional Partnership`, `Consortia Partnership`, `National Consortia Partnership`, `Funder Partnership`, `Other`

**PaymentTerm__c values:** `CI: Annual Prepayment`, `Central Invoicing: Direct`, `Central Invoicing: Monthly`, `Central Invoicing: Prepayment`, `CI-MP Pilot: *`, `Fixed Fee Pilot`, `Flat-Fee *`, `Other Pilot`, `Supporter`

### Campaign — Outreach Campaigns (~163K)

Marketing and editorial outreach. 312 fields.

**Record types (active):**

`RT Outreach`, `RT Recruitment`, `RT Proposal`, `RT Automation`, `EBG Outreach`, `EBG Automation`, `Editor Onboarding`, `MS Submissions`, `Event/Sponsorship`, `Event/Sponsorship Parent`, `ACP Campaign`, `Customer Research`, `FPP - Invitation`, `FPP - Registered Follow-up`, `FaaS`, `Relationship Building`, `SPP Outreach`, `SPP Partnership`, `Section Tracking RT Proposal`, `Standard`, `Task Nudging`

**Key fields:**

| Field | Type | Description |
|-------|------|-------------|
| `Name` | string | Campaign name |
| `Type` | picklist | Campaign type |
| `Status` | picklist | Current status |
| `StartDate` / `EndDate` | date | Campaign period |
| `IsActive` | boolean | Active flag |
| `NumberOfContacts` | int | Related contacts |
| `NumberOfLeads` | int | Related leads |
| `RTOpportunity__c` | reference → Opportunity | RT opportunity link |
| `Journal__c` | reference → Journal__c | Related journal |
| `ArticleHub__c` | reference → ArticleHub__c | Related article hub |
| `Exclusive__c` | boolean | Exclusive campaign |
| `NoOfCampaignMembers__c` | double | Campaign members |
| `NoOfInvitedCampaignMembers__c` | double | Invited campaign members |
| `FirstInvitationDate__c` | date | First invite sent |
| `LastInvitationDate__c` | date | Last invite sent |
| `Program__c` | picklist | Journal program |
| `SendCMsToJourney__c` | boolean | Send CMs to journey |
| `PerfectEmailEnabled__c` | boolean | Perfect email enabled |

**Type values:** `Research Topics`, `RT Recruitment`, `Email`, `Conference / Event`, `Survey`, `Webinar`, `Ad-Hoc`, `ACP Campaign`, `Customer Research`, `Other`

**Status values:** `Planned`, `In Progress`, `Complete`, `Aborted`, `Cancelled`, `Sent`, `Pending`

### Case — Support Cases (~13.3M)

Customer and internal support tickets. 192 fields.

**Record types (active):** `Service Case`, `Application Support`, `CRM Support`, `Accounting Support`, `Research Topic`, `Ebooks Production`, `Institutional Partnerships`, `Publishing Partnerships`, `Frontiers in Science`, `Social Media`

**Key fields:**

| Field | Type | Description |
|-------|------|-------------|
| `CaseNumber` | string | Case number |
| `Subject` | string | Case subject |
| `Status` | picklist | Case status |
| `Type` | picklist | Case type (123 values) |
| `SubType__c` | picklist | Case sub-type (579 values) |
| `Priority` | picklist | Priority level |
| `Origin` | picklist | Case origin |
| `ContactId` | reference → Contact | Related contact |
| `AccountId` | reference → Account | Related account |
| `Article__c` | reference → Article__c | Related article |
| `ResearchTopic__c` | reference → ResearchTopic__c | Related RT |
| `RT_Investigated__c` | reference → ResearchTopic__c | RT under investigation |
| `RelatedJournal__c` | reference → Journal__c | Related journal |
| `SourceOpportunity__c` | reference → Opportunity | Source opportunity |
| `SourceCampaign__c` | reference → Campaign | Source campaign |
| `RICaseReason__c` | multipicklist | RI case reasons (52 values) |
| `IntentType__c` | picklist | AI-classified intent type |
| `IntentSubtype__c` | picklist | AI-classified intent subtype |
| `IntentConfidence__c` | percent | Intent classification confidence |
| `Team__c` | picklist | Assigned team |
| `NumberOfDaysOpen__c` | double | Days open |
| `TimeUntilFirstEmailResponse__c` | double | First response time |
| `TimeToAssignment__c` | double | Time to assignment |
| `SLABreachStatus__c` | string | SLA breach status |
| `IsDuplicate__c` | boolean | Marked as duplicate |
| `DuplicateOf__c` | reference → Case | Duplicate of case |
| `Complaint__c` | boolean | Complaint flag |
| `FiniProcessed__c` | boolean | Processed by Fini AI |

**Status values:** `New`, `In Progress`, `Pending Response`, `On Hold`, `User Responded`, `Closed`

**Priority values:** `Urgent`, `High`, `Medium`, `Low`, `Normal`

**Origin values:** `Email`, `User`, `Phone`, `Review Forum`, `Support`, `J-DEV`, `Research Integrity`, `POF`, `Production Forum`, `Chat`, `RTM`, `Social Media`, `Web`, `Submissions`, `Whatsapp`, `My Frontiers`, `Automation-Created`, `Staff-created`

**IntentType__c values:** `Amend decision`, `Certificates and confirmation`, `Customer update`, `Editor Assignment`, `Editorial Board membership`, `Extension Request`, `General Peer Review`, `General Publishing`, `Institution Update`, `Journal`, `Manuscript Revisions`, `Other`, `Payment query`, `Production`, `Research Topic`, `Reviewer assignment`, `Status Update Request`, `Technical issues`, `Withdrawal Request`

### Lead — Prospective Contacts (~7.0M)

Potential researchers and institutional partners. 195 fields.

**Record types:** `Researcher`, `Institutional Partnership`

**Key fields:** Same profile as Contact but for unconverted prospects. Key fields: `FirstName`, `LastName`, `Email`, `Company`, `Title`, `HIndex__c`, `Country__c`, `NumberOfPublications__c`, `No_of_Citations__c`, `Coauthorships__c`, `Field__c`, `SFClosestFrontiersJournal__c`

**Status values:** `New`, `Nurturing`, `Discovery`, `Working`, `Opportunity Created`, `Qualified`, `Lost`, `Unqualified`

### Account — Institutions (~varies)

Institutions, universities, societies. 127 fields.

**Record types:** `Frontiers Account`, `Society Account`

**Key fields:**

| Field | Type | Description |
|-------|------|-------------|
| `Name` | string | Account name |
| `Type` | picklist | Account type |
| `BillingCountry__c` | picklist | Country |
| `InstitutionalAgreement__c` | boolean | Has institutional agreement |
| `InstitutionalPlan__c` | picklist | Institutional plan |
| `ContractedAmount__c` | currency | Contracted amount |
| `SubmissionsAmount__c` | currency | Submissions amount |
| `FPPAccount__c` | boolean | FPP account |
| `FPPStatus__c` | picklist | FPP status |
| `Classification__c` | picklist | Account classification |
| `Tier__c` | picklist | Account tier |
| `Top150__c` | boolean | Top 150 institution |
| `Top500__c` | boolean | Top 500 institution |
| `QualityRanking__c` | double | Quality ranking |
| `NoOfFrontiersAuthors__c` | double | Frontiers authors count |
| `DiscountPercentage__c` | picklist | Discount percentage |
| `InsightsPlatformAccessGranted__c` | boolean | Insights platform access |
| `PrimaryIP__c` | boolean | Primary institutional partner |
| `NumberOfIPOpportunities__c` | double | IP opportunities count |
| `Region__c` | reference → Region__c | Region |

## Relationship Objects

### ArticleAuthor__c (~8.3M)

Links articles to their authors with ordering and role information.

| Field | Type | Description |
|-------|------|-------------|
| `Article__c` | reference → Article__c | Article |
| `Contact__c` | reference → Contact | Author contact |
| `Role__c` | picklist | Author role |
| `Order__c` | double | Author position |
| `FirstName__c` / `LastName__c` / `Email__c` | string | Author details |
| `Affiliation__c` | string | Author affiliation |
| `SubmissionAffiliationName__c` | string | Affiliation at submission |
| `ArticleSubmitted__c` | date | Article submission date |
| `ArticleStage__c` | string | Article stage |
| `Journal__c` | string | Journal name |
| `InvoicePaid__c` | boolean | Invoices paid |
| `RTContributor__c` | reference → ResearchTopicContributor__c | RT contributor link |
| `AccountRIMonitoring__c` | boolean | Account RI monitoring flag |
| Survey fields: `SurveyPromoterScore__c`, `SurveySatisfactionWithProcess__c`, `SurveyEditorialOfficeSupport__c`, `SurveyWillSubmitAgain__c`, `SurveyDateTime__c` |

### ArticleEditor__c (~1.1M)

Editor assignments on articles.

| Field | Type | Description |
|-------|------|-------------|
| `Article__c` | reference → Article__c | Article |
| `Contact__c` | reference → Contact | Editor contact |
| `Role__c` | picklist | Editor role |
| `Status__c` | picklist | Assignment status |
| `AssignDate__c` | datetime | When assigned |
| `Affiliation__c` | string | Editor affiliation |
| `Article_Journal__c` | string | Journal name |
| `Article_Section__c` | string | Section name |
| `Article_Stage__c` | string | Article stage |

### ArticleReviewer__c (~2.4M)

Reviewer assignments on articles.

| Field | Type | Description |
|-------|------|-------------|
| `Article__c` | reference → Article__c | Article |
| `Contact__c` | reference → Contact | Reviewer contact |
| `Role__c` | picklist | Reviewer role |
| `Status__c` | picklist | Review status |
| `AssignDate__c` | datetime | When assigned |
| `ReportQuality__c` | picklist | Report quality rating |
| `ReportSubmissionDate__c` | date | Report submission date |
| `Affiliation__c` | string | Reviewer affiliation |
| `ArticleJournal__c` | string | Journal name |

### EditorialBoardMember__c (~647K)

Board memberships linking contacts to journals/sections.

| Field | Type | Description |
|-------|------|-------------|
| `Contact__c` | reference → Contact | Board member |
| `Role__c` | picklist | Board role |
| `Status__c` | picklist | Status |
| `Taxonomy__c` | reference → Taxonomy__c | Board (journal/section) |
| `Field__c` | reference → Field__c | Field |
| `Specialty__c` | reference → Specialty__c | Specialty |
| `Domain__c` | reference → Domain__c | Domain |
| `ResearchTopic__c` | reference → ResearchTopic__c | Related RT (if applicable) |
| `IsRemoved__c` | boolean | Removed from board |
| `Order__c` | double | Sort order |
| `CreateDate__c` | date | Joined on |
| `EditorRemovalResignationDate__c` | date | Removal/resignation date |
| `EditorRemovalResignationReason__c` | picklist | Removal reason |
| `EB_Validation__c` | picklist | EB validation status |
| `Validated_Date__c` | date | Validated date |
| `FollowUpPhase__c` | picklist | Follow-up phase |
| `DoNotContactUntil__c` | date | Do not contact until |

**Role__c values:** `Field Chief Editor`, `Assistant Field Chief Editor`, `Specialty Chief Editor`, `Assistant Specialty Chief Editor`, `Associate Editor`, `Guest Associate Editor`, `Review Editor`, `Managing Editor`, `Editor-in-Chief`, `Reviewer`

**Status__c values:** `Active`, `Opt-out`, `NotStarted`, `Ongoing`, `NotNeeded`, `Failed`

**EditorRemovalResignationReason__c values:** `Resigned - other`, `Resigned - retired`, `Removed - ethical concerns`, `Removed - insufficient seniority requirements`, `Removed - substandard performance`, `Removed - wrong section`, `Resigned - no time/not interested`, `Resigned - dissatisfied`, `Removed - unresponsive/inactive`, `Removed - other`

### ResearchTopicContributor__c (~15M)

RT contributor invitations and participation tracking. 129 fields.

| Field | Type | Description |
|-------|------|-------------|
| `ResearchTopic__c` | reference → ResearchTopic__c | Research topic |
| `Contact__c` | reference → Contact | Contributor contact |
| `Lead__c` | reference → Lead | Or a lead |
| `InvitationStatus__c` | picklist | Invitation status |
| `Email__c` | email | Contributor email |
| `FirstName__c` / `LastName__c` | string | Contributor name |
| `ContributionTitle__c` | textarea | Proposed contribution title |
| `DeclinationReason__c` | picklist | Why declined |
| `InvitedDate__c` | date | When invited (personal) |
| `ConfirmedDate__c` | date | When confirmed |
| `PendingDate__c` | date | When set to pending |
| `NoSubmittedManuscripts__c` | double | Submitted manuscripts |
| `NoExpectedManuscripts__c` | double | Expected manuscripts |
| `Source__c` | picklist | Contributor source |
| `HIndex__c` | double | h-index |
| `Country__c` | string | Country |
| `IsVIP__c` | boolean | VIP flag |
| `IsRTCaTE__c` | boolean | Is contributor a TE |
| `NewAuthor__c` | boolean | New to Frontiers |
| `AbstractStatus__c` | picklist | MS Summary status |
| `AbstractTitle__c` | textarea | MS Summary title |
| `CfPEmailSent__c` | boolean | Call for Papers email sent |
| `CfPJourneyStatus__c` | picklist | CfP journey status |
| `CCEngagement__c` | picklist | CC Engagement status |
| `AssignedEditor__c` | reference → ResearchTopicEditor__c | Assigned editor |
| `PersonalMessageSender__c` | reference → Contact | Personal message sender |
| `NoOfRemindersSent__c` | double | Reminders sent |
| `WithdrawalReasonType__c` | picklist | Withdrawal reason type |
| `PersonalisedSnippet__c` | textarea | AI-generated snippet |
| `PersonalisedInsights__c` | textarea | AI-generated insights |
| `AIEmailInvitationGenerationStatus__c` | picklist | AI email generation status |
| `InvitationSentWithPerfectEmail__c` | boolean | Perfect email used |

**InvitationStatus__c values:** `Status`, `Pending`, `Declined`, `Confirmed`, `Co-author`, `Unresponsive`, `Withdrawn`, `ToBeContacted`

**AbstractStatus__c values:** `In Preparation`, `Submitted`, `Accepted`, `Rejected`, `Deleted`

**CfPJourneyStatus__c values:** `In journey`, `Finished Journey`, `Unqualified`, `Inactive`, `Re-entry`

### ResearchTopicEditor__c (~258K)

Topic editor assignments.

| Field | Type | Description |
|-------|------|-------------|
| `ResearchTopic__c` | reference → ResearchTopic__c | Research topic |
| `Contact__c` | reference → Contact | Editor contact |
| `Lead__c` | reference → Lead | Or a lead |
| `Type__c` | picklist | Topic Editor / Topic Coordinator |
| `Country__c` | string | Editor country |
| `Email__c` | string | Editor email |
| `HIndex__c` | double | h-index |
| `SequenceID__c` | double | Sequence ID |
| `PCLBLastLogin__c` | datetime | Last PCLB login |
| `PCLBNumberLogins__c` | double | PCLB login count |

### BoardInvitation__c (~943K)

Editorial board recruitment invitations.

| Field | Type | Description |
|-------|------|-------------|
| `Contact__c` | reference → Contact | Invited contact |
| `Lead__c` | reference → Lead | Or a lead |
| `Journal__c` | reference → Journal__c | Target journal |
| `Taxonomy__c` | reference → Taxonomy__c | Target board |
| `Role__c` | picklist | Proposed role |
| `Status__c` | picklist | Invitation status |
| `InvitationDate__c` | date | When sent |
| `InvitationType__c` | picklist | Invitation type |
| `DeclineReason__c` | picklist | If declined, why |
| `NoOfReminders__c` | double | Reminders sent |
| `StatusDate__c` | date | Status date |
| `Inviter__c` | reference → Contact | Who invited |

**Status__c values:** `Accepted`, `Appointed`, `Declined`, `Pending`, `Role Changed`, `Role Revoked`, `Revoked`

**Role__c values:** `Review Editor`, `Associate Editor`, `Assistant Specialty Chief Editor`, `Specialty Chief Editor`, `Field Chief Editor`, `Assistant Field Chief Editor`

**InvitationType__c values:** `Change Role`, `Invitation`, `Suggestion: Invitation`, `Suggestion: Change Role`

**DeclineReason__c values:** `I cannot commit the time right now`, `I'm part of another Editorial Board`, `Not within my expertise`, `Other`

### Invoice__c (~1.3M)

Article processing charge invoices.

| Field | Type | Description |
|-------|------|-------------|
| `Article__c` | reference → Article__c | Related article |
| `ArticleAuthor__c` | reference → ArticleAuthor__c | Paying author |
| `InvoiceNumber__c` | string | Invoice number |
| `Status__c` | picklist | Open / Closed / Deleted |
| `DueDate__c` | date | Due date |
| `PayerName__c` | string | Payer name |
| `PayerEmail__c` | email | Payer email |
| `PaymentUrl__c` | url | Payment link |

### Discount_Code__c (~432K)

Fee waivers and discounts for article processing charges.

| Field | Type | Description |
|-------|------|-------------|
| `Contact__c` | reference → Contact | Recipient |
| `Referrer__c` | reference → Contact | Referrer |
| `Article__c` | reference → Article__c | Applied to article |
| `ArticleReviewed__c` | reference → Article__c | Reviewed article |
| `Journal__c` | reference → Journal__c | Applicable journal |
| `Research_Topic__c` | reference → ResearchTopic__c | Related RT |
| `DiscountPercentage__c` | percent | Discount % |
| `InitialFee__c` | currency | Original fee |
| `DiscountedAmount__c` | currency | Discount amount |
| `NetFee__c` | currency | Net fee after discount |
| `VoucherValue__c` | currency | Voucher value |
| `Type__c` | picklist | Discount type |
| `Category__c` | picklist | Discount category (23 values) |
| `DecisionStatus__c` | picklist | Approval status |
| `ApprovalStatus__c` | picklist | Pending / Approved / Rejected |
| `ExpirationDate__c` | date | Expiry date (submission) |
| `Application_Date__c` | date | Application date |
| `ArticlePublishedDate__c` | date | Article published date |

**Type__c values:** `Rewards`, `Societies`, `Strategic`, `Waivers`, `Special Initiatives`

**DecisionStatus__c values:** `Not Processed`, `Processed_Approved`, `Processed - Rejected`, `In_Review`

### AIRAIndicator__c (~8.9M)

AI Review Assistant (AIRA) quality flags raised during article processing.

| Field | Type | Description |
|-------|------|-------------|
| `Article__c` | reference → Article__c | Related article |
| `Category__c` | picklist | Manuscript / Review |
| `GroupName__c` | picklist | Group name |
| `GroupStatus__c` | picklist | Group-level status |
| `IndicatorName__c` | picklist | Specific indicator |
| `IndicatorStatus__c` | picklist | Indicator status |
| `ProcessingStatus__c` | picklist | Processing status |
| `IndicatorAttribute__c` | textarea | Details |
| `InitialIndicatorStatus__c` | string | Initial status |
| `InitialIndicatorAttribute__c` | string | Initial attribute |

**GroupStatus__c / IndicatorStatus__c values:** `Blocked`, `Warning`, `Checked`, `Unchecked`, `Notapplicable`

**ProcessingStatus__c values:** `Pending`, `Resolved`, `Unprocessed`

**GroupName__c values (25):** `Internal flagged author list`, `Language Quality`, `Manual Quality checks`, `Out of scope`, `Repeat submission (Duplicates)`, `Reviewer behavior assessment`, `Service level`, `Text overlap`, `COI: Preferred Associate Editor - Author`, `Ethics guidelines`, `Controversial topics`, `COI: Editor - Author`, `COI: Editor-Reviewer`, `COI: Author - Reviewer`, `Image integrity check`, `Commercial conflicts`, `Submission guidelines`, `Flagged Reviewers`, `Human images`, `Data availability verification`, `Reviewers behaviors`, `Flagged Editors`, `Reviewer reports quality`, `Flagged authors`, `Editorial board`

**IndicatorName__c values (35):** `Frontiers language rating`, `Language evaluation`, `Detection done by iThenticate`, `Frontiers manuscript matches`, `Internal flagged author list`, `Internal flagged editors list`, `Internal flagged reviewer list`, `Animal studies statement verification`, `Human studies statement verification`, `Identifiable images and data statement verification`, `Data availability statement checks`, `Face and body detection`, `Feature duplication detection`, `Frontiers Commercial keyword detection`, `Scope verification v1`, `Scope verification v2`, `Controversial keywords (global and journal specific)`, `Controversial themes`, `Board availability`, `Matches on affiliations`, `Matches on past collaborations`, `Rejections and withdrawals`, `Reports word count`, `Single or missing author`, `Submission evaluation`, `Submission evaluation v2`, `Manufactured Manuscripts (Paper Mill)`, `IP address check`, `IP data verification`

### CampaignMember (junction, 244 fields)

Links Contacts/Leads to Campaigns. Key fields:

| Field | Type | Description |
|-------|------|-------------|
| `CampaignId` | reference → Campaign | Campaign |
| `ContactId` | reference → Contact | Contact (if contact) |
| `LeadId` | reference → Lead | Lead (if lead) |
| `Status` | picklist | Campaign member status (32 values) |
| `HasResponded` | boolean | Responded |
| `InvitedDate__c` | date | When invited |
| `LastRemindedOn__c` | date | Last reminded |
| `NumberOfReminders__c` | double | Reminders count |
| `HIndex__c` | double | h-index |
| `VettingStatus__c` | picklist | Pending / Approved / Rejected |
| `Opportunity__c` | reference → Opportunity | Related opportunity |
| `Opportunity_Won__c` | boolean | Opportunity won |
| `SystemArchived__c` | boolean | System archived |
| `SolicitationType__c` | picklist | EBG / RTA / MS Submission |
| `CallStatus__c` | picklist | Scheduled / Cancelled / Done / Not Attended |
| `PerfectEmailEnabled__c` | boolean | Perfect email enabled |
| Many AUCO, CRTS, EBCO, PTE, REVCO, TDL, TECO fields for audience segmentation data |

### ArticleWorkflow__c / ArticleWorkflowDelay__c

Track article workflow execution and delays.

**ArticleWorkflow__c key fields:** `Article__c`, `Contact__c`, `WorkflowName__c`, `WorkflowStatus__c` (Running), `NextScheduledDate__c`, `DaysUntilNextScheduledDate__c`, `LastTimeout__c`, `NextTimeout__c`

**ArticleWorkflowDelay__c key fields:** `Article__c`, `Status__c` (Running / On Time / Delayed / Requires Action / Completed), `ProcessName__c`, `SubProcessName__c`, `StartDate__c`, `EndDate__c`, `DueDate__c`, `LastDelayDaysCount__c`, `UrgentRequiresAction__c` (On-time / Delayed / Action Required)

### CallLog__c

Call logs for RT management.

| Field | Type | Description |
|-------|------|-------------|
| `CallType__c` | picklist | RT Kickoff Call, CfP Follow-up Call, Final CfP Review Call, Submission Deadline Call, Submission Review Call, Non-standard call, PCLB Call |
| `Status__c` | picklist | Call Taken / Call Not Taken |

## Common SOQL Patterns

### Article queries

```sql
-- Articles published in a date range
SELECT ArticleId__c, Title__c, DOI__c, Stage__c, Journal__c,
       Published_on__c, Views__c, Downloads__c
FROM Article__c
WHERE Published_on__c >= 2025-01-01 AND Published_on__c <= 2025-12-31
ORDER BY Published_on__c DESC
LIMIT 100

-- Articles in review with service level
SELECT ArticleId__c, Title__c, Stage__c, ServiceLevel__c,
       DaysInReview__c, NoOfReviewers__c, CreateDate__c
FROM Article__c
WHERE Stage__c IN ('In Independent Review', 'In Interactive Review')
ORDER BY DaysInReview__c DESC
LIMIT 50

-- Article with related journal info
SELECT ArticleId__c, Title__c, Stage__c,
       Journal__r.Name__c, Journal__r.ImpactFactor__c
FROM Article__c
WHERE Stage__c = 'Published'
LIMIT 10

-- Articles under investigation
SELECT ArticleId__c, Title__c, InvestigationStatus__c,
       Stage__c, Journal__r.Name__c
FROM Article__c
WHERE ArticleUnderInvestigation__c = true

-- Articles by source (RT-IC vs RT-CC)
SELECT Source__c, Stage__c, COUNT(Id) total
FROM Article__c
WHERE Submitted_on__c >= 2025-01-01
GROUP BY Source__c, Stage__c

-- Articles with quality issues
SELECT ArticleId__c, Title__c, LanguageQualityIndicator__c,
       TextOverlapIndicator__c, QualityFunnelStatus__c
FROM Article__c
WHERE LanguageQualityIndicator__c = 'Blocked'
   OR TextOverlapIndicator__c = 'Blocked'
LIMIT 50
```

### Journal queries

```sql
-- Active journals with impact metrics
SELECT Name__c, Abbreviation__c, ImpactFactor__c, CiteScore__c,
       ArticleProcessingCharge__c, Indexing__c, Program__c
FROM Journal__c
WHERE IsOnline__c = true AND IsDeleted__c = false
ORDER BY ImpactFactor__c DESC NULLS LAST

-- Journal with editor-in-chief
SELECT Name__c, ImpactFactor__c,
       EditorInChief__r.FirstName, EditorInChief__r.LastName,
       Manager__r.Name
FROM Journal__c
WHERE IsOnline__c = true

-- Journals by program with budgets
SELECT Name__c, Program__c, ImpactFactor__c,
       CurrentYearlyWaiverBudget__c, CurrentYearPubDevBudget__c
FROM Journal__c
WHERE IsOnline__c = true AND Program__c != null
ORDER BY Program__c, ImpactFactor__c DESC NULLS LAST
```

### Research topic queries

```sql
-- Active research topics with performance
SELECT Title__c, Stage__c, Journal__r.Name__c,
       NoOfPCs__c, NoContributorsConfirmed__c,
       Submitted_Manuscripts__c, NoPublishedArticles__c,
       AcceptanceRate__c, RTSL_Score__c
FROM ResearchTopic__c
WHERE Stage__c = 'Online'
ORDER BY Submitted_Manuscripts__c DESC
LIMIT 50

-- RT health monitoring
SELECT Title__c, RTHealthStatus__c, Stage__c,
       SubmissionDeadline__c, Days_Since_Deadline__c,
       Submitted_Manuscripts__c, NoOfAcceptances__c
FROM ResearchTopic__c
WHERE Stage__c = 'Online'
  AND RTHealthStatus__c IN ('Red', 'Amber')
ORDER BY RTSL_Score__c ASC

-- RT operational steps
SELECT Title__c, Step__c, StepDate__c, Stage__c,
       NoContributorsConfirmed__c, Submitted_Manuscripts__c
FROM ResearchTopic__c
WHERE Stage__c = 'Online'
  AND Step__c IN ('Manuscript Submission', 'Late Submissions')
```

### Contact / people queries

```sql
-- Top researchers by h-index in a field
SELECT FirstName, LastName, Email, Affiliation__c,
       HIndex__c, No_of_Citations__c, NumberOfPublications__c,
       NoArticlesAuthored__c, ActiveEBMRoles__c
FROM Contact
WHERE Field__c = 'Neuroscience'
  AND HIndex__c > 20
ORDER BY HIndex__c DESC
LIMIT 50

-- Editorial board members for a journal section
SELECT Contact__r.FirstName, Contact__r.LastName,
       Contact__r.Email, Role__c, Contact__r.HIndex__c,
       Status__c, CreateDate__c
FROM EditorialBoardMember__c
WHERE Taxonomy__r.Name = 'Some Section Name'
  AND IsRemoved__c = false
  AND Status__c = 'Active'

-- Contact engagement summary
SELECT FirstName, LastName, HIndex__c,
       LastEngagementActivity__c, LastEngagementDate__c,
       NoArticlesAuthored__c, NoArticlesEdited__c,
       ActiveEBMRoles__c, TotalWonOpportunities__c
FROM Contact
WHERE LastEngagementDate__c >= 2025-01-01
ORDER BY HIndex__c DESC
LIMIT 100
```

### Opportunity pipeline queries

```sql
-- RT opportunity pipeline
SELECT Name, StageName, CloseDate, Contact__r.Name,
       Journal__r.Name__c, NoOfTEs__c, LeadTeHIndex__c
FROM Opportunity
WHERE RecordType.Name = 'Research Topic'
  AND IsClosed = false
ORDER BY CloseDate ASC

-- Won opportunities by journal
SELECT Journal__r.Name__c, COUNT(Id) total, SUM(Amount) revenue
FROM Opportunity
WHERE IsWon = true AND CloseDate >= 2025-01-01
GROUP BY Journal__r.Name__c
ORDER BY COUNT(Id) DESC

-- IP pipeline by stage
SELECT StageName, AgreementType__c, COUNT(Id) total, SUM(Amount) revenue
FROM Opportunity
WHERE RecordType.Name = 'Institutional and Consortia Partnership'
  AND IsClosed = false
GROUP BY StageName, AgreementType__c

-- Blocked opportunities
SELECT Name, StageName, BlockedReason__c, StageDuration__c,
       Contact__r.Name, Journal__r.Name__c
FROM Opportunity
WHERE BlockedReason__c != null
  AND IsClosed = false
ORDER BY StageDuration__c DESC
```

### Case & support queries

```sql
-- Open cases by type
SELECT Type, Status, COUNT(Id) total
FROM Case
WHERE Status != 'Closed'
GROUP BY Type, Status
ORDER BY COUNT(Id) DESC

-- Recent support cases for a contact
SELECT CaseNumber, Subject, Status, Type, CreatedDate
FROM Case
WHERE ContactId = '003...'
ORDER BY CreatedDate DESC
LIMIT 20

-- Cases by intent (AI-classified)
SELECT IntentType__c, Status, COUNT(Id) total
FROM Case
WHERE IntentType__c != null AND CreatedDate = THIS_YEAR
GROUP BY IntentType__c, Status
ORDER BY COUNT(Id) DESC

-- SLA breach monitoring
SELECT CaseNumber, Subject, Type, Status,
       NumberOfDaysOpen__c, SLABreachStatus__c
FROM Case
WHERE Status != 'Closed'
  AND SLABreachStatus__c != null
ORDER BY NumberOfDaysOpen__c DESC
LIMIT 50
```

### Invoice & financial queries

```sql
-- Unpaid invoices
SELECT InvoiceNumber__c, Article__r.Title__c,
       PayerName__c, DueDate__c, Status__c
FROM Invoice__c
WHERE Status__c = 'Open'
ORDER BY DueDate__c ASC
LIMIT 100

-- Discount codes by type and status
SELECT Type__c, DecisionStatus__c,
       COUNT(Id) total,
       AVG(DiscountPercentage__c) avg_discount
FROM Discount_Code__c
WHERE Application_Date__c >= 2025-01-01
GROUP BY Type__c, DecisionStatus__c
```

### Board invitation queries

```sql
-- Pending board invitations
SELECT Contact__r.FirstName, Contact__r.LastName,
       Journal__r.Name__c, Role__c, Status__c,
       InvitationDate__c, NoOfReminders__c
FROM BoardInvitation__c
WHERE Status__c = 'Pending'
ORDER BY InvitationDate__c ASC
LIMIT 100

-- Invitation outcomes
SELECT Role__c, Status__c, COUNT(Id) total
FROM BoardInvitation__c
WHERE InvitationDate__c >= 2025-01-01
GROUP BY Role__c, Status__c
```

### Campaign queries

```sql
-- Active RT campaigns with performance
SELECT Name, Type, Status, Journal__r.Name__c,
       NoOfCampaignMembers__c, FirstInvitationDate__c
FROM Campaign
WHERE IsActive = true
  AND RecordType.Name = 'RT Outreach'
ORDER BY NoOfCampaignMembers__c DESC
LIMIT 50
```

### AIRA indicator queries

```sql
-- AIRA flags by category for recent articles
SELECT Category__c, GroupName__c, IndicatorStatus__c,
       COUNT(Id) total
FROM AIRAIndicator__c
WHERE Article__r.CreateDate__c >= 2025-01-01
GROUP BY Category__c, GroupName__c, IndicatorStatus__c
ORDER BY COUNT(Id) DESC

-- Blocked indicators by indicator name
SELECT IndicatorName__c, ProcessingStatus__c, COUNT(Id) total
FROM AIRAIndicator__c
WHERE IndicatorStatus__c = 'Blocked'
  AND Article__r.CreateDate__c >= 2025-01-01
GROUP BY IndicatorName__c, ProcessingStatus__c
ORDER BY COUNT(Id) DESC
```

### RT Contributor queries

```sql
-- Contributor funnel for a specific RT
SELECT InvitationStatus__c, COUNT(Id) total
FROM ResearchTopicContributor__c
WHERE ResearchTopic__c = '...'
GROUP BY InvitationStatus__c

-- VIP contributors
SELECT Name__c, Email__c, HIndex__c,
       InvitationStatus__c, ContributionTitle__c,
       ResearchTopic__r.Title__c
FROM ResearchTopicContributor__c
WHERE IsVIP__c = true
  AND InvitationStatus__c = 'Confirmed'
ORDER BY HIndex__c DESC
LIMIT 50

-- CfP journey status
SELECT CfPJourneyStatus__c, COUNT(Id) total
FROM ResearchTopicContributor__c
WHERE ResearchTopic__r.Stage__c = 'Online'
GROUP BY CfPJourneyStatus__c
```

### Workflow delay queries

```sql
-- Articles requiring action
SELECT Article__r.ArticleId__c, Article__r.Title__c,
       ProcessName__c, SubProcessName__c, Status__c,
       LastDelayDaysCount__c, DueDate__c
FROM ArticleWorkflowDelay__c
WHERE UrgentRequiresAction__c = 'Action Required'
ORDER BY LastDelayDaysCount__c DESC
LIMIT 50
```

## SOQL Best Practices

### Always use LIMIT during exploration
```sql
SELECT Id, Name FROM Article__c LIMIT 10
```

### Use relationship queries for parent fields
```sql
-- Traverse up (parent): use __r instead of __c
SELECT Title__c, Journal__r.Name__c, Journal__r.ImpactFactor__c
FROM Article__c LIMIT 5

-- Standard relationships use direct name
SELECT Name, Account.Name FROM Contact LIMIT 5
```

### Use date literals for dynamic ranges
```sql
WHERE CreatedDate = THIS_YEAR
WHERE CreatedDate = LAST_N_DAYS:30
WHERE CloseDate = NEXT_QUARTER
WHERE Published_on__c >= 2025-01-01
```

### Aggregate queries
```sql
SELECT Stage__c, COUNT(Id) total
FROM Article__c
GROUP BY Stage__c
ORDER BY COUNT(Id) DESC

-- Note: SOQL aggregate queries have specific rules:
-- - Non-aggregated fields must be in GROUP BY
-- - HAVING clause filters on aggregates
-- - ORDER BY can use aggregate functions
```

### Query limits and governor limits
- **Max 2,000 records** per query response (paginate with `nextRecordsUrl`)
- **Max 100,000 records** per SOQL query total
- For very large result sets, use `queryAll` or add filters to reduce scope
- Use `COUNT()` first to check result set size before pulling data
- **Avoid SELECT * —** SOQL does not support it. Always list specific fields.

## Quick Reference

| Question | Query approach |
|----------|---------------|
| Article status / lifecycle | `Article__c` filtered by `Stage__c` |
| Who authored/edited/reviewed an article? | `ArticleAuthor__c`, `ArticleEditor__c`, `ArticleReviewer__c` filtered by `Article__c` |
| Journal list and metrics | `Journal__c` with `IsOnline__c = true` |
| Journal budgets and targets | `Journal__c` with `CurrentYear*` fields |
| Research topic health | `ResearchTopic__c` with `RTHealthStatus__c`, `RTSL_Score__c` |
| RT operational step | `ResearchTopic__c` filtered by `Step__c` |
| RT contributor funnel | `ResearchTopicContributor__c` grouped by `InvitationStatus__c` |
| RT editors | `ResearchTopicEditor__c` |
| Contact/researcher lookup | `Contact` by email, name, or `ContactId__c` |
| Researcher metrics | `Contact` with `HIndex__c`, `*_Percentile__c` fields |
| Editorial board members | `EditorialBoardMember__c` joined with `Contact` |
| Board invitations | `BoardInvitation__c` by `Status__c`, `Role__c` |
| Sales pipeline | `Opportunity` by `RecordType.Name` and `StageName` |
| IP partnerships | `Opportunity` where `RecordType.Name = 'Institutional and Consortia Partnership'` |
| Campaigns and outreach | `Campaign` and `CampaignMember` |
| Support tickets | `Case` by `Type`, `Status`, `RecordType.Name` |
| Case intent classification | `Case` by `IntentType__c` |
| Invoices and payments | `Invoice__c` by `Status__c` |
| Fee waivers | `Discount_Code__c` by `Type__c`, `DecisionStatus__c` |
| AIRA quality flags | `AIRAIndicator__c` by `GroupName__c`, `IndicatorStatus__c` |
| Article workflow delays | `ArticleWorkflowDelay__c` by `Status__c`, `UrgentRequiresAction__c` |
| Taxonomy hierarchy | `Space__c` → `Domain__c` → `Field__c` → `Specialty__c` → `Journal__c` → `JournalSection__c` |
| Object metadata / fields | `describe` API: `/services/data/v59.0/sobjects/{Object}/describe` |
