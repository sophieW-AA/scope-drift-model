# NDM index — `references/ndm/`

One-line summary of every Narrow Data Model (NDM) YAML shipped with this skill. Use this index to pick the correct NDM file before drilling into keys, grain, or foreign keys. Each NDM carries primary keys, foreign keys with cardinality, `space_id` scoping rules, and grain per entity.

**Filename pattern:** `<project>.<dataset>_NDM.yaml`. Path is always `references/ndm/<file>`.

**Coverage:** 27 NDMs across tiers 1–3. `ocean-breeze-tier-4` and `gcp-innovation-hub` datasets have no NDM YAMLs in this skill — use `references/bigquery-schemas.json`, `references/bigquery-tables.json`, and `references/dataset-integration-map.yaml` for those.

## Tier 1 — `ocean-breeze-tier-1`

| NDM file | Covers |
|---|---|
| `ocean-breeze-tier-1.ai_enhanced_profile_NDM.yaml` | AI-generated researcher profiles: `enhanced_profiles_validated` — one row per validated profile keyed on `aira_id` (= AIRAK `AuthorId`); carries expertise, career stage, publishing interests, ORCID, institutional affiliation, quality/decision labels |
| `ocean-breeze-tier-1.airak_NDM.yaml` | AIRAK author/publication graph: `Author`, `Publication`, `Journal`, `Organization`, `AuthorOrganization`, `PublicationAuthor`, `PublicationCitation`, editorial contributions, research topics, watchlist, fields of study |
| `ocean-breeze-tier-1.reporting_data_mart_NDM.yaml` | Core mart: `article`, `author`, `author_organizations`, `person`, `journal`, `research_topic`, `research_topic_*`, `contributor`, `editorial_board_member`, `editorial_board_invitations`, `organization`, `spaces`, `taxonomy`, metrics tables |

## Tier 2 — `ocean-breeze-tier-2`

| NDM file | Covers |
|---|---|
| `ocean-breeze-tier-2.dimensions_NDM.yaml` | Dimensions.ai external bibliometrics: `publications`, `grants`, `metrics` |
| `ocean-breeze-tier-2.editorial_assignment_NDM.yaml` | Review board invitation fact + dimensions: `review_board_invitation`, `review_board_invitation_status_history`, `review_board_invitation_algorithm`, `review_board_invitation_audience_group`, `review_board_invitation_declination_reason`, `review_board_invitation_status`, `review_board_invitation_tracking_method` |
| `ocean-breeze-tier-2.market_intelligence_NDM.yaml` | Market intelligence: `article_impact`, `journal`, `journal_impact`, `market`, `market_journal`, `market_type` |
| `ocean-breeze-tier-2.peer_review_NDM.yaml` | Peer review annotations and turns: `annotation`, `annotation_comment`, `review_turn` |
| `ocean-breeze-tier-2.production_forum_NDM.yaml` | Production system replica (partial from Oct 2025): `article`, `author`, `institution`, `content_type`, `file` |
| `ocean-breeze-tier-2.rosst_NDM.yaml` | Frontiers organization master data: `organization`, `organization_address`, `organization_alias`, `organization_external_identifiers`, `organization_hierarchy`, `organization_inactive_source`, `organization_main_ugarit_id`, `organization_metrics`, `organization_ontology`, `organization_root_hierarchy`, `organization_source`, `organization_source_lookup`, `organization_type`, `organization_url`, `countries`, `consortium_membership`, `publications_funding`, `publications_year_funding`, `rosst_article_awards`, `rosst_article_funding`, `rosst_external_affiliations` |
| `ocean-breeze-tier-2.salesforce_NDM.yaml` | Salesforce CRM replica: `Article__c`, `Article__History`, `ArticleAuthor__c`, `ArticleEditor__c`, `ArticleEditor__History`, `ArticleReviewer__c`, `ArticleWorkflowDelay__c`, `Account`, `AIContent__c`, `AudienceAllocation__c`, `Campaign`, `CampaignMember`, `Case`, `CaseHistory`, `Contact`, `ContactHistory`, `Contract`, `Discount_Code__c`, `Domain`, `EditorialBoardMember__c`, `EditorialBoardMember__History`, `EmailMessage`, `EmailPreference__c`, `Event`, `Field__c`, `Journal__c`, `JournalSection__c`, `Lead`, `LeadHistory`, `LiveChatTranscript`, `LoopInformation__c`, `Opportunity`, `OpportunityContactRole`, `OpportunityStage`, `OpportunityStageDuration__c`, `Opportunity__hd`, `QualtricsSurveyAnswer__c`, `QualtricsSurveyReply__c`, `RecordType`, `Region__c`, `ResearchTopic__c`, `ResearchTopic__History`, `ResearchTopicContributor__c`, `ResearchTopicEditor__c`, `ReservedRecord__c`, `Space__c`, `Specialty__c`, `Task`, `Taxonomy__c`, `User` |
| `ocean-breeze-tier-2.senscience_NDM.yaml` | SENSCIENCE / ScienceRadar platform events: `event` |
| `ocean-breeze-tier-2.workday_adaptive_planning_NDM.yaml` | PubDev financial planning: `allocations_pubdev`, `allocations_pubdev_hierarchy`, `allocations_pubdev_historical`, `employee_status`, `employee_status_historical` |

## Tier 3 — `ocean-breeze-tier-3`

| NDM file | Covers |
|---|---|
| `ocean-breeze-tier-3.arxiv_NDM.yaml` | arXiv preprint metadata |
| `ocean-breeze-tier-3.conference_NDM.yaml` | Conference curation files |
| `ocean-breeze-tier-3.crossref_NDM.yaml` | Crossref DOI metadata: `works`, `works_history` |
| `ocean-breeze-tier-3.digital_tracking_NDM.yaml` | Digital tracking events (status: to be verified) |
| `ocean-breeze-tier-3.doaj_NDM.yaml` | DOAJ open-access journal directory |
| `ocean-breeze-tier-3.manuscript_live_NDM.yaml` | Manuscript content + metadata: `manuscript`, `extractedManuscriptMetadata`, `ContentType`, `FileFormat` |
| `ocean-breeze-tier-3.openalex_NDM.yaml` | OpenAlex academic graph: `works`, `authors`, `institutions`, `sources`, `publishers`, `funders`, `concepts`, `topics`, `domains`, `fields`, `subfields`, `keywords`, `awards` |
| `ocean-breeze-tier-3.orcid_NDM.yaml` | ORCID profiles: `records`, `works`, `peer_reviews` |
| `ocean-breeze-tier-3.organization_curation_files_NDM.yaml` | Organization curation single table (status: to be deleted) |
| `ocean-breeze-tier-3.pubmed_central_NDM.yaml` | PubMed Central: `views_downloads` |
| `ocean-breeze-tier-3.qualtrics_NDM.yaml` | Qualtrics surveys: author, editor, reviewer, NPS, FAAS, and other response tables |
| `ocean-breeze-tier-3.researchgate_NDM.yaml` | ResearchGate article statistics |
| `ocean-breeze-tier-3.retractionwatch_NDM.yaml` | Retraction Watch retraction records |
| `ocean-breeze-tier-3.ringgold_NDM.yaml` | Ringgold institution identifiers: `organizations`, `organizations_deleted`, `ontology`, `org_alt_names`, `org_classifications`, `org_external_classifications`, `org_external_identifiers`, `org_notes`, `org_relationships`, `org_sizes`, `org_urls`, `places` |
| `ocean-breeze-tier-3.workday_reference_data_NDM.yaml` | HR reference: `employee`, `frontiers_role`, `journal_cost_center`, `journal_owner`, `journal_segment`, `journal_team`, `journal_workday`, `program_name`, `project_role` (and each `_historical` variant) |

## How to use an NDM YAML

Each entity in an NDM YAML carries:

- `source_table` — fully-qualified BigQuery path
- `grain` — column list that uniquely identifies one row (use for `DISTINCT`, window `PARTITION BY`, and join keys)
- `primary_key` — primary key column(s)
- `columns[].foreign_keys[]` with `scope` (`internal` to same dataset, `external` to another dataset), target `dataset`/`entity`/`column`, `cardinality` (`many_to_one`, `optional_many_to_one`, `one_to_one`), and a `relationship` phrase

For actual cross-dataset join SQL (which key + `SAFE_CAST` + space filter combination is proven to work), read `references/dataset-integration-map.yaml` in addition to the NDM.
