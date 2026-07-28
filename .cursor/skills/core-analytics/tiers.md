# Tier architecture — detailed catalog

Full per-dataset reference for every tier of the Frontiers BigQuery lakehouse, plus `gcp-innovation-hub`. For quick routing ("which dataset holds X?") use the tables in `SKILL.md` → *How to Use This Skill*, then come here for table-level detail and key columns. For full column schemas see `references/bigquery-schemas.json`. For the complete table inventory across all 68 datasets see `references/bigquery-tables.json`. For keys/grain/joins see `references/ndm/` (indexed in `references/ndm-index.md`).

## Tier 1 — `ocean-breeze-tier-1` (Curated / Business-Ready)

Start here. Tier 1 contains cleaned, enriched, and joined datasets optimized for analysis and reporting. Prefer Tier 1 tables unless the user needs raw or external data.

### `reporting_data_mart` — Core Business Tables

The primary dataset for Frontiers operational reporting. Wide, denormalized tables designed for direct querying.

| Table | Description |
|-------|-------------|
| `article` | Articles with full lifecycle data: submission, review stages, acceptance, publication, metrics. **486 columns** — very wide, always SELECT specific columns. Key columns: `article_id`, `doi`, `title`, `stage`, `is_submitted`, `is_accepted`, `is_published`, `is_rejected`, `create_date`, `article_type`, `submission_type` |
| `person` | People (authors, editors, reviewers) with organization and geographic data. **119 columns**. Key columns: `personuser_id`, `person_email`, `primary_organization`, `primary_organization_country`, `country`, `continent` |
| `contributor` | Research topic contributors with invitation, confirmation, and submission tracking. **282 columns**. Key columns: `contributor_id`, `contributor_email`, `contributor_name`, `contributor_source`, `has_contributor_been_invited`, `has_confirmed_invitation` |
| `journal` | Journal and section taxonomy with management hierarchy. Key columns: `journal_id`, `journal_name`, `section`, `domain`, `field`, `specialty`, `segment`, `portfolio`, `status`, `issn` |
| `author` | Authors with publication metrics and organizational affiliations |
| `author_organizations` | Author–organization relationships |
| `editorial_board_member` | Editorial board membership data |
| `editorial_board_invitations` | Board invitation tracking |
| `research_topic` | Research topics with metadata |
| `research_topic_abstract` | Research topic abstracts |
| `research_topic_coordinator` | RT coordinator assignments |
| `research_topic_editor` | RT editor assignments |
| `review_board_member` | Review board membership |
| `campaign_member` | Marketing campaign membership |
| `email_metrics` | Email delivery and engagement metrics |
| `country_metrics` | Country-level aggregated metrics |
| `journal_role` | Journal role assignments |
| `journal_user_metrics` | Per-journal user-level metrics |
| `organization` | Organization reference data |
| `spaces` | Frontiers spaces |
| `taxonomy` | Journal taxonomy hierarchy |
| `taxonomy_metrics` | Taxonomy-level metrics |
| `user_metrics` | User-level aggregated metrics |

### `airak` — Author Intelligence & Research Analytics Knowledge Base

Large-scale academic entity database. Use for bibliometric analysis, author discovery, and research landscape mapping.

**Core entities:**
- `Author` — `AuthorId`, `FullName`, `NormalizedName`, `IsFrontiersAuthor`, `HasVerifiedEmail`, `HasLoopProfile`
- `Publication` — `PublicationId`, `Doi`, `Title`, `PublishedYear`, `CitationCount`, `JournalId`
- `Journal` — `JournalId`, `DisplayName`, `PublisherId`, `PublicationCount`
- `Organization` — `OrganizationId`, `DisplayName`, `CountryIsoCode3`, `AuthorCount`, `CitationCount`

**Relationship tables:** `AuthorEmail`, `AuthorOrganization`, `AuthorFieldOfStudy`, `AuthorMetric`, `PublicationAuthor`, `PublicationCitation`, `PublicationFieldOfStudy`, `PublicationAbstract`, `PublicationFullText`, `JournalFieldOfStudy`, `JournalSection`

**Editorial & review:** `EditorialBoardRole`, `EditorialContribution`, `EditorialContributionRole`, `EditorialContributionStatus`, `EditorialRole`, `EditorialRoleType`

**Research topics:** `ResearchTopic`, `ResearchTopicContributor`, `ResearchTopicPublication`, `ResearchTopicKeyword`, `ResearchTopicTaxonomy`

**Risk & watchlist:** `WatchlistAuthor`, `WatchlistCategory`, `WatchlistReasonRole`, `WatchlistReasonType`, `Retraction`, `RetractionReason`, `PubpeerComment`

**Other:** `FieldOfStudy`, `FieldOfStudyChildren`, `Country`, `Ranking`, `OrganizationRanking`, `Funders`, `Grants`, `Source`, `FocusMarket`, `ScienceRadarMetrics`, `AuthorClosestFrontiersJournalRank`, `AuthorClosestFrontiersSectionRank`

### `airak_extended`
- `AuthorExclusion` — Extended exclusion data for authors

### `ai_enhanced_profile`
- `enhanced_profiles_validated` — AI-enriched author profiles with `career_stage`, `decision_label`, `quality_score`, `expertise`, ORCID, institutional affiliation. Join: `airak.Author.AuthorId → enhanced_profiles_validated.aira_id`

## Tier 2 — `ocean-breeze-tier-2` (Internal Systems)

Data replicated from Frontiers internal systems. Use when you need system-of-record detail not available in Tier 1.

### `salesforce` — CRM Data (51 tables)
Core Salesforce objects mirrored into BigQuery. Key tables:
- `Article__c`, `ArticleAuthor__c`, `ArticleEditor__c`, `ArticleReviewer__c` — Article lifecycle in SF
- `Contact`, `Account`, `Lead` — CRM contacts and accounts
- `Journal__c`, `JournalSection__c`, `Field__c`, `Specialty__c`, `Taxonomy__c` — Journal hierarchy
- `EditorialBoardMember__c` — Board membership
- `ResearchTopic__c`, `ResearchTopicContributor__c`, `ResearchTopicEditor__c` — Research topics
- `Opportunity`, `OpportunityContactRole`, `OpportunityStage` — Sales pipeline
- `Campaign`, `CampaignMember` — Marketing campaigns
- `Case`, `EmailMessage`, `LiveChatTranscript` — Support
- `Space__c` — Frontiers spaces
- `EmailPreference__c` — Email preferences

### `peer_review` — Peer Review Data
- `annotation` — Review annotations
- `annotation_comment` — Comments on annotations
- `review_turn` — Review round tracking

### `editorial_assignment` — Review Board Invitations & Tracking

Handling editor and review board assignment tracking. Fact + dimensions around review board invitations, with `space_id` scoping on every table. Use `references/ndm/ocean-breeze-tier-2.editorial_assignment_NDM.yaml` for primary keys, grain, and join rules.

- Fact: `review_board_invitation` — main fact for review board invitations; grain `review_board_invitation_id, space_id`. Joins to `reporting_data_mart.article` via `article_id → article_id_original`, and to `reporting_data_mart.user_metrics` via `invitee_user_id` / `inviter_user_id`.
- History: `review_board_invitation_status_history` — aggregated status history per invitation.
- Dimensions: `review_board_invitation_algorithm`, `review_board_invitation_audience_group`, `review_board_invitation_declination_reason`, `review_board_invitation_status`, `review_board_invitation_tracking_method`.

### `senscience` — Senscience / ScienceRadar Events

Frontiers-specific events emitted by the SENSCIENCE platform (article publication tracking, ScienceRadar). Use `references/ndm/ocean-breeze-tier-2.senscience_NDM.yaml` for keys and join rules.

- `event` — grain `space_id, submission_id`. Joins to `reporting_data_mart.article` via `submission_id → first_submission_id_original`, and to `reporting_data_mart.user_metrics` via `user_id`. `publication_id` is a UUID with **no confirmed join** to DWH article/DOI — see `dataset-integration-map.yaml` (SENS-001) before using.

### `production_forum` — Production System

**Default path:** Use **`reporting_data_mart`** for article, author, and institution analytics and joins. **Use `production_forum` only** when the user explicitly requests this replica, needs Forums production fields not exposed on the mart, or the mart cannot answer the question. It appears under **Do not use unless the user explicitly names the source** because coverage is **partial from Oct 2025**; when you do query it, use `references/ndm/ocean-breeze-tier-2.production_forum_NDM.yaml` and `references/dataset-integration-map.yaml` for keys and joins.

- `article`, `author`, `author_institution`, `institution` — Production article data
- `content_type`, `file` — Content and file metadata

### `rosst` — Organization Registry (19 tables)
Frontiers organization master data. Key tables: `organization`, `organization_hierarchy`, `organization_metrics`, `organization_alias`, `organization_external_identifiers`, `organization_url`, `countries`, `consortium_membership`, `publications_funding`

### `market_intelligence` — Journal Market & Citation Intelligence

Dimensions-based journal market definitions and monthly citation metrics for articles and journals. Use for competitive landscape analysis, journal benchmarking, and market sizing.

- `journal` — Journal reference with Dimensions, OpenAlex, Scopus, and JCR identifiers; links to `reporting_data_mart.taxonomy` and `reporting_data_mart.journal`
- `journal_impact` — Monthly citation metrics per journal (grain: `journal_id`)
- `article_impact` — Monthly citation metrics per article (grain: `publication_id`); joins to `airak.PublicationSource` via `publication_id → SourceValue`
- `market` — Journal market definitions (subject categories from Dimensions, ASJC/Scopus, JCR/Clarivate); grain `market_id`
- `market_journal` — Journal membership in each market with optional weight; grain `market_id, journal_id`
- `market_type` — Market type definitions and formation rules

For join keys see `references/ndm/ocean-breeze-tier-2.market_intelligence_NDM.yaml`; for the confirmed `article_impact → airak.Publication` join see `references/dataset-integration-map.yaml` (ART-008).

### `dimensions` — Dimensions.ai Data
- `publications`, `grants`, `metrics` — External bibliometric data from Dimensions

### `workday_adaptive_planning` — Financial Planning
- `allocations_pubdev`, `allocations_pubdev_hierarchy` — PubDev budget allocations
- `employee_status` — Employee status data

## Tier 3 — `ocean-breeze-tier-3` (External & Reference Data)

External academic datasets and reference data. Use for enrichment, benchmarking, or cross-referencing.

### `openalex` — OpenAlex Academic Graph (13 tables)
Open academic metadata: `works`, `authors`, `institutions`, `sources`, `publishers`, `funders`, `concepts`, `topics`, `domains`, `fields`, `subfields`, `keywords`, `awards`

### `crossref` — Crossref Metadata
- `works` — DOI metadata from Crossref
- `works_history` — Historical snapshots

### `orcid` — ORCID Records
- `records` — ORCID researcher profiles
- `works` — Publications linked to ORCID
- `peer_reviews` — Peer review activity on ORCID

### `manuscript_live` — Manuscript Data
- `manuscript`, `extractedManuscriptMetadata` — Manuscript content and metadata
- `ContentType`, `FileFormat` — Reference tables

### `qualtrics` — Survey Data (21 tables)
Survey responses across the publication lifecycle:
- Author surveys: `author_post_submission_survey`, `author_post_publication_survey`, `author_peer_review_experience_survey`, `author_peer_review_survey`
- Editor surveys: `editor_exit_survey`, `editor_onboarding_survey`, `handling_editor_experience_survey`, `topic_editor_experience_survey`
- Reviewer surveys: `peer_reviewer_post_peer_review_survey`
- NPS: `editorial_board_nps`, `brand_nps_web_homepage_survey`, `topic_editor_nps_measure`
- FAAS: `faas_author_peer_review_experience_survey`, `faas_handling_editor_experience_survey`, `faas_peer_reviewer_post_peer_review_survey`
- Other: `customer_service_survey`, `fee_support_application_owner`, `frontiers_pof_survey`, `research_topic_management_topic_editors_survey`

### `ringgold` — Organization Reference (12 tables)
Ringgold institution identifiers: `organizations`, `org_alt_names`, `org_classifications`, `org_external_identifiers`, `org_relationships`, `org_sizes`, `org_urls`, `places`

### `workday_reference_data` — HR Reference Data (18 tables)
Employee and journal management reference: `employee`, `frontiers_role`, `journal_cost_center`, `journal_owner`, `journal_segment`, `journal_team`, `journal_workday`, `program_name`, `project_role` (each with `_historical` variant)

### Other External Sources
- `arxiv` → `metadata`
- `doaj` → `journals`
- `pubmed_central` → `views_downloads`
- `researchgate` → `statistics`
- `retractionwatch` → `retractions`
- `conference` → `curation_files`
- `digital_tracking` → `digital_tracking_events`
- `organization_curation_files` → single table

## Tier 4 — `ocean-breeze-tier-4` (Analytics & Tracking)

Web analytics, marketing, and behavioral data. Often large and partitioned.

### `snowplow_analytics` — Web Analytics
- `daily_active_users`, `weekly_active_users`, `monthly_active_users` — DAU/WAU/MAU metrics
- `t_space`, `t_user_journey`, `t_user_journey_path_following_N_actions` — User journey analysis
- Views: `v_dt_events`, `v_genericSchema_Snowplow_live_raw_events_real_time`

### `snowplow_personalization` — Personalization
- `t_dim_visitor`, `t_fact_visitor_behaviour` — Visitor profiles and behavior
- `t_lookup_customer_session`, `t_stg_events`, `t_stg_user_session_relationships`

### `snowplow_personalization_campaigns` — Campaign Visitor Data
- `t_dim_visitor_campaigns` — Visitor-level campaign attribution profiles

### `marketing_campaigns_snowplow` — Campaign Attribution (11 tables)
- `t_submission_attribution_campaign` — Submission attribution to campaigns
- `t_agg_campaign_metrics`, `t_dim_campaign`, `t_dim_journal` — Campaign dimensions and metrics
- `t_fact_sp_events_with_utm_dragged`, `t_ga4_session_campaigns` — Event-level campaign data

### `impact_demographics`
- `t_article_geolocation` — Geographic impact data for articles

### Google Analytics & Search Console
Large date-sharded datasets — query with `_TABLE_SUFFIX` filters:
- `google_analytics_aira_list` (~988 tables) — AIRA List GA data
- `google_analytics_publishing_partners` (~877 tables) — Publishing Partners GA data
- `google_searchconsole_frontiersin_org` — frontiersin.org search performance
- `google_searchconsole_loop_frontiersin` — Loop search performance
- Other search console datasets: `escubed`, `frontierspartnership`, `kids_frontiersin`, `por_journal`, `ssph_journal`

## Innovation Hub — `gcp-innovation-hub` (Experimental)

**WARNING:** this project is primarily for experimentation and innovation projects. For production analytics, always prefer Tier 1–4 datasets. Data here may be experimental, incomplete, or refreshed on different schedules than production pipelines.

Application datasets, next-generation data products, and AI/ML workloads.

### `impact_data_platform_v1` — Article Impact Metrics (13 tables, ~345 GB)

Centralized impact metrics platform tracking views, downloads, and citations across Frontiers properties. The daily metrics table is very large — always filter by date and entity.

**Fact tables (star schema, join on dimension IDs):**

| Table | Description |
|-------|-------------|
| `t_daily_metrics` | Daily metrics by entity, action, provider, country |
| `t_monthly_metrics` | Monthly aggregation |
| `t_quarterly_metrics` | Quarterly aggregation |
| `t_yearly_metrics` | Yearly aggregation |
| `t_alltime_metrics` | All-time cumulative metrics |
| `t_daily_summary` | Daily summary statistics |

Columns: `id_time` (DATE), `id_provider`, `id_space`, `id_entity_type`, `id_action`, `id_data` (the entity ID, e.g. article ID), `id_country`, `unique_human_amount`, `human_amount`

**Dimension tables:**

| Dimension | Values |
|-----------|--------|
| `t_dim_action_extended` | `article_views`, `article_downloads`, `article_citations`, `rt_home_views`, `rt_downloads`, `journal_home_views`, `section_home_views`, `profile_views` |
| `t_dim_provider` | `Impact`, `Dimensions`, `Pubmed`, `ResearchGate` |
| `t_dim_entity_type` | `article`, `profile`, `research_topic`, `journal`, `section` |
| `t_dim_space` | `frontiers`, `fship`, `alf`, `ssph`, `loop`, `sebm` |
| `t_dim_country` | 251 countries |
| `t_dim_time` | Date dimension (36K+ dates) |
| `t_dim_language` | 6 languages |

For example SQL, see [examples.md](examples.md) → *Article impact over time*.

### `prime` — Author Ranking & Matching (6 tables, ~45 GB)

Precomputed rankings and metrics for author–journal matching and editorial recommendations.

| Table | Description |
|-------|-------------|
| `precomputed_section_ranks` | Author proximity rankings per journal section |
| `precomputed_journal_ranks` | Author proximity rankings per journal |
| `precomputed_recent_pub_authors` | Recently publishing authors |
| `precomputed_author_metrics` | Author-level aggregated metrics |
| `precomputed_author_org_topparent` | Author to top-parent organization mapping |
| `te_prime_comparison` | Topic editor comparison data |

### `frontongpt_AL` — AI Agent Analytics (29 tables)

**WARNING: SUSPENDED.** Usage and conversation analytics for Frontiers' internal AI agents (FrontonGPT platform).

| Table | Description |
|-------|-------------|
| `inbound_conversations` | Inbound conversations from all channels |
| `Agent_usage` | Per-conversation agent usage records |
| `Conversation` | Full conversation data with messages |
| `adoption_daily` | Daily adoption metrics |
| `Prime_usage` | Prime feature usage tracking |
| `Agent_user` | Registered agent users |
| `Agent` | Agent definitions |
| `Agent_metric` | Agent-level performance metrics |
| `Model` | LLM model registry |
| `Model_metric` | Model-level performance metrics |

### `review_report` — Review Analytics
- `precomputed_author_org_topparent` — Author to top-parent org mapping for review assignment
- `precomputed_coauthorships` — Co-authorship network for conflict-of-interest checks

### `agent_reports` — AI Agent Outputs
- `rtfinder_analysis` — Research Topic Finder analysis results
- `rtfinder_article` — Articles matched by RT Finder
- `rtfinder_article_summary` — AI-generated article summaries

### `verloop` — Customer Support Chatbot
- `inbound_conversations` — Customer support chatbot conversations

### `workday_data` — HR Data
- `employee_enriched` — Enriched employee data
