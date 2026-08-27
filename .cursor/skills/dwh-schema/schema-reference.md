# DWH Schema Reference

Generated from SQL Server. 12338 columns across 565 tables.


## [FrontiersReports].[AOf]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `UpdateDate` | datetime | YES |

### Accounting_DailyMonitor

| Column | Type | Nullable |
|---|---|---|
| `Invoice Id` | nvarchar(20) | NO |
| `Product Id` | int(10) | YES |
| `Issued Date` | datetime | YES |
| `Due Date` | datetime | YES |
| `Currency` | nvarchar(10) | YES |
| `Status` | varchar(9) | NO |
| `Due Amount` | numeric(18) | YES |
| `Amount Outstanding` | numeric(18) | YES |
| `Payment Date` | datetime | YES |
| `Payment Delay` | int(10) | YES |
| `Payment Type` | nvarchar(50) | YES |
| `Amount Paid` | numeric(18) | YES |
| `Balance Waived` | numeric(18) | YES |
| `Frontiers waiver` | numeric(18) | YES |
| `Frontiers discount` | numeric(18) | YES |
| `Inaugural Article discount` | numeric(18) | YES |
| `Aggregated under Payment Plan` | numeric(18) | YES |

### Accounting_DailyMonitor_History

| Column | Type | Nullable |
|---|---|---|
| `Invoice Id` | nvarchar(20) | NO |
| `Product Id` | int(10) | YES |
| `Issued Date` | datetime | YES |
| `Due Date` | datetime | YES |
| `Currency` | nvarchar(10) | YES |
| `Status` | varchar(9) | NO |
| `Due Amount` | numeric(18) | YES |
| `Amount Outstanding` | numeric(18) | YES |
| `Payment Date` | datetime | YES |
| `Payment Delay` | int(10) | YES |
| `Payment Type` | nvarchar(50) | YES |
| `Amount Paid` | numeric(18) | YES |
| `Balance Waived` | numeric(18) | YES |
| `Frontiers waiver` | numeric(18) | YES |
| `Frontiers discount` | numeric(18) | YES |
| `Inaugural Article discount` | numeric(18) | YES |
| `Aggregated under Payment Plan` | numeric(18) | YES |
| `Refresh Time` | datetime | YES |

### InvoiceDiscounts.Pivot

| Column | Type | Nullable |
|---|---|---|
| `InvoiceId` | bigint(19) | NO |
| `InvoiceNoDisplay` | nvarchar(50) | YES |
| `ArticleId` | bigint(19) | YES |
| `InvoiceDate` | datetime | YES |
| `Research Topic discount` | numeric(38) | YES |
| `Frontiers Subsidy to All Authors` | numeric(38) | YES |
| `Associate Editor discount` | numeric(38) | YES |
| `Emerging journal` | numeric(38) | YES |
| `Research Topic Discount for Editors` | numeric(38) | YES |
| `Frontiers Waiver` | numeric(38) | YES |
| `Inaugural Article Discount` | numeric(38) | YES |
| `DFG Funding Cap` | numeric(38) | YES |
| `Support Plan discount` | numeric(38) | YES |
| `Institutional Membership Discount` | numeric(38) | YES |
| `Journal Manager Discount` | numeric(38) | YES |
| `Research Topic discount for Associate Editors` | numeric(38) | YES |
| `Frontiers discount` | numeric(38) | YES |
| `Aggregated under Payment Plan` | numeric(38) | YES |
| `Special Topic discount` | numeric(38) | YES |
| `Review Editor discount` | numeric(38) | YES |
| `Newly launched journal` | numeric(38) | YES |
| `Chief Editor discount` | numeric(38) | YES |
| `Research Topic discount for Review Editors` | numeric(38) | YES |
| `Research Topic discount for Chief Editors` | numeric(38) | YES |
| `Frontiers Subsidy` | numeric(38) | YES |
| `Special Topic discount for Associate Editors` | numeric(38) | YES |
| `Research Topic` | numeric(38) | YES |
| `Direct Invoicing Discount` | numeric(38) | YES |
| `EOF Waiver` | numeric(38) | YES |
| `CSF 100% Research Topic Submission Discount` | numeric(38) | YES |
| `2020 Editorial Discount` | numeric(38) | YES |
| `Aggregate under Payment Plan` | numeric(38) | YES |
| `Publishing Discount Other` | numeric(38) | YES |
| `Fee Support` | numeric(38) | YES |
| `Aggregated Monthly Invoicing` | numeric(38) | YES |
| `Aggregated Under Sponsorship Plan` | numeric(38) | YES |
| `Post Publication Fee Support` | numeric(38) | YES |
| `Funding Cap` | numeric(38) | YES |
| `Publishing Discount` | numeric(38) | YES |
| `Article Fee Support` | numeric(38) | YES |
| `Publishing Discount Prior Years` | numeric(38) | YES |
| `Partially Aggregated Under Payment Plan` | numeric(38) | YES |
| `Partially Aggregated Monthly Invoicing` | numeric(38) | YES |
| `Partially Aggregated Under Sponsorship Plan` | numeric(38) | YES |
| `COVID` | numeric(38) | YES |
| `Other` | numeric(38) | YES |

### Invoices.Merged

| Column | Type | Nullable |
|---|---|---|
| `InvoiceId` | bigint(19) | NO |
| `PaymentId` | bigint(19) | NO |
| `InvoiceId.Original` | int(10) | YES |
| `SpaceId` | smallint(5) | NO |
| `TaxonomyId` | bigint(19) | YES |
| `ArticleId` | bigint(19) | NO |
| `ArticleId.Original` | int(10) | YES |
| `ArticleTitle` | nvarchar | YES |
| `ArticleType` | nvarchar(50) | YES |
| `StageDate.Published` | datetime | YES |
| `StageDate.Accepted` | datetime | YES |
| `StageDate.ReceivedbyJournal` | datetime | YES |
| `StageDate.Deleted` | datetime | YES |
| `ArticleStage` | nvarchar(40) | YES |
| `ArticleStageCategory` | nvarchar(30) | YES |
| `InvoiceNo` | int(10) | NO |
| `InvoiceNoDisplay` | nvarchar(50) | YES |
| `DueAmount` | numeric(18) | YES |
| `AmountOutstanding` | numeric(18) | YES |
| `DueAmountSwissVAT` | numeric(22) | YES |
| `Currency` | nvarchar(10) | YES |
| `RevenueId` | int(10) | YES |
| `Revenue` | nvarchar(20) | YES |
| `InvoiceDate` | datetime | YES |
| `InvoiceDueDate` | datetime | YES |
| `IsProforma` | varchar(3) | NO |
| `IsDeleted` | bit | NO |
| `InvoiceVersion` | int(10) | YES |
| `InvoiceValidityId` | tinyint(3) | YES |
| `InvoiceStatusId` | tinyint(3) | YES |
| `InvoiceValidity` | varchar(9) | YES |
| `InvoiceStatus` | varchar(9) | YES |
| `PaymentDate` | datetime | YES |
| `PaymentDelay` | int(10) | YES |
| `PaidAmount` | numeric(18) | YES |
| `PaymentTypeId` | int(10) | YES |
| `PaymentType` | nvarchar(50) | YES |
| `PaymentAccount` | nvarchar(50) | YES |
| `PaymentVisible` | varchar(3) | YES |
| `PayerFirstName` | nvarchar(400) | YES |
| `PayerMiddleName` | nvarchar(500) | YES |
| `PayerLastName` | nvarchar(200) | YES |
| `PayerOrganizationId` | int(10) | YES |
| `PayerOrganization` | nvarchar(200) | YES |
| `PayerAddress` | nvarchar(500) | YES |
| `PayerCity` | nvarchar(50) | YES |
| `PayerCountryId` | nvarchar(5) | YES |
| `PayerCountry` | nvarchar(100) | YES |
| `PayerContinent` | varchar(13) | YES |
| `CorrespondingAuthorsEmails` | nvarchar | YES |
| `CorrespondingAuthorsAffiliations` | nvarchar | YES |
| `FrontiersWaiver` | numeric(38) | YES |
| `FrontiersDiscount` | numeric(38) | YES |
| `InvoiceDiscountCode` | nvarchar(200) | YES |
| `DiscountCode` | varchar(8) | NO |
| `CodeType` | varchar(8) | NO |
| `AggregatedunderPaymentPlan` | numeric(38) | YES |
| `InauguralArticleDiscount` | numeric(38) | YES |
| `DFGFundingCap` | numeric(38) | YES |
| `SupportPlandiscount` | numeric(38) | YES |
| `InstitutionalMembershipDiscount` | numeric(38) | YES |
| `JournalManagerDiscount` | numeric(38) | YES |
| `ResearchTopicdiscount` | numeric(38) | YES |
| `FrontiersSubsidytoAllAuthors` | numeric(38) | YES |
| `AssociateEditordiscount` | numeric(38) | YES |
| `Emergingjournal` | numeric(38) | YES |
| `ResearchTopicDiscountforEditors` | numeric(38) | YES |
| `ResearchTopicdiscountforAssociateEditors` | numeric(38) | YES |
| `SpecialTopicdiscount` | numeric(38) | YES |
| `ReviewEditordiscount` | numeric(38) | YES |
| `Newlylaunchedjournal` | numeric(38) | YES |
| `ChiefEditordiscount` | numeric(38) | YES |
| `ResearchTopicdiscountforReviewEditors` | numeric(38) | YES |
| `ResearchTopicdiscountforChiefEditors` | numeric(38) | YES |
| `FrontiersSubsidy` | numeric(38) | YES |
| `SpecialTopicdiscountforAssociateEditors` | numeric(38) | YES |
| `ResearchTopic` | numeric(38) | YES |
| `EOFWaiver` | numeric(38) | YES |
| `CSF100%ResearchTopicSubmissionDiscount` | numeric(38) | YES |
| `Other` | numeric(38) | YES |
| `COVID` | numeric(38) | YES |
| `2020EditorialDiscount` | numeric(38) | YES |
| `AggregateunderPaymentPlan` | numeric(38) | YES |
| `PublishingDiscountOther` | numeric(38) | YES |
| `FeeSupport` | numeric(38) | YES |
| `AggregatedMonthlyInvoicing` | numeric(38) | YES |
| `AggregatedUnderSponsorshipPlan` | numeric(38) | YES |
| `PostPublicationFeeSupport` | numeric(38) | YES |
| `FundingCap` | numeric(38) | YES |
| `PublishingDiscount` | numeric(38) | YES |
| `ArticleFeeSupport` | numeric(38) | YES |
| `PublishingDiscountPriorYears` | numeric(38) | YES |
| `PartiallyAggregatedUnderPaymentPlan` | numeric(38) | YES |
| `PartiallyAggregatedMonthlyInvoicing` | numeric(38) | YES |
| `PartiallyAggregatedUnderSponsorshipPlan` | numeric(38) | YES |
| `IsRejected` | varchar(3) | YES |
| `IsResearchTopic` | varchar(3) | YES |
| `ResearchTopicId` | bigint(19) | YES |
| `ResearchTopicId.Original` | int(10) | YES |
| `ResearchTopicTitle` | nvarchar(1100) | YES |
| `ResearchTopicOnlineDate` | datetime | YES |
| `ResearchTopicDeletedDate` | datetime | YES |
| `Journal` | nvarchar(150) | YES |
| `JournalFullName` | nvarchar(200) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `Field` | nvarchar(150) | YES |
| `Specialty` | nvarchar(100) | YES |
| `Program` | nvarchar(50) | YES |
| `InvoiceDedupId` | bigint(19) | YES |

## [FrontiersReports].[BIRep]


### ArticlesDS.Workflows

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `Current Workflow` | nvarchar(10) | YES |
| `Next Time Out` | nchar(10) | YES |
| `Next Time Out Date` | datetime | YES |

### DecisionTime

| Column | Type | Nullable |
|---|---|---|
| `PK_Date` | datetime | NO |
| `NbOfManuscripts` | int(10) | YES |
| `ListOfManuscripts` | varchar | YES |
| `NbOfDays` | decimal(9) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### EBCapacity

| Column | Type | Nullable |
|---|---|---|
| `SnapshotDate` | datetime | NO |
| `TaxonomyId` | bigint(19) | NO |
| `DefaultTaxonomyId` | bigint(19) | NO |
| `Program` | nvarchar(50) | YES |
| `Journal` | nvarchar(150) | YES |
| `Section` | nvarchar(100) | YES |
| `Publish Date` | datetime | YES |
| `Space` | nvarchar(100) | YES |
| `Articles in Review - Last 90 days` | float(53) | YES |
| `RT Articles In Review - Last 90 days` | float(53) | YES |
| `Spontaneous Articles In Review - Last 90 days` | float(53) | YES |
| `Cumulative Articles Entered in Review - Last 90 days` | int(10) | YES |
| `Cumulative RT Articles Entered In Review - Last 90 days` | int(10) | YES |
| `Cumulative Spontaneous Articles Entered In Review - Last 90 days` | int(10) | YES |
| `Articles Received - Last 90 days` | int(10) | YES |
| `RT Articles Received - Last 90 days` | int(10) | YES |
| `Spontaneous Articles Received - Last 90 days` | int(10) | YES |
| `Articles Submitted - Last 90 days` | int(10) | YES |
| `Articles Submitted - Last 90 days year before` | int(10) | YES |
| `Articles Accepted - Last 90 days` | int(10) | YES |
| `Articles Accepted - Last 90 days year before` | int(10) | YES |
| `Articles Rejected - Last 90 days` | int(10) | YES |
| `Articles Rejected - Last 90 days year before` | int(10) | YES |
| `Articles Decided - Last 90 days` | int(10) | YES |
| `Articles Decided - Last 90 days year before` | int(10) | YES |
| `Active AEs - Last 90 days` | int(10) | YES |
| `Active REs - Last 90 days` | int(10) | YES |
| `Review Board Invitations - Last 90 days` | int(10) | YES |
| `Time to Assign AE - Last 90 days` | decimal(10) | YES |
| `Time to Assign AE - Last 90 days year before` | decimal(10) | YES |
| `Time to Assign AE - Last 91 to 180 days` | decimal(10) | YES |
| `Time to Assign AE to Spontaneous Articles - Last 90 days` | decimal(10) | YES |
| `Time to Assign AE to Spontaneous Articles - Last 90 days year before` | decimal(10) | YES |
| `Time to Assign AE to RT Articles - Last 90 days` | decimal(10) | YES |
| `Time to Assign AE to RT Articles - Last 90 days year before` | decimal(10) | YES |
| `Time to Assign RE - Last 90 days` | decimal(10) | YES |
| `Time to Assign RE - Last 90 days year before` | decimal(10) | YES |
| `Time to Assign RE to Spontaneous Articles - Last 90 days` | decimal(10) | YES |
| `Time to Assign RE to Spontaneous Articles - Last 90 days year before` | decimal(10) | YES |
| `Time to Assign RE to RT Articles - Last 90 days` | decimal(10) | YES |
| `Time to Assign RE to RT Articles - Last 90 days year before` | decimal(10) | YES |
| `AE Ratio` | decimal(10) | YES |
| `RE Ratio` | decimal(10) | YES |
| `Invitations Ratio` | decimal(10) | YES |

### HotspotsDS

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `DateOfInterest` | datetime | NO |
| `SegmentHead` | nvarchar(100) | YES |
| `Segment` | nvarchar(50) | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(100) | YES |
| `Journal` | nvarchar(150) | YES |
| `Section` | nvarchar(100) | YES |
| `HotspotFlag` | smallint(5) | YES |
| `PfM` | nvarchar(4000) | YES |
| `JM Concat` | nvarchar(4000) | YES |
| `PRM Concat` | nvarchar(4000) | YES |
| `All Articles in Review` | int(10) | YES |
| `RT Articles In Review` | int(10) | YES |
| `Spontaneous Articles In Review` | int(10) | YES |
| `Articles with No HE` | int(10) | YES |
| `Not enough Reviewers` | int(10) | YES |
| `Article Count` | int(10) | YES |
| `All AE` | int(10) | YES |
| `AE Edit last 6 months` | int(10) | YES |
| `AE Not edited last 6 months` | int(10) | YES |
| `All RE` | int(10) | YES |
| `RE Review last 6 months` | int(10) | YES |
| `RE Not reviewed last 6 months` | int(10) | YES |
| `AE New` | int(10) | YES |

### IndexingRI

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | int(10) | YES |
| `Space` | nvarchar(150) | YES |
| `ArticleId.Original` | bigint(19) | NO |
| `ArticleTitle` | nvarchar(1000) | YES |
| `DOI` | nvarchar(1000) | YES |
| `ArticleType` | nvarchar(150) | YES |
| `Program` | nvarchar(150) | YES |
| `Domain` | nvarchar(150) | YES |
| `Field` | nvarchar(150) | YES |
| `Specialty` | nvarchar(150) | YES |
| `Journal` | nvarchar(150) | YES |
| `Section` | nvarchar(150) | YES |
| `ArticleCountry` | nvarchar(150) | YES |
| `StageDate.Submitted` | datetime | NO |
| `StageDate.Published` | datetime | NO |
| `ResearchIntegrity.Owner.UserId` | bigint(19) | YES |
| `ResearchIntegrity.Owner.Email` | nvarchar(150) | YES |
| `ResearchIntegrity.Owner.FirstName` | nvarchar(150) | YES |
| `ResearchIntegrity.Owner.LastName` | nvarchar(150) | YES |
| `ArticleCountry3RegionsBinFocus` | nvarchar(150) | YES |
| `ArticleCountry5RegionsBin` | nvarchar(150) | YES |
| `ArticleCountry8RegionsBin` | nvarchar(150) | YES |
| `ArticleCountry8RegionsBin-China` | nvarchar(150) | YES |
| `ArticleCountry8RegionsBin-ChinaCAS` | nvarchar(150) | YES |
| `OverallQualityRating` | decimal(10) | YES |
| `OverallQualityRatingBins` | nvarchar(150) | YES |
| `AvgQualityRating` | decimal(10) | YES |
| `ReviewersAssigned` | bigint(19) | YES |
| `Reviewers` | bigint(19) | YES |
| `ActiveReviewers` | bigint(19) | YES |
| `ReviewBoardMemberId` | bigint(19) | YES |
| `RoleId` | int(10) | NO |
| `Name` | nvarchar(150) | YES |
| `Email` | nvarchar(150) | YES |
| `UserId` | bigint(19) | NO |
| `Statistical` | nvarchar(150) | YES |
| `Reproducibility` | nvarchar(150) | YES |
| `Figures` | nvarchar(150) | YES |
| `AvgReviewerRating` | decimal(10) | YES |
| `Quality` | nvarchar(150) | YES |
| `Language.Status.Last` | nvarchar(1000) | YES |
| `Scope.Status.Last` | nvarchar(1000) | YES |
| `LastIndRevSubm` | datetime | YES |
| `LastResubmission` | datetime | YES |
| `ResubAfterLastIndRev` | int(10) | YES |

### JournalAndSectionTargetData

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `JournalTaxonomyId` | bigint(19) | NO |
| `Date` | date | NO |
| `Days In Month` | int(10) | NO |
| `Quarter` | varchar(2) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `Domain` | nvarchar(50) | YES |
| `Field` | nvarchar(150) | YES |
| `Journal` | nvarchar(150) | YES |
| `Program` | nvarchar(50) | YES |
| `Section` | nvarchar(100) | YES |
| `Is Default` | bit | YES |
| `Journal Responsible` | nvarchar(100) | YES |
| `Program Responsible` | nvarchar(100) | YES |
| `RT Posted` | int(10) | YES |
| `RT Posted PY` | int(10) | YES |
| `RT Posted PY Full` | int(10) | YES |
| `EBM RT Posted` | int(10) | YES |
| `EBM RT Posted PY` | int(10) | YES |
| `EBM RT Posted PY Full` | int(10) | YES |
| `Confirmed Contributors` | int(10) | YES |
| `Confirmed Contributors PY` | int(10) | YES |
| `Confirmed Contributors PY Full` | int(10) | YES |
| `RT Submissions` | int(10) | YES |
| `IC RT Submissions` | int(10) | YES |
| `CC RT Submissions` | int(10) | YES |
| `SP RT Submissions` | int(10) | YES |
| `EBM RT Submissions` | int(10) | YES |
| `Reviewable RT Submissions` | int(10) | YES |
| `Reviewable Submissions by EBM/REV` | int(10) | YES |
| `Reviewable Submissions by return authors` | int(10) | YES |
| `Reviewable RT IC Submissions` | int(10) | YES |
| `Reviewable Submissions` | int(10) | YES |
| `Reviewable RT Submissions PY` | int(10) | YES |
| `Reviewable Submissions by EBM/REV PY` | int(10) | YES |
| `Reviewable Submissions by return authors PY` | int(10) | YES |
| `Reviewable RT IC Submissions PY` | int(10) | YES |
| `Reviewable Submissions PY` | int(10) | YES |
| `Reviewable RT Submissions PY Full` | int(10) | YES |
| `Reviewable Submissions by EBM/REV PY Full` | int(10) | YES |
| `Reviewable Submissions by return authors PY Full` | int(10) | YES |
| `Reviewable RT IC Submissions PY Full` | int(10) | YES |
| `Reviewable Submissions PY Full` | int(10) | YES |
| `RT Acceptances` | int(10) | YES |
| `IC RT Acceptances` | int(10) | YES |
| `CC RT Acceptances` | int(10) | YES |
| `SP RT Acceptances` | int(10) | YES |
| `RT Submissions PY` | int(10) | YES |
| `IC RT Submissions PY` | int(10) | YES |
| `CC RT Submissions PY` | int(10) | YES |
| `SP RT Submissions PY` | int(10) | YES |
| `EBM RT Submissions PY` | int(10) | YES |
| `RT Acceptances PY` | int(10) | YES |
| `IC RT Acceptances PY` | int(10) | YES |
| `CC RT Acceptances PY` | int(10) | YES |
| `SP RT Acceptances PY` | int(10) | YES |
| `RT Submissions PY Full` | int(10) | YES |
| `IC RT Submissions PY Full` | int(10) | YES |
| `CC RT Submissions PY Full` | int(10) | YES |
| `SP RT Submissions PY Full` | int(10) | YES |
| `EBM RT Submissions PY Full` | int(10) | YES |
| `RT Acceptances PY Full` | int(10) | YES |
| `IC RT Acceptances PY Full` | int(10) | YES |
| `CC RT Acceptances PY Full` | int(10) | YES |
| `SP RT Acceptances PY Full` | int(10) | YES |
| `SP Submissions` | int(10) | YES |
| `Submissions` | int(10) | YES |
| `EBM Submissions` | int(10) | YES |
| `REV Submissions` | int(10) | YES |
| `EBM + REV Submissions` | int(10) | YES |
| `EBM SP Submissions` | int(10) | YES |
| `CC Submissions` | int(10) | YES |
| `Acceptances` | int(10) | YES |
| `EBM Acceptances` | int(10) | YES |
| `REV Acceptances` | int(10) | YES |
| `EBM + REV Acceptances` | int(10) | YES |
| `SP Acceptances` | int(10) | YES |
| `SP Submissions PY` | int(10) | YES |
| `Submissions PY` | int(10) | YES |
| `EBM Submissions PY` | int(10) | YES |
| `REV Submissions PY` | int(10) | YES |
| `EBM + REV Submissions PY` | int(10) | YES |
| `EBM SP Submissions PY` | int(10) | YES |
| `CC Submissions PY` | int(10) | YES |
| `Acceptances PY` | int(10) | YES |
| `EBM Acceptances PY` | int(10) | YES |
| `REV Acceptances PY` | int(10) | YES |
| `EBM + REV Acceptances PY` | int(10) | YES |
| `SP Acceptances PY` | int(10) | YES |
| `Nb Days Accepted PY` | decimal(38) | YES |
| `SP Submissions PY Full` | int(10) | YES |
| `Submissions PY Full` | int(10) | YES |
| `EBM Submissions PY Full` | int(10) | YES |
| `REV Submissions PY Full` | int(10) | YES |
| `EBM + REV Submissions PY Full` | int(10) | YES |
| `EBM SP Submissions PY Full` | int(10) | YES |
| `CC Submissions PY Full` | int(10) | YES |
| `Acceptances PY Full` | int(10) | YES |
| `EBM Acceptances PY Full` | int(10) | YES |
| `REV Acceptances PY Full` | int(10) | YES |
| `EBM + REV Acceptances PY Full` | int(10) | YES |
| `SP Acceptances PY Full` | int(10) | YES |
| `Nb Days Accepted PY Full` | decimal(38) | YES |
| `Submitted Articles Target` | float(53) | YES |
| `Submitted Spontaneous Articles Target` | float(53) | YES |
| `Accepted Articles Target` | float(53) | YES |
| `Submitted Research Topic Articles Target` | float(53) | YES |
| `Posted Research Topics Target` | float(53) | YES |
| `RT Accepted Articles Target` | float(53) | YES |
| `Reviewable Submissions Target` | float(53) | YES |
| `Reviewable RT Submissions Target` | float(53) | YES |
| `Reviewable RT IC Submissions Target` | float(53) | YES |
| `Reviewable Submissions by EBM/REV Target` | float(53) | YES |
| `Reviewable Submissions by return authors Target` | float(53) | YES |

### JournalSegment_Temp

| Column | Type | Nullable |
|---|---|---|
| `Journal` | nvarchar(100) | NO |
| `Segment` | nvarchar(50) | NO |

### KPIChartsDataSource

| Column | Type | Nullable |
|---|---|---|
| `Element_Type` | int(10) | NO |
| `Element ID` | bigint(19) | YES |
| `Original Element ID` | bigint(19) | YES |
| `SpaceId` | int(10) | YES |
| `Space` | nvarchar(200) | YES |
| `Is Frontiers ?` | varchar(9) | NO |
| `Element Name` | nvarchar(400) | YES |
| `Element Email` | nvarchar(150) | YES |
| `UserIsDeleted` | bit | YES |
| `Element Status ID` | int(10) | YES |
| `Element Title` | nvarchar | YES |
| `Article Type` | nvarchar(50) | YES |
| `Is Element from EBM` | bit | YES |
| `Element Role ID` | int(10) | YES |
| `Element Role` | nvarchar(50) | YES |
| `Author Email` | nvarchar(100) | YES |
| `Element Highest Role ID` | nvarchar(10) | YES |
| `Element Highest Role` | nvarchar(50) | YES |
| `Element Highest Role ID ART` | nvarchar(10) | YES |
| `Element Highest Role ART` | nvarchar(52) | YES |
| `Is Element COVID Related ?` | bit | YES |
| `Is Element from Return Author ?` | bit | YES |
| `Is Element from Return Author CA?` | bit | YES |
| `Is Element from Return Author SA?` | bit | YES |
| `Is Element from Return Author EBM?` | bit | YES |
| `Is Element from Return Author RT?` | bit | YES |
| `Journal Launch Date` | datetime | YES |
| `Journal Maturity` | nvarchar(50) | YES |
| `Journal_Maturity_2` | varchar(24) | YES |
| `Journal_Maturity_3` | varchar(24) | YES |
| `Journal Impact Factor Bin` | nvarchar(50) | YES |
| `Program` | nvarchar(50) | YES |
| `Field` | nvarchar(150) | YES |
| `Journal` | nvarchar(150) | YES |
| `Section` | nvarchar(100) | YES |
| `Journal Responsible` | nvarchar(100) | YES |
| `Program Responsible` | nvarchar(100) | YES |
| `IsResearchTopic` | bit | YES |
| `IsDeleted` | bit | YES |
| `IsAccepted` | bit | YES |
| `IsSubmitted` | bit | YES |
| `IsPublished` | bit | YES |
| `IsRejected` | bit | YES |
| `Is Article from Invited Contributor ?` | bit | YES |
| `Is Article from Confirmed Contributor ?` | bit | YES |
| `Rejection Reason Label` | nvarchar(100) | YES |
| `Rejecter Role` | nvarchar(10) | YES |
| `DeskAcceptedArticle` | bit | YES |
| `TimeOnlinetoSubmitted` | nvarchar(20) | YES |
| `TimeFirstSubmissionDeadlinetoSubmitted` | nvarchar(20) | YES |
| `StageatDecision` | nvarchar(100) | YES |
| `ArticleStage` | nvarchar(30) | YES |
| `IsRTClosed` | bit | YES |
| `IsRTCompleted` | bit | YES |
| `IsRTDeleted` | bit | YES |
| `IsRTOnline` | bit | YES |
| `Is RT COVID Related?` | bit | YES |
| `Part Of ACP` | bit | YES |
| `Organization` | nvarchar(200) | YES |
| `OrganizationsHighestRankWoS` | nvarchar(200) | YES |
| `OrganizationsHighestRankWoSValue` | int(10) | YES |
| `Organization Rejection Rate Bin <1 Decision` | nvarchar(50) | YES |
| `Organization Rejection Rate Bin <3 Decisions` | nvarchar(50) | YES |
| `Organization Rejection Rate Bin <10 Decisions` | nvarchar(50) | YES |
| `Country` | nvarchar(100) | YES |
| `Country Rejection Rate` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Regions 5 Bins` | nvarchar(100) | YES |
| `Regions 8 Bins` | nvarchar(100) | YES |
| `Regions 8 Bins - China` | nvarchar(100) | YES |
| `Regions 3 Focus` | nvarchar(100) | YES |
| `Regions 13 Bins` | nvarchar(100) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `FrontiersViews` | int(10) | YES |
| `FrontiersDownloads` | int(10) | YES |
| `FrontiersCitations` | int(10) | YES |
| `ThisYear` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `Activity Bins` | nvarchar(20) | YES |
| `Connectivity Bins` | nvarchar(20) | YES |
| `Frontiers Bins` | varchar(20) | YES |
| `H Index Bins` | varchar(20) | YES |
| `Influence Bins` | nvarchar(20) | YES |
| `Productivity Bins` | nvarchar(20) | YES |
| `Article Service Level Bins` | nvarchar(3) | YES |
| `Overall Quality Rating Bins` | nvarchar(20) | YES |
| `Review_Time` | nvarchar(20) | YES |
| `Initial Validation` | nvarchar(20) | YES |
| `Editorial_Assignment` | nvarchar(20) | YES |
| `AE_Assignment` | nvarchar(20) | YES |
| `RE_Assignment` | nvarchar(20) | YES |
| `Independent_Review` | nvarchar(20) | YES |
| `Interactive_Review` | nvarchar(20) | YES |
| `Final_Validation` | nvarchar(20) | YES |
| `SubmissionsPassedDeskReview` | nvarchar(20) | YES |
| `Time to Assign Any AE` | nvarchar(20) | YES |
| `Time to Assign Preferred AE` | nvarchar(20) | YES |
| `Time to Assign AE Manually` | nvarchar(20) | YES |
| `Time to Assign TE` | nvarchar(20) | YES |
| `Time to Assign any Reviewer` | nvarchar(20) | YES |
| `Time to Assign Required Reviewer` | nvarchar(20) | YES |
| `Time to Assign RE` | nvarchar(20) | YES |
| `Time to Assign REV` | nvarchar(20) | YES |
| `Time to Submit required IRRs` | nvarchar(20) | YES |
| `Time to Submit IRR by RE` | nvarchar(20) | YES |
| `Time Submit IRR by a Reviewer` | nvarchar(20) | YES |
| `Time Submit Any IRR` | nvarchar(20) | YES |
| `Time to First reply of the Author` | nvarchar(20) | YES |
| `Time to Last Author Reply` | nvarchar(20) | YES |
| `Time to First Reviewer Reply` | nvarchar(20) | YES |
| `Time to Last RE Reply` | nvarchar(20) | YES |
| `Time to Send First REV Invitation` | nvarchar(20) | YES |
| `Time to Assign any Reviewer Static` | nvarchar(20) | YES |
| `Time to Assign Required Reviewer Static` | nvarchar(20) | YES |
| `Returning Author Last Submission Bin` | nvarchar(20) | YES |
| `Returning Author Last Acceptance Bin` | nvarchar(20) | YES |
| `Returning Author Last Rejection Bin` | nvarchar(20) | YES |
| `Returning Author Last Decision Bin` | nvarchar(20) | YES |
| `Returning Author Last Publication Bin` | nvarchar(20) | YES |
| `Returning Author Previous Decision Time Bin` | nvarchar(20) | YES |
| `Emails_Review_Process_Bins` | varchar(30) | YES |
| `GrossRevenue_USD` | numeric(38) | YES |
| `NetRevenue_USD` | numeric(38) | YES |
| `DiscountType` | nvarchar(255) | YES |
| `DiscountCategory` | nvarchar(255) | YES |
| `DiscountAmount_USD` | float(53) | YES |
| `Discount Status` | varchar(8) | NO |
| `Invitation Source` | nvarchar(100) | YES |
| `Articles Submitted Bins` | nvarchar(50) | YES |
| `Articles Accepted Bins` | nvarchar(50) | YES |
| `Time Since Last Submitted Article Bins` | nvarchar(50) | YES |
| `Time Since Last Accepted Article Bins` | nvarchar(50) | YES |
| `Time Since Last Rejected Article Bins` | nvarchar(50) | YES |
| `RTs Hosted Bins` | nvarchar(50) | YES |
| `Time Since Last Topic Hosted Bins` | nvarchar(50) | YES |
| `# Articles Edited Bins` | nvarchar(50) | YES |
| `Time Since Last Editing Assignment Bins` | nvarchar(50) | YES |
| `# Articles Reviewed Bins` | nvarchar(50) | YES |
| `Time Since Last REV Assignment Bins` | nvarchar(50) | YES |
| `# Articles Reviewed or Edited Bins` | nvarchar(50) | YES |
| `Time Since Last REV or Editing Assignment Bins` | nvarchar(50) | YES |
| `Article Stage Detail` | nvarchar(50) | YES |
| `Article Rejected at Stage (Non Static)` | varchar(45) | NO |
| `Article Rejected at Stage (Static)` | nvarchar(50) | YES |
| `Submission Status` | varchar(24) | NO |
| `Is Faas Transfer` | varchar(17) | NO |
| `Has Transfer Opportunity` | bit | YES |
| `Review Report Rating Bins` | varchar(7) | YES |
| `Regions 8 Bins Priority Contact` | nvarchar(50) | YES |
| `Regions 13 Bins Priority Contact` | nvarchar(50) | YES |
| `JournalSegment` | nvarchar(50) | YES |
| `JournalSegment Previous` | nvarchar(50) | YES |
| `Date_Value` | datetime | YES |
| `Type_Of_Date` | nvarchar(128) | YES |

### QueueTime

| Column | Type | Nullable |
|---|---|---|
| `PK_Date` | datetime | NO |
| `NbOfSubmissions` | int(10) | YES |
| `NbOfManuscripts` | int(10) | YES |
| `Cumulative` | int(10) | YES |
| `NbOfDays` | decimal(9) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### SectionSegment_Temp

| Column | Type | Nullable |
|---|---|---|
| `Section` | nvarchar(100) | NO |
| `Segment` | nvarchar(50) | NO |

### StgSuggestionsTracking

| Column | Type | Nullable |
|---|---|---|
| `Id` | int(10) | NO |
| `RequestDate` | datetime2 | NO |
| `ApplicationName` | nvarchar(50) | NO |
| `ApiId` | nvarchar(50) | NO |
| `AlgorithmVersion` | smallint(5) | YES |
| `EntityId` | nvarchar(50) | YES |
| `KeyTerms` | nvarchar | YES |
| `PublicationScoreThreshold` | float(53) | YES |
| `MaxScoredPublications` | int(10) | YES |
| `ScoreBoost` | bit | YES |
| `ExcludeAuthors` | bit | YES |
| `LimitToRole` | nvarchar(20) | YES |
| `MinPublications` | int(10) | YES |
| `MaxPublications` | int(10) | YES |
| `MinYearsOfActivity` | int(10) | YES |
| `MaxYearsOfActivity` | int(10) | YES |
| `MinHIndex` | int(10) | YES |
| `MaxHIndex` | int(10) | YES |
| `IncludePeopleSource` | nvarchar(20) | YES |
| `IncludePeople` | nvarchar | YES |
| `ExcludePeopleSource` | nvarchar(20) | YES |
| `ExcludePeople` | nvarchar | YES |
| `ExcludeWatchlistType` | nvarchar(20) | YES |
| `ExcludeWatchlist` | nvarchar | YES |
| `PublishedAfter` | datetime | YES |
| `LastUpdateBy` | varchar(255) | YES |
| `LastUpdateDate` | smalldatetime | YES |

### StgSuggestionsTrackingPeople

| Column | Type | Nullable |
|---|---|---|
| `TrackingId` | int(10) | NO |
| `Position` | int(10) | NO |
| `FullName` | nvarchar(500) | YES |
| `Email` | nvarchar(500) | YES |
| `MatchedPubs` | nvarchar | YES |
| `NessieLink` | nvarchar | YES |
| `LastUpdateBy` | varchar(255) | YES |
| `LastUpdateDate` | smalldatetime | YES |

### SuggestionsTracking

| Column | Type | Nullable |
|---|---|---|
| `Id` | int(10) | NO |
| `RequestDate` | datetime2 | NO |
| `ApplicationName` | nvarchar(50) | NO |
| `ApiId` | nvarchar(50) | NO |
| `AlgorithmVersion` | smallint(5) | YES |
| `EntityId` | nvarchar(50) | YES |
| `KeyTerms` | nvarchar | YES |
| `PublicationScoreThreshold` | float(53) | YES |
| `MaxScoredPublications` | int(10) | YES |
| `ScoreBoost` | bit | YES |
| `ExcludeAuthors` | bit | YES |
| `LimitToRole` | nvarchar(20) | YES |
| `MinPublications` | int(10) | YES |
| `MaxPublications` | int(10) | YES |
| `MinYearsOfActivity` | int(10) | YES |
| `MaxYearsOfActivity` | int(10) | YES |
| `MinHIndex` | int(10) | YES |
| `MaxHIndex` | int(10) | YES |
| `IncludePeopleSource` | nvarchar(20) | YES |
| `IncludePeople` | nvarchar | YES |
| `ExcludePeopleSource` | nvarchar(20) | YES |
| `ExcludePeople` | nvarchar | YES |
| `ExcludeWatchlistType` | nvarchar(20) | YES |
| `ExcludeWatchlist` | nvarchar | YES |
| `PublishedAfter` | datetime | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### SuggestionsTrackingPeople

| Column | Type | Nullable |
|---|---|---|
| `Id` | int(10) | NO |
| `TrackingId` | int(10) | NO |
| `Position` | int(10) | NO |
| `FullName` | nvarchar(500) | YES |
| `Email` | nvarchar(500) | YES |
| `MatchedPubs` | nvarchar | YES |
| `NessieLink` | nvarchar | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

## [FrontiersReports].[Common]


### MasterDataFlatFeeAgreements

| Column | Type | Nullable |
|---|---|---|
| `InstitutionId_Original` | smallint(5) | NO |
| `AgreementId` | nvarchar(50) | NO |
| `InstitutionId` | bigint(19) | NO |
| `OrganizationId` | int(10) | NO |
| `Organization` | nvarchar(100) | NO |
| `ConsortiumInstitutionId` | bigint(19) | YES |
| `ConsortiumInstitution` | nvarchar(50) | NO |
| `StartDate` | date | NO |
| `EndDate` | date | NO |
| `DealAmount` | float(53) | NO |
| `IsSplitByConsortium` | tinyint(3) | YES |
| `Currency` | nvarchar(50) | NO |

## [FrontiersReports].[EOf]


### Review_BlacklistPeople

| Column | Type | Nullable |
|---|---|---|
| `BlacklistPeopleId` | int(10) | NO |
| `UserId` | int(10) | YES |
| `BlacklistPeopleCategoryId` | int(10) | YES |
| `Name` | nvarchar(200) | YES |
| `Email` | nvarchar(200) | YES |
| `Reason` | nvarchar | YES |

### Review_BlacklistPeopleCategory

| Column | Type | Nullable |
|---|---|---|
| `BlacklistPeopleCategoryId` | int(10) | NO |
| `BlacklistPeopleCategory` | nvarchar(100) | YES |

### Review_TitleChecklistWords

| Column | Type | Nullable |
|---|---|---|
| `TitleChecklistWordsId` | int(10) | NO |
| `Word` | nvarchar(200) | YES |

## [FrontiersReports].[ETLStaging]


### DimMeasure_Base

| Column | Type | Nullable |
|---|---|---|
| `MeasureId` | int(10) | NO |
| `MeasureSourceId` | nvarchar(50) | NO |
| `MeasureName` | nvarchar(100) | NO |
| `MeasureDescription` | nvarchar(255) | YES |
| `MeasureType` | nvarchar(50) | NO |
| `AggregationType` | nvarchar(50) | YES |
| `DataType` | nvarchar(50) | YES |
| `BusinessEntity` | nvarchar(50) | YES |
| `MeasureGoal` | nvarchar(50) | YES |
| `MeasureCategoryId` | int(10) | YES |
| `MeasureGroupId` | int(10) | YES |
| `PriorityMeasure` | bit | YES |
| `IsActive` | bit | YES |
| `ShowDetailData` | bit | YES |
| `DenominatorDescription` | nvarchar(255) | YES |
| `NumeratorDescription` | nvarchar(255) | YES |
| `ThresholdType` | nvarchar(50) | YES |
| `ThresholdGreen` | numeric(18) | YES |
| `ThresholdAmber` | numeric(18) | YES |
| `ThresholdRed` | numeric(18) | YES |
| `AggregationPeriod` | nvarchar(50) | YES |
| `DateType` | nvarchar(50) | YES |
| `Owner` | nvarchar(255) | YES |
| `ReportingLead` | nvarchar(255) | YES |
| `DuplicateMeasureSourceId` | int(10) | YES |
| `CreateDate` | datetime2 | NO |
| `CreatedBy` | nvarchar(255) | NO |
| `UpdateDate` | datetime2 | YES |
| `UpdatedBy` | nvarchar(255) | YES |

### DimScenario_Base

| Column | Type | Nullable |
|---|---|---|
| `ScenarioId` | int(10) | NO |
| `ScenarioName` | nvarchar(50) | NO |
| `ScenarioDescription` | nvarchar(255) | NO |
| `ScenarioType` | nvarchar(50) | NO |
| `CreateDate` | datetime2 | NO |
| `CreatedBy` | nvarchar(255) | NO |
| `UpdateDate` | datetime2 | YES |
| `UpdatedBy` | nvarchar(255) | YES |

### FactManualKPI_Base

| Column | Type | Nullable |
|---|---|---|
| `MeasureId` | int(10) | NO |
| `ScenarioId` | int(10) | NO |
| `Year` | int(10) | NO |
| `Jan` | numeric(18) | YES |
| `Feb` | numeric(18) | YES |
| `Mar` | numeric(18) | YES |
| `Apr` | numeric(18) | YES |
| `May` | numeric(18) | YES |
| `Jun` | numeric(18) | YES |
| `Jul` | numeric(18) | YES |
| `Aug` | numeric(18) | YES |
| `Sep` | numeric(18) | YES |
| `Oct` | numeric(18) | YES |
| `Nov` | numeric(18) | YES |
| `Dec` | numeric(18) | YES |
| `CreateDate` | datetime2 | NO |
| `CreatedBy` | nvarchar(255) | NO |
| `UpdateDate` | datetime2 | YES |
| `UpdatedBy` | nvarchar(255) | YES |

### MeasureCategory

| Column | Type | Nullable |
|---|---|---|
| `MeasureCategoryId` | int(10) | NO |
| `MeasureCategoryName` | nvarchar(50) | NO |
| `MeasureCategoryDescription` | nvarchar(255) | NO |
| `CreateDate` | datetime2 | NO |
| `CreatedBy` | nvarchar(255) | NO |
| `UpdateDate` | datetime2 | YES |
| `UpdatedBy` | nvarchar(255) | YES |

### MeasureGroup

| Column | Type | Nullable |
|---|---|---|
| `MeasureCategoryId` | int(10) | NO |
| `MeasureGroupId` | int(10) | NO |
| `MeasureGroupName` | nvarchar(50) | NO |
| `MeasureGroupDescription` | nvarchar(255) | YES |
| `CreateDate` | datetime2 | NO |
| `CreatedBy` | nvarchar(255) | NO |
| `UpdateDate` | datetime2 | YES |
| `UpdatedBy` | nvarchar(255) | YES |

## [FrontiersReports].[JournalDashboard]


### ActualValues.@SnapshotSummary

| Column | Type | Nullable |
|---|---|---|
| `UpdateDate` | datetime | NO |
| `DataMartsUpdateDate` | datetime | NO |

### ActualValues.Monthly

| Column | Type | Nullable |
|---|---|---|
| `Grouping` | varchar(3) | NO |
| `TaxonomyId` | bigint(19) | NO |
| `MeasureId` | int(10) | NO |
| `Year` | int(10) | NO |
| `Month` | int(10) | NO |
| `Value` | int(10) | YES |

### ActualValues.YTD

| Column | Type | Nullable |
|---|---|---|
| `Grouping` | varchar(3) | NO |
| `TaxonomyId` | bigint(19) | NO |
| `MeasureId` | int(10) | NO |
| `ValueLastYear` | int(10) | YES |
| `YTDValue` | int(10) | YES |
| `YTDValueLastYear` | int(10) | YES |
| `YOYGrowth` | decimal(10) | YES |

### IndividualTargets_Actuals

| Column | Type | Nullable |
|---|---|---|
| `EmployeeId` | nvarchar(150) | YES |
| `JobProfile` | nvarchar(150) | YES |
| `JobProfileId` | int(10) | YES |
| `EmployeeLoopUserId` | bigint(19) | YES |
| `WorkdayEmployeeName` | nvarchar(1000) | YES |
| `IsUnclaimedValue?` | bit | YES |
| `Measure` | nvarchar(150) | YES |
| `MeasureId` | int(10) | NO |
| `Journal` | nvarchar(1000) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `Domain` | nvarchar(150) | YES |
| `Field` | nvarchar(150) | YES |
| `Program` | nvarchar(150) | YES |
| `Journal Manager` | nvarchar(1000) | YES |
| `Program Manager` | nvarchar(1000) | YES |
| `Month` | int(10) | YES |
| `Year` | int(10) | YES |
| `IndividualTarget` | int(10) | YES |
| `Actual` | int(10) | YES |

### KPIMeasures_Enrichment_DataSource

| Column | Type | Nullable |
|---|---|---|
| `JournalTaxonomyId` | bigint(19) | YES |
| `Region 8 Bins` | nvarchar(50) | YES |
| `Date` | date | YES |
| `Days In Month` | int(10) | YES |
| `Domain` | nvarchar(50) | YES |
| `Field` | nvarchar(150) | YES |
| `Journal` | nvarchar(150) | YES |
| `Program` | nvarchar(50) | YES |
| `Specialty` | nvarchar(150) | YES |
| `Journal Responsible` | nvarchar(100) | YES |
| `Program Responsible` | nvarchar(100) | YES |
| `Unique EBMs` | int(10) | YES |
| `Associate Editors` | int(10) | YES |
| `Review Editors` | int(10) | YES |
| `EBM or Reviewers` | int(10) | YES |
| `Reviewers` | int(10) | YES |
| `EBM who Edited` | int(10) | YES |
| `EBM who Reviewed` | int(10) | YES |
| `Potential Contributors` | int(10) | YES |
| `Invited Contributors` | int(10) | YES |
| `Confirmed Contributors` | int(10) | YES |
| `Research Topics by Online Date` | int(10) | YES |
| `Research Topics by First Deadline Date` | int(10) | YES |
| `Research Topics by Public Deadline Date` | int(10) | YES |
| `Research Topics by Max Deadline Date` | int(10) | YES |
| `EBM RT Posted` | int(10) | YES |
| `RT Articles Submitted` | int(10) | YES |
| `IC RT Articles Submitted` | int(10) | YES |
| `CC RT Articles Submitted` | int(10) | YES |
| `SP RT Articles Submitted` | int(10) | YES |
| `EBM RT Articles Submitted` | int(10) | YES |
| `IC RT EBM Articles Submitted` | int(10) | YES |
| `SP RT EBM Articles Submitted` | int(10) | YES |
| `IC RT REV Articles Submitted` | int(10) | YES |
| `SP REV Articles Submitted` | int(10) | YES |
| `SP RT REV Articles Submitted` | int(10) | YES |
| `RT Articles Accepted` | int(10) | YES |
| `IC RT Articles Accepted` | int(10) | YES |
| `CC RT Articles Accepted` | int(10) | YES |
| `SP RT Articles Accepted` | int(10) | YES |
| `IC RT EBM Articles Accepted` | int(10) | YES |
| `SP RT EBM Articles Accepted` | int(10) | YES |
| `IC RT REV Articles Accepted` | int(10) | YES |
| `SP REV Articles Accepted` | int(10) | YES |
| `SP RT REV Articles Accepted` | int(10) | YES |
| `RT Articles Rejected` | int(10) | YES |
| `IC RT Articles Rejected` | int(10) | YES |
| `CC RT Articles Rejected` | int(10) | YES |
| `SP RT Articles Rejected` | int(10) | YES |
| `IC RT EBM Articles Rejected` | int(10) | YES |
| `SP RT EBM Articles Rejected` | int(10) | YES |
| `IC RT REV Articles Rejected` | int(10) | YES |
| `SP REV Articles Rejected` | int(10) | YES |
| `SP RT REV Articles Rejected` | int(10) | YES |
| `RT Articles Decided` | int(10) | YES |
| `IC RT Articles Decided` | int(10) | YES |
| `CC RT Articles Decided` | int(10) | YES |
| `SP RT Articles Decided` | int(10) | YES |
| `SP Articles Submitted` | int(10) | YES |
| `Articles Submitted` | int(10) | YES |
| `EBM Articles Submitted` | int(10) | YES |
| `REV Articles Submitted` | int(10) | YES |
| `EBM + REV Articles Submitted` | int(10) | YES |
| `EBM SP Articles Submitted` | int(10) | YES |
| `Articles Accepted` | int(10) | YES |
| `SP Articles Accepted` | int(10) | YES |
| `EBM Articles Accepted` | int(10) | YES |
| `REV Articles Accepted` | int(10) | YES |
| `EBM + REV Articles Accepted` | int(10) | YES |
| `SP EBM Articles Accepted` | int(10) | YES |
| `Articles Rejected` | int(10) | YES |
| `SP Articles Rejected` | int(10) | YES |
| `EBM Articles Rejected` | int(10) | YES |
| `REV Articles Rejected` | int(10) | YES |
| `EBM + REV Articles Rejected` | int(10) | YES |
| `SP EBM Articles Rejected` | int(10) | YES |
| `Articles Decided` | int(10) | YES |
| `Nb Days Accepted` | decimal(18) | YES |
| `Nb Days Rejected` | decimal(18) | YES |
| `Potential RT Editors` | int(10) | YES |
| `Campaign Members Invited` | int(10) | YES |
| `MQL Campaign Members Invited` | int(10) | YES |
| `SQL RT Opportunities` | int(10) | YES |
| `Interested RT Opportunities` | int(10) | YES |
| `Commitment RT Opportunities` | int(10) | YES |
| `Final Stage RT Opportunities` | int(10) | YES |
| `In DEO RT Opportunities` | int(10) | YES |

### ResearchTopicsExceptions

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicId` | int(10) | NO |
| `IsException` | bit | NO |
| `LastUpdateDate` | datetime | NO |

## [FrontiersReports].[PM]


### DomainFlag

| Column | Type | Nullable |
|---|---|---|
| `Domain` | nvarchar(2000) | YES |

### RobotsTerms

| Column | Type | Nullable |
|---|---|---|
| `Term` | nvarchar(2000) | YES |

## [FrontiersReports].[Reporting]


### DateTaxonomy

| Column | Type | Nullable |
|---|---|---|
| `LastDayOfMonth` | date | NO |
| `DateId` | int(10) | NO |
| `JournalTaxonomyId` | bigint(19) | NO |

### DateTaxonomySection

| Column | Type | Nullable |
|---|---|---|
| `LastDayOfMonth` | date | NO |
| `DateId` | int(10) | NO |
| `JournalTaxonomyId` | bigint(19) | NO |
| `TaxonomyId` | bigint(19) | NO |

### DimDate_Base

| Column | Type | Nullable |
|---|---|---|
| `DateId` | int(10) | NO |
| `Date` | date | NO |
| `Year` | smallint(5) | NO |
| `Quarter` | smallint(5) | NO |
| `Month` | smallint(5) | NO |
| `Day` | smallint(5) | NO |
| `MonthName` | varchar(10) | NO |
| `MonthShortName` | char(3) | NO |
| `DateString` | char(10) | NO |
| `DaysInYear` | smallint(5) | NO |
| `DaysInQuarter` | tinyint(3) | NO |
| `DaysInMonth` | tinyint(3) | NO |

### DimMeasure_Base

| Column | Type | Nullable |
|---|---|---|
| `MeasureId` | int(10) | NO |
| `MeasureSourceId` | nvarchar(50) | NO |
| `MeasureName` | nvarchar(100) | NO |
| `MeasureDescription` | nvarchar(255) | YES |
| `MeasureType` | nvarchar(50) | NO |
| `AggregationType` | nvarchar(50) | YES |
| `DataType` | nvarchar(50) | YES |
| `BusinessEntity` | nvarchar(50) | YES |
| `MeasureGoal` | nvarchar(50) | YES |
| `MeasureCategoryId` | int(10) | YES |
| `MeasureGroupId` | int(10) | YES |
| `PriorityMeasure` | bit | YES |
| `IsActive` | bit | YES |
| `ShowDetailData` | bit | YES |
| `DenominatorDescription` | nvarchar(255) | YES |
| `NumeratorDescription` | nvarchar(255) | YES |
| `ThresholdType` | nvarchar(50) | YES |
| `ThresholdGreen` | numeric(18) | YES |
| `ThresholdAmber` | numeric(18) | YES |
| `ThresholdRed` | numeric(18) | YES |
| `AggregationPeriod` | nvarchar(50) | YES |
| `DateType` | nvarchar(50) | YES |
| `Owner` | nvarchar(255) | YES |
| `ReportingLead` | nvarchar(255) | YES |
| `DuplicateMeasureSourceId` | int(10) | YES |
| `CreateDate` | datetime2 | NO |
| `CreatedBy` | nvarchar(255) | NO |
| `UpdateDate` | datetime2 | YES |
| `UpdatedBy` | nvarchar(255) | YES |

### DimScenario_Base

| Column | Type | Nullable |
|---|---|---|
| `ScenarioId` | int(10) | NO |
| `ScenarioName` | nvarchar(50) | NO |
| `ScenarioDescription` | nvarchar(255) | NO |
| `ScenarioType` | nvarchar(50) | NO |
| `CreateDate` | datetime2 | NO |
| `CreatedBy` | nvarchar(255) | NO |
| `UpdateDate` | datetime2 | YES |
| `UpdatedBy` | nvarchar(255) | YES |

### DimTaxonomySection_Base

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(100) | NO |
| `JournalId` | int(10) | NO |
| `JournalTaxonomyId` | bigint(19) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | NO |
| `Section` | nvarchar(150) | YES |
| `JournalManager` | nvarchar(100) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `ProgramManager` | nvarchar(100) | YES |
| `PortfolioId` | int(10) | YES |
| `Portfolio` | nvarchar(50) | YES |
| `PortfolioManager` | nvarchar(100) | YES |
| `SectionSegment` | nvarchar(100) | YES |
| `IsDeleted` | bit | YES |
| `CreateDate` | datetime2 | YES |
| `UpdateDate` | datetime2 | YES |

### DimTaxonomy_Base

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(100) | NO |
| `JournalId` | int(10) | NO |
| `Journal` | nvarchar(150) | YES |
| `JournalManager` | nvarchar(100) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `ProgramManager` | nvarchar(100) | YES |
| `PortfolioId` | int(10) | YES |
| `Portfolio` | nvarchar(50) | YES |
| `PortfolioManager` | nvarchar(100) | YES |
| `JournalSegment` | nvarchar(100) | YES |

### FactJournalAnalytics_Base

| Column | Type | Nullable |
|---|---|---|
| `DateID` | int(10) | NO |
| `MeasureID` | int(10) | NO |
| `ScenarioID` | int(10) | NO |
| `TaxonomyID` | bigint(19) | NO |
| `ValueNumerator` | decimal(19) | YES |
| `ValueDenominator` | decimal(19) | YES |

### FactJournalAnalytics_Drillthrough_Base

| Column | Type | Nullable |
|---|---|---|
| `MeasureID` | int(10) | NO |
| `TaxonomyID` | bigint(19) | NO |
| `DateID` | int(10) | NO |
| `EntityID` | bigint(19) | NO |
| `Value` | decimal(19) | YES |

### FactJournalAnalytics_Static

| Column | Type | Nullable |
|---|---|---|
| `DateID` | int(10) | NO |
| `MeasureID` | int(10) | NO |
| `ScenarioID` | int(10) | NO |
| `TaxonomyID` | bigint(19) | NO |
| `ValueNumerator` | decimal(19) | YES |
| `ValueDenominator` | decimal(19) | YES |

### FactManagementDashboard_Base

| Column | Type | Nullable |
|---|---|---|
| `Date` | date | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `TaxonomyID` | bigint(19) | YES |
| `MeasureID` | int(10) | NO |
| `ValueNumerator` | decimal(19) | YES |
| `ValueDenominator` | decimal(19) | YES |

### FactManualKPI_Base

| Column | Type | Nullable |
|---|---|---|
| `MeasureId` | int(10) | NO |
| `ScenarioId` | int(10) | NO |
| `Year` | int(10) | NO |
| `Jan` | numeric(18) | YES |
| `Feb` | numeric(18) | YES |
| `Mar` | numeric(18) | YES |
| `Apr` | numeric(18) | YES |
| `May` | numeric(18) | YES |
| `Jun` | numeric(18) | YES |
| `Jul` | numeric(18) | YES |
| `Aug` | numeric(18) | YES |
| `Sep` | numeric(18) | YES |
| `Oct` | numeric(18) | YES |
| `Nov` | numeric(18) | YES |
| `Dec` | numeric(18) | YES |
| `CreateDate` | datetime2 | NO |
| `CreatedBy` | nvarchar(255) | NO |
| `UpdateDate` | datetime2 | YES |
| `UpdatedBy` | nvarchar(255) | YES |

### FactRTOwners_Base

| Column | Type | Nullable |
|---|---|---|
| `Date` | date | YES |
| `DateType` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `TaxonomyID` | bigint(19) | YES |
| `MeasureId` | int(10) | NO |
| `RTOwner_UserId` | bigint(19) | YES |
| `RTOwner_WorkdayId` | nvarchar(100) | YES |
| `ResearchTopicId` | bigint(19) | YES |
| `ArticleId` | bigint(19) | YES |
| `ValueNumerator` | decimal(19) | YES |
| `ValueDenominator` | decimal(19) | YES |

### FactSectionAnalytics_Base

| Column | Type | Nullable |
|---|---|---|
| `DateID` | int(10) | NO |
| `MeasureID` | int(10) | NO |
| `ScenarioID` | int(10) | NO |
| `TaxonomyID` | bigint(19) | NO |
| `ValueNumerator` | decimal(19) | YES |
| `ValueDenominator` | decimal(19) | YES |
| `IsDeleted` | bit | YES |
| `CreateDate` | datetime2 | YES |
| `UpdateDate` | datetime2 | YES |

### FactSectionAnalytics_Drillthrough_Base

| Column | Type | Nullable |
|---|---|---|
| `MeasureID` | int(10) | NO |
| `TaxonomyID` | bigint(19) | NO |
| `DateID` | int(10) | NO |
| `EntityID` | bigint(19) | NO |
| `Value` | decimal(19) | YES |

### MeasureCategory

| Column | Type | Nullable |
|---|---|---|
| `MeasureCategoryId` | int(10) | NO |
| `MeasureCategoryName` | nvarchar(50) | NO |
| `MeasureCategoryDescription` | nvarchar(255) | NO |
| `CreateDate` | datetime2 | NO |
| `CreatedBy` | nvarchar(255) | NO |
| `UpdateDate` | datetime2 | YES |
| `UpdatedBy` | nvarchar(255) | YES |

### MeasureGroup

| Column | Type | Nullable |
|---|---|---|
| `MeasureCategoryId` | int(10) | NO |
| `MeasureGroupId` | int(10) | NO |
| `MeasureGroupName` | nvarchar(50) | NO |
| `MeasureGroupDescription` | nvarchar(255) | YES |
| `CreateDate` | datetime2 | NO |
| `CreatedBy` | nvarchar(255) | NO |
| `UpdateDate` | datetime2 | YES |
| `UpdatedBy` | nvarchar(255) | YES |

## [FrontiersReports].[SubmissionsReviewDashboard]


### Articles_StagesHistory

| Column | Type | Nullable |
|---|---|---|
| `StageInPeriod` | varchar(17) | NO |
| `TotalArticles` | int(10) | NO |
| `ArticleId` | int(10) | NO |
| `Domain` | nvarchar(50) | YES |
| `Program` | nvarchar(100) | YES |
| `Journal` | nvarchar(2000) | YES |
| `Field` | nvarchar(250) | YES |
| `Specialty` | nvarchar(250) | YES |
| `Section` | nvarchar(2000) | YES |
| `Stage` | nvarchar(150) | YES |
| `IsDeleted` | bit | YES |
| `IsResearchTopic` | int(10) | NO |
| `StageDate` | datetime | YES |

### Articles_StagesHistoryTotals

| Column | Type | Nullable |
|---|---|---|
| `StageInPeriod` | varchar(15) | NO |
| `TotalArticles` | int(10) | YES |
| `Domain` | nvarchar(50) | YES |
| `Program` | nvarchar(100) | YES |
| `Journal` | nvarchar(2000) | YES |
| `Field` | nvarchar(250) | YES |
| `Specialty` | nvarchar(250) | YES |
| `Section` | nvarchar(2000) | YES |
| `Stage` | varchar(21) | NO |
| `IsDeleted` | varchar(1) | NO |
| `IsResearchTopic` | int(10) | NO |
| `StageDate` | date | YES |

## [FrontiersReports].[dbo]


### __RefactorLog

| Column | Type | Nullable |
|---|---|---|
| `OperationKey` | uniqueidentifier | NO |

### sysdiagrams

| Column | Type | Nullable |
|---|---|---|
| `name` | nvarchar(128) | NO |
| `principal_id` | int(10) | NO |
| `diagram_id` | int(10) | NO |
| `version` | int(10) | YES |
| `definition` | varbinary | YES |

## [ReportingDataMart].[Admin]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `PrimaryKey` | nvarchar(256) | YES |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `PreviousRowVersion` | binary(8) | YES |
| `CurrentRowVersion` | binary(8) | YES |

### CDC_Objects

| Column | Type | Nullable |
|---|---|---|
| `Schema` | nvarchar(128) | NO |
| `Table` | nvarchar(128) | NO |

### Configurations

| Column | Type | Nullable |
|---|---|---|
| `Id` | int(10) | NO |
| `ETLProjectId` | int(10) | NO |
| `SourceObject` | nvarchar(150) | NO |
| `DestinationObject` | nvarchar(150) | YES |
| `PrimaryKey` | nvarchar(128) | YES |
| `LoadType` | int(10) | YES |
| `DropAddConstraint` | bit | YES |
| `DropAddIndex` | bit | YES |

### ConfigurationsIndexes

| Column | Type | Nullable |
|---|---|---|
| `Id` | int(10) | NO |
| `ETLProjectId` | int(10) | NO |
| `DestinationObject` | nvarchar(150) | NO |
| `IndexName` | nvarchar(150) | NO |
| `IndexType` | nvarchar(50) | NO |
| `IndexColumns` | nvarchar(300) | NO |
| `IndexIncludeColumns` | nvarchar(300) | YES |

### Constraints

| Column | Type | Nullable |
|---|---|---|
| `ConstraintName` | nvarchar(255) | NO |
| `ConstraintType` | nvarchar(2) | NO |
| `Table` | nvarchar(255) | YES |
| `Columns` | nvarchar(2000) | YES |
| `ReferenceTable` | nvarchar(255) | YES |
| `Reference` | nvarchar(2000) | YES |
| `Configurations` | nvarchar(7) | NO |
| `IsActive` | bit | YES |

### DataLineage

| Column | Type | Nullable |
|---|---|---|
| `LineageId` | int(10) | NO |
| `UltimateParentDependencyId` | int(10) | NO |
| `Level` | smallint(5) | NO |
| `ParentDependencyId` | int(10) | NO |
| `DependencyId` | int(10) | NO |
| `DestinationDatabase` | nvarchar(128) | NO |
| `DestinationObject` | nvarchar(256) | NO |
| `DestinationPlatform` | nvarchar(128) | NO |
| `DependencyType` | nvarchar(10) | NO |
| `ETLType` | nvarchar(10) | NO |
| `ETLProject` | nvarchar(128) | NO |
| `SourceDatabase` | nvarchar(128) | NO |
| `SourceObject` | nvarchar(256) | NO |
| `SourcePlatform` | nvarchar(128) | NO |
| `CreateDate` | datetime | NO |

### Dependencies

| Column | Type | Nullable |
|---|---|---|
| `DependencyId` | int(10) | NO |
| `DestinationDatabase` | nvarchar(128) | NO |
| `DestinationObject` | nvarchar(256) | NO |
| `DestinationPlatform` | nvarchar(128) | NO |
| `DependencyType` | nvarchar(10) | NO |
| `ETLType` | nvarchar(10) | NO |
| `ETLProject` | nvarchar(128) | NO |
| `SourceDatabase` | nvarchar(128) | NO |
| `SourceObject` | nvarchar(256) | NO |
| `SourcePlatform` | nvarchar(128) | NO |

### ObjectDefinition

| Column | Type | Nullable |
|---|---|---|
| `OBJECT_ID` | int(10) | NO |
| `DATA_DOMAIN` | nvarchar(255) | YES |
| `OBJECT_NAME` | nvarchar(255) | YES |
| `OBJECT_TYPE` | nvarchar(255) | YES |
| `OBJECT_DEFINITION` | nvarchar | YES |
| `TECHNICAL_OWNER` | nvarchar(255) | YES |
| `BUSINESS_OWNER` | nvarchar(255) | YES |
| `TABLE_SCHEMA` | nvarchar(255) | YES |
| `TABLE_NAME` | nvarchar(255) | YES |
| `SOURCE_OBJECT_SCHEMA` | nvarchar(255) | YES |
| `SOURCE_OBJECT` | nvarchar(255) | YES |
| `SOURCE_OBJECT_TYPE` | nvarchar(255) | YES |
| `STATUS` | nvarchar(255) | YES |
| `COMMENTS` | nvarchar(255) | YES |
| `LAST_MODIFIEDDATE` | datetime | YES |
| `LAST_UPDATEDATE` | datetime | YES |

### ObjectDependencies

| Column | Type | Nullable |
|---|---|---|
| `LINEAGEID` | bigint(19) | YES |
| `DEPENDENCY_TYPE` | nvarchar(21) | NO |
| `REPORTING_OBJECT` | nvarchar(517) | YES |
| `ETL_PIPELINE_1` | nvarchar(517) | YES |
| `DEPENDENCY_1` | nvarchar(517) | YES |
| `ETL_PIPELINE_2` | nvarchar(264) | YES |
| `DEPENDENCY_2` | nvarchar(255) | YES |
| `DEPENDENCY_2_PARENT` | nvarchar(255) | YES |
| `DEPENDENCY_2_LEVEL` | int(10) | YES |
| `ETL_PIPELINE_3` | nvarchar(350) | YES |
| `DEPENDENCY_3` | nvarchar(600) | YES |
| `DEPENDENCY_3_LEVEL` | int(10) | YES |
| `DEPENDENCY_3_PARENT` | nvarchar(517) | YES |
| `SOURCE_SYSTEM` | nvarchar(250) | YES |
| `ETL_PIPELINE_1_CODE_URL` | nvarchar(4000) | YES |
| `ETL_PIPELINE_2_CODE_URL` | nvarchar(4000) | YES |
| `ETL_PIPELINE_3_CODE_URL` | nvarchar(4000) | YES |
| `DEPENDENCY_2_PARENT_PIPELINE_CODE_URL` | nvarchar(4000) | YES |

### ObjectPipelineExecution

| Column | Type | Nullable |
|---|---|---|
| `ExecutionId` | uniqueidentifier | NO |
| `Environment` | nvarchar(50) | YES |
| `Application` | varchar(128) | YES |
| `ETLProjectId` | int(10) | YES |
| `ETLProject` | varchar(128) | YES |
| `Project` | varchar(22) | YES |
| `Source` | nvarchar(1024) | YES |
| `ExecutionDate` | date | YES |
| `ExecutionStartDate` | date | YES |
| `ExecutionStart` | datetime | YES |
| `ExecutionEndDate` | date | YES |
| `ExecutionEnd` | datetime | YES |
| `ExecutionEndTime` | numeric(16) | YES |
| `IsCurrentDate` | int(10) | NO |
| `IsFirstExecution` | bigint(19) | YES |
| `Duration` | int(10) | YES |
| `CountLogRows` | int(10) | YES |
| `CountErrors` | int(10) | YES |
| `Status` | int(10) | NO |
| `SuccessfulExecution` | int(10) | NO |
| `TotalExecution` | int(10) | NO |
| `LogMessage` | nvarchar | YES |
| `IsHeaderRow` | int(10) | NO |
| `IsProjectLevel` | int(10) | NO |
| `AvailabilityThreshold` | numeric(11) | YES |

### ObjectSchemaChangeLog

| Column | Type | Nullable |
|---|---|---|
| `TABLE_SCHEMA` | nvarchar(255) | YES |
| `TABLE_NAME` | nvarchar(255) | YES |
| `COLUMN_NAME` | nvarchar(255) | YES |
| `COLUMN_DEFINITION` | nvarchar(3000) | YES |
| `IS_NULLABLE` | nvarchar(3) | YES |
| `DATA_TYPE` | nvarchar(100) | YES |
| `CHANGE` | nvarchar(13) | NO |
| `RELEASE_DATE` | datetime | YES |
| `RELEASE_VERSION` | nvarchar(20) | NO |
| `RELEASE_VERSION_ID` | int(10) | YES |

### ObjectSchemaHistory

| Column | Type | Nullable |
|---|---|---|
| `COLUMN_ID` | int(10) | NO |
| `VERSION_ID` | bigint(19) | NO |
| `TABLE_SCHEMA` | nvarchar(255) | YES |
| `TABLE_NAME` | nvarchar(255) | YES |
| `COLUMN_NAME` | nvarchar(255) | YES |
| `COLUMN_DEFINITION` | nvarchar(3000) | YES |
| `ORDINAL_POSITION` | int(10) | YES |
| `IS_NULLABLE` | nvarchar(3) | YES |
| `DATA_TYPE` | nvarchar(100) | YES |
| `RELEASE_DATE` | datetime | YES |
| `RELEASE_VERSION` | nvarchar(20) | YES |

## [ReportingDataMart].[BMD]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### AnalyticBins

| Column | Type | Nullable |
|---|---|---|
| `AnalyticBin` | nvarchar(255) | NO |
| `Country` | nvarchar(255) | NO |
| `ChinaClassificationId` | nvarchar(255) | NO |
| `BinClassification` | nvarchar(255) | NO |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### AnalyticBuckets

| Column | Type | Nullable |
|---|---|---|
| `BucketValueId` | int(10) | NO |
| `Bucket` | nvarchar(255) | NO |
| `StartValue` | decimal(18) | YES |
| `EndValue` | decimal(18) | YES |
| `BucketValue` | nvarchar(255) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### AnalyticLists

| Column | Type | Nullable |
|---|---|---|
| `List` | nvarchar(255) | NO |
| `ListValue` | nvarchar(1000) | NO |
| `ListValueId` | int(10) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### BusinessUnits

| Column | Type | Nullable |
|---|---|---|
| `BUId` | int(10) | NO |
| `BUName` | nvarchar(150) | NO |
| `IsActive` | bit | NO |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### ChinaTopInstitutes

| Column | Type | Nullable |
|---|---|---|
| `Organization` | nvarchar(255) | NO |
| `OrganizationType` | nvarchar(255) | NO |
| `ClassificationId` | nvarchar(255) | NO |
| `AddAncestors` | bit | NO |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### Classifications

| Column | Type | Nullable |
|---|---|---|
| `ClassificationId` | int(10) | NO |
| `Classification` | nvarchar(255) | NO |
| `Tag` | nvarchar(255) | NO |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### Countries

| Column | Type | Nullable |
|---|---|---|
| `Name` | nvarchar(200) | NO |
| `Country` | nvarchar(200) | NO |
| `Alpha_2` | nchar(2) | NO |
| `Alpha_3` | nchar(3) | NO |
| `Country_code` | int(10) | YES |
| `Iso_3166_2` | nvarchar(50) | YES |
| `Region` | nvarchar(50) | YES |
| `Sub_region` | nvarchar(50) | YES |
| `Intermediate_region` | nvarchar(50) | YES |
| `Region_code` | nvarchar(50) | YES |
| `Sub_region_code` | nvarchar(50) | YES |
| `Intermediate_region_code` | nvarchar(50) | YES |
| `RejectionRate` | nvarchar(50) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### CountryRejectionRates

| Column | Type | Nullable |
|---|---|---|
| `Country` | nvarchar(100) | NO |
| `RejectionRate` | nvarchar(50) | NO |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### DataDefinitions

| Column | Type | Nullable |
|---|---|---|
| `TABLE_CATALOG` | nvarchar(255) | YES |
| `TABLE_SCHEMA` | nvarchar(255) | YES |
| `TABLE_NAME` | nvarchar(255) | YES |
| `COLUMN_NAME` | nvarchar(255) | YES |
| `COLUMN_DATATYPE` | nvarchar(255) | YES |
| `COLUMN_ALT_NAME` | nvarchar(255) | YES |
| `USAGE` | nvarchar(255) | YES |
| `COLUMN_DEFINITION` | nvarchar(2000) | YES |
| `VALIDATED_COLUMN_DEFINITION` | nvarchar(4000) | YES |
| `COLUMN_COMMENT` | nvarchar(4000) | YES |
| `COLUMN_DERIVATION` | nvarchar(255) | YES |
| `NAME_VALIDATED?` | bit | YES |
| `DEFINITION_DEFINED?` | bit | YES |
| `DEFINITION_VALIDATED?` | bit | YES |
| `SOURCE_TABLE_SCHEMA` | nvarchar(255) | YES |
| `SOURCE_NAME` | nvarchar(255) | YES |
| `STATUS` | nvarchar(255) | YES |
| `BUSINESS_OWNER` | nvarchar(255) | YES |
| `REQUEST_BY` | nvarchar(255) | YES |
| `REQUEST_DATE` | datetime | YES |
| `REQUEST_REF` | nvarchar(255) | YES |

### FactJournalAnalytics_AA

| Column | Type | Nullable |
|---|---|---|
| `dateid` | int(10) | YES |
| `measureid` | int(10) | YES |
| `scenarioid` | int(10) | YES |
| `taxonomyid` | bigint(19) | YES |
| `valuenumerator` | decimal(19) | YES |
| `valuedenominator` | decimal(19) | YES |

### FactJournalAnalytics_Drillthrough

| Column | Type | Nullable |
|---|---|---|
| `DateId` | int(10) | YES |
| `MeasureId` | bigint(19) | YES |
| `ScenarioId` | bigint(19) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `EntityId` | bigint(19) | YES |
| `ValueNumerator` | decimal(19) | YES |
| `CreateDate` | datetime | YES |

### FactJournalAnalytics_Management

| Column | Type | Nullable |
|---|---|---|
| `DateId` | date | YES |
| `Country8RegionsBin` | nvarchar(50) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `MeasureId` | int(10) | YES |
| `ValueNumerator` | decimal(19) | YES |
| `ValueDenominator` | decimal(19) | YES |

### FactJournalAnalytics_SI

| Column | Type | Nullable |
|---|---|---|
| `dateid` | int(10) | YES |
| `measureid` | int(10) | YES |
| `scenarioid` | int(10) | YES |
| `taxonomyid` | bigint(19) | YES |
| `valuenumerator` | decimal(19) | YES |
| `valuedenominator` | decimal(19) | YES |

### OKR.2024.KPITargets

| Column | Type | Nullable |
|---|---|---|
| `MeasureSourceId` | nvarchar(255) | NO |
| `MeasureName` | nvarchar(255) | NO |
| `BaselineValue` | numeric(18) | YES |
| `FinalTargetValue` | numeric(18) | YES |
| `2024Target` | numeric(18) | YES |
| `MonthlySplit` | bit | YES |
| `ThresholdType` | nvarchar(50) | YES |
| `ThresholdGreen` | numeric(18) | YES |
| `ThresholdAmber` | numeric(18) | YES |
| `ThresholdRed` | numeric(18) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### OKR.2024.KPIs

| Column | Type | Nullable |
|---|---|---|
| `MeasureId` | int(10) | NO |
| `MeasureSourceId` | nvarchar(255) | YES |
| `MeasureName` | nvarchar(255) | YES |
| `MeasureDescription` | nvarchar(255) | YES |
| `MeasureType` | nvarchar(255) | YES |
| `AggregationType` | nvarchar(255) | YES |
| `DataType` | nvarchar(255) | YES |
| `FormatString` | nvarchar(255) | YES |
| `MeasureGoal` | nvarchar(255) | YES |
| `Source` | nvarchar(255) | YES |
| `Notes` | nvarchar(255) | YES |
| `MeasureCategoryId` | int(10) | YES |
| `MeasureGroupId` | int(10) | YES |
| `PriorityMeasure` | bit | YES |
| `Owner` | nvarchar(255) | YES |
| `CreateDate` | datetime | YES |
| `CreatedByEmployeeId` | bigint(19) | YES |
| `UpdateDate` | datetime | YES |
| `UpdatedByEmployeeId` | bigint(19) | YES |
| `BusinessEntity` | nvarchar(50) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### OKR.2024.ManualKPIs

| Column | Type | Nullable |
|---|---|---|
| `KPI` | nvarchar(255) | NO |
| `KPIName` | nvarchar(255) | NO |
| `Jan` | numeric(18) | YES |
| `Feb` | numeric(18) | YES |
| `Mar` | numeric(18) | YES |
| `Apr` | numeric(18) | YES |
| `May` | numeric(18) | YES |
| `Jun` | numeric(18) | YES |
| `Jul` | numeric(18) | YES |
| `Aug` | numeric(18) | YES |
| `Sep` | numeric(18) | YES |
| `Oct` | numeric(18) | YES |
| `Nov` | numeric(18) | YES |
| `Dec` | numeric(18) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### OKR.2024.ManualOKRs

| Column | Type | Nullable |
|---|---|---|
| `OKR` | nvarchar(255) | NO |
| `OKRName` | nvarchar(255) | NO |
| `Jan` | numeric(18) | YES |
| `Feb` | numeric(18) | YES |
| `Mar` | numeric(18) | YES |
| `Apr` | numeric(18) | YES |
| `May` | numeric(18) | YES |
| `Jun` | numeric(18) | YES |
| `Jul` | numeric(18) | YES |
| `Aug` | numeric(18) | YES |
| `Sep` | numeric(18) | YES |
| `Oct` | numeric(18) | YES |
| `Nov` | numeric(18) | YES |
| `Dec` | numeric(18) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### OKR.2024.OKRTargets

| Column | Type | Nullable |
|---|---|---|
| `MeasureSourceId` | nvarchar(255) | NO |
| `MeasureName` | nvarchar(255) | NO |
| `BaselineValue` | numeric(18) | YES |
| `FinalTargetValue` | numeric(18) | YES |
| `2024Target` | numeric(18) | YES |
| `MonthlySplit` | bit | YES |
| `ThresholdType` | nvarchar(50) | YES |
| `ThresholdGreen` | numeric(18) | YES |
| `ThresholdAmber` | numeric(18) | YES |
| `ThresholdRed` | numeric(18) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### OKR.2024.OKRs

| Column | Type | Nullable |
|---|---|---|
| `MeasureId` | int(10) | NO |
| `MeasureSourceId` | nvarchar(255) | YES |
| `MeasureName` | nvarchar(255) | YES |
| `MeasureDescription` | nvarchar(255) | YES |
| `MeasureType` | nvarchar(255) | YES |
| `AggregationType` | nvarchar(255) | YES |
| `DataType` | nvarchar(255) | YES |
| `FormatString` | nvarchar(255) | YES |
| `MeasureGoal` | nvarchar(255) | YES |
| `Source` | nvarchar(255) | YES |
| `Notes` | nvarchar(255) | YES |
| `MeasureCategoryId` | int(10) | YES |
| `MeasureGroupId` | int(10) | YES |
| `PriorityMeasure` | bit | YES |
| `Owner` | nvarchar(255) | YES |
| `CreateDate` | datetime | YES |
| `CreatedByEmployeeId` | bigint(19) | YES |
| `UpdateDate` | datetime | YES |
| `UpdatedByEmployeeId` | bigint(19) | YES |
| `BusinessEntity` | nvarchar(50) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### OKR.2025.KPITargets

| Column | Type | Nullable |
|---|---|---|
| `MeasureSourceId` | nvarchar(255) | NO |
| `MeasureName` | nvarchar(255) | NO |
| `BaselineValue` | numeric(18) | YES |
| `FinalTargetValue` | numeric(18) | YES |
| `2025Target` | numeric(18) | YES |
| `MonthlySplit` | bit | YES |
| `ThresholdType` | nvarchar(50) | YES |
| `ThresholdGreen` | numeric(18) | YES |
| `ThresholdAmber` | numeric(18) | YES |
| `ThresholdRed` | numeric(18) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### OKR.2025.KPIs

| Column | Type | Nullable |
|---|---|---|
| `MeasureId` | int(10) | NO |
| `MeasureSourceId` | nvarchar(255) | YES |
| `MeasureName` | nvarchar(255) | YES |
| `MeasureDescription` | nvarchar(255) | YES |
| `MeasureType` | nvarchar(255) | YES |
| `AggregationType` | nvarchar(255) | YES |
| `IsTrackable` | bit | YES |
| `DataType` | nvarchar(255) | YES |
| `FormatString` | nvarchar(255) | YES |
| `MeasureGoal` | nvarchar(255) | YES |
| `Source` | nvarchar(255) | YES |
| `Notes` | nvarchar(255) | YES |
| `MeasureCategoryId` | int(10) | YES |
| `MeasureGroupId` | int(10) | YES |
| `PriorityMeasure` | bit | YES |
| `Owner` | nvarchar(255) | YES |
| `CreateDate` | datetime | YES |
| `CreatedByEmployeeId` | bigint(19) | YES |
| `UpdateDate` | datetime | YES |
| `UpdatedByEmployeeId` | bigint(19) | YES |
| `BusinessEntity` | nvarchar(50) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### OKR.2025.ManualKPIs

| Column | Type | Nullable |
|---|---|---|
| `KPI` | nvarchar(255) | NO |
| `KPIName` | nvarchar(255) | NO |
| `Jan` | numeric(18) | YES |
| `Feb` | numeric(18) | YES |
| `Mar` | numeric(18) | YES |
| `Apr` | numeric(18) | YES |
| `May` | numeric(18) | YES |
| `Jun` | numeric(18) | YES |
| `Jul` | numeric(18) | YES |
| `Aug` | numeric(18) | YES |
| `Sep` | numeric(18) | YES |
| `Oct` | numeric(18) | YES |
| `Nov` | numeric(18) | YES |
| `Dec` | numeric(18) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### OKR.2025.ManualOKRs

| Column | Type | Nullable |
|---|---|---|
| `OKR` | nvarchar(255) | NO |
| `OKRName` | nvarchar(255) | NO |
| `Jan` | numeric(18) | YES |
| `Feb` | numeric(18) | YES |
| `Mar` | numeric(18) | YES |
| `Apr` | numeric(18) | YES |
| `May` | numeric(18) | YES |
| `Jun` | numeric(18) | YES |
| `Jul` | numeric(18) | YES |
| `Aug` | numeric(18) | YES |
| `Sep` | numeric(18) | YES |
| `Oct` | numeric(18) | YES |
| `Nov` | numeric(18) | YES |
| `Dec` | numeric(18) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### OKR.2025.MeasureGroup

| Column | Type | Nullable |
|---|---|---|
| `MeasureCategoryId` | int(10) | NO |
| `MeasureGroupId` | int(10) | NO |
| `MeasureGroupName` | nvarchar(255) | YES |
| `MeasureGroupDescription` | nvarchar(255) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### OKR.2025.OKRTargets

| Column | Type | Nullable |
|---|---|---|
| `MeasureSourceId` | nvarchar(255) | NO |
| `MeasureName` | nvarchar(255) | NO |
| `BaselineValue` | numeric(18) | YES |
| `FinalTargetValue` | numeric(18) | YES |
| `2025Target` | numeric(18) | YES |
| `MonthlySplit` | bit | YES |
| `ThresholdType` | nvarchar(50) | YES |
| `ThresholdGreen` | numeric(18) | YES |
| `ThresholdAmber` | numeric(18) | YES |
| `ThresholdRed` | numeric(18) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### OKR.2025.OKRs

| Column | Type | Nullable |
|---|---|---|
| `MeasureId` | int(10) | NO |
| `MeasureSourceId` | nvarchar(255) | YES |
| `MeasureName` | nvarchar(255) | YES |
| `MeasureDescription` | nvarchar(255) | YES |
| `MeasureType` | nvarchar(255) | YES |
| `AggregationType` | nvarchar(255) | YES |
| `IsTrackable` | bit | YES |
| `DataType` | nvarchar(255) | YES |
| `FormatString` | nvarchar(255) | YES |
| `MeasureGoal` | nvarchar(255) | YES |
| `Source` | nvarchar(255) | YES |
| `Notes` | nvarchar(255) | YES |
| `MeasureCategoryId` | int(10) | YES |
| `MeasureGroupId` | int(10) | YES |
| `PriorityMeasure` | bit | YES |
| `Owner` | nvarchar(255) | YES |
| `CreateDate` | datetime | YES |
| `CreatedByEmployeeId` | bigint(19) | YES |
| `UpdateDate` | datetime | YES |
| `UpdatedByEmployeeId` | bigint(19) | YES |
| `BusinessEntity` | nvarchar(50) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### OKR.MeasureCategory

| Column | Type | Nullable |
|---|---|---|
| `MeasureCategoryId` | int(10) | NO |
| `MeasureCategoryName` | nvarchar(255) | YES |
| `MeasureCategoryDescription` | nvarchar(255) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### OKR.MeasureGroup

| Column | Type | Nullable |
|---|---|---|
| `MeasureCategoryId` | int(10) | NO |
| `MeasureGroupId` | int(10) | NO |
| `MeasureGroupName` | nvarchar(255) | YES |
| `MeasureGroupDescription` | nvarchar(255) | YES |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### ReviewBoardInvitation_AlgorithmDetail

| Column | Type | Nullable |
|---|---|---|
| `AlgorithmDetailId` | int(10) | NO |
| `WorkflowId` | int(10) | NO |
| `SystemRoleId` | int(10) | NO |
| `MessageTypeId` | int(10) | NO |
| `InvitationMethodId` | int(10) | NO |
| `InvitationAlgorithmType` | varchar(255) | YES |
| `AlgorithmDetail` | varchar(255) | NO |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### Teams

| Column | Type | Nullable |
|---|---|---|
| `TeamId` | int(10) | NO |
| `TeamName` | nvarchar(150) | NO |
| `UserId` | int(10) | NO |
| `BUId` | int(10) | NO |
| `PrimaryEmailAddress` | nvarchar(150) | NO |
| `TeamLead` | varchar(100) | NO |
| `IsActive` | bit | NO |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### Teams_Journals

| Column | Type | Nullable |
|---|---|---|
| `PKTeams_JournalsId` | int(10) | NO |
| `TeamId` | int(10) | NO |
| `BUId` | int(10) | NO |
| `JournalTaxonomyId` | bigint(19) | YES |
| `Journal` | nvarchar(2000) | YES |
| `IsActive` | bit | NO |
| `LastUpdateBy` | varchar(255) | NO |
| `LastUpdateDate` | smalldatetime | NO |

### WAP_allocations_pubdev_hierarchy

| Column | Type | Nullable |
|---|---|---|
| `InternalID` | nvarchar(50) | YES |
| `LevelName` | nvarchar(50) | YES |
| `IgnoreName` | nvarchar(50) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `ProgramId` | smallint(5) | YES |
| `Program` | nvarchar(100) | YES |
| `JournalId` | smallint(5) | YES |
| `Journal` | nvarchar(200) | YES |
| `SectionId` | smallint(5) | YES |
| `Section` | nvarchar(200) | YES |
| `Level` | nvarchar(50) | YES |
| `IsDefault` | bit | YES |
| `IsDeleted` | bit | YES |
| `IsOpenForSubmission` | bit | YES |
| `IsOnline` | bit | YES |
| `HeadSegment` | nvarchar(50) | YES |
| `HeadSegmentId` | nvarchar(50) | YES |
| `PortfolioManager` | nvarchar(300) | YES |
| `PortfolioManagerId` | nvarchar(100) | YES |
| `JournalManager` | nvarchar(300) | YES |
| `JournalManagerId` | nvarchar(100) | YES |
| `JournalSectionManager` | nvarchar(300) | YES |
| `JournalSectionManagerId` | nvarchar(100) | YES |
| `JournalSectionSeniorSpecialist` | nvarchar(300) | YES |
| `JournalSectionSeniorSpecialistId` | nvarchar(100) | YES |
| `JournalSectionSpecialist` | nvarchar(300) | YES |
| `JournalSectionSpecialistId` | nvarchar(100) | YES |
| `PeerReviewManager` | nvarchar(300) | YES |
| `PeerReviewManagerId` | nvarchar(100) | YES |

### WAP_employee_status

| Column | Type | Nullable |
|---|---|---|
| `InternalId` | nvarchar(10) | YES |
| `EmployeeId` | nvarchar(50) | YES |
| `EmployeeName` | nvarchar(120) | YES |
| `Period` | date | YES |
| `Status` | nvarchar(20) | YES |
| `LevelName` | nvarchar(20) | YES |
| `EndDate` | date | YES |
| `StartDate` | date | YES |

## [ReportingDataMart].[Common]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### Country

| Column | Type | Nullable |
|---|---|---|
| `CountryId` | char(3) | NO |
| `Country` | nvarchar(100) | NO |
| `EnglishShortName` | nvarchar(255) | YES |
| `Alpha2Code` | char(2) | YES |
| `Numeric` | char(3) | YES |
| `ccTLD` | char(3) | YES |
| `ContinentId` | char(2) | YES |
| `Continent` | varchar(13) | YES |
| `Latitude` | decimal(10) | YES |
| `Longitude` | decimal(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### CountryMetrics

| Column | Type | Nullable |
|---|---|---|
| `CountryId` | nvarchar(3) | NO |
| `Country` | nvarchar(50) | YES |
| `ContinentId` | nvarchar(3) | YES |
| `Continent` | nvarchar(50) | YES |
| `Country3RegionsBinFocus` | nvarchar(50) | YES |
| `Country4RegionsBin` | nvarchar(50) | YES |
| `Country5RegionsBin` | nvarchar(50) | YES |
| `Country7RegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin` | nvarchar(50) | YES |
| `Country13RegionsBin` | nvarchar(50) | YES |
| `IsFocusRegion` | bit | YES |
| `CountryRejectionRate` | nvarchar(50) | YES |
| `CountryOrder` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### EmailMetrics

| Column | Type | Nullable |
|---|---|---|
| `Email` | nvarchar(150) | NO |
| `PersonId` | bigint(19) | YES |
| `UserId` | bigint(19) | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | char(3) | YES |
| `PrimaryOrganizationRosstCountryId` | char(3) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationRosstCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | nvarchar(13) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `OrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `OrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `OrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `OrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `OrganizationsHighestRankFrontiersPriorityBins` | nvarchar(50) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(3) | YES |
| `RosstCountryId` | nvarchar(3) | YES |
| `Country` | nvarchar(100) | YES |
| `RosstCountry` | nvarchar(100) | YES |
| `Continent` | nvarchar(13) | YES |
| `Country3RegionsBinFocus` | nvarchar(50) | YES |
| `Country5RegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin` | nvarchar(50) | YES |
| `Country13RegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin-China` | nvarchar(50) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(50) | YES |
| `CountryRejectionRate` | nvarchar(50) | YES |
| `CountryOrder` | int(10) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `OwnerEmployeeCountry13RegionsBin` | nvarchar(50) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(50) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Funder

| Column | Type | Nullable |
|---|---|---|
| `FunderId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Funder` | nvarchar(400) | NO |
| `OriginalId` | nvarchar(500) | YES |
| `DOI` | nvarchar(500) | YES |
| `CreateDate` | datetime | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### JournalUsers

| Column | Type | Nullable |
|---|---|---|
| `JournalUsers.Id` | int(10) | NO |
| `Journal.UserId` | int(10) | NO |
| `Journal.SpaceId` | smallint(5) | NO |
| `Journal.Email` | nvarchar(150) | YES |
| `JournalUserId` | bigint(19) | YES |
| `CreateDate` | datetime | NO |

### Organization

| Column | Type | Nullable |
|---|---|---|
| `OrganizationId` | int(10) | NO |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | NO |
| `Description` | nvarchar | YES |
| `Street` | nvarchar(200) | YES |
| `ZipCode` | nvarchar(30) | YES |
| `CityId` | int(10) | YES |
| `City` | nvarchar(200) | YES |
| `StateId` | int(10) | YES |
| `State` | nvarchar(150) | YES |
| `CountryId` | char(3) | YES |
| `RosstCountryId` | char(3) | YES |
| `Country` | nvarchar(100) | YES |
| `RosstCountry` | nvarchar(100) | YES |
| `ContinentId` | char(2) | YES |
| `Continent` | varchar(13) | YES |
| `ChinaClassificationId` | int(10) | YES |
| `IsCTI` | bit | YES |
| `IsCAS` | bit | YES |
| `IsCountryInWatchlist` | bit | NO |
| `Email` | nvarchar(100) | YES |
| `URL` | nvarchar(500) | YES |
| `Phone` | nvarchar(30) | YES |
| `Logo` | nvarchar(32) | YES |
| `IsDeleted` | bit | NO |
| `IsUserCreated` | bit | NO |
| `IsValidated` | bit | NO |
| `IsUnaffiliatedOption` | bit | NO |
| `Domains` | nvarchar(4000) | YES |
| `PrimaryTypeId` | int(10) | YES |
| `PrimaryType` | nvarchar(30) | YES |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | NO |
| `RankFrontiersPriority` | int(10) | YES |
| `AncestorsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `AncestorsTopRankRosstId` | nvarchar(40) | YES |
| `AncestorsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `AncestorsHighestRankFrontiersPriority` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### OrganizationMetrics

| Column | Type | Nullable |
|---|---|---|
| `OrganizationId` | bigint(19) | NO |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | YES |
| `OrganizationCountryId` | char(3) | YES |
| `RosstCountryId` | char(3) | YES |
| `OrganizationCountry` | nvarchar(100) | YES |
| `RosstCountry` | nvarchar(100) | YES |
| `OrganizationContinentId` | char(2) | YES |
| `OrganizationContinent` | nvarchar(13) | YES |
| `OrganizationCityId` | int(10) | YES |
| `OrganizationCity` | nvarchar(200) | YES |
| `OrganizationIsCTI` | bit | YES |
| `OrganizationIsCAS` | bit | YES |
| `IsOrganizationCountryInWatchlist` | bit | YES |
| `HighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `TopRankRosstId` | nvarchar(40) | YES |
| `HighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `HighestRankFrontiersPriority` | int(10) | YES |
| `HighestRankFrontiersPriorityBins` | nvarchar(200) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `OrganizationCountry3RegionsBinFocus` | nvarchar(50) | YES |
| `OrganizationCountry5RegionsBin` | nvarchar(50) | YES |
| `OrganizationCountry8RegionsBin` | nvarchar(50) | YES |
| `OrganizationCountry13RegionsBin` | nvarchar(50) | YES |
| `OrganizationCountry8RegionsBin-China` | nvarchar(50) | YES |
| `OrganizationCountry8RegionsBin-ChinaCAS` | nvarchar(50) | YES |
| `OrganizationCountryRejectionRate` | nvarchar(100) | YES |
| `OrganizationCountryOrder` | int(10) | YES |
| `OrganizationCountryPriorityOrder` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### OrganizationRankings

| Column | Type | Nullable |
|---|---|---|
| `OrganizationId` | int(10) | NO |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | NO |
| `RankFrontiersPriority` | int(10) | YES |
| `ParentRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `ParentRankRosstId` | nvarchar(40) | YES |
| `ParentRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `ParentRankFrontiersPriority` | int(10) | YES |
| `AncestorsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `AncestorsTopRankRosstId` | nvarchar(40) | YES |
| `AncestorsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `AncestorsHighestRankFrontiersPriority` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### OrganizationRejectionRates

| Column | Type | Nullable |
|---|---|---|
| `OrganizationId` | bigint(19) | NO |
| `RosstId` | nvarchar(40) | YES |
| `ArticleDecisions` | int(10) | YES |
| `ArticleRejections` | int(10) | YES |
| `RejectionRate` | nvarchar(4000) | YES |
| `RejectionRateBin` | varchar(22) | NO |
| `RejectionRateBin3` | varchar(22) | NO |
| `RejectionRateBin10` | varchar(22) | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### PersonMetrics

| Column | Type | Nullable |
|---|---|---|
| `PersonUserId` | bigint(19) | NO |
| `PersonUserId.Original` | bigint(19) | NO |
| `PersonId` | bigint(19) | NO |
| `Person.JournalUserId` | bigint(19) | NO |
| `Person.SpaceId` | int(10) | YES |
| `Person.UserId` | int(10) | YES |
| `Person.Email` | nvarchar(300) | YES |
| `IsPrimaryEmail` | bit | YES |
| `IsJournalUser` | bit | YES |
| `IsRegisteredUser` | bit | YES |
| `IsNonRegisteredUser` | bit | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | char(3) | YES |
| `PrimaryOrganizationRosstCountryId` | char(3) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationRosstCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | nvarchar(50) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `HighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `TopRankRosstId` | nvarchar(40) | YES |
| `HighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `HighestRankFrontiersPriority` | int(10) | YES |
| `HighestRankFrontiersPriorityBins` | nvarchar(50) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `RosstCountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `RosstCountry` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `CountryOrder` | int(10) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `OwnerEmployeeCountry13RegionsBin` | nvarchar(50) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `EditingInvitationsReceivedCount` | int(10) | YES |
| `EditingInvitationsAcceptedCount` | int(10) | YES |
| `EditingInvitationsDeclinedCount` | int(10) | YES |
| `ReviewingInvitationsReceivedCount` | int(10) | YES |
| `ReviewingInvitationsAcceptedCount` | int(10) | YES |
| `ReviewingInvitationsDeclinedCount` | int(10) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserFirstName` | nvarchar(150) | YES |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserLastName` | nvarchar(150) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserRegisterDate` | datetime | YES |
| `UserActivateDate` | datetime | YES |
| `UserModifyDate` | datetime | YES |
| `UserIsDeleted` | bit | YES |
| `UserIsActivated` | bit | YES |
| `UserStatus` | nvarchar(30) | YES |
| `UserCompletedRegistration` | bit | YES |
| `UserIsLoggedIn` | bit | YES |
| `UserIsAdmin` | bit | YES |
| `UserIsAuthor` | bit | YES |
| `UserIsEditor` | bit | YES |
| `UserIsResearchTopicEditor` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserEditorialBoardRoles` | varchar(500) | YES |
| `UserAuthorRoles` | varchar(500) | YES |
| `UserRolesNames` | varchar(500) | YES |
| `UserIsAdmin.Frontiers` | bit | YES |
| `UserIsAuthor.Frontiers` | bit | YES |
| `UserIsEditor.Frontiers` | bit | YES |
| `UserIsResearchTopicEditor.Frontiers` | bit | YES |
| `UserIsReviewer.Frontiers` | bit | YES |
| `IsUserInWatchList` | bit | YES |
| `JournalUserIsEditor` | bit | YES |
| `JournalUserIsEBM` | bit | YES |
| `JournalUserIsReviewer` | bit | YES |
| `JournalUserIsAuthor` | bit | YES |
| `JournalRoleId` | nvarchar(50) | YES |
| `JournalUserRoleId` | int(10) | YES |
| `JournalUserRole` | nvarchar(50) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `JournalRole.FirstAssigned.Date` | datetime | YES |
| `Rank.ResearchTopic` | int(10) | YES |
| `Rank.Article` | int(10) | YES |
| `JournalUserFirstTaxonomyId` | bigint(19) | YES |
| `JournalUserFirstJoinDate` | datetime | YES |
| `JournalUserOrder` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### PersonUser

| Column | Type | Nullable |
|---|---|---|
| `PersonUserId` | bigint(19) | NO |
| `Person.UserId` | int(10) | NO |
| `Person.Email` | nvarchar(300) | YES |
| `CreateDate` | datetime | NO |

### Person_Profile

| Column | Type | Nullable |
|---|---|---|
| `PersonUserId` | bigint(19) | NO |
| `PersonId` | bigint(19) | NO |
| `Person.UserId` | int(10) | NO |
| `Person.Email` | nvarchar(300) | YES |
| `IsPrimaryEmail` | bit | YES |
| `IsActive` | bit | YES |
| `IsRegistered` | bit | YES |
| `IsNonRegistered` | bit | YES |
| `UserOrder` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Person_PublishingMetrics

| Column | Type | Nullable |
|---|---|---|
| `PublishingMetricsPersonId` | bigint(19) | NO |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchOrganization

| Column | Type | Nullable |
|---|---|---|
| `RosstId` | nvarchar(40) | NO |
| `Organization` | nvarchar(250) | NO |
| `OrganizationTypeId` | int(10) | NO |
| `OrganizationType` | nvarchar(200) | NO |
| `City` | nvarchar(150) | NO |
| `CountryIsoCode2` | char(2) | NO |
| `CountryId` | char(3) | YES |
| `Country` | nvarchar(100) | YES |
| `Rank` | int(10) | YES |
| `AncestorsTopRankRosstId` | nvarchar(40) | YES |
| `AncestorsTopRankOrganization` | nvarchar(250) | YES |
| `AncestorsTopRank` | int(10) | YES |
| `CreatedDate` | datetime | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchOrganizationRankings

| Column | Type | Nullable |
|---|---|---|
| `RosstId` | nvarchar(40) | NO |
| `Organization` | nvarchar(250) | NO |
| `Rank` | int(10) | YES |
| `ParentRankRosstId` | nvarchar(40) | YES |
| `ParentRankOrganization` | nvarchar(250) | YES |
| `ParentRank` | int(10) | YES |
| `AncestorsTopRankRosstId` | nvarchar(40) | YES |
| `AncestorsTopRankOrganization` | nvarchar(250) | YES |
| `AncestorsTopRank` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Space

| Column | Type | Nullable |
|---|---|---|
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(200) | YES |
| `SpaceShortName` | nvarchar(20) | YES |
| `SpaceGUID` | uniqueidentifier | NO |
| `TenantGroup` | nvarchar(50) | YES |
| `WebDomain` | nvarchar(128) | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Taxonomy

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(100) | NO |
| `Taxonomy` | nvarchar(200) | YES |
| `TaxonomyLevel` | varchar(9) | YES |
| `DomainId` | bigint(19) | NO |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `ParentTaxonomyId` | bigint(19) | YES |
| `ParentTaxonomy` | nvarchar(150) | YES |
| `IsDefault` | bit | NO |
| `DefaultTaxonomyId` | bigint(19) | NO |
| `DefaultTaxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | varchar(21) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalDevelopment.SeniorJournalManager` | nvarchar(100) | YES |
| `JournalSpecialist.Count` | int(10) | YES |
| `JournalSegmentId` | nvarchar(30) | YES |
| `JournalSegment` | nvarchar(100) | YES |
| `JournalSegmentId.Previous` | nvarchar(30) | YES |
| `JournalSegment.Previous` | nvarchar(100) | YES |
| `SegmentId` | nvarchar(30) | YES |
| `Segment` | nvarchar(100) | YES |
| `SegmentId.Previous` | nvarchar(30) | YES |
| `Segment.Previous` | nvarchar(100) | YES |
| `SegmentBonusId` | nvarchar(30) | YES |
| `SegmentBonus` | nvarchar(100) | YES |
| `JournalDevelopment.SegmentManager` | nvarchar(100) | YES |
| `PortfolioId` | nvarchar(32) | YES |
| `Portfolio` | nvarchar(128) | YES |
| `JournalDevelopment.PortfolioManager` | nvarchar(400) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `JournalFullName` | nvarchar(200) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `TypeId` | int(10) | YES |
| `Type` | nvarchar(30) | YES |
| `Level` | nvarchar(20) | YES |
| `StatusId` | int(10) | YES |
| `Status` | varchar(7) | YES |
| `IsOnline` | bit | YES |
| `IsDeleted` | bit | YES |
| `IsOpenForSubmission` | bit | YES |
| `SubmissionStatus` | varchar(6) | YES |
| `MissionStatement` | nvarchar | YES |
| `TypeSetterUserId` | int(10) | YES |
| `TypeSetterUserName` | nvarchar(400) | YES |
| `CreateDate` | datetime | YES |
| `ModifyDate` | datetime | YES |
| `PublishDate.Original` | datetime | YES |
| `PublishDate` | datetime | YES |
| `JournalCreateDate` | datetime | YES |
| `JournalModifyDate` | datetime | YES |
| `JournalPublishDate.Original` | datetime | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalUrl` | nvarchar(100) | YES |
| `SectionUrl` | nvarchar(100) | YES |
| `JournalUrlExpanded` | nvarchar(200) | YES |
| `SectionUrlExpanded` | nvarchar(250) | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.Year.Last` | smallint(5) | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(20) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JCR.ESCI.Year.First` | int(10) | YES |
| `JCR.ESCI.Year.Last` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### TaxonomyMetrics

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### UserMetrics

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `PersonId` | bigint(19) | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | char(3) | YES |
| `PrimaryOrganizationRosstCountryId` | char(3) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationRosstCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | nvarchar(13) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `OrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `OrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `OrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `OrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `OrganizationsHighestRankFrontiersPriorityBins` | nvarchar(50) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(3) | YES |
| `RosstCountryId` | nvarchar(3) | YES |
| `Country` | nvarchar(100) | YES |
| `RosstCountry` | nvarchar(100) | YES |
| `Continent` | nvarchar(13) | YES |
| `Country3RegionsBinFocus` | nvarchar(50) | YES |
| `Country5RegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin` | nvarchar(50) | YES |
| `Country13RegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin-China` | nvarchar(50) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(50) | YES |
| `CountryRejectionRate` | nvarchar(50) | YES |
| `CountryOrder` | int(10) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `OwnerEmployeeCountry13RegionsBin` | nvarchar(50) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(50) | YES |
| `EditingInvitationsReceivedCount` | int(10) | YES |
| `EditingInvitationsAcceptedCount` | int(10) | YES |
| `EditingInvitationsDeclinedCount` | int(10) | YES |
| `ReviewingInvitationsReceivedCount` | int(10) | YES |
| `ReviewingInvitationsAcceptedCount` | int(10) | YES |
| `ReviewingInvitationsDeclinedCount` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### User_JournalRoleMetrics

| Column | Type | Nullable |
|---|---|---|
| `JournalUserId` | bigint(19) | NO |
| `UserId` | int(10) | YES |
| `SpaceId` | smallint(5) | YES |
| `JournalUserIsEditor` | bit | YES |
| `JournalUserIsEBM` | bit | YES |
| `JournalUserIsReviewer` | bit | YES |
| `JournalUserIsAuthor` | bit | YES |
| `JournalRoleId` | nvarchar(50) | YES |
| `JournalUserRoleId` | int(10) | YES |
| `JournalUserRole` | nvarchar(50) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `JournalRole.FirstAssigned.Date` | datetime | YES |
| `Rank.ResearchTopic` | int(10) | YES |
| `Rank.Article` | int(10) | YES |
| `JournalUserFirstTaxonomyId` | bigint(19) | YES |
| `JournalUserFirstJoinDate` | datetime | YES |
| `JournalUserOrder` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### User_Profile

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `UserPersonUserId` | bigint(19) | NO |
| `UserPrimaryEmailAddress` | nvarchar(100) | NO |
| `UserTitle` | nvarchar(15) | YES |
| `UserFirstName` | nvarchar(150) | NO |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserLastName` | nvarchar(150) | NO |
| `UserName` | nvarchar(400) | NO |
| `RegisterDate` | datetime | YES |
| `ActivateDate` | datetime | YES |
| `UserModifyDate` | datetime | YES |
| `UserIsDeleted` | bit | NO |
| `UserIsActivated` | bit | NO |
| `UserStatus` | varchar(30) | NO |
| `CompletedRegistration` | bit | NO |
| `LoggedIn` | bit | NO |
| `UserIsAdmin` | bit | NO |
| `UserIsAuthor` | bit | NO |
| `UserIsEditor` | bit | NO |
| `UserIsResearchTopicEditor` | bit | NO |
| `UserIsReviewer` | bit | NO |
| `Roles` | varchar(300) | YES |
| `RolesNames` | varchar(1000) | YES |
| `EditorialBoardRoles` | varchar(500) | YES |
| `AuthorRoles` | varchar(500) | YES |
| `IsAdmin.Frontiers` | bit | NO |
| `IsAuthor.Frontiers` | bit | NO |
| `IsEditor.Frontiers` | bit | NO |
| `IsResearchTopicEditor.Frontiers` | bit | NO |
| `IsReviewer.Frontiers` | bit | NO |
| `Roles.Frontiers` | varchar(300) | YES |
| `RolesNames.Frontiers` | varchar(1000) | YES |
| `EditorialBoardRoles.Frontiers` | varchar(30) | YES |
| `AuthorRoles.Frontiers` | varchar(50) | YES |
| `IsUserInWatchList` | bit | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

## [ReportingDataMart].[Person]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### AuthorOrganizations

| Column | Type | Nullable |
|---|---|---|
| `AuthorOrganizationsId` | bigint(19) | NO |
| `AuthorId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `OrganizationId` | int(10) | NO |
| `RosstId` | nvarchar(40) | YES |
| `OrganizationOrder` | int(10) | NO |
| `OrganizationSourceId` | char(1) | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Author_Affiliations

| Column | Type | Nullable |
|---|---|---|
| `Affiliations.AuthorId` | bigint(19) | NO |
| `LegacyAffiliationCountries` | nvarchar(500) | YES |
| `LegacyAffiliations` | nvarchar(4000) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Author_AnalyticBins

| Column | Type | Nullable |
|---|---|---|
| `AnalyticBins.AuthorId` | bigint(19) | NO |
| `TimeSinceLastSubmission.Bin` | nvarchar(20) | YES |
| `TimeSinceLastAcceptance.Bin` | nvarchar(20) | YES |
| `TimeSinceLastRejection.Bin` | nvarchar(20) | YES |
| `TimeSinceLastDecision.Bin` | nvarchar(20) | YES |
| `TimeSinceLastPublication.Bin` | nvarchar(20) | YES |
| `PreviousReviewDecisionTime.Bin` | nvarchar(20) | YES |
| `Submitted Articles Bins` | nvarchar(50) | YES |
| `Accepted Articles Bins` | nvarchar(50) | YES |
| `Time Since Last Submitted Article Bins` | nvarchar(50) | YES |
| `Time Since Last Accepted Article Bins` | nvarchar(50) | YES |
| `Time Since Last Rejected Article Bins` | nvarchar(50) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Author_KeyMetrics

| Column | Type | Nullable |
|---|---|---|
| `KeyMetrics.AuthorId` | bigint(19) | NO |
| `KeyMetrics.ArticleId` | bigint(19) | NO |
| `Articles Submitted per Author` | int(10) | YES |
| `Articles Accepted per Author` | int(10) | YES |
| `First.SubmissionDate` | datetime | YES |
| `Last.Submitted` | datetime | YES |
| `Last.Accepted` | datetime | YES |
| `Last.Rejection` | datetime | YES |
| `Last.Decided` | datetime | YES |
| `Last.Decided.ArticleId` | bigint(19) | YES |
| `IsLatestArticleDecision` | bit | YES |
| `IsReturningAuthor` | bit | YES |
| `IsReturningAuthorCA` | bit | YES |
| `IsReturningAuthorSA` | bit | YES |
| `IsReturningAuthorEBM` | bit | YES |
| `IsReturningAuthorRT` | bit | YES |
| `IsReturningAuthorRTE` | bit | YES |
| `DaysSinceLastSubmission` | int(10) | YES |
| `DaysSinceLastAcceptance` | int(10) | YES |
| `DaysSinceLastRejection` | int(10) | YES |
| `DaysSinceLastDecision` | int(10) | YES |
| `DaysSinceLastPublication` | int(10) | YES |
| `LastDecidedReviewDays` | int(10) | YES |
| `ArticlesSubmitted.Count` | int(10) | YES |
| `ArticlesAccepted.Count` | int(10) | YES |
| `Last.Submitted.Article` | datetime | YES |
| `Last.Accepted.Article` | datetime | YES |
| `Last.Rejected.Article` | datetime | YES |
| `TimeSince.Last.Submitted.Article` | int(10) | NO |
| `TimeSince.Last.Accepted.Article` | int(10) | NO |
| `TimeSince.Last.Rejected.Article` | int(10) | NO |
| `AuthorRank` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Author_Organization

| Column | Type | Nullable |
|---|---|---|
| `Organization.AuthorId` | bigint(19) | NO |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | nvarchar(10) | YES |
| `PrimaryOrganizationRosstCountryId` | nvarchar(10) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationRosstCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | nvarchar(10) | YES |
| `PrimaryOrganizationContinent` | nvarchar(13) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | NO |
| `AuthorOrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `AuthorOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `AuthorOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `AuthorOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Author_Profile

| Column | Type | Nullable |
|---|---|---|
| `AuthorId` | bigint(19) | NO |
| `AuthorUserId` | int(10) | YES |
| `AuthorJournalUserId` | bigint(19) | YES |
| `AuthorPersonUserId` | bigint(19) | YES |
| `AuthorEmail` | nvarchar(100) | YES |
| `AuthorSpaceId` | smallint(5) | YES |
| `RoleId` | int(10) | YES |
| `Role` | nvarchar(50) | YES |
| `RoleAbbr` | nvarchar(20) | YES |
| `JournalRoleId` | nvarchar(10) | YES |
| `AuthorArticleId` | bigint(19) | YES |
| `AuthorTaxonomyId` | bigint(19) | YES |
| `AuthorOrganizationId` | int(10) | YES |
| `AuthorRosstId` | nvarchar(40) | YES |
| `AuthorSource` | char(1) | YES |
| `ReviewAuthorId` | bigint(19) | YES |
| `ProductionAuthorId` | bigint(19) | YES |
| `AuthorTitle` | nvarchar(15) | YES |
| `AuthorFirstName` | nvarchar(300) | YES |
| `AuthorMiddleName` | nvarchar(100) | YES |
| `AuthorLastName` | nvarchar(300) | YES |
| `AuthorName` | nvarchar(600) | YES |
| `AuthorOriginalEmail` | nvarchar(100) | YES |
| `AuthorPrimaryEmailAddress` | nvarchar(100) | YES |
| `AuthorSuffix` | nvarchar(50) | YES |
| `AuthorOrder` | int(10) | YES |
| `IsCorrespondingAuthor` | bit | NO |
| `IsSubmittingAuthor` | bit | NO |
| `IsMainCorrespondingAuthor` | bit | NO |
| `IsLastAuthor` | bit | NO |
| `AuthorEmailOrder` | int(10) | YES |
| `ReviewerAuthorUserId` | int(10) | YES |
| `AuthorUserOrder` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### CampaignMember_KeyMetrics

| Column | Type | Nullable |
|---|---|---|
| `KeyMetrics.CampaignMemberId` | char(18) | NO |
| `Last.Reviewer.ReviewDate` | datetime | YES |
| `Last.Reviewer.EditDate` | datetime | YES |
| `LastSubmissionDate` | datetime | YES |
| `Is Returning Author?` | bit | YES |
| `Has Hosted RT?` | bit | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### CampaignMember_Profile

| Column | Type | Nullable |
|---|---|---|
| `CampaignMemberId` | char(18) | NO |
| `CampaignStatus` | nvarchar(40) | YES |
| `CampaignCRMId` | nvarchar(20) | YES |
| `CampaignName` | nvarchar(500) | YES |
| `ParentCampaignName` | nvarchar(100) | YES |
| `UltimateParentCampaignName` | nvarchar(100) | YES |
| `EmailAddress` | nvarchar(100) | YES |
| `CampaignMemberEmail` | nvarchar(200) | YES |
| `CampaignMemberUserId` | int(10) | YES |
| `CampaignMemberPersonUserId` | bigint(19) | YES |
| `CampaignMemberJournalUserId` | bigint(19) | YES |
| `CampaignMemberTaxonomyId` | bigint(19) | YES |
| `Is CM EBM` | bit | YES |
| `Is CM REV` | bit | YES |
| `JoinDate` | date | YES |
| `InviteDate` | date | YES |
| `CampaignRecordTypeCRMId` | nvarchar(20) | YES |
| `CampaignType` | nvarchar(50) | YES |
| `CampaignMemberCRMIdOrder` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Contributor_Invitation

| Column | Type | Nullable |
|---|---|---|
| `Invitation.ContributorId` | bigint(19) | NO |
| `InviteDate` | datetime | YES |
| `InviterUserId` | int(10) | YES |
| `ConfirmedDate` | datetime | YES |
| `ExpectedSubmissionDate` | datetime | YES |
| `InvitationInitiatorRoleId` | int(10) | YES |
| `InvitationInitiatorRole` | nvarchar(50) | YES |
| `InvitationStatusId` | int(10) | NO |
| `InvitationStatus` | nvarchar(50) | YES |
| `InvitationStatusDate` | datetime | YES |
| `InvitationSentRemindersCount` | int(10) | NO |
| `InvitationLastReminderDate` | datetime | YES |
| `InvitationActivationNumber` | uniqueidentifier | YES |
| `ActivationLink` | nvarchar(251) | YES |
| `InvitationStatusDate.Confirmed.First` | datetime | YES |
| `InvitationStatusDate.Confirmed.Last` | datetime | YES |
| `Invitation.InitiationDate` | datetime | YES |
| `DeclinationOtherReason` | nvarchar(200) | YES |
| `DeclinationReason` | nvarchar(200) | YES |
| `DeclinationCreateDate` | datetime | YES |
| `DeclinationReasons` | nvarchar(50) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Contributor_KeyMetrics

| Column | Type | Nullable |
|---|---|---|
| `KeyMetrics.ContributorId` | bigint(19) | NO |
| `ResearchTopicAbstractAcceptedDate.First` | datetime | YES |
| `SuggestedContributorUploadTypeId` | int(10) | YES |
| `SuggestedContributorAlgorithmTypeId` | int(10) | YES |
| `SuggestedContributorAlgorithmType` | nvarchar(100) | YES |
| `First.RT.SubmissionDate` | datetime | YES |
| `Reminders.Count.InvitationtoConfirmation` | int(10) | YES |
| `Reminders.Count.ConfirmationtoSubmission` | int(10) | YES |
| `Reminders.Count.Total` | int(10) | YES |
| `HasContributorBeenInvited` | bit | YES |
| `HasContributorBeenInvited.Cfp` | bit | YES |
| `ContributorInvitationDate.Logical` | datetime | YES |
| `HasConfirmedInvitation` | bit | YES |
| `ContributorIsSuggested` | bit | YES |
| `First.Author.SubmissionDate` | datetime | YES |
| `ContributorIsRTEditor` | bit | YES |
| `IsConfirmedContributor` | bit | YES |
| `IsSpontaneousSubmission` | bit | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Contributor_Profile

| Column | Type | Nullable |
|---|---|---|
| `ContributorId` | bigint(19) | NO |
| `ContributorId.Original` | int(10) | YES |
| `ContributorSpaceId` | smallint(5) | NO |
| `ContributorUserId` | int(10) | YES |
| `ContributorJournalUserId` | bigint(19) | YES |
| `ContributorPersonUserId` | bigint(19) | YES |
| `ContributorResearchTopicId` | bigint(19) | YES |
| `ContributorResearchTopicId.Original` | bigint(19) | YES |
| `ContributorTaxonomyId` | bigint(19) | YES |
| `ContributorTheme` | nvarchar(500) | YES |
| `ContributorCreatorUserTypeRoleId` | int(10) | YES |
| `ContributorCreatorUserTypeRole` | nvarchar(100) | YES |
| `ContributorEmail` | nvarchar(100) | YES |
| `Email` | nvarchar(100) | YES |
| `ContributorName` | nvarchar(400) | YES |
| `ContributorFirstName` | nvarchar(200) | YES |
| `ContributorMiddleName` | nvarchar(200) | YES |
| `ContributorLastName` | nvarchar(200) | YES |
| `ContributorSourceId` | int(10) | NO |
| `ContributorSource` | nvarchar(100) | YES |
| `ContributorSecondarySourceId` | int(10) | YES |
| `ContributorSecondarySource` | nvarchar(50) | YES |
| `ContributorCreateDate` | datetime | NO |
| `SalesForceMessageCreateDate` | datetime | YES |
| `ContributorSortOrder` | bigint(19) | NO |
| `CountExpectedArticles` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### EditorialBoardMember_Invitation

| Column | Type | Nullable |
|---|---|---|
| `Invitation.EditorialBoardMemberId` | bigint(19) | NO |
| `EditorialBoardInvitationId` | bigint(19) | YES |
| `InviterUserId` | int(10) | YES |
| `Inviter` | nvarchar(400) | YES |
| `InviteDate` | datetime | YES |
| `InvitationSourceId` | int(10) | YES |
| `InvitationSource` | nvarchar(100) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### EditorialBoardMember_KeyMetrics

| Column | Type | Nullable |
|---|---|---|
| `KeyMetrics.EditorialBoardMemberId` | bigint(19) | NO |
| `CountPublicationsConfirmed` | int(10) | YES |
| `CrossListedFields` | nvarchar(4000) | YES |
| `ActiveModifyDate` | datetime | YES |
| `MinJoinDate` | datetime | YES |
| `MinStartDate` | datetime | YES |
| `MaxEndDate` | datetime | YES |
| `SectionJoinDate` | datetime | YES |
| `SectionEndDate` | datetime | YES |
| `FirstTaxonomyRoleId` | int(10) | YES |
| `CountofTaxonomyRoles` | int(10) | YES |
| `ActiveEditorialBoards` | int(10) | YES |
| `HasOpportunity` | bit | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### EditorialBoardMember_Profile

| Column | Type | Nullable |
|---|---|---|
| `EditorialBoardMemberId` | bigint(19) | NO |
| `EditorialBoardMemberSpaceId` | smallint(5) | NO |
| `EditorialBoardMemberUserId` | int(10) | NO |
| `EditorialBoardMemberJournalUserId` | bigint(19) | YES |
| `EditorialBoardMemberPersonUserId` | bigint(19) | NO |
| `EditorialBoardMemberTaxonomyId` | bigint(19) | YES |
| `RoleJoinOrder` | int(10) | NO |
| `IsFirstJoinedRole` | bit | YES |
| `RoleLevelOrder` | int(10) | NO |
| `IsTopFirstRole` | bit | YES |
| `RoleId` | int(10) | NO |
| `Role` | varchar(50) | YES |
| `RoleAbbr` | varchar(20) | YES |
| `RoleLevel` | varchar(9) | YES |
| `JoinDate` | datetime | YES |
| `EndDate` | datetime | YES |
| `IsActive` | bit | NO |
| `ModifyDate` | datetime | YES |
| `IsFirstTaxonomyRole` | bit | YES |
| `TaxonomyRoleOrder` | int(10) | YES |
| `InauguralArticleStage` | nvarchar(40) | YES |
| `EditorialBoardMemberUserOrder` | bigint(19) | YES |
| `EndReasonId` | int(10) | YES |
| `EndReason` | nvarchar(50) | YES |
| `EndReasonRoleChangeFlag` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopicCoordinator_KeyMetrics

| Column | Type | Nullable |
|---|---|---|
| `KeyMetrics.CoordinatorId` | bigint(19) | NO |
| `BL Author` | int(10) | YES |
| `BL Coordinator` | int(10) | YES |
| `RT Hosted by AE` | int(10) | NO |
| `RT Hosted by AE Own Section` | int(10) | NO |
| `TE EB Max Role` | nvarchar(50) | YES |
| `TE Promotable` | int(10) | YES |
| `RT.Hosted.Count` | int(10) | YES |
| `Last.TopicHosted` | datetime | YES |
| `TimeSince.Last.TopicHosted` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopicCoordinator_Profile

| Column | Type | Nullable |
|---|---|---|
| `CoordinatorId` | bigint(19) | NO |
| `CoordinatorSpaceId` | smallint(5) | YES |
| `CoordinatorUserId` | int(10) | NO |
| `CoordinatorPersonUserId` | bigint(19) | NO |
| `CoordinatorJournalUserId` | bigint(19) | YES |
| `CoordinatorTaxonomyId` | bigint(19) | NO |
| `CoordinatorResearchTopicId` | bigint(19) | NO |
| `IsFrontiers` | varchar(20) | YES |
| `IsQualitricsSurveyForCFP` | bit | NO |
| `IsQualitricsSurveyForClosedRT` | bit | NO |
| `CoordinatorCreateDate` | datetime | NO |
| `CoordinatorModifyDate` | datetime | YES |
| `CoordinatorOrder` | int(10) | NO |
| `CoordinatorUserOrder` | int(10) | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopicEditor_AnalyticBins

| Column | Type | Nullable |
|---|---|---|
| `AnalyticBins.EditorId` | bigint(19) | NO |
| `RT Hosted Bins` | nvarchar(50) | YES |
| `Time since last RT Hosted Bins` | nvarchar(50) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopicEditor_KeyMetrics

| Column | Type | Nullable |
|---|---|---|
| `KeyMetrics.EditorId` | bigint(19) | NO |
| `BL Author` | int(10) | YES |
| `BL Editor` | int(10) | YES |
| `RT Hosted by AE` | int(10) | NO |
| `RT Hosted by AE Own Section` | int(10) | NO |
| `TE EB Max Role` | nvarchar(50) | YES |
| `TE Promotable` | int(10) | YES |
| `RT.Hosted.Count` | int(10) | YES |
| `Last.TopicHosted` | datetime | YES |
| `TimeSince.Last.TopicHosted` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopicEditor_Profile

| Column | Type | Nullable |
|---|---|---|
| `EditorId` | bigint(19) | NO |
| `EditorSpaceId` | smallint(5) | YES |
| `EditorUserId` | int(10) | NO |
| `EditorPersonUserId` | bigint(19) | NO |
| `EditorJournalUserId` | bigint(19) | YES |
| `EditorTaxonomyId` | bigint(19) | NO |
| `EditorResearchTopicId` | bigint(19) | NO |
| `IsFrontiers` | varchar(20) | YES |
| `IsNotificationEnabled` | bit | NO |
| `LastNotificationSendDate` | datetime | YES |
| `EditorCreateDate` | datetime | NO |
| `EditorModifyDate` | datetime | NO |
| `EditorOrder` | bigint(19) | YES |
| `EditorUserOrder` | bigint(19) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ReviewBoardMember_AnalyticBins

| Column | Type | Nullable |
|---|---|---|
| `AnalyticBins.ReviewBoardMemberId` | bigint(19) | NO |
| `ArticlesReviewed.Count.Bin` | nvarchar(50) | YES |
| `ArticlesEdited.Count.Bin` | nvarchar(50) | YES |
| `ArticlesEditedOrReviewed.Count.Bin` | nvarchar(50) | YES |
| `TimeSince.Last.Reviewer.EditingAssignment.Bin` | nvarchar(50) | YES |
| `TimeSince.Last.Reviewer.ReviewAssignment.Bin` | nvarchar(50) | YES |
| `TimeSince.Last.Reviewer.EditingOrReviewAssignment.Bin` | nvarchar(50) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ReviewBoardMember_Invitation

| Column | Type | Nullable |
|---|---|---|
| `Invitation.ReviewBoardMemberId` | bigint(19) | NO |
| `ReviewBoardInvitationId` | bigint(19) | YES |
| `InviterUserId` | int(10) | YES |
| `Inviter` | nvarchar(150) | YES |
| `InviterEmail` | nvarchar(100) | YES |
| `InviteDate` | datetime | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ReviewBoardMember_KeyMetrics

| Column | Type | Nullable |
|---|---|---|
| `KeyMetrics.ReviewBoardMemberId` | bigint(19) | NO |
| `IsTopFirstAssignedRole` | bit | YES |
| `IsReviewMember` | bit | YES |
| `Reviewer.LatestInviteDate` | datetime | YES |
| `Reviewer.WithdrawDate` | datetime | YES |
| `ReviewReportDate.IndependentReviewSubmitted` | datetime | YES |
| `ReviewReportDate.FinalReportSubmitted` | datetime | YES |
| `ArticlesReviewed.Count` | int(10) | YES |
| `ArticlesEdited.Count` | int(10) | YES |
| `ArticlesEditedOrReviewed.Count` | int(10) | YES |
| `Last.Reviewer.ReviewDate` | datetime | YES |
| `Last.Reviewer.EditDate` | datetime | YES |
| `TimeSince.Last.Reviewer.ReviewAssignment` | int(10) | YES |
| `TimeSince.Last.Reviewer.EditingAssignment` | int(10) | YES |
| `TimeSince.Last.Reviewer.EditingOrReviewAssignment` | int(10) | YES |
| `ReviewReportRating` | decimal(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ReviewBoardMember_Profile

| Column | Type | Nullable |
|---|---|---|
| `ReviewBoardMemberId` | bigint(19) | NO |
| `ReviewBoardMemberSpaceId` | smallint(5) | YES |
| `ReviewBoardMemberUserId` | int(10) | YES |
| `ReviewBoardMemberJournalUserId` | bigint(19) | YES |
| `ReviewBoardMemberPersonUserId` | bigint(19) | YES |
| `ReviewBoardMemberArticleId` | bigint(19) | YES |
| `ReviewBoardMemberTaxonomyId` | bigint(19) | YES |
| `Email` | nvarchar(100) | YES |
| `FirstName` | nvarchar(150) | YES |
| `LastName` | nvarchar(150) | YES |
| `Name` | nvarchar(400) | YES |
| `JoinDate` | datetime | YES |
| `RoleId` | int(10) | YES |
| `Role` | varchar(50) | YES |
| `RoleAbbr` | varchar(20) | YES |
| `OriginalRoleId` | int(10) | YES |
| `IsVolunteer` | bit | YES |
| `IsVolunteerExcluded` | bit | YES |
| `VolunteerExclusionReason` | nvarchar(250) | YES |
| `ReviewBoardStatusId` | tinyint(3) | YES |
| `ReviewBoardStatus` | varchar(25) | YES |
| `ReviewBoardMemberUserOrder` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

## [ReportingDataMart].[Process]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### AIRA_Indicators

| Column | Type | Nullable |
|---|---|---|
| `Indicator.Id` | bigint(19) | NO |
| `Article.Id` | bigint(19) | YES |
| `Indicator.Type.Id` | bigint(19) | YES |
| `Indicator.Status.Id` | int(10) | YES |
| `Indicator.Group.Id` | bigint(19) | YES |
| `Indicator.Group.Type.Id` | bigint(19) | YES |
| `Indicator.Group.Status.Id` | int(10) | YES |
| `Category.Id` | bigint(19) | YES |
| `Category.Type.Id` | int(10) | YES |
| `Category.Status.Id` | int(10) | YES |
| `Trigger.Id` | bigint(19) | YES |
| `Trigger.Type.Id` | int(10) | YES |
| `Trigger.Status.Id` | int(10) | YES |
| `ReviewDate` | datetime | YES |
| `EnablerUserId` | int(10) | YES |
| `EnablerEmail` | nvarchar(100) | YES |
| `Description` | nvarchar(150) | YES |
| `EnableDate` | datetime | YES |
| `TransferId` | uniqueidentifier | YES |
| `RowNumberAsc` | bigint(19) | YES |
| `RowNumberDesc` | bigint(19) | YES |

### Accounting_Discount

| Column | Type | Nullable |
|---|---|---|
| `DiscountMappingId` | bigint(19) | NO |
| `DiscountName` | nvarchar(255) | NO |
| `DiscountTypeId` | int(10) | NO |
| `DiscountType` | nvarchar(255) | YES |
| `DiscountCategoryId` | int(10) | NO |
| `DiscountCategory` | nvarchar(255) | YES |
| `IsAggregated` | bit | NO |
| `IsHidden` | bit | NO |
| `IsPublisherDiscount` | bit | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Accounting_InvoiceRecipient

| Column | Type | Nullable |
|---|---|---|
| `PayerId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `InvoiceId` | bigint(19) | NO |
| `Email` | nvarchar(100) | YES |
| `Name` | nvarchar(400) | YES |
| `PayerUserId` | int(10) | YES |
| `PayerTypeId` | int(10) | NO |
| `PayerType` | nvarchar(30) | YES |
| `PayerIsInstitution` | bit | YES |
| `PayerInstitutionOrganizationId` | int(10) | YES |
| `PayerInstitutionRosstId` | nvarchar(40) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | YES |
| `LegacyOrganization` | nvarchar(700) | YES |
| `LegacyDepartment` | nvarchar(800) | YES |
| `LegacyLaboratory` | nvarchar(400) | YES |
| `Address` | nvarchar(500) | YES |
| `City` | nvarchar(50) | YES |
| `PostalCode` | nvarchar(50) | YES |
| `State` | nvarchar(50) | YES |
| `CountryId` | char(3) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | varchar(13) | YES |
| `Country3RegionsBinFocus` | nvarchar(50) | YES |
| `Country5RegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin` | nvarchar(50) | YES |
| `Country13RegionsBin` | nvarchar(50) | YES |
| `PhoneNumber` | nvarchar(30) | YES |
| `UserReference` | nvarchar | YES |
| `Comments` | nvarchar(500) | YES |
| `AttentionName` | nvarchar(350) | YES |
| `AttentionEmail` | nvarchar(150) | YES |
| `AttentionIsPayer` | bit | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `IsDeleted` | bit | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Accounting_InvoiceSummary

| Column | Type | Nullable |
|---|---|---|
| `InvoiceNo` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `TotalRevenue` | numeric(38) | YES |
| `TotalDiscountAmount` | numeric(38) | YES |
| `TotalVATAmount` | numeric(38) | YES |
| `TotalPaidAmount` | numeric(38) | YES |
| `PaidAmount.BankTransfer` | numeric(38) | YES |
| `PaidAmount.BalanceWaived` | numeric(38) | YES |
| `PaidAmount.CreditCard` | numeric(38) | YES |
| `PaidAmount.Refund` | numeric(38) | YES |
| `PaidAmount.UseAward` | numeric(38) | YES |
| `PaidAmount.BankCheque` | numeric(38) | YES |
| `PaidAmount.BankPaypal` | numeric(38) | YES |
| `PaidAmount.BalanceWaivedOverpayment` | numeric(38) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Accounting_InvoiceTransactions

| Column | Type | Nullable |
|---|---|---|
| `TransactionId` | int(10) | NO |
| `InvoiceId` | bigint(19) | NO |
| `InvoiceId.Original` | int(10) | NO |
| `InvoiceNoDisplay` | nvarchar(50) | YES |
| `InvoiceNo` | int(10) | NO |
| `InvoiceItemId` | bigint(19) | NO |
| `RevenueId` | int(10) | YES |
| `RevenueItemId` | bigint(19) | YES |
| `InvoiceItemDiscountId` | bigint(19) | NO |
| `RevenueItemDiscountId` | bigint(19) | YES |
| `ArticleId` | bigint(19) | YES |
| `DiscountId` | bigint(19) | YES |
| `DiscountMappingId` | int(10) | NO |
| `PaymentId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Amount` | numeric(19) | YES |
| `VATRate` | numeric(9) | YES |
| `ExchangeRate.USD` | numeric(9) | YES |
| `ExchangeRate.CHF` | numeric(9) | YES |
| `TransactionTypeId` | int(10) | NO |
| `InvoiceDueAmount` | numeric(18) | YES |
| `InvoiceVATAmount` | numeric(21) | YES |
| `InvoiceAmountOutstanding` | numeric(18) | YES |
| `InvoiceCurrency` | nvarchar(10) | YES |
| `InvoiceValidityId` | tinyint(3) | YES |
| `InvoiceValidity` | varchar(9) | YES |
| `InvoiceStatusId` | tinyint(3) | YES |
| `InvoiceStatus` | varchar(9) | YES |
| `InvoiceDiscountCode` | nvarchar(500) | YES |
| `InvoiceDate` | datetime | YES |
| `InvoiceDueDate` | datetime | YES |
| `InvoiceCreateDate` | date | YES |
| `InvoiceModifyDate` | datetime | YES |
| `InvoiceVersion` | int(10) | YES |
| `InvoiceIsDeleted` | bit | NO |
| `InvoiceIsProforma` | bit | YES |
| `InvoiceIsLatest` | bit | NO |
| `InvoiceId.Latest` | bigint(19) | NO |
| `InvoiceVersion.Latest` | bigint(19) | YES |
| `IsLastInvoiceinDate` | bit | NO |
| `TransactionAmount` | numeric(19) | YES |
| `GrossAmount` | numeric(19) | YES |
| `DiscountAmount` | numeric(19) | YES |
| `VATAmount` | numeric(19) | YES |
| `PaidAmount` | numeric(19) | YES |
| `NetAmount.ExclVAT` | numeric(19) | YES |
| `NetAmount.InclVAT` | numeric(19) | YES |
| `DiscountAmount.Aggregated` | numeric(19) | YES |
| `DiscountAmount.HiddenDiscounts` | numeric(19) | YES |
| `DiscountAmount.PublisherDiscounts` | numeric(19) | YES |
| `DiscountAmount.SocietyDiscounts` | numeric(19) | YES |
| `DiscountCode` | nvarchar(500) | YES |
| `DiscountIsDeleted` | bit | YES |
| `IsPrepayedInvoice` | bit | YES |
| `LastPaymentDate` | datetime | YES |
| `PaymentsTypeOrder` | bigint(19) | YES |
| `PaymentDelayDays` | int(10) | YES |
| `DaysToPayment` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Accounting_Payment

| Column | Type | Nullable |
|---|---|---|
| `PaymentId` | bigint(19) | NO |
| `PaymentTypeId` | int(10) | NO |
| `PaymentType` | nvarchar(50) | YES |
| `PaymentDescription` | nvarchar(100) | YES |
| `PaymentDate` | datetime | YES |
| `PaymentCreateDate` | datetime | NO |
| `PaymentAccountId` | bigint(19) | YES |
| `PaymentAccount` | nvarchar(50) | YES |
| `PaymentBankReferenceId` | nvarchar(30) | YES |
| `PaymentIsVisible` | bit | YES |
| `PaymentIsDeleted` | bit | YES |
| `PayerUserId` | int(10) | YES |
| `PayerName` | nvarchar(400) | YES |
| `PayerEmail` | nvarchar(150) | YES |
| `PayerAddress` | nvarchar(500) | YES |
| `PayerCity` | nvarchar(50) | YES |
| `PayerCountryId` | char(3) | YES |
| `PayerCountry` | nvarchar(100) | YES |
| `PayerContinent` | varchar(13) | YES |
| `PayerOrganizationId` | int(10) | YES |
| `PayerRosstId` | nvarchar(40) | YES |
| `PayerOrganization` | nvarchar(200) | YES |
| `PayerIsInstitution` | bit | YES |
| `PayerInstitutionOrganizationId` | int(10) | YES |
| `PayerInstitutionRosstId` | nvarchar(40) | YES |
| `AttentionIsPayer` | bit | YES |
| `PayerAttentionName` | nvarchar(350) | YES |
| `PayerAttentionEmail` | nvarchar(150) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Accounting_RevenueAllocation

| Column | Type | Nullable |
|---|---|---|
| `InvoiceId` | bigint(19) | NO |
| `InvoiceId.Original` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `InvoiceNoDisplay` | nvarchar(50) | YES |
| `ArticleId` | bigint(19) | YES |
| `ArticleId.Original` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `ArticleType` | nvarchar(50) | YES |
| `Article.Invoices.Count` | int(10) | YES |
| `LastPaymentDate` | datetime | YES |
| `InvoiceCurrency` | nvarchar(10) | YES |
| `JournalCurrency` | nvarchar(10) | YES |
| `ExchangeRate.InvoiceCurrencyToJournalCurrency` | float(53) | YES |
| `GrossAmount.InvoiceCurrrency` | numeric(38) | YES |
| `GrossAmount.JournalCurrency` | numeric(18) | YES |
| `DiscountAmount.PublisherDiscounts.JournalCurrency` | numeric(18) | YES |
| `DiscountAmount.SocietyDiscounts.JournalCurrency` | numeric(18) | YES |
| `Revenue.Frontiers.JournalCurrency` | numeric(18) | YES |
| `Revenue.Society.JournalCurrency` | numeric(18) | YES |
| `NetRevenue.Frontiers.JournalCurrency` | numeric(18) | YES |
| `NetRevenue.Society.JournalCurrency` | numeric(18) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Accounting_RevenueItem

| Column | Type | Nullable |
|---|---|---|
| `RevenueItemId` | bigint(19) | NO |
| `RevenueItem` | nvarchar(100) | YES |
| `RevenueId` | int(10) | YES |
| `Revenue` | nvarchar(50) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Accounting_TransactionType

| Column | Type | Nullable |
|---|---|---|
| `TransactionTypeId` | int(10) | NO |
| `TransactionType` | nvarchar(50) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ArticlesFunders

| Column | Type | Nullable |
|---|---|---|
| `ArticlesFundersId` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `FunderId` | bigint(19) | NO |
| `Awards` | nvarchar(4000) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### CRM_Employee

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `UserCRMId` | char(18) | NO |
| `Email` | nvarchar(128) | YES |
| `Firstname` | nvarchar(40) | YES |
| `Lastname` | nvarchar(80) | YES |
| `FullName` | nvarchar(121) | NO |
| `EmployeeRoleId` | nvarchar(18) | YES |
| `EmployeeRole` | nvarchar(80) | YES |
| `EmployeeRolePrefix` | nvarchar(80) | YES |
| `EmployeeRoleDescription` | nvarchar(80) | YES |
| `EmploymentCountryId` | char(3) | YES |
| `EmployeeCreateDate` | datetime | YES |
| `EmployeeModifyDate` | datetime | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### CRM_Opportunities

| Column | Type | Nullable |
|---|---|---|
| `OpportunityStageCRMId` | char(18) | NO |
| `OpportunityCRMId` | char(18) | NO |
| `RecordTypeCRMId` | char(18) | NO |
| `ParentOpportunityCRMId` | char(18) | YES |
| `CampaignCRMId` | char(18) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `ResearchTopicId` | bigint(19) | YES |
| `OwnerUserId` | int(10) | YES |
| `ContactCampaignMemberCRMId` | char(18) | YES |
| `StageDuration` | int(10) | YES |
| `StageDurationDerived` | int(10) | YES |
| `StageDurationRolling` | int(10) | YES |
| `IsStageMovedForward` | tinyint(3) | YES |
| `IsCurrentStage` | tinyint(3) | YES |
| `IsCurrentStageSQL` | tinyint(3) | YES |
| `IsCurrentStageInterested` | tinyint(3) | YES |
| `IsCurrentStageCommitment` | tinyint(3) | YES |
| `IsCurrentStageFinalStage` | tinyint(3) | YES |
| `IsCurrentStageInDEO` | tinyint(3) | YES |
| `IsOpportunityClosed` | tinyint(3) | YES |
| `IsOpportunityWon` | tinyint(3) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### CRM_Opportunity

| Column | Type | Nullable |
|---|---|---|
| `OpportunityCRMId` | char(18) | NO |
| `OpportunityName` | nvarchar(500) | NO |
| `RecordTypeCRMId` | char(18) | NO |
| `ParentOpportunityCRMId` | char(18) | YES |
| `CampaignCRMId` | char(18) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `ResearchTopicId` | bigint(19) | YES |
| `RTOpportunityCountry` | nvarchar(100) | YES |
| `RTOpportunityRank` | int(10) | YES |
| `OwnerUserId` | int(10) | YES |
| `ContactUserId` | int(10) | YES |
| `ContactEmailAddress` | nvarchar(80) | YES |
| `CurrentStage` | nvarchar(40) | NO |
| `PartOfACP` | bit | YES |
| `OpportunityCreateDate` | datetime | NO |
| `OpportunityCloseDate` | datetime | YES |
| `OpportunityModifyDate` | datetime | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### CRM_OpportunityStage

| Column | Type | Nullable |
|---|---|---|
| `OpportunityStageCRMId` | char(18) | NO |
| `OpportunityCRMId` | char(18) | NO |
| `StageOrder` | int(10) | NO |
| `IsCurrentStage` | tinyint(3) | NO |
| `Stage.Previous` | nvarchar(40) | YES |
| `Stage` | nvarchar(40) | NO |
| `StageDuration` | int(10) | YES |
| `Stage.Next` | nvarchar(40) | YES |
| `StageEntryDate` | datetime | YES |
| `StageExitDate` | datetime | YES |
| `RTOpportunityStageRank` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ContributorTracking

| Column | Type | Nullable |
|---|---|---|
| `ContributorTrackingId` | bigint(19) | NO |
| `ContributorId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `TrackingEventDate` | date | YES |
| `ResearchTopicId` | bigint(19) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `PersonUserId` | bigint(19) | YES |
| `ContributorTrackingEventId` | int(10) | NO |
| `ContributorTrackingId.Original` | int(10) | NO |
| `URL` | nvarchar(1000) | NO |
| `ReferrerURL` | nvarchar(1000) | YES |
| `VisitDate` | datetime | YES |
| `ReferrerEmailType` | nvarchar(250) | YES |
| `Source` | nvarchar(128) | YES |
| `CreateDate` | datetime | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Contributor_Invitations

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicContributorArticleId` | int(10) | NO |
| `ResearchTopicId` | bigint(19) | YES |
| `ContributorId` | bigint(19) | YES |
| `ArticleId` | bigint(19) | YES |
| `SpaceId` | smallint(5) | YES |
| `ResearchTopicOnlineDate` | datetime | YES |
| `ResearchTopicDeletedDate` | datetime | YES |
| `ResearchTopicJournalTaxonomyId` | bigint(19) | YES |
| `ArticleStageDate.ReceivedbyJournal` | datetime | YES |
| `ArticleStageDate.Accepted` | datetime | YES |
| `HasContributorBeenInvited` | bit | YES |
| `HasContributorBeenInvited.Cfp` | bit | YES |
| `ContributorInvitationDate.logical` | datetime | YES |
| `ArticleIsfromatleastoneInvitedContributor` | int(10) | YES |
| `ArticleSubmissionOrderSameResearchTopic` | bigint(19) | YES |
| `ArticleSubmissionOrderAnyResearchTopic` | bigint(19) | YES |
| `HasContributorSubmittedbeforeonanyArticle` | bit | YES |
| `ContributorIsArticleCorrespondingAuthor` | bit | YES |
| `ContributorIsArticleSubmittingAuthor` | bit | YES |
| `AuthorIsEBM` | bit | YES |
| `HasContributorParticipatedinArticleswithConfirmedContributor` | bit | YES |
| `FunnelContributorArticleInvitedBins` | int(10) | YES |

### Contributor_Invitations_Targets

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicContributorArticleId` | bigint(19) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `ResearchTopicOnlineDate` | date | YES |
| `ResearchTopicDeletedDate` | date | YES |
| `ArticleStageDate.Submitted` | date | YES |
| `ArticleStageDate.Accepted` | date | YES |
| `PostedResearchTopics.Target` | decimal(24) | YES |
| `SubmittedArticles.Target` | decimal(24) | YES |
| `SubmittedRTArticlesbyContributors.Target` | decimal(24) | YES |
| `AcceptedArticles.Target` | decimal(24) | YES |
| `SubmittedArticles.JournalTarget` | decimal(24) | YES |
| `AcceptedArticles.JournalTarget` | decimal(24) | YES |
| `FunnelContributorArticleInvitedBins` | int(10) | YES |

### EditorialBoard_Invitations

| Column | Type | Nullable |
|---|---|---|
| `EditorialBoardInvitationId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `TaxonomyId` | bigint(19) | NO |
| `InvitationDate` | datetime | NO |
| `InvitationTypeId` | int(10) | NO |
| `InvitationType` | varchar(50) | YES |
| `InvitationSourceId` | int(10) | YES |
| `InvitationSource` | varchar(100) | YES |
| `InviterUserId` | int(10) | YES |
| `InviterEmail` | nvarchar(300) | YES |
| `InviterPersonUserId` | bigint(19) | YES |
| `InviterName` | nvarchar(400) | YES |
| `InviteeUserId` | int(10) | YES |
| `InviteeEmail` | varchar(150) | NO |
| `InviteePersonUserId` | bigint(19) | YES |
| `InviteeName` | nvarchar(452) | YES |
| `InviteeRoleId` | varchar(10) | NO |
| `InviteeRole` | varchar(50) | YES |
| `InviteeIsOnBoard` | bit | YES |
| `InvitationActivationNumber` | uniqueidentifier | NO |
| `InvitationStatusId` | int(10) | YES |
| `InvitationStatus` | varchar | YES |
| `InvitationStatusModifyDate` | datetime | YES |
| `LastReminderDate` | datetime | YES |
| `TotalReminderCount` | int(10) | YES |
| `DeclinationReasonId` | int(10) | YES |
| `DeclinationReason` | varchar(150) | YES |
| `DeclinationPersonalNote` | varchar | YES |
| `DeclinationComment` | varchar | YES |
| `InvitationReviewStatusId` | int(10) | YES |
| `InvitationReviewStatus` | nvarchar(100) | YES |
| `ReviewDecisionTypeId` | int(10) | YES |
| `ReviewDecisionType` | nvarchar(100) | YES |
| `ReviewRejectionReasonId` | int(10) | YES |
| `ReviewRejectionReason` | varchar(150) | YES |
| `ReviewInvalidReasonId` | int(10) | YES |
| `ReviewInvalidReason` | varchar(150) | YES |
| `SuggestedEditorId` | bigint(19) | YES |
| `SuggestedEditorUserId` | int(10) | YES |
| `SuggestedEditorEmail` | varchar(150) | YES |
| `SuggestedEditorPersonUserId` | bigint(19) | YES |
| `SuggestedEditorName` | nvarchar(301) | YES |
| `SuggestionMethodId` | bigint(19) | YES |
| `SuggestionMethod` | varchar(100) | YES |
| `SuggestionMethodType` | nvarchar(200) | YES |
| `SuggestionSourceId` | bigint(19) | YES |
| `SuggestionSource` | varchar(100) | YES |
| `SuggestionDiscardReasonId` | bigint(19) | YES |
| `SuggestionDiscardReason` | varchar(100) | YES |
| `SuggestionComments` | varchar(200) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### JournalRole_MembershipMetrics

| Column | Type | Nullable |
|---|---|---|
| `DateId` | datetime | NO |
| `TaxonomyId` | bigint(19) | NO |
| `JournalRoleId` | nvarchar(10) | NO |
| `EndReasonId` | int(10) | NO |
| `EndReasonRoleChangeFlag` | int(10) | NO |
| `Cumulative_Joined_Members.Count` | int(10) | NO |
| `Cumulative_Ended_Members.Count` | int(10) | NO |
| `Cumulative_Active_Members.Count` | int(10) | NO |
| `Ended_Members.Count` | int(10) | NO |
| `Joined_Members.Count` | int(10) | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ReviewBoard_Invitations

| Column | Type | Nullable |
|---|---|---|
| `ReviewBoardInvitationId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | YES |
| `ArticleId` | bigint(19) | YES |
| `UserId` | int(10) | YES |
| `Email` | nvarchar(150) | NO |
| `EmailId` | int(10) | YES |
| `PersonUserId` | bigint(19) | YES |
| `InviteeName` | nvarchar(200) | YES |
| `OriginalRoleId` | int(10) | YES |
| `RoleId` | int(10) | NO |
| `WorkflowId` | int(10) | YES |
| `WorkflowEmailId` | bigint(19) | YES |
| `WorkflowMessageTypeId` | int(10) | YES |
| `InviterUserId` | int(10) | NO |
| `InviterRoleId` | int(10) | YES |
| `InviteDate` | datetime | NO |
| `ReplyDate` | datetime | YES |
| `InvitationReply` | nvarchar(150) | YES |
| `ReviewActionReasonId` | bigint(19) | YES |
| `ReviewActionReasonLabel` | nvarchar(50) | YES |
| `InvitationStatusDate` | datetime | YES |
| `IsAutomaticInvitation` | bit | YES |
| `InvitationBatch` | int(10) | YES |
| `InvitationMethodId` | int(10) | YES |
| `ReviewBoardInvitationStatusId` | int(10) | YES |
| `InvitationAlgorithmTypeId` | int(10) | YES |
| `InvitationAudienceGroupId` | int(10) | YES |
| `InvitationRelevancyScore` | float(53) | YES |
| `ManuscriptContextPromptVersion` | nvarchar(50) | YES |
| `ManuscriptContextModel` | nvarchar(100) | YES |
| `PerfectEmailPromptVersion` | nvarchar(50) | YES |
| `PerfectEmailModel` | nvarchar(100) | YES |
| `ExplainabilityPromptVersion` | nvarchar(50) | YES |
| `ExplainabilityModel` | nvarchar(100) | YES |
| `IsMatch` | bit | YES |
| `PersonId.Original` | bigint(19) | YES |
| `PersonId` | bigint(19) | YES |
| `InvitationAudienceId` | int(10) | YES |
| `InvitationAlgorithmDetailId` | int(10) | YES |
| `SystemRoleId` | int(10) | YES |
| `RowVersion` | binary(8) | YES |

### ReviewBoard_Invitations_Email

| Column | Type | Nullable |
|---|---|---|
| `EmailId` | bigint(19) | NO |
| `Email` | nvarchar(300) | YES |
| `CreateDate` | datetime | NO |

### ReviewTimes

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `AEUserId` | int(10) | YES |
| `AEName` | nvarchar(300) | YES |
| `IRRSubBy1st` | datetime | YES |
| `IRRSubBy2nd` | datetime | YES |
| `1stAUTReply` | datetime | YES |
| `2ndAUTReply` | datetime | YES |
| `3rdAUTReply` | datetime | YES |
| `1stREReply` | datetime | YES |
| `2ndREReply` | datetime | YES |
| `3rdREReply` | datetime | YES |
| `LatestSubsequentAUTReply` | datetime | YES |
| `LatestREReply` | datetime | YES |
| `Current Workflow` | nvarchar(10) | YES |
| `Next Time Out` | nchar(10) | YES |
| `Next Time Out Date` | datetime | YES |
| `PrevWF` | nvarchar(10) | YES |
| `PrevTO` | nchar(10) | YES |
| `PrevTODate` | datetime | YES |
| `REWithdrew` | int(10) | YES |
| `WithdrawalCount` | int(10) | YES |
| `REWitdrawalReason` | nvarchar(300) | YES |
| `REEditorialRole` | varchar(6) | YES |

## [ReportingDataMart].[Product]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### Article_Accounting

| Column | Type | Nullable |
|---|---|---|
| `Accounting.ArticleId` | bigint(19) | NO |
| `IsPayingArticle` | bit | NO |
| `IsPayingArticleYN` | varchar(1) | YES |
| `IsPayingArticleType` | bit | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Article_AnalyticBins

| Column | Type | Nullable |
|---|---|---|
| `AnalyticBins.ArticleId` | bigint(19) | NO |
| `Time in ReviewTime` | nvarchar(20) | YES |
| `Time in InitialValidation` | nvarchar(20) | YES |
| `Time in EditorialAssignment` | nvarchar(20) | YES |
| `Time in AEAssignment` | nvarchar(20) | YES |
| `Time in REAssignment` | nvarchar(20) | YES |
| `Time in REAssignment.Static` | nvarchar(20) | YES |
| `Time in IndependentReview` | nvarchar(20) | YES |
| `Time in InteractiveReview` | nvarchar(20) | YES |
| `Time in FinalValidation` | nvarchar(20) | YES |
| `Time to Send First REV Invitation` | nvarchar(20) | YES |
| `Time to Assign Any AE` | nvarchar(20) | YES |
| `Time to Assign Preferred AE` | nvarchar(20) | YES |
| `Time to Assign TE` | nvarchar(20) | YES |
| `Time to Assign AE Manually` | nvarchar(20) | YES |
| `Time to Assign any Reviewer` | nvarchar(20) | YES |
| `Time to Assign any Reviewer.Static` | nvarchar(20) | YES |
| `Time to Assign Required Reviewer` | nvarchar(20) | YES |
| `Time to Assign Required Reviewer.Static` | nvarchar(20) | YES |
| `Time to Assign RE` | nvarchar(20) | YES |
| `Time to Assign REV` | nvarchar(20) | YES |
| `Time to Submit required IRRs` | nvarchar(20) | YES |
| `Time to Submit IRR by RE` | nvarchar(20) | YES |
| `Time Submit IRR by a Reviewer` | nvarchar(20) | YES |
| `Time Submit Any IRR` | nvarchar(20) | YES |
| `Time to First reply of the Author` | nvarchar(20) | YES |
| `Time to Last Author Reply` | nvarchar(20) | YES |
| `Time to First Reviewer Reply` | nvarchar(20) | YES |
| `Time to Last RE Reply` | nvarchar(20) | YES |
| `TimeSinceLastSubmission` | nvarchar(20) | YES |
| `TimeSinceLastAcceptance` | nvarchar(20) | YES |
| `TimeSinceLastRejection` | nvarchar(20) | YES |
| `TimeSinceLastDecision` | nvarchar(20) | YES |
| `TimeSinceLastPublication` | nvarchar(20) | YES |
| `PreviousReviewDecisionTime` | nvarchar(20) | YES |
| `TimeOnlinetoSubmitted` | nvarchar(20) | YES |
| `TimeFirstSubmissionDeadlinetoSubmitted` | nvarchar(20) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Article_Dates

| Column | Type | Nullable |
|---|---|---|
| `Dates.ArticleId` | bigint(19) | NO |
| `StageDate` | datetime | YES |
| `StageDate.InPreparation` | datetime | YES |
| `StageDate.Submitted` | datetime | YES |
| `StageDate.ReceivedByJournal` | datetime | YES |
| `StageDate.InitialValidation` | datetime | YES |
| `StageDate.JournalTransferCompleted` | datetime | YES |
| `StageDate.EditorialAssignment.Source` | datetime | YES |
| `StageDate.InReview` | datetime | YES |
| `StageDate.InIndependentReview` | datetime | YES |
| `StageDate.InInteractiveReview` | datetime | YES |
| `StageDate.ReviewFinalized` | datetime | YES |
| `StageDate.RejectionRecommended` | datetime | YES |
| `StageDate.Rejected` | datetime | YES |
| `StageDate.FinalValidation` | datetime | YES |
| `StageDate.RecommendationForRejectionRevoked` | datetime | YES |
| `StageDate.Accepted` | datetime | YES |
| `StageDate.InProduction` | datetime | YES |
| `StageDate.AuthorProof` | datetime | YES |
| `StageDate.AuthorProofApproved` | datetime | YES |
| `StageDate.Published` | datetime | YES |
| `StageDate.Deleted` | datetime | YES |
| `StageDate.Decision` | datetime | YES |
| `PartnerAcceptArticleDateTime` | datetime | YES |
| `PartnerRecommendRejectionDateTime` | datetime | YES |
| `PartnerRejectionDateTime` | datetime | YES |
| `PartnerRecommendValidationDateTime` | datetime | YES |
| `PartnerRecommendValidationApprovalDateTime` | datetime | YES |
| `PartnerPrescreeningEinCAssignedDateTime` | datetime | YES |
| `PartnerFinalizeReviewDateTime` | datetime | YES |
| `PartnerMonitorAEtoAccept/RejectDateTime` | datetime | YES |
| `PartnerAEtabnotificationDateTime` | datetime | YES |
| `PartnerAUTtabnotificationDateTime` | datetime | YES |
| `PartnerAEtab-MonitoringAUTtoreplyDateTime` | datetime | YES |
| `PartnerRe-submitManuscriptDateTime` | datetime | YES |
| `PartnerMonitorAUT_To_ResubmitReplyDateTime_Days` | datetime | YES |
| `SuggestedforResearchTopic.InviteDate` | datetime | YES |
| `SuggestedforResearchTopic.DiscardDate` | datetime | YES |
| `SuggestedforResearchTopic.AuthorAcceptDate` | datetime | YES |
| `SuggestedforResearchTopic.AuthorDeclineDate` | datetime | YES |
| `FirstPublishDate` | datetime | YES |
| `RequestforAuthortoReviseManuscriptDateTime` | datetime | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Article_KeyMetrics

| Column | Type | Nullable |
|---|---|---|
| `KeyMetrics.ArticleId` | bigint(19) | NO |
| `EditorialAssignmentDate` | datetime | YES |
| `1st.Editor.JoinDate` | datetime | YES |
| `Reviewer.First.JoinDate` | datetime | YES |
| `Reviewer.Second.JoinDate` | datetime | YES |
| `Reviewer.First.JoinDate.Static` | datetime | YES |
| `Reviewer.Second.JoinDate.Static` | datetime | YES |
| `REAssignment.JoinDate` | datetime | YES |
| `REAssignment.JoinDate.Static` | datetime | YES |
| `Reviewer.First.IndependentReviewSubmitted` | datetime | YES |
| `Reviewer.Last.IndependentReviewSubmitted` | datetime | YES |
| `Avg.DaystoAssign.PreferredAE` | int(10) | YES |
| `Avg.DaystoAssign.AnyAE` | int(10) | YES |
| `Avg.DaystoAssign.EOF` | int(10) | YES |
| `Avg.DaystoAssign.TE` | int(10) | YES |
| `Avg.DaystoAssign.Manual` | int(10) | YES |
| `Avg.DaystoAssign.AnyReviewer` | int(10) | YES |
| `Avg.DaystoAssign.AnyReviewer.Static` | int(10) | YES |
| `Avg.DaystoAssign.RE` | int(10) | YES |
| `Avg.DaystoAssign.REV` | int(10) | YES |
| `Avg.DaystoSubmit.RequiredIIR` | int(10) | YES |
| `Avg.DaystoSubmit.IIRRE` | int(10) | YES |
| `Avg.DaystoSubmit.IIRREV` | int(10) | YES |
| `Avg.DaystoSubmit.AnyIIR` | int(10) | YES |
| `Avg.Daysto.1stAUTReply` | int(10) | YES |
| `Avg.Daysto.LatestAUTReply` | int(10) | YES |
| `Avg.Daysto.1stREReply` | int(10) | YES |
| `Avg.Daysto.LatestREReply` | int(10) | YES |
| `Avg.Daysto.ReviewFinalized` | int(10) | YES |
| `DaysTo.Reviewer.First.Invitation` | int(10) | YES |
| `DaysTo.Reviewer.First.InvitationByEditor` | int(10) | YES |
| `DaysIn.ReviewTime` | int(10) | YES |
| `DaysIn.InitialValidation` | int(10) | YES |
| `DaysIn.EditorialAssignment` | int(10) | YES |
| `DaysIn.AEAssignment` | int(10) | YES |
| `DaysIn.REAssignment` | int(10) | YES |
| `DaysIn.REAssignment.Static` | int(10) | YES |
| `DaysIn.IndependentReview` | int(10) | YES |
| `DaysIn.InteractiveReview` | int(10) | YES |
| `DaysIn.FinalValidation` | int(10) | YES |
| `DaysIn.ReviewFinalized` | int(10) | YES |
| `Avg.DaystoAssign.RequiredReviewer` | int(10) | YES |
| `Avg.DaystoAssign.RequiredReviewer.Static` | int(10) | YES |
| `Time.OnlinetoSubmitted` | int(10) | YES |
| `Time.FirstSubmissionDeadlinetoSubmitted` | int(10) | YES |
| `DecidedDate` | datetime | YES |
| `ResearchTopicTimePostedtoSubmission` | int(10) | YES |
| `CountViews` | int(10) | YES |
| `CountDownloads` | int(10) | YES |
| `CountCitations` | int(10) | YES |
| `CountArticleCitations` | int(10) | YES |
| `CountFrontiersViews` | int(10) | YES |
| `CountFrontiersDownloads` | int(10) | YES |
| `CountPMCViews` | int(10) | YES |
| `CountPMCDownloads` | int(10) | YES |
| `CountScopusCitations` | int(10) | YES |
| `CountCrossrefCitations` | int(10) | YES |
| `ArticleIsCOVIDRelated` | bit | YES |
| `ArticleIsFromInvitedContributor` | bit | YES |
| `ArticleIsFromConfirmedContributor` | bit | YES |
| `ArticleHasBeenTransferred` | bit | YES |
| `IsFaaSTransfer` | bit | YES |
| `HasFaaSTransferOpportunity` | bit | YES |
| `HasBeenFaaSTransferred` | bit | YES |
| `SourceSpaceId` | int(10) | YES |
| `SourceArticleId` | bigint(19) | YES |
| `SourceTaxonomyId` | bigint(19) | YES |
| `EinCFinalValidationApprovalDays` | int(10) | YES |
| `EinCRejectionDays` | int(10) | YES |
| `EOFInitialValidationChecksDays` | int(10) | YES |
| `AEProvAcceptToEOFEinCValidationDays` | int(10) | YES |
| `FinalisedReviewtoEditorCommentsDays` | int(10) | YES |
| `EditorCommentstoAuthorCommentsDays` | int(10) | YES |
| `EditorCommentsUntilResubmissionDays` | int(10) | YES |
| `ReviewReportRating` | decimal(10) | YES |
| `IsAnyAuthorInWatchlist` | bit | YES |
| `DaysIn.ActivePipeline` | int(10) | YES |
| `ArticleStageDetail` | nvarchar(50) | YES |
| `ArticlesRejectedAtStage` | nvarchar(50) | YES |
| `ArticlesRejectedAtStage.Static` | nvarchar(50) | YES |
| `Time.FirstDecision` | int(10) | YES |
| `DeskAcceptedArticle` | bit | YES |
| `SubmissionPassedDeskReview` | nvarchar(20) | YES |
| `Time to Author Resubmission from Revision Request` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Article_Keywords

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(50) | NO |
| `KeywordId` | bigint(19) | NO |
| `Keyword` | nvarchar(256) | NO |
| `SortOrder` | tinyint(3) | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Article_Organization

| Column | Type | Nullable |
|---|---|---|
| `Organization.ArticleId` | bigint(19) | NO |
| `AuthorsOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `AuthorsOrganizationsHighestRankFrontiersPriorityOrganizationId` | bigint(19) | YES |
| `AuthorsOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `AuthorsOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `IsAnyAuthorOrganizationCountryInWatchlist` | bit | YES |
| `PrimaryOrganizationId` | bigint(19) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `Country3RegionsBinFocus` | nvarchar(50) | YES |
| `Country4RegionsBin` | nvarchar(50) | YES |
| `Country5RegionsBin` | nvarchar(50) | YES |
| `Country7RegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin` | nvarchar(50) | YES |
| `Country13RegionsBin` | nvarchar(50) | YES |
| `CountryFocusRegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin-China` | nvarchar(50) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(50) | YES |
| `CountryRejectionRate` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Article_Other

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `FundingStatement` | nvarchar(4000) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Article_Profile

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(100) | NO |
| `ArticleId.Original` | int(10) | NO |
| `ArticleResearchTopicId` | bigint(19) | YES |
| `ArticleTaxonomyId` | bigint(19) | YES |
| `ArticleJournalTaxonomyId` | bigint(19) | YES |
| `IsResearchTopic` | bit | YES |
| `DOI` | nvarchar(50) | YES |
| `Title` | nvarchar(1000) | NO |
| `CreateDate` | datetime | NO |
| `ArticleTypeId.Original` | int(10) | NO |
| `ArticleTypeId` | bigint(19) | NO |
| `ArticleType` | nvarchar(50) | NO |
| `ArticleTypeCategory` | nvarchar(10) | YES |
| `ArticleSequenceNumber.Original` | int(10) | NO |
| `HasSupplementaryMaterials` | bit | NO |
| `RequestedRevisionLevelId` | int(10) | YES |
| `IsReviewFastForward` | bit | YES |
| `IsDirectCommission` | bit | NO |
| `IsRTIC` | bit | YES |
| `StageId` | int(10) | NO |
| `Stage` | nvarchar(40) | YES |
| `StageCategoryId` | int(10) | YES |
| `StageCategory` | nvarchar(30) | YES |
| `IsSubmitted` | bit | NO |
| `IsAccepted` | bit | NO |
| `IsPublished` | bit | NO |
| `IsRejected` | bit | NO |
| `IsDeleted` | bit | NO |
| `IsDecided` | bit | NO |
| `SubmissionType` | nvarchar(30) | YES |
| `AcceptedAtStageId` | int(10) | YES |
| `AcceptedAtStage` | nvarchar(40) | YES |
| `RejectedAtStageId` | int(10) | YES |
| `RejectedAtStage` | nvarchar(100) | YES |
| `SuggestedforResearchTopic.StatusId` | int(10) | YES |
| `EOfComments` | nvarchar | YES |
| `EOfPOfComments` | nvarchar | YES |
| `JournalTeamComments` | nvarchar | YES |
| `LastEOfCommentDate` | datetime | YES |
| `LastEOfPOfCommentDate` | datetime | YES |
| `LastComment` | datetime | YES |
| `URLArticlePage` | nvarchar(100) | YES |
| `ShortURLArticlePage` | nvarchar(50) | YES |
| `ShortURLReviewForum` | nvarchar(50) | YES |
| `ArticleURL` | nvarchar(180) | YES |
| `URLReviewForum` | nvarchar(169) | YES |
| `IsControversial` | bit | NO |
| `ControversialityReason` | nvarchar(30) | YES |
| `JournalVolume` | int(10) | YES |
| `ResearchTopicAssignmentType.Latest` | nvarchar(30) | YES |
| `ResearchTopicAssignmentDate.Latest` | datetime | YES |
| `AssignmentResearchTopicId` | bigint(19) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Article_PublishingMetrics

| Column | Type | Nullable |
|---|---|---|
| `PublishingMetrics.ArticleId` | bigint(19) | NO |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Article_RankingRatings

| Column | Type | Nullable |
|---|---|---|
| `RankingRatings.ArticleId` | bigint(19) | NO |
| `QualityRating.Study.Overall` | float(53) | YES |
| `QualityRating.Study.OverallRatingBin` | nvarchar(20) | YES |
| `QualityRating.Study.Average` | int(10) | YES |
| `AvgQualityRating` | int(10) | YES |
| `ArticleLanguageRating` | nvarchar(50) | YES |
| `AvgGeneralInterestRating` | int(10) | YES |
| `AuthorIsEBM` | bit | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `RankArticleSubmitted` | bit | YES |
| `RankArticleSubmittedCA` | bit | YES |
| `RankArticleSubmittedSA` | bit | YES |
| `RankArticleSubmittedEBM` | bit | YES |
| `RankArticleSubmittedRT` | bit | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Article_ReviewMetrics

| Column | Type | Nullable |
|---|---|---|
| `ReviewMetrics.ArticleId` | bigint(19) | NO |
| `Editor.First.UserId` | int(10) | YES |
| `Editor.First.Name` | nvarchar(400) | YES |
| `Editor.First.Email` | nvarchar(100) | YES |
| `Editor.Last.UserId` | int(10) | YES |
| `Editor.Last.Name` | nvarchar(400) | YES |
| `Editor.Last.Email` | nvarchar(100) | YES |
| `Editor.First.JoinDate` | datetime | YES |
| `Editor.Last.JoinDate` | datetime | YES |
| `EditorOrigin` | nvarchar(50) | YES |
| `Reviewer.1st.JoinDate` | datetime | YES |
| `Reviewer.2nd.JoinDate` | datetime | YES |
| `Reviewer.First.InvitationDate` | datetime | YES |
| `Reviewer.First.InvitationDate.ByEditor` | datetime | YES |
| `Reviewers.Count` | int(10) | YES |
| `Reviewers.Count.Assigned` | int(10) | YES |
| `Reviewers.Count.Active` | int(10) | YES |
| `Reviewers.Count.Withdrawn` | int(10) | YES |
| `Reviewers.Count.RecommendedRejection` | int(10) | YES |
| `RequiredReviewersCount` | int(10) | YES |
| `RequiredIndependentReviewReportsCount` | int(10) | YES |
| `ReviewersAssigned` | int(10) | YES |
| `Reviewers` | int(10) | YES |
| `ActiveReviewers` | int(10) | YES |
| `WithdrawnReviewers` | int(10) | YES |
| `IsEditorialBoardArticle` | int(10) | YES |
| `IsCitableItem` | nvarchar(1) | YES |
| `IsRejectedByEditorialOffice` | int(10) | YES |
| `IsSubmittedbyRTCC` | int(10) | YES |
| `EditedBy` | nvarchar(1000) | YES |
| `FirstManualReviewerInvitation` | datetime | YES |
| `FirstAutomaticReviewerInvitation` | datetime | YES |
| `AssignmentTypeFirstEditor` | varchar(19) | YES |
| `FirstAssignmentDate` | datetime | YES |
| `AssignmentTypeCurrentEditor` | varchar(19) | YES |
| `CurrentAssignmentDate` | datetime | YES |
| `InvitationEmailCount` | int(10) | YES |
| `EmailReviewProcessBins` | varchar(30) | YES |
| `InvitationEmailCount.Editors` | int(10) | YES |
| `InvitationEmailCount.Reviewers` | int(10) | YES |
| `RequestedRevisionLevel` | nvarchar(100) | YES |
| `FirstRejectionReasonLabel` | nvarchar(100) | YES |
| `ReviewActionReasonLabel` | nvarchar(50) | YES |
| `ReviewActionSubReasonLabel` | nvarchar(200) | YES |
| `ArticleRejectionReason_Full` | nvarchar(300) | YES |
| `IsWithdrawnByAuthors` | bit | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Article_SubmissionMetrics

| Column | Type | Nullable |
|---|---|---|
| `Submission.ArticleId` | bigint(19) | NO |
| `FirstSubmissionId` | bigint(19) | YES |
| `FirstSubmissionId.Original` | int(10) | YES |
| `LatestSubmissionId` | bigint(19) | YES |
| `LatestSubmissionId.Original` | int(10) | YES |
| `SubmissionCount` | int(10) | YES |
| `SubmissionTrustScore` | decimal(5) | YES |
| `SubmissionServiceLevel` | tinyint(3) | YES |
| `ServiceLevelBins` | nvarchar(3) | YES |
| `SubmissionCountWordsAbstract` | int(10) | NO |
| `SubmissionCountWordsBodyText` | int(10) | NO |
| `SubmissionCountWordsCOI` | int(10) | NO |
| `SubmissionCountFigures` | int(10) | NO |
| `SubmissionCountTables` | int(10) | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Article_Users

| Column | Type | Nullable |
|---|---|---|
| `Users.ArticleId` | bigint(19) | NO |
| `MainCorrespondingAuthor.AuthorId` | bigint(19) | YES |
| `MainCorrespondingAuthor.UserId` | int(10) | YES |
| `MainCorrespondingAuthor.JournalUserId` | bigint(19) | YES |
| `MainCorrespondingAuthor.Name` | nvarchar(300) | YES |
| `MainCorrespondingAuthor.PrimaryEmail` | nvarchar(100) | YES |
| `MainCorrespondingAuthor.Email` | nvarchar(100) | YES |
| `MainCorrespondingAuthor.PrimaryOrganizationId` | int(10) | YES |
| `MainCorrespondingAuthor.PrimaryRosstId` | nvarchar(40) | YES |
| `MainCorrespondingAuthor.PrimaryOrganization` | nvarchar(200) | YES |
| `MainCorrespondingAuthor.PrimaryOrganization.Continent` | nvarchar(13) | YES |
| `MainCorrespondingAuthor.PrimaryOrganization.CountryId` | char(3) | YES |
| `MainCorrespondingAuthor.PrimaryOrganization.RosstCountryId` | char(3) | YES |
| `MainCorrespondingAuthor.PrimaryOrganization.Country` | nvarchar(100) | YES |
| `MainCorrespondingAuthor.PrimaryOrganization.RosstCountry` | nvarchar(100) | YES |
| `MainCorrespondingAuthor.PrimaryOrganization.City` | nvarchar(200) | YES |
| `MainCorrespondingAuthor.UserPrimaryOrganizationId` | int(10) | YES |
| `MainCorrespondingAuthor.UserPrimaryRosstId` | nvarchar(40) | YES |
| `MainCorrespondingAuthor.UserPrimaryOrganization` | nvarchar(200) | YES |
| `SubmittingAuthor.Name` | nvarchar(300) | YES |
| `SubmittingAuthor.PrimaryEmail` | nvarchar(100) | YES |
| `SubmittingAuthor.PrimaryOrganizationId` | int(10) | YES |
| `SubmittingAuthor.PrimaryRosstId` | nvarchar(40) | YES |
| `SubmittingAuthor.PrimaryOrganization` | nvarchar(200) | YES |
| `SubmittingAuthor.PrimaryOrganization.Continent` | nvarchar(13) | YES |
| `SubmittingAuthor.PrimaryOrganization.Country` | nvarchar(100) | YES |
| `SubmittingAuthor.PrimaryOrganization.RosstCountry` | nvarchar(100) | YES |
| `SubmittingAuthor.PrimaryOrganization.City` | nvarchar(200) | YES |
| `SubmittingAuthor.IsResearchTopicContributor` | bit | YES |
| `TypeSetterUserId` | int(10) | YES |
| `TypeSetterUserName` | nvarchar(400) | YES |
| `Authors` | nvarchar | YES |
| `AuthorsEmails` | nvarchar | YES |
| `AuthorsAffiliations` | nvarchar | YES |
| `CorrespondingAuthors` | nvarchar | YES |
| `CorrespondingAuthorsEmails` | nvarchar | YES |
| `CorrespondingAuthorsAffiliations` | nvarchar | YES |
| `CreatorUserId` | int(10) | YES |
| `InauguralArticleUserId` | int(10) | YES |
| `InauguralArticleUserName` | nvarchar(400) | YES |
| `IsInauguralArticleUserIdYN` | nvarchar(1) | YES |
| `RejectionRecommenderUserId` | int(10) | YES |
| `RejectionRecommenderRoleId` | int(10) | YES |
| `RejectionRecommenderRoleAbbr` | nvarchar(10) | YES |
| `RejectionRecommenderJournalRoleId` | nvarchar(10) | YES |
| `RejecterUserId` | int(10) | YES |
| `RejecterRoleId` | int(10) | YES |
| `RejecterRoleAbbr` | nvarchar(10) | YES |
| `RejecterJournalRoleId` | nvarchar(10) | YES |
| `AnyAuthorIsEditor` | bit | YES |
| `AnyAuthorIsReturning` | bit | YES |
| `AnyAuthorIsReturningAndEditor` | bit | YES |
| `AnyAuthorIsResearchTopicSubmittor` | bit | YES |
| `ReviewOperations.Owner.UserId` | int(10) | YES |
| `ReviewOperations.Owner.Email` | nvarchar(128) | YES |
| `ReviewOperations.Owner.FirstName` | nvarchar(40) | YES |
| `ReviewOperations.Owner.LastName` | nvarchar(80) | YES |
| `ResearchIntegrity.Owner.UserId` | int(10) | YES |
| `ResearchIntegrity.Owner.Email` | nvarchar(128) | YES |
| `ResearchIntegrity.Owner.FirstName` | nvarchar(40) | YES |
| `ResearchIntegrity.Owner.LastName` | nvarchar(80) | YES |
| `OpportunityOwner.UserId` | int(10) | YES |
| `Is_MainCorrespondingAuthor_EBMember` | bit | YES |
| `Article_MainCorrespondingAuthor_HighestEBRoleId` | int(10) | YES |
| `Article_MainCorrespondingAuthor_HighestEBRole` | nvarchar(50) | YES |
| `Article_Authors_HighestEBRoleId` | int(10) | YES |
| `Article_Authors_HighestEBRole` | nvarchar(50) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopicAbstract_Profile

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicAbstractId` | bigint(19) | NO |
| `ResearchTopicAbstractId.Original` | int(10) | NO |
| `AbstractResearchTopicId` | bigint(19) | NO |
| `AbstractTaxonomyId` | bigint(19) | YES |
| `AbstractTitle` | nvarchar(2000) | YES |
| `AbstractStage` | nvarchar(100) | YES |
| `AbstractAuthorPrimaryAffiliationCountry` | nvarchar(100) | YES |
| `AbstractAuthorEmail` | nvarchar(100) | YES |
| `Abstract.Submitted` | datetime | YES |
| `Abstract.Accepted` | datetime | YES |
| `Abstract.Rejected` | datetime | YES |
| `AbstractOrder` | bigint(19) | YES |
| `OrganizationId` | bigint(19) | YES |
| `RosstId` | nvarchar(40) | YES |
| `AbstractCountryId` | nvarchar(10) | YES |
| `AbstractCountry` | nvarchar(100) | YES |
| `AbstractContinent` | nvarchar(13) | YES |
| `AbstractCountry3RegionsBinFocus` | nvarchar(50) | YES |
| `AbstractCountry4RegionsBin` | nvarchar(50) | YES |
| `AbstractCountry5RegionsBin` | nvarchar(50) | YES |
| `AbstractCountry8RegionsBin` | nvarchar(50) | YES |
| `AbstractCountry13RegionsBin` | nvarchar(50) | YES |
| `AbstractCountry8RegionsBin-China` | nvarchar(50) | YES |
| `AbstractCountry8RegionsBin-ChinaCAS` | nvarchar(50) | YES |
| `AbstractCountryFocusRegionsBin` | nvarchar(50) | YES |
| `AbstractCountryRejectionRate` | nvarchar(50) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopic_Dates

| Column | Type | Nullable |
|---|---|---|
| `Dates.ResearchTopicId` | bigint(19) | NO |
| `CreateDate` | datetime | NO |
| `StageDate` | datetime | YES |
| `OnlineDate` | datetime | YES |
| `DeletedDate` | datetime | YES |
| `CloseDate` | datetime | YES |
| `CompleteDate` | datetime | YES |
| `ShareEBookDate` | datetime | YES |
| `SubmissionInvitationSendDate` | datetime | YES |
| `EditorialRequestDate` | datetime | YES |
| `SubmissionDeadline` | datetime | YES |
| `AbstractSubmissionDeadline` | datetime | YES |
| `ExtendedSubmissionDeadline` | datetime | YES |
| `PublicExtendedDeadline` | datetime | YES |
| `InPreparationStageDate` | datetime | YES |
| `SuggestedStageDate` | datetime | YES |
| `RejectedStageDate` | datetime | YES |
| `DeletedStageDate` | datetime | YES |
| `InDiscussionStageDate` | datetime | YES |
| `LostStageDate` | datetime | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopic_KeyMetrics

| Column | Type | Nullable |
|---|---|---|
| `KeyMetrics.ResearchTopicId` | bigint(19) | NO |
| `CountParticipatingJournals` | int(10) | YES |
| `ResearchTopicIsCrossListed` | bit | YES |
| `CountSubmissionDeadlineDates` | int(10) | YES |
| `CountExtendedSubmissionDeadlineDates` | int(10) | YES |
| `CountExpectedArticles` | int(10) | YES |
| `CountAbstractsNotRejected` | int(10) | YES |
| `CountAbstractsSubmitted` | int(10) | YES |
| `Facebook Inbound` | float(53) | YES |
| `Facebook Outbound` | float(53) | YES |
| `Twitter Inbound` | float(53) | YES |
| `Twitter Outbound` | float(53) | YES |
| `GooglePlus Inbound` | float(53) | YES |
| `GooglePlus Outbound` | float(53) | YES |
| `Linkedin Inbound` | float(53) | YES |
| `Linkedin Outbound` | float(53) | YES |
| `Others Inbound` | float(53) | YES |
| `Others Outbound` | float(53) | YES |
| `CountArticlesViews` | int(10) | YES |
| `CountArticlesDownloads` | int(10) | YES |
| `CountArticlesFrontiersViews` | int(10) | YES |
| `CountArticlesFrontiersDownloads` | int(10) | YES |
| `CountFrontiersViewsDownloads` | int(10) | YES |
| `CountArticlesCrossrefCitations` | int(10) | YES |
| `CountArticlesScopusCitations` | int(10) | YES |
| `CountArticlesPMCViews` | int(10) | YES |
| `CountArticlesPMCDownloads` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `CountArticlesCitations` | int(10) | NO |
| `CountArticlesCitationsArticles` | int(10) | NO |
| `CountSubmittedArticles` | int(10) | YES |
| `CountAcceptedArticles` | int(10) | YES |
| `CountPublishedArticles` | int(10) | YES |
| `CountRejectedArticles` | int(10) | YES |
| `CountInReviewArticles` | int(10) | YES |
| `SubmittedManuscriptsbyInvitedContributors.cfp` | int(10) | YES |
| `CountEditorialArticles` | int(10) | YES |
| `CountEditorialArticlesPublished` | int(10) | YES |
| `CountNonRejectedAbstracts` | int(10) | YES |
| `CountSubmittedAbstracts` | int(10) | YES |
| `RTEditors.Count` | int(10) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopic_Organization

| Column | Type | Nullable |
|---|---|---|
| `Organization.ResearchTopicId` | bigint(19) | NO |
| `EditorsOrganizationsHighestRankFrontiersPriorityOrganizationId` | bigint(19) | YES |
| `EditorsOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `EditorsOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `EditorsOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `PrimaryOrganizationId` | bigint(19) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(50) | YES |
| `Continent` | nvarchar(50) | YES |
| `Country3RegionsBinFocus` | nvarchar(50) | YES |
| `Country4RegionsBin` | nvarchar(50) | YES |
| `Country5RegionsBin` | nvarchar(50) | YES |
| `Country7RegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin` | nvarchar(50) | YES |
| `Country13RegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin-China` | nvarchar(50) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(50) | YES |
| `CountryFocusRegionsBin` | nvarchar(50) | YES |
| `CountryRejectionRate` | nvarchar(50) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `OwnerEmployeeCountry13RegionsBin` | nvarchar(50) | YES |
| `Country_RegionPriority` | nvarchar(50) | YES |
| `Country8RegionsBin_RegionPriority` | nvarchar(50) | YES |
| `Country13RegionsBin_RegionPriority` | nvarchar(50) | YES |
| `Country_ContactPriority` | nvarchar(50) | YES |
| `Country8RegionsBin_ContactPriority` | nvarchar(50) | YES |
| `Country13RegionsBin_ContactPriority` | nvarchar(50) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopic_Profile

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(100) | NO |
| `ResearchTopicId.Original` | int(10) | NO |
| `ResearchTopicTaxonomyId` | bigint(19) | NO |
| `Title` | nvarchar | NO |
| `Description` | nvarchar | YES |
| `ParticipatingJournals` | nvarchar | YES |
| `StageId` | int(10) | YES |
| `Stage` | nvarchar(30) | YES |
| `EBookId` | bigint(19) | YES |
| `EBookId.Original` | int(10) | YES |
| `EBookPublishYear` | int(10) | YES |
| `EBookStatus` | nvarchar(150) | YES |
| `URLEBookPage` | nvarchar(122) | YES |
| `IsActive` | bit | NO |
| `IsOnline` | bit | NO |
| `IsClosed` | bit | NO |
| `IsCompleted` | bit | NO |
| `IsSuggested` | bit | NO |
| `IsRejected` | bit | NO |
| `IsDeleted` | bit | NO |
| `DeletionReasonId` | int(10) | YES |
| `DeletionReason` | varchar(500) | YES |
| `URLResearchTopicPage` | nvarchar(100) | YES |
| `ShortURLResearchTopicPage` | nvarchar(50) | YES |
| `Comments` | nvarchar | YES |
| `SuggestedArticles.Count` | int(10) | YES |
| `SuggestedArticles.Count.Discarded` | int(10) | YES |
| `SuggestedArticles.Count.Invited` | int(10) | YES |
| `SuggestedArticles.Count.Accepted` | int(10) | YES |
| `SuggestedArticles.Count.Declined` | int(10) | YES |
| `SuggestedArticles.ConversionRate` | int(10) | YES |
| `IsSuggestedContributorsEnabledForTopicEditors` | bit | YES |
| `IsSuggestedManuscriptEnabledForTopicEditors` | bit | YES |
| `TopicEditorsMonitoringStartDate` | datetime | YES |
| `TopicEditorsMonitoringReminderFrequency` | int(10) | YES |
| `IsCOVIDRelated` | bit | YES |
| `IsFromACPOpportunity` | bit | YES |
| `CampaignName` | nvarchar(500) | YES |
| `ParentCampaignName` | nvarchar(500) | YES |
| `UltimateParentCampaign` | nvarchar(100) | YES |
| `IsCollectionSeries` | bit | YES |
| `IsSocietyAffiliation` | bit | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopic_PublishingMetrics

| Column | Type | Nullable |
|---|---|---|
| `PublishingMetrics.ResearchTopicId` | bigint(19) | NO |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopic_Users

| Column | Type | Nullable |
|---|---|---|
| `Users.ResearchTopicId` | bigint(19) | NO |
| `Editors` | nvarchar(2000) | YES |
| `EditorIsEBM` | int(10) | YES |
| `AnyEditorIsJournalEditor` | bit | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `OwnerUserId` | int(10) | YES |
| `OwnerUserName` | nvarchar(400) | YES |
| `CreatorUserId` | int(10) | YES |
| `CreatorUserName` | nvarchar(400) | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

## [ReportingDataMart].[Reporting]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### Articles

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(100) | NO |
| `ArticleId.Original` | int(10) | NO |
| `ArticleResearchTopicId` | bigint(19) | YES |
| `ArticleTaxonomyId` | bigint(19) | YES |
| `ArticleJournalTaxonomyId` | bigint(19) | YES |
| `IsResearchTopic` | bit | YES |
| `DOI` | nvarchar(50) | YES |
| `Title` | nvarchar(1000) | NO |
| `CreateDate` | datetime | NO |
| `ArticleTypeId.Original` | int(10) | NO |
| `ArticleTypeId` | bigint(19) | NO |
| `ArticleType` | nvarchar(50) | NO |
| `ArticleTypeCategory` | nvarchar(10) | YES |
| `ArticleSequenceNumber.Original` | int(10) | NO |
| `HasSupplementaryMaterials` | bit | NO |
| `RequestedRevisionLevelId` | int(10) | YES |
| `IsReviewFastForward` | bit | YES |
| `IsDirectCommission` | bit | NO |
| `StageId` | int(10) | NO |
| `Stage` | nvarchar(40) | YES |
| `StageCategoryId` | int(10) | YES |
| `StageCategory` | nvarchar(30) | YES |
| `IsSubmitted` | bit | NO |
| `IsAccepted` | bit | NO |
| `IsPublished` | bit | NO |
| `IsRejected` | bit | NO |
| `IsDeleted` | bit | NO |
| `IsDecided` | bit | NO |
| `SubmissionType` | nvarchar(30) | YES |
| `AcceptedAtStageId` | int(10) | YES |
| `AcceptedAtStage` | nvarchar(40) | YES |
| `RejectedAtStageId` | int(10) | YES |
| `RejectedAtStage` | nvarchar(100) | YES |
| `SuggestedforResearchTopic.StatusId` | int(10) | YES |
| `EOfComments` | nvarchar | YES |
| `EOfPOfComments` | nvarchar | YES |
| `JournalTeamComments` | nvarchar | YES |
| `LastEOfCommentDate` | datetime | YES |
| `LastEOfPOfCommentDate` | datetime | YES |
| `LastComment` | datetime | YES |
| `URLArticlePage` | nvarchar(100) | YES |
| `ShortURLArticlePage` | nvarchar(50) | YES |
| `ShortURLReviewForum` | nvarchar(50) | YES |
| `ArticleURL` | nvarchar(180) | YES |
| `URLReviewForum` | nvarchar(169) | YES |
| `IsControversial` | bit | NO |
| `ControversialityReason` | nvarchar(30) | YES |
| `JournalVolume` | int(10) | YES |
| `ResearchTopicAssignmentType.Latest` | nvarchar(30) | YES |
| `ResearchTopicAssignmentDate.Latest` | datetime | YES |
| `AssignmentResearchTopicId` | bigint(19) | YES |
| `Accounting.ArticleId` | bigint(19) | YES |
| `IsPayingArticle` | bit | YES |
| `IsPayingArticleYN` | varchar(1) | YES |
| `IsPayingArticleType` | bit | YES |
| `Dates.ArticleId` | bigint(19) | YES |
| `StageDate` | datetime | YES |
| `StageDate.InPreparation` | datetime | YES |
| `StageDate.Submitted` | datetime | YES |
| `StageDate.ReceivedByJournal` | datetime | YES |
| `StageDate.InitialValidation` | datetime | YES |
| `StageDate.JournalTransferCompleted` | datetime | YES |
| `StageDate.EditorialAssignment.Source` | datetime | YES |
| `StageDate.InReview` | datetime | YES |
| `StageDate.InIndependentReview` | datetime | YES |
| `StageDate.InInteractiveReview` | datetime | YES |
| `StageDate.ReviewFinalized` | datetime | YES |
| `StageDate.RejectionRecommended` | datetime | YES |
| `StageDate.Rejected` | datetime | YES |
| `StageDate.FinalValidation` | datetime | YES |
| `StageDate.RecommendationForRejectionRevoked` | datetime | YES |
| `StageDate.Accepted` | datetime | YES |
| `StageDate.InProduction` | datetime | YES |
| `StageDate.AuthorProof` | datetime | YES |
| `StageDate.AuthorProofApproved` | datetime | YES |
| `StageDate.Published` | datetime | YES |
| `StageDate.Deleted` | datetime | YES |
| `StageDate.Decision` | datetime | YES |
| `PartnerAcceptArticleDateTime` | datetime | YES |
| `PartnerRecommendRejectionDateTime` | datetime | YES |
| `PartnerRejectionDateTime` | datetime | YES |
| `PartnerRecommendValidationDateTime` | datetime | YES |
| `PartnerRecommendValidationApprovalDateTime` | datetime | YES |
| `PartnerPrescreeningEinCAssignedDateTime` | datetime | YES |
| `PartnerFinalizeReviewDateTime` | datetime | YES |
| `PartnerMonitorAEtoAccept/RejectDateTime` | datetime | YES |
| `PartnerAEtabnotificationDateTime` | datetime | YES |
| `PartnerAUTtabnotificationDateTime` | datetime | YES |
| `PartnerAEtab-MonitoringAUTtoreplyDateTime` | datetime | YES |
| `PartnerRe-submitManuscriptDateTime` | datetime | YES |
| `PartnerMonitorAUT_To_ResubmitReplyDateTime_Days` | datetime | YES |
| `SuggestedforResearchTopic.InviteDate` | datetime | YES |
| `SuggestedforResearchTopic.DiscardDate` | datetime | YES |
| `SuggestedforResearchTopic.AuthorAcceptDate` | datetime | YES |
| `SuggestedforResearchTopic.AuthorDeclineDate` | datetime | YES |
| `FirstPublishDate` | datetime | YES |
| `RequestforAuthortoReviseManuscriptDateTime` | datetime | YES |
| `KeyMetrics.ArticleId` | bigint(19) | YES |
| `EditorialAssignmentDate` | datetime | YES |
| `1st.Editor.JoinDate` | datetime | YES |
| `Reviewer.First.JoinDate` | datetime | YES |
| `Reviewer.Second.JoinDate` | datetime | YES |
| `Reviewer.First.JoinDate.Static` | datetime | YES |
| `Reviewer.Second.JoinDate.Static` | datetime | YES |
| `REAssignment.JoinDate` | datetime | YES |
| `REAssignment.JoinDate.Static` | datetime | YES |
| `Reviewer.First.IndependentReviewSubmitted` | datetime | YES |
| `Reviewer.Last.IndependentReviewSubmitted` | datetime | YES |
| `Avg.DaystoAssign.PreferredAE` | int(10) | YES |
| `Avg.DaystoAssign.AnyAE` | int(10) | YES |
| `Avg.DaystoAssign.EOF` | int(10) | YES |
| `Avg.DaystoAssign.TE` | int(10) | YES |
| `Avg.DaystoAssign.Manual` | int(10) | YES |
| `Avg.DaystoAssign.AnyReviewer` | int(10) | YES |
| `Avg.DaystoAssign.AnyReviewer.Static` | int(10) | YES |
| `Avg.DaystoAssign.RE` | int(10) | YES |
| `Avg.DaystoAssign.REV` | int(10) | YES |
| `Avg.DaystoSubmit.RequiredIIR` | int(10) | YES |
| `Avg.DaystoSubmit.IIRRE` | int(10) | YES |
| `Avg.DaystoSubmit.IIRREV` | int(10) | YES |
| `Avg.DaystoSubmit.AnyIIR` | int(10) | YES |
| `Avg.Daysto.1stAUTReply` | int(10) | YES |
| `Avg.Daysto.LatestAUTReply` | int(10) | YES |
| `Avg.Daysto.1stREReply` | int(10) | YES |
| `Avg.Daysto.LatestREReply` | int(10) | YES |
| `Avg.Daysto.ReviewFinalized` | int(10) | YES |
| `DaysTo.Reviewer.First.Invitation` | int(10) | YES |
| `DaysTo.Reviewer.First.InvitationByEditor` | int(10) | YES |
| `DaysIn.ReviewTime` | int(10) | YES |
| `DaysIn.InitialValidation` | int(10) | YES |
| `DaysIn.EditorialAssignment` | int(10) | YES |
| `DaysIn.AEAssignment` | int(10) | YES |
| `DaysIn.REAssignment` | int(10) | YES |
| `DaysIn.REAssignment.Static` | int(10) | YES |
| `DaysIn.IndependentReview` | int(10) | YES |
| `DaysIn.InteractiveReview` | int(10) | YES |
| `DaysIn.FinalValidation` | int(10) | YES |
| `DaysIn.ReviewFinalized` | int(10) | YES |
| `Avg.DaystoAssign.RequiredReviewer` | int(10) | YES |
| `Avg.DaystoAssign.RequiredReviewer.Static` | int(10) | YES |
| `Time.OnlinetoSubmitted` | int(10) | YES |
| `Time.FirstSubmissionDeadlinetoSubmitted` | int(10) | YES |
| `DecidedDate` | datetime | YES |
| `ResearchTopicTimePostedtoSubmission` | int(10) | YES |
| `CountViews` | int(10) | YES |
| `CountDownloads` | int(10) | YES |
| `CountCitations` | int(10) | YES |
| `CountArticleCitations` | int(10) | YES |
| `CountFrontiersViews` | int(10) | YES |
| `CountFrontiersDownloads` | int(10) | YES |
| `CountPMCViews` | int(10) | YES |
| `CountPMCDownloads` | int(10) | YES |
| `CountScopusCitations` | int(10) | YES |
| `CountCrossrefCitations` | int(10) | YES |
| `ArticleIsCOVIDRelated` | bit | YES |
| `ArticleIsFromInvitedContributor` | bit | YES |
| `ArticleIsFromConfirmedContributor` | bit | YES |
| `ArticleHasBeenTransferred` | bit | YES |
| `IsFaaSTransfer` | bit | YES |
| `HasFaaSTransferOpportunity` | bit | YES |
| `HasBeenFaaSTransferred` | bit | YES |
| `SourceSpaceId` | int(10) | YES |
| `SourceArticleId` | bigint(19) | YES |
| `SourceTaxonomyId` | bigint(19) | YES |
| `EinCFinalValidationApprovalDays` | int(10) | YES |
| `EinCRejectionDays` | int(10) | YES |
| `EOFInitialValidationChecksDays` | int(10) | YES |
| `AEProvAcceptToEOFEinCValidationDays` | int(10) | YES |
| `FinalisedReviewtoEditorCommentsDays` | int(10) | YES |
| `EditorCommentstoAuthorCommentsDays` | int(10) | YES |
| `EditorCommentsUntilResubmissionDays` | int(10) | YES |
| `ReviewReportRating` | decimal(10) | YES |
| `IsAnyAuthorInWatchlist` | bit | YES |
| `DaysIn.ActivePipeline` | int(10) | YES |
| `ArticleStageDetail` | nvarchar(50) | YES |
| `ArticlesRejectedAtStage` | nvarchar(50) | YES |
| `ArticlesRejectedAtStage.Static` | nvarchar(50) | YES |
| `Time.FirstDecision` | int(10) | YES |
| `DeskAcceptedArticle` | bit | YES |
| `SubmissionPassedDeskReview` | nvarchar(20) | YES |
| `Time to Author Resubmission from Revision Request` | int(10) | YES |
| `AnalyticBins.ArticleId` | bigint(19) | YES |
| `Time in ReviewTime` | nvarchar(20) | YES |
| `Time in InitialValidation` | nvarchar(20) | YES |
| `Time in EditorialAssignment` | nvarchar(20) | YES |
| `Time in AEAssignment` | nvarchar(20) | YES |
| `Time in REAssignment` | nvarchar(20) | YES |
| `Time in REAssignment.Static` | nvarchar(20) | YES |
| `Time in IndependentReview` | nvarchar(20) | YES |
| `Time in InteractiveReview` | nvarchar(20) | YES |
| `Time in FinalValidation` | nvarchar(20) | YES |
| `Time to Send First REV Invitation` | nvarchar(20) | YES |
| `Time to Assign Any AE` | nvarchar(20) | YES |
| `Time to Assign Preferred AE` | nvarchar(20) | YES |
| `Time to Assign TE` | nvarchar(20) | YES |
| `Time to Assign AE Manually` | nvarchar(20) | YES |
| `Time to Assign any Reviewer` | nvarchar(20) | YES |
| `Time to Assign any Reviewer.Static` | nvarchar(20) | YES |
| `Time to Assign Required Reviewer` | nvarchar(20) | YES |
| `Time to Assign Required Reviewer.Static` | nvarchar(20) | YES |
| `Time to Assign RE` | nvarchar(20) | YES |
| `Time to Assign REV` | nvarchar(20) | YES |
| `Time to Submit required IRRs` | nvarchar(20) | YES |
| `Time to Submit IRR by RE` | nvarchar(20) | YES |
| `Time Submit IRR by a Reviewer` | nvarchar(20) | YES |
| `Time Submit Any IRR` | nvarchar(20) | YES |
| `Time to First reply of the Author` | nvarchar(20) | YES |
| `Time to Last Author Reply` | nvarchar(20) | YES |
| `Time to First Reviewer Reply` | nvarchar(20) | YES |
| `Time to Last RE Reply` | nvarchar(20) | YES |
| `TimeSinceLastSubmission` | nvarchar(20) | YES |
| `TimeSinceLastAcceptance` | nvarchar(20) | YES |
| `TimeSinceLastRejection` | nvarchar(20) | YES |
| `TimeSinceLastDecision` | nvarchar(20) | YES |
| `TimeSinceLastPublication` | nvarchar(20) | YES |
| `PreviousReviewDecisionTime` | nvarchar(20) | YES |
| `TimeOnlinetoSubmitted` | nvarchar(20) | YES |
| `TimeFirstSubmissionDeadlinetoSubmitted` | nvarchar(20) | YES |
| `PublishingMetrics.ArticleId` | bigint(19) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `RankingRatings.ArticleId` | bigint(19) | YES |
| `QualityRating.Study.Overall` | float(53) | YES |
| `QualityRating.Study.OverallRatingBin` | nvarchar(20) | YES |
| `QualityRating.Study.Average` | int(10) | YES |
| `AvgQualityRating` | int(10) | YES |
| `ArticleLanguageRating` | nvarchar(50) | YES |
| `AvgGeneralInterestRating` | int(10) | YES |
| `AuthorIsEBM` | bit | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `RankArticleSubmitted` | bit | YES |
| `RankArticleSubmittedCA` | bit | YES |
| `RankArticleSubmittedSA` | bit | YES |
| `RankArticleSubmittedEBM` | bit | YES |
| `RankArticleSubmittedRT` | bit | YES |
| `ReviewMetrics.ArticleId` | bigint(19) | YES |
| `Editor.First.UserId` | int(10) | YES |
| `Editor.First.Name` | nvarchar(400) | YES |
| `Editor.First.Email` | nvarchar(100) | YES |
| `Editor.Last.UserId` | int(10) | YES |
| `Editor.Last.Name` | nvarchar(400) | YES |
| `Editor.Last.Email` | nvarchar(100) | YES |
| `Editor.First.JoinDate` | datetime | YES |
| `Editor.Last.JoinDate` | datetime | YES |
| `EditorOrigin` | nvarchar(50) | YES |
| `Reviewer.1st.JoinDate` | datetime | YES |
| `Reviewer.2nd.JoinDate` | datetime | YES |
| `Reviewer.First.InvitationDate` | datetime | YES |
| `Reviewer.First.InvitationDate.ByEditor` | datetime | YES |
| `Reviewers.Count` | int(10) | YES |
| `Reviewers.Count.Assigned` | int(10) | YES |
| `Reviewers.Count.Active` | int(10) | YES |
| `Reviewers.Count.Withdrawn` | int(10) | YES |
| `Reviewers.Count.RecommendedRejection` | int(10) | YES |
| `RequiredReviewersCount` | int(10) | YES |
| `RequiredIndependentReviewReportsCount` | int(10) | YES |
| `ReviewersAssigned` | int(10) | YES |
| `Reviewers` | int(10) | YES |
| `ActiveReviewers` | int(10) | YES |
| `WithdrawnReviewers` | int(10) | YES |
| `IsEditorialBoardArticle` | int(10) | YES |
| `IsCitableItem` | nvarchar(1) | YES |
| `IsRejectedByEditorialOffice` | int(10) | YES |
| `IsSubmittedbyRTCC` | int(10) | YES |
| `EditedBy` | nvarchar(1000) | YES |
| `FirstManualReviewerInvitation` | datetime | YES |
| `FirstAutomaticReviewerInvitation` | datetime | YES |
| `AssignmentTypeFirstEditor` | varchar(19) | YES |
| `FirstAssignmentDate` | datetime | YES |
| `AssignmentTypeCurrentEditor` | varchar(19) | YES |
| `CurrentAssignmentDate` | datetime | YES |
| `InvitationEmailCount` | int(10) | YES |
| `EmailReviewProcessBins` | varchar(30) | YES |
| `InvitationEmailCount.Editors` | int(10) | YES |
| `InvitationEmailCount.Reviewers` | int(10) | YES |
| `RequestedRevisionLevel` | nvarchar(100) | YES |
| `FirstRejectionReasonLabel` | nvarchar(100) | YES |
| `ReviewActionReasonLabel` | nvarchar(50) | YES |
| `ReviewActionSubReasonLabel` | nvarchar(200) | YES |
| `ArticleRejectionReason_Full` | nvarchar(300) | YES |
| `IsWithdrawnByAuthors` | bit | YES |
| `Users.ArticleId` | bigint(19) | YES |
| `MainCorrespondingAuthor.AuthorId` | bigint(19) | YES |
| `MainCorrespondingAuthor.UserId` | int(10) | YES |
| `MainCorrespondingAuthor.JournalUserId` | bigint(19) | YES |
| `MainCorrespondingAuthor.Name` | nvarchar(300) | YES |
| `MainCorrespondingAuthor.PrimaryEmail` | nvarchar(100) | YES |
| `MainCorrespondingAuthor.Email` | nvarchar(100) | YES |
| `MainCorrespondingAuthor.PrimaryOrganizationId` | int(10) | YES |
| `MainCorrespondingAuthor.PrimaryRosstId` | nvarchar(40) | YES |
| `MainCorrespondingAuthor.PrimaryOrganization` | nvarchar(200) | YES |
| `MainCorrespondingAuthor.PrimaryOrganization.Continent` | nvarchar(13) | YES |
| `MainCorrespondingAuthor.PrimaryOrganization.CountryId` | char(3) | YES |
| `MainCorrespondingAuthor.PrimaryOrganization.RosstCountryId` | char(3) | YES |
| `MainCorrespondingAuthor.PrimaryOrganization.Country` | nvarchar(100) | YES |
| `MainCorrespondingAuthor.PrimaryOrganization.RosstCountry` | nvarchar(100) | YES |
| `MainCorrespondingAuthor.PrimaryOrganization.City` | nvarchar(200) | YES |
| `MainCorrespondingAuthor.UserPrimaryOrganizationId` | int(10) | YES |
| `MainCorrespondingAuthor.UserPrimaryRosstId` | nvarchar(40) | YES |
| `MainCorrespondingAuthor.UserPrimaryOrganization` | nvarchar(200) | YES |
| `SubmittingAuthor.Name` | nvarchar(300) | YES |
| `SubmittingAuthor.PrimaryEmail` | nvarchar(100) | YES |
| `SubmittingAuthor.PrimaryOrganizationId` | int(10) | YES |
| `SubmittingAuthor.PrimaryRosstId` | nvarchar(40) | YES |
| `SubmittingAuthor.PrimaryOrganization` | nvarchar(200) | YES |
| `SubmittingAuthor.PrimaryOrganization.Continent` | nvarchar(13) | YES |
| `SubmittingAuthor.PrimaryOrganization.Country` | nvarchar(100) | YES |
| `SubmittingAuthor.PrimaryOrganization.RosstCountry` | nvarchar(100) | YES |
| `SubmittingAuthor.PrimaryOrganization.City` | nvarchar(200) | YES |
| `SubmittingAuthor.IsResearchTopicContributor` | bit | YES |
| `TypeSetterUserId` | int(10) | YES |
| `TypeSetterUserName` | nvarchar(400) | YES |
| `Authors` | nvarchar | YES |
| `AuthorsEmails` | nvarchar | YES |
| `AuthorsAffiliations` | nvarchar | YES |
| `CorrespondingAuthors` | nvarchar | YES |
| `CorrespondingAuthorsEmails` | nvarchar | YES |
| `CorrespondingAuthorsAffiliations` | nvarchar | YES |
| `CreatorUserId` | int(10) | YES |
| `InauguralArticleUserId` | int(10) | YES |
| `InauguralArticleUserName` | nvarchar(400) | YES |
| `IsInauguralArticleUserIdYN` | nvarchar(1) | YES |
| `RejectionRecommenderUserId` | int(10) | YES |
| `RejectionRecommenderRoleId` | int(10) | YES |
| `RejectionRecommenderRoleAbbr` | nvarchar(10) | YES |
| `RejectionRecommenderJournalRoleId` | nvarchar(10) | YES |
| `RejecterUserId` | int(10) | YES |
| `RejecterRoleId` | int(10) | YES |
| `RejecterRoleAbbr` | nvarchar(10) | YES |
| `RejecterJournalRoleId` | nvarchar(10) | YES |
| `AnyAuthorIsEditor` | bit | YES |
| `AnyAuthorIsReturning` | bit | YES |
| `AnyAuthorIsReturningAndEditor` | bit | YES |
| `AnyAuthorIsResearchTopicSubmittor` | bit | YES |
| `ReviewOperations.Owner.UserId` | int(10) | YES |
| `ReviewOperations.Owner.Email` | nvarchar(128) | YES |
| `ReviewOperations.Owner.FirstName` | nvarchar(40) | YES |
| `ReviewOperations.Owner.LastName` | nvarchar(80) | YES |
| `ResearchIntegrity.Owner.UserId` | int(10) | YES |
| `ResearchIntegrity.Owner.Email` | nvarchar(128) | YES |
| `ResearchIntegrity.Owner.FirstName` | nvarchar(40) | YES |
| `ResearchIntegrity.Owner.LastName` | nvarchar(80) | YES |
| `OpportunityOwner.UserId` | int(10) | YES |
| `Is_MainCorrespondingAuthor_EBMember` | bit | YES |
| `Article_MainCorrespondingAuthor_HighestEBRoleId` | int(10) | YES |
| `Article_MainCorrespondingAuthor_HighestEBRole` | nvarchar(50) | YES |
| `Article_Authors_HighestEBRoleId` | int(10) | YES |
| `Article_Authors_HighestEBRole` | nvarchar(50) | YES |
| `Submission.ArticleId` | bigint(19) | YES |
| `FirstSubmissionId` | bigint(19) | YES |
| `FirstSubmissionId.Original` | int(10) | YES |
| `LatestSubmissionId` | bigint(19) | YES |
| `LatestSubmissionId.Original` | int(10) | YES |
| `SubmissionCount` | int(10) | YES |
| `SubmissionTrustScore` | tinyint(3) | YES |
| `SubmissionServiceLevel` | tinyint(3) | YES |
| `ServiceLevelBins` | nvarchar(3) | YES |
| `SubmissionCountWordsAbstract` | int(10) | YES |
| `SubmissionCountWordsBodyText` | int(10) | YES |
| `SubmissionCountWordsCOI` | int(10) | YES |
| `SubmissionCountFigures` | int(10) | YES |
| `SubmissionCountTables` | int(10) | YES |
| `Organization.ArticleId` | bigint(19) | YES |
| `AuthorsOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `AuthorsOrganizationsHighestRankFrontiersPriorityOrganizationId` | bigint(19) | YES |
| `AuthorsOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `AuthorsOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `IsAnyAuthorOrganizationCountryInWatchlist` | bit | YES |
| `PrimaryOrganizationId` | bigint(19) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `Country3RegionsBinFocus` | nvarchar(50) | YES |
| `Country4RegionsBin` | nvarchar(50) | YES |
| `Country5RegionsBin` | nvarchar(50) | YES |
| `Country7RegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin` | nvarchar(50) | YES |
| `Country13RegionsBin` | nvarchar(50) | YES |
| `CountryFocusRegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin-China` | nvarchar(50) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(50) | YES |
| `CountryRejectionRate` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | datetime | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | datetime | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `ArticleDOI` | nvarchar(50) | YES |
| `ArticleTitle` | nvarchar(1000) | NO |
| `ResearchTopicId` | bigint(19) | YES |
| `Is Article from Invited Contributor ?` | bit | YES |
| `Is Article from Confirmed Contributor ?` | bit | YES |
| `InitialValidation` | nvarchar(20) | YES |
| `EditorialAssignment` | nvarchar(20) | YES |
| `AEAssignment` | nvarchar(20) | YES |
| `IndependentReview` | nvarchar(20) | YES |
| `InteractiveReview` | nvarchar(20) | YES |
| `FinalValidation` | nvarchar(20) | YES |
| `REAssignment` | nvarchar(20) | YES |
| `ReviewTime` | nvarchar(20) | YES |
| `OverallQualityRating` | float(53) | YES |
| `OverallQualityRatingBins` | nvarchar(20) | YES |
| `CorrespondingAuthorName` | nvarchar(300) | YES |
| `CorrespondingAuthorPrimaryEmail` | nvarchar(100) | YES |
| `CorrespondingAuthorCountry` | nvarchar(100) | YES |
| `CorrespondingAuthorRosstCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationRosstCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinent` | nvarchar(13) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | YES |
| `ArticleCountry` | nvarchar(100) | YES |
| `ArticleRosstCountry` | nvarchar(100) | YES |
| `ArticleContinent` | nvarchar(50) | YES |
| `ArticleCountry3RegionsBinFocus` | nvarchar(50) | YES |
| `ArticleCountry4RegionsBin` | nvarchar(50) | YES |
| `ArticleCountry5RegionsBin` | nvarchar(50) | YES |
| `ArticleCountry8RegionsBin` | nvarchar(50) | YES |
| `ArticleCountry13RegionsBin` | nvarchar(50) | YES |
| `ArticleCountryFocusRegionsBin` | nvarchar(50) | YES |
| `ArticleCountry8RegionsBin-China` | nvarchar(50) | YES |
| `ArticleCountry8RegionsBin-ChinaCAS` | nvarchar(50) | YES |
| `ResearchTopicId.Original` | int(10) | YES |
| `ResearchTopicTitle` | nvarchar | YES |
| `ResearchTopicTaxonomyId` | bigint(19) | YES |
| `ResearchTopicIsPublished` | bit | YES |
| `ResearchTopicIsClosed` | bit | YES |
| `ResearchTopicIsCompleted` | bit | YES |
| `ResearchTopicIsDeleted` | bit | YES |
| `ResearchTopicIsRejected` | bit | YES |
| `ResearchTopicIsSuggested` | bit | YES |
| `ResearchTopicStageId` | int(10) | YES |
| `ResearchTopicStage` | nvarchar(30) | YES |
| `ResearchTopicIsCOVIDRelated` | bit | YES |
| `ResearchTopicIsFromACPOpportunity` | bit | YES |
| `ResearchTopicCompleteDate` | datetime | YES |
| `ResearchTopicCreateDate` | datetime | YES |
| `ResearchTopicExtendedSubmissionDeadline` | datetime | YES |
| `ResearchTopicOnlineDate` | datetime | YES |
| `ResearchTopicDeletedDate` | datetime | YES |
| `ResearchTopicPostedDate` | datetime | YES |
| `ResearchTopicSubmissionDeadline` | datetime | YES |
| `ResearchTopicIsCrossListed` | bit | NO |
| `ResearchTopicOwnerUserId` | int(10) | YES |
| `ResearchTopicOwnerUserName` | nvarchar(400) | YES |
| `SourceJournal` | nvarchar(150) | YES |
| `IsRTIC` | bit | YES |

### AuthorOrganizations

| Column | Type | Nullable |
|---|---|---|
| `AuthorOrganizationsId` | bigint(19) | NO |
| `AuthorId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `OrganizationId` | int(10) | NO |
| `RosstId` | nvarchar(40) | YES |
| `OrganizationOrder` | int(10) | NO |
| `OrganizationSourceId` | char(1) | NO |
| `AuthorName` | nvarchar(300) | YES |
| `Organization` | nvarchar(200) | NO |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### Authors

| Column | Type | Nullable |
|---|---|---|
| `AuthorId` | bigint(19) | NO |
| `AuthorUserId` | int(10) | YES |
| `AuthorJournalUserId` | bigint(19) | YES |
| `AuthorPersonUserId` | bigint(19) | YES |
| `AuthorEmail` | nvarchar(100) | YES |
| `AuthorSpaceId` | smallint(5) | YES |
| `RoleId` | int(10) | YES |
| `Role` | nvarchar(50) | YES |
| `RoleAbbr` | nvarchar(20) | YES |
| `JournalRoleId` | nvarchar(10) | YES |
| `AuthorArticleId` | bigint(19) | YES |
| `AuthorTaxonomyId` | bigint(19) | YES |
| `AuthorOrganizationId` | int(10) | YES |
| `AuthorRosstId` | nvarchar(40) | YES |
| `AuthorSource` | char(1) | YES |
| `ReviewAuthorId` | bigint(19) | YES |
| `ProductionAuthorId` | bigint(19) | YES |
| `AuthorTitle` | nvarchar(15) | YES |
| `AuthorFirstName` | nvarchar(300) | YES |
| `AuthorMiddleName` | nvarchar(100) | YES |
| `AuthorLastName` | nvarchar(300) | YES |
| `AuthorName` | nvarchar(600) | YES |
| `AuthorOriginalEmail` | nvarchar(100) | YES |
| `AuthorPrimaryEmailAddress` | nvarchar(100) | YES |
| `AuthorSuffix` | nvarchar(50) | YES |
| `AuthorOrder` | int(10) | YES |
| `IsCorrespondingAuthor` | bit | NO |
| `IsSubmittingAuthor` | bit | NO |
| `IsMainCorrespondingAuthor` | bit | NO |
| `IsLastAuthor` | bit | NO |
| `AuthorEmailOrder` | int(10) | YES |
| `ReviewerAuthorUserId` | int(10) | YES |
| `AuthorUserOrder` | int(10) | YES |
| `Dates.ArticleId` | bigint(19) | YES |
| `StageDate` | datetime | YES |
| `StageDate.InPreparation` | datetime | YES |
| `StageDate.Submitted` | datetime | YES |
| `StageDate.ReceivedByJournal` | datetime | YES |
| `StageDate.InitialValidation` | datetime | YES |
| `StageDate.JournalTransferCompleted` | datetime | YES |
| `StageDate.EditorialAssignment.Source` | datetime | YES |
| `StageDate.InReview` | datetime | YES |
| `StageDate.InIndependentReview` | datetime | YES |
| `StageDate.InInteractiveReview` | datetime | YES |
| `StageDate.ReviewFinalized` | datetime | YES |
| `StageDate.RejectionRecommended` | datetime | YES |
| `StageDate.Rejected` | datetime | YES |
| `StageDate.FinalValidation` | datetime | YES |
| `StageDate.RecommendationForRejectionRevoked` | datetime | YES |
| `StageDate.Accepted` | datetime | YES |
| `StageDate.InProduction` | datetime | YES |
| `StageDate.AuthorProof` | datetime | YES |
| `StageDate.AuthorProofApproved` | datetime | YES |
| `StageDate.Published` | datetime | YES |
| `StageDate.Deleted` | datetime | YES |
| `StageDate.Decision` | datetime | YES |
| `PartnerAcceptArticleDateTime` | datetime | YES |
| `PartnerRecommendRejectionDateTime` | datetime | YES |
| `PartnerRejectionDateTime` | datetime | YES |
| `PartnerRecommendValidationDateTime` | datetime | YES |
| `PartnerRecommendValidationApprovalDateTime` | datetime | YES |
| `PartnerPrescreeningEinCAssignedDateTime` | datetime | YES |
| `PartnerFinalizeReviewDateTime` | datetime | YES |
| `PartnerMonitorAEtoAccept/RejectDateTime` | datetime | YES |
| `PartnerAEtabnotificationDateTime` | datetime | YES |
| `PartnerAUTtabnotificationDateTime` | datetime | YES |
| `PartnerAEtab-MonitoringAUTtoreplyDateTime` | datetime | YES |
| `PartnerRe-submitManuscriptDateTime` | datetime | YES |
| `PartnerMonitorAUT_To_ResubmitReplyDateTime_Days` | datetime | YES |
| `SuggestedforResearchTopic.InviteDate` | datetime | YES |
| `SuggestedforResearchTopic.DiscardDate` | datetime | YES |
| `SuggestedforResearchTopic.AuthorAcceptDate` | datetime | YES |
| `SuggestedforResearchTopic.AuthorDeclineDate` | datetime | YES |
| `FirstPublishDate` | datetime | YES |
| `RequestforAuthortoReviseManuscriptDateTime` | datetime | YES |
| `KeyMetrics.AuthorId` | bigint(19) | YES |
| `KeyMetrics.ArticleId` | bigint(19) | YES |
| `Articles Submitted per Author` | int(10) | YES |
| `Articles Accepted per Author` | int(10) | YES |
| `First.SubmissionDate` | datetime | YES |
| `Last.Submitted` | datetime | YES |
| `Last.Accepted` | datetime | YES |
| `Last.Rejection` | datetime | YES |
| `Last.Decided` | datetime | YES |
| `Last.Decided.ArticleId` | bigint(19) | YES |
| `IsLatestArticleDecision` | bit | YES |
| `IsReturningAuthor` | bit | YES |
| `IsReturningAuthorCA` | bit | YES |
| `IsReturningAuthorSA` | bit | YES |
| `IsReturningAuthorEBM` | bit | YES |
| `IsReturningAuthorRT` | bit | YES |
| `IsReturningAuthorRTE` | bit | YES |
| `DaysSinceLastSubmission` | int(10) | YES |
| `DaysSinceLastAcceptance` | int(10) | YES |
| `DaysSinceLastRejection` | int(10) | YES |
| `DaysSinceLastDecision` | int(10) | YES |
| `DaysSinceLastPublication` | int(10) | YES |
| `LastDecidedReviewDays` | int(10) | YES |
| `ArticlesSubmitted.Count` | int(10) | YES |
| `ArticlesAccepted.Count` | int(10) | YES |
| `TimeSince.Last.Submitted.Article` | int(10) | YES |
| `TimeSince.Last.Accepted.Article` | int(10) | YES |
| `TimeSince.Last.Rejected.Article` | int(10) | YES |
| `AuthorRank` | int(10) | YES |
| `AnalyticBins.AuthorId` | bigint(19) | YES |
| `TimeSinceLastSubmission.Bin` | nvarchar(20) | YES |
| `TimeSinceLastAcceptance.Bin` | nvarchar(20) | YES |
| `TimeSinceLastRejection.Bin` | nvarchar(20) | YES |
| `TimeSinceLastDecision.Bin` | nvarchar(20) | YES |
| `TimeSinceLastPublication.Bin` | nvarchar(20) | YES |
| `PreviousReviewDecisionTime.Bin` | nvarchar(20) | YES |
| `Submitted Articles Bins` | nvarchar(50) | YES |
| `Accepted Articles Bins` | nvarchar(50) | YES |
| `Time Since Last Submitted Article Bins` | nvarchar(50) | YES |
| `Time Since Last Accepted Article Bins` | nvarchar(50) | YES |
| `Time Since Last Rejected Article Bins` | nvarchar(50) | YES |
| `Affiliations.AuthorId` | bigint(19) | YES |
| `LegacyAffiliationCountries` | nvarchar(500) | YES |
| `LegacyAffiliations` | nvarchar(4000) | YES |
| `Organization.AuthorId` | bigint(19) | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | nvarchar(10) | YES |
| `PrimaryOrganizationRosstCountryId` | nvarchar(10) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationRosstCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | nvarchar(10) | YES |
| `PrimaryOrganizationContinent` | nvarchar(13) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `AuthorOrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `AuthorOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `AuthorOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `AuthorOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(200) | YES |
| `TenantGroup` | nvarchar(50) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | datetime | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | datetime | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `ArticleId` | bigint(19) | YES |
| `Title` | nvarchar(15) | YES |
| `FirstName` | nvarchar(300) | YES |
| `MiddleName` | nvarchar(100) | YES |
| `LastName` | nvarchar(300) | YES |
| `Name` | nvarchar(600) | YES |
| `Email` | nvarchar(100) | YES |
| `Suffix` | nvarchar(50) | YES |
| `UserIdOrder` | int(10) | YES |
| `Article.StageDate.ReceivedByJournal` | datetime | YES |
| `Article.StageDate.Accepted` | datetime | YES |
| `Article.StageDate.Rejected` | datetime | YES |
| `Time Since Last Submitted Article` | int(10) | YES |
| `Time Since Last Accepted Article` | int(10) | YES |
| `Time Since Last Rejected Article` | int(10) | YES |
| `TimeSinceLast.Submission` | nvarchar(20) | YES |
| `TimeSinceLast.Acceptance` | nvarchar(20) | YES |
| `TimeSinceLast.Rejection` | nvarchar(20) | YES |
| `TimeSinceLast.Decision` | nvarchar(20) | YES |
| `ArticleId.Original` | int(10) | YES |
| `Article.IsSubmitted` | bit | YES |
| `Article.IsAccepted` | bit | YES |
| `Article.IsDeleted` | bit | YES |
| `IsFrontiers` | nvarchar(50) | YES |
| `PersonId` | bigint(19) | YES |
| `UserIsEditor.Frontiers` | bit | YES |
| `UserIsEditor` | bit | YES |
| `UserIsResearchTopicEditor.Frontiers` | bit | YES |
| `UserIsResearchTopicEditor` | bit | YES |
| `UserIsReviewer.Frontiers` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserLastName` | nvarchar(150) | YES |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserFirstName` | nvarchar(150) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `HIndex` | int(10) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `InfluencePercentile` | float(53) | YES |
| `IsAuthorInWatchlist` | bit | YES |
| `CountryId` | nvarchar(10) | YES |
| `RosstCountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `RosstCountry` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `IsAuthorFromWatchlistCountry` | bit | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `UserPrimaryOrganizationId` | int(10) | YES |
| `UserPrimaryRosstId` | nvarchar(40) | YES |
| `UserPrimaryOrganization` | nvarchar(200) | YES |
| `UserOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `UserOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `AuthorIsEBM` | bit | YES |
| `UserHIndex` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |

### CampaignMembers

| Column | Type | Nullable |
|---|---|---|
| `CampaignMemberId` | char(18) | NO |
| `CampaignStatus` | nvarchar(40) | YES |
| `CampaignCRMId` | nvarchar(20) | YES |
| `CampaignName` | nvarchar(100) | YES |
| `ParentCampaignName` | nvarchar(100) | YES |
| `UltimateParentCampaignName` | nvarchar(100) | YES |
| `EmailAddress` | nvarchar(100) | YES |
| `CampaignMemberEmail` | nvarchar(200) | YES |
| `CampaignMemberUserId` | int(10) | YES |
| `CampaignMemberPersonUserId` | bigint(19) | YES |
| `CampaignMemberJournalUserId` | bigint(19) | YES |
| `CampaignMemberTaxonomyId` | bigint(19) | YES |
| `Is CM EBM` | bit | YES |
| `Is CM REV` | bit | YES |
| `JoinDate` | date | YES |
| `InviteDate` | date | YES |
| `CampaignRecordTypeCRMId` | nvarchar(20) | YES |
| `CampaignType` | nvarchar(50) | YES |
| `CampaignMemberCRMIdOrder` | int(10) | YES |
| `KeyMetrics.CampaignMemberId` | char(18) | YES |
| `Last.Reviewer.ReviewDate` | datetime | YES |
| `Last.Reviewer.EditDate` | datetime | YES |
| `LastSubmissionDate` | datetime | YES |
| `Days Since Last REV Assignment` | int(10) | YES |
| `Days Since Last Editing Assignment` | int(10) | YES |
| `Days Since Last Submission` | int(10) | YES |
| `Is Returning Author?` | bit | YES |
| `Has Hosted RT?` | bit | YES |
| `PersonUserId` | bigint(19) | YES |
| `PersonUserId.Original` | bigint(19) | YES |
| `PersonId` | bigint(19) | YES |
| `Person.JournalUserId` | bigint(19) | YES |
| `Person.SpaceId` | int(10) | YES |
| `Person.UserId` | int(10) | YES |
| `Person.Email` | nvarchar(300) | YES |
| `IsPrimaryEmail` | bit | YES |
| `IsJournalUser` | bit | YES |
| `IsRegisteredUser` | bit | YES |
| `IsNonRegisteredUser` | bit | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | char(3) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | nvarchar(50) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `HighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `TopRankRosstId` | nvarchar(40) | YES |
| `HighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `HighestRankFrontiersPriority` | int(10) | YES |
| `HighestRankFrontiersPriorityBins` | nvarchar(50) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `CountryOrder` | int(10) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `OwnerEmployeeCountry13RegionsBin` | nvarchar(50) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserFirstName` | nvarchar(150) | YES |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserLastName` | nvarchar(150) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserRegisterDate` | datetime | YES |
| `UserActivateDate` | datetime | YES |
| `UserModifyDate` | datetime | YES |
| `UserIsDeleted` | bit | YES |
| `UserIsActivated` | bit | YES |
| `UserStatus` | nvarchar(30) | YES |
| `UserCompletedRegistration` | bit | YES |
| `UserIsLoggedIn` | bit | YES |
| `UserIsAdmin` | bit | YES |
| `UserIsAuthor` | bit | YES |
| `UserIsEditor` | bit | YES |
| `UserIsResearchTopicEditor` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserEditorialBoardRoles` | varchar(500) | YES |
| `UserAuthorRoles` | varchar(500) | YES |
| `UserRolesNames` | varchar(500) | YES |
| `UserIsAdmin.Frontiers` | bit | YES |
| `UserIsAuthor.Frontiers` | bit | YES |
| `UserIsEditor.Frontiers` | bit | YES |
| `UserIsResearchTopicEditor.Frontiers` | bit | YES |
| `UserIsReviewer.Frontiers` | bit | YES |
| `IsUserInWatchList` | bit | YES |
| `JournalUserIsEditor` | bit | YES |
| `JournalUserIsEBM` | bit | YES |
| `JournalUserIsReviewer` | bit | YES |
| `JournalUserIsAuthor` | bit | YES |
| `JournalRoleId` | nvarchar(50) | YES |
| `JournalUserRoleId` | int(10) | YES |
| `JournalUserRole` | nvarchar(50) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `JournalRole.FirstAssigned.Date` | datetime | YES |
| `Rank.ResearchTopic` | int(10) | YES |
| `Rank.Article` | int(10) | YES |
| `JournalUserFirstTaxonomyId` | bigint(19) | YES |
| `JournalUserFirstJoinDate` | datetime | YES |
| `JournalUserOrder` | int(10) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `Campaign Name` | nvarchar(100) | YES |
| `Campaign Status` | nvarchar(40) | YES |
| `CampaignMemberCRMId` | char(18) | NO |
| `Campaign Type` | nvarchar(50) | YES |
| `UserId` | int(10) | YES |
| `UserPrimaryEmail` | nvarchar(100) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | YES |
| `OrganizationsHighestRank` | int(10) | YES |
| `Role` | nvarchar(50) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### Contributors

| Column | Type | Nullable |
|---|---|---|
| `ContributorId` | bigint(19) | NO |
| `ContributorId.Original` | int(10) | YES |
| `ContributorSpaceId` | smallint(5) | NO |
| `ContributorUserId` | int(10) | YES |
| `ContributorJournalUserId` | bigint(19) | YES |
| `ContributorPersonUserId` | bigint(19) | YES |
| `ContributorResearchTopicId` | bigint(19) | YES |
| `ContributorResearchTopicId.Original` | bigint(19) | YES |
| `ContributorTaxonomyId` | bigint(19) | YES |
| `ContributorTheme` | nvarchar(500) | YES |
| `ContributorCreatorUserTypeRoleId` | int(10) | YES |
| `ContributorCreatorUserTypeRole` | nvarchar(100) | YES |
| `ContributorEmail` | nvarchar(100) | YES |
| `Email` | nvarchar(100) | YES |
| `ContributorName` | nvarchar(400) | YES |
| `ContributorFirstName` | nvarchar(200) | YES |
| `ContributorMiddleName` | nvarchar(200) | YES |
| `ContributorLastName` | nvarchar(200) | YES |
| `ContributorSourceId` | int(10) | NO |
| `ContributorSource` | nvarchar(100) | YES |
| `ContributorSecondarySourceId` | int(10) | YES |
| `ContributorSecondarySource` | nvarchar(50) | YES |
| `ContributorCreateDate` | datetime | NO |
| `SalesForceMessageCreateDate` | datetime | YES |
| `ContributorSortOrder` | bigint(19) | NO |
| `CountExpectedArticles` | int(10) | YES |
| `KeyMetrics.ContributorId` | bigint(19) | YES |
| `ResearchTopicAbstractAcceptedDate.First` | datetime | YES |
| `SuggestedContributorUploadTypeId` | int(10) | YES |
| `SuggestedContributorAlgorithmTypeId` | int(10) | YES |
| `SuggestedContributorAlgorithmType` | nvarchar(100) | YES |
| `First.RT.SubmissionDate` | datetime | YES |
| `Reminders.Count.InvitationtoConfirmation` | int(10) | YES |
| `Reminders.Count.ConfirmationtoSubmission` | int(10) | YES |
| `Reminders.Count.Total` | int(10) | YES |
| `HasContributorBeenInvited` | bit | YES |
| `HasContributorBeenInvited.Cfp` | bit | YES |
| `ContributorInvitationDate.Logical` | datetime | YES |
| `HasConfirmedInvitation` | bit | YES |
| `ContributorIsSuggested` | bit | YES |
| `First.Author.SubmissionDate` | datetime | YES |
| `ContributorIsRTEditor` | bit | YES |
| `IsConfirmedContributor` | bit | YES |
| `IsSpontaneousSubmission` | bit | YES |
| `Invitation.ContributorId` | bigint(19) | YES |
| `InviteDate` | datetime | YES |
| `InviterUserId` | int(10) | YES |
| `ConfirmedDate` | datetime | YES |
| `ExpectedSubmissionDate` | datetime | YES |
| `InvitationInitiatorRoleId` | int(10) | YES |
| `InvitationInitiatorRole` | nvarchar(50) | YES |
| `InvitationStatusId` | int(10) | YES |
| `InvitationStatus` | nvarchar(50) | YES |
| `InvitationStatusDate` | datetime | YES |
| `InvitationSentRemindersCount` | int(10) | YES |
| `InvitationLastReminderDate` | datetime | YES |
| `InvitationActivationNumber` | uniqueidentifier | YES |
| `ActivationLink` | nvarchar(251) | YES |
| `InvitationStatusDate.Confirmed.First` | datetime | YES |
| `InvitationStatusDate.Confirmed.Last` | datetime | YES |
| `Invitation.InitiationDate` | datetime | YES |
| `DeclinationOtherReason` | nvarchar(200) | YES |
| `DeclinationReason` | nvarchar(200) | YES |
| `DeclinationCreateDate` | datetime | YES |
| `DeclinationReasons` | nvarchar(50) | YES |
| `PersonUserId` | bigint(19) | YES |
| `PersonUserId.Original` | bigint(19) | YES |
| `PersonId` | bigint(19) | YES |
| `Person.JournalUserId` | bigint(19) | YES |
| `Person.SpaceId` | int(10) | YES |
| `Person.UserId` | int(10) | YES |
| `Person.Email` | nvarchar(300) | YES |
| `IsPrimaryEmail` | bit | YES |
| `IsJournalUser` | bit | YES |
| `IsRegisteredUser` | bit | YES |
| `IsNonRegisteredUser` | bit | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | char(3) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | nvarchar(50) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `HighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `TopRankRosstId` | nvarchar(40) | YES |
| `HighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `HighestRankFrontiersPriority` | int(10) | YES |
| `HighestRankFrontiersPriorityBins` | nvarchar(50) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `CountryOrder` | int(10) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `OwnerEmployeeCountry13RegionsBin` | nvarchar(50) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserFirstName` | nvarchar(150) | YES |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserLastName` | nvarchar(150) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserRegisterDate` | datetime | YES |
| `UserActivateDate` | datetime | YES |
| `UserModifyDate` | datetime | YES |
| `UserIsDeleted` | bit | YES |
| `UserIsActivated` | bit | YES |
| `UserStatus` | nvarchar(30) | YES |
| `UserCompletedRegistration` | bit | YES |
| `UserIsLoggedIn` | bit | YES |
| `UserIsAdmin` | bit | YES |
| `UserIsAuthor` | bit | YES |
| `UserIsEditor` | bit | YES |
| `UserIsResearchTopicEditor` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserEditorialBoardRoles` | varchar(500) | YES |
| `UserAuthorRoles` | varchar(500) | YES |
| `UserRolesNames` | varchar(500) | YES |
| `UserIsAdmin.Frontiers` | bit | YES |
| `UserIsAuthor.Frontiers` | bit | YES |
| `UserIsEditor.Frontiers` | bit | YES |
| `UserIsResearchTopicEditor.Frontiers` | bit | YES |
| `UserIsReviewer.Frontiers` | bit | YES |
| `IsUserInWatchList` | bit | YES |
| `JournalUserIsEditor` | bit | YES |
| `JournalUserIsEBM` | bit | YES |
| `JournalUserIsReviewer` | bit | YES |
| `JournalUserIsAuthor` | bit | YES |
| `JournalRoleId` | nvarchar(50) | YES |
| `JournalUserRoleId` | int(10) | YES |
| `JournalUserRole` | nvarchar(50) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `JournalRole.FirstAssigned.Date` | datetime | YES |
| `Rank.ResearchTopic` | int(10) | YES |
| `Rank.Article` | int(10) | YES |
| `JournalUserFirstTaxonomyId` | bigint(19) | YES |
| `JournalUserFirstJoinDate` | datetime | YES |
| `JournalUserOrder` | int(10) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(200) | YES |
| `TenantGroup` | nvarchar(50) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `FirstName` | nvarchar(200) | YES |
| `MiddleName` | nvarchar(200) | YES |
| `LastName` | nvarchar(200) | YES |
| `Name` | nvarchar(400) | YES |
| `ResearchTopicId` | bigint(19) | YES |
| `ResearchTopicId.Original` | bigint(19) | YES |
| `Contributor.Creator.UserTypeRoleId` | int(10) | YES |
| `Contributor.Creator.UserTypeRole` | nvarchar(100) | YES |
| `UserId` | int(10) | YES |
| `CreateDate` | datetime | NO |
| `SortOrder` | bigint(19) | NO |
| `Theme` | nvarchar(500) | YES |
| `ContributorExpectedArticles.Count` | int(10) | YES |
| `ContributorInvitationDate` | datetime | YES |
| `ContributorConfirmedDate` | datetime | YES |
| `ContributorExpectedSubmissionDate` | datetime | YES |
| `ContributorInvitationStatusId` | int(10) | YES |
| `ContributorInvitationStatus` | nvarchar(50) | YES |
| `ContributorInvitationStatusDate` | datetime | YES |
| `ContributorInvitationActivationNumber` | uniqueidentifier | YES |
| `ContributorDeclinationOtherReason` | nvarchar(200) | YES |
| `ContributorDeclinationReason` | nvarchar(200) | YES |
| `ContributorDeclinationCreateDate` | datetime | YES |
| `ContributorInvitationSentRemindersCount` | int(10) | YES |
| `Invitation.Initiator.RoleId` | int(10) | YES |
| `Invitation.Initiator.Role` | nvarchar(50) | YES |
| `ContributorInvitationLastReminderDate` | datetime | YES |
| `Organization` | nvarchar(200) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `UserPrimaryEmail` | nvarchar(100) | YES |
| `UserOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `ContributorOrganizationsHighestRankWoS` | int(10) | YES |
| `ContributorOrganizationId` | int(10) | YES |
| `ContributorRosstId` | nvarchar(40) | YES |
| `ContributorOrganization` | nvarchar(200) | YES |
| `ContributorCountryId` | nvarchar(10) | YES |
| `ContributorCountry` | nvarchar(100) | YES |
| `ContributorCountinent` | nvarchar(100) | YES |
| `ContributorCountryRejectionRate` | nvarchar(100) | YES |
| `IsUserEditor` | bit | YES |
| `IsUserResearchTopicEditor` | bit | YES |
| `IsResearchTopicEditor` | bit | YES |
| `IsUserReviewer` | bit | YES |
| `ContributorActivityPercentile` | float(53) | YES |
| `ContributorConnectivityPercentile` | float(53) | YES |
| `ContributorInfluencePercentile` | float(53) | YES |
| `ContributorProductivityPercentile` | float(53) | YES |
| `ContributorHIndexBins` | nvarchar(20) | YES |
| `ContributorActivityBins` | nvarchar(20) | YES |
| `ContributorConnectivityBins` | nvarchar(20) | YES |
| `ContributorInfluenceBins` | nvarchar(20) | YES |
| `ContributorProductivityBins` | nvarchar(20) | YES |
| `ContributorFrontiersBins` | nvarchar(20) | YES |
| `ContributorOrganizationRejectionRateBin` | nvarchar(50) | YES |
| `ContributorOrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `ContributorOrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `ContributorCountry3RegionsBinFocus` | nvarchar(100) | YES |
| `ContributorCountry4RegionsBin` | nvarchar(100) | YES |
| `ContributorCountry5RegionsBin` | nvarchar(100) | YES |
| `ContributorCountry7RegionsBin` | nvarchar(100) | YES |
| `ContributorCountry8RegionsBin` | nvarchar(100) | YES |
| `ContributorCountry13RegionsBin` | nvarchar(100) | YES |
| `ContributorCountryFocusRegionsBin` | nvarchar(100) | YES |
| `ContributorCountry8RegionsBin-China` | nvarchar(100) | YES |
| `ContributorCountry8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `ContributorHIndex` | int(10) | YES |
| `ContributorIsEBM` | bit | YES |
| `ContributorIsEditor` | bit | YES |
| `IsJournalEditor` | bit | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### CountryMetrics

| Column | Type | Nullable |
|---|---|---|
| `CountryId` | nvarchar(3) | NO |
| `Country` | nvarchar(50) | YES |
| `ContinentId` | nvarchar(3) | YES |
| `Continent` | nvarchar(50) | YES |
| `3RegionsBinFocus` | nvarchar(50) | YES |
| `4RegionsBin` | nvarchar(50) | YES |
| `5RegionsBin` | nvarchar(50) | YES |
| `7RegionsBin` | nvarchar(50) | YES |
| `8RegionsBin` | nvarchar(50) | YES |
| `13RegionsBin` | nvarchar(50) | YES |
| `IsFocusRegion` | bit | YES |
| `FocusRegionsBin` | nvarchar(50) | YES |
| `RejectionRate` | nvarchar(50) | YES |
| `CountrySortOrder` | int(10) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### EditorialBoardMembers

| Column | Type | Nullable |
|---|---|---|
| `EditorialBoardMemberId` | bigint(19) | NO |
| `EditorialBoardMemberSpaceId` | smallint(5) | NO |
| `EditorialBoardMemberUserId` | int(10) | NO |
| `EditorialBoardMemberJournalUserId` | bigint(19) | YES |
| `EditorialBoardMemberPersonUserId` | bigint(19) | NO |
| `EditorialBoardMemberTaxonomyId` | bigint(19) | YES |
| `RoleJoinOrder` | int(10) | NO |
| `IsFirstJoinedRole` | bit | YES |
| `RoleLevelOrder` | int(10) | NO |
| `IsTopFirstRole` | bit | YES |
| `RoleId` | int(10) | NO |
| `Role` | varchar(50) | YES |
| `RoleAbbr` | varchar(20) | YES |
| `RoleLevel` | varchar(9) | YES |
| `JoinDate` | datetime | YES |
| `EndDate` | datetime | YES |
| `IsActive` | bit | NO |
| `ModifyDate` | datetime | YES |
| `IsFirstTaxonomyRole` | bit | YES |
| `TaxonomyRoleOrder` | int(10) | YES |
| `InauguralArticleStage` | nvarchar(40) | YES |
| `EditorialBoardMemberUserOrder` | bigint(19) | YES |
| `EndReasonId` | int(10) | YES |
| `EndReason` | nvarchar(50) | YES |
| `EndReasonRoleChangeFlag` | int(10) | YES |
| `KeyMetrics.EditorialBoardMemberId` | bigint(19) | YES |
| `CountPublicationsConfirmed` | int(10) | YES |
| `CrossListedFields` | nvarchar(4000) | YES |
| `ActiveModifyDate` | datetime | YES |
| `MinJoinDate` | datetime | YES |
| `MinStartDate` | datetime | YES |
| `MaxEndDate` | datetime | YES |
| `SectionJoinDate` | datetime | YES |
| `SectionEndDate` | datetime | YES |
| `FirstTaxonomyRoleId` | int(10) | YES |
| `CountofTaxonomyRoles` | int(10) | YES |
| `ActiveEditorialBoards` | int(10) | YES |
| `HasOpportunity` | bit | YES |
| `Invitation.EditorialBoardMemberId` | bigint(19) | YES |
| `EditorialBoardInvitationId` | bigint(19) | YES |
| `InviterUserId` | int(10) | YES |
| `Inviter` | nvarchar(400) | YES |
| `InviteDate` | datetime | YES |
| `InvitationSourceId` | int(10) | YES |
| `InvitationSource` | nvarchar(100) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(200) | YES |
| `TenantGroup` | nvarchar(50) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `UserId` | int(10) | NO |
| `UserIdOrder` | bigint(19) | YES |
| `PersonId` | bigint(19) | YES |
| `UserIsEBM` | bit | NO |
| `UserIsEditor` | bit | NO |
| `JournalRoleId` | varchar(10) | YES |
| `Email` | nvarchar(100) | YES |
| `FirstName` | nvarchar(150) | YES |
| `LastName` | nvarchar(150) | YES |
| `Name` | nvarchar(400) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `UserOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `UserOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | YES |
| `OrganizationsHighestRankWoS` | int(10) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserPrimaryOrganizationId` | int(10) | YES |
| `UserPrimaryRosstId` | nvarchar(40) | YES |
| `UserPrimaryOrganization` | nvarchar(200) | YES |
| `UserPrimaryOrganizationCountry` | nvarchar(100) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | varchar(13) | YES |
| `PrimaryOrganizationCountry` | nvarchar(50) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `EditingInvitationsReceivedCount` | int(10) | YES |
| `EditingInvitationsAcceptedCount` | int(10) | YES |
| `EditingInvitationsDeclinedCount` | int(10) | YES |
| `ReviewingInvitationsReceivedCount` | int(10) | YES |
| `ReviewingInvitationsAcceptedCount` | int(10) | YES |
| `ReviewingInvitationsDeclinedCount` | int(10) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### EmailMetrics

| Column | Type | Nullable |
|---|---|---|
| `Email` | nvarchar(300) | NO |
| `UserId` | int(10) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `UserPrimaryOrganizationId` | int(10) | YES |
| `UserPrimaryRosstId` | nvarchar(40) | YES |
| `UserPrimaryOrganization` | nvarchar(200) | YES |
| `UserOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `UserOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `UserOrganizationIsTop150` | bit | YES |
| `IsUserPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `IsUserInWatchlist` | bit | YES |
| `UserOrganizationRejectionRateBin` | nvarchar(50) | YES |
| `UserOrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `UserOrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `HIndex` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | varchar(14) | YES |
| `ActivityBins` | varchar(14) | YES |
| `ConnectivityBins` | varchar(14) | YES |
| `InfluenceBins` | varchar(14) | YES |
| `ProductivityBins` | varchar(14) | YES |
| `FrontiersBins` | varchar(14) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### JournalRole

| Column | Type | Nullable |
|---|---|---|
| `JournalRoleId` | nvarchar(10) | NO |
| `RoleId` | int(10) | NO |
| `Role` | varchar(50) | NO |
| `RoleGroup` | nvarchar(50) | NO |
| `IsAdminOfficeRole` | bit | NO |
| `IsJournalEditorialBoardRole` | bit | NO |
| `IsResearchTopicEditorRole` | bit | NO |
| `IsArticleReviewBoardRole` | bit | NO |
| `IsArticleAuthorsRole` | bit | NO |
| `Rank.ResearchTopic` | smallint(5) | YES |
| `Rank.Article` | smallint(5) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### JournalUserMetrics

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(100) | YES |
| `TenantGroup` | varchar(20) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserIsEditor` | bit | YES |
| `UserIsEBM` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserIsAuthor` | bit | YES |
| `UserOrder` | bigint(19) | YES |
| `RoleId` | int(10) | YES |
| `Role` | nvarchar(50) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `JournalRole.FirstAssigned.Date` | datetime | YES |
| `Rank.ResearchTopic` | int(10) | YES |
| `Rank.Article` | int(10) | YES |
| `JoinDate` | datetime | YES |
| `RegistrationDate` | datetime | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `Program` | nvarchar(50) | YES |
| `Domain` | nvarchar(50) | YES |
| `Field` | nvarchar(150) | YES |
| `Journal` | nvarchar(150) | YES |
| `Specialty` | nvarchar(150) | YES |
| `Section` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `OrganizationsHighestRankWoS` | int(10) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | YES |
| `IsUserPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `IsUserInWatchlist` | bit | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### Journals

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Taxonomy` | nvarchar(200) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `TaxonomyLevel` | varchar(9) | YES |
| `JournalLevel` | nvarchar(20) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalId` | int(10) | NO |
| `Journal` | nvarchar(150) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalDevelopment.SeniorJournalManager` | nvarchar(100) | YES |
| `JournalSpecialist.Count` | int(10) | YES |
| `JournalSegmentId` | nvarchar(30) | YES |
| `JournalSegment` | nvarchar(100) | YES |
| `JournalSegmentId.Previous` | nvarchar(30) | YES |
| `JournalSegment.Previous` | nvarchar(100) | YES |
| `SegmentId` | nvarchar(30) | YES |
| `Segment` | nvarchar(100) | YES |
| `SegmentId.Previous` | nvarchar(30) | YES |
| `Segment.Previous` | nvarchar(100) | YES |
| `SegmentBonusId` | nvarchar(30) | YES |
| `SegmentBonus` | nvarchar(100) | YES |
| `JournalDevelopment.SegmentManager` | nvarchar(100) | YES |
| `PortfolioId` | nvarchar(32) | YES |
| `Portfolio` | nvarchar(128) | YES |
| `JournalDevelopment.PortfolioManager` | nvarchar(400) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `FullName` | nvarchar(200) | YES |
| `Abbreviation` | nvarchar(100) | YES |
| `ParentTaxonomyId` | bigint(19) | YES |
| `DomainId` | bigint(19) | NO |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `TypeId` | int(10) | YES |
| `Type` | nvarchar(30) | YES |
| `ISSN` | nvarchar(30) | YES |
| `StatusId` | int(10) | YES |
| `Status` | varchar(7) | YES |
| `IsOnline` | bit | YES |
| `IsDeleted` | bit | YES |
| `IsOpenForSubmission` | bit | YES |
| `SubmissionStatus` | varchar(6) | YES |
| `MissionStatement` | nvarchar | YES |
| `PublishDate` | datetime | YES |
| `ModifyDate` | datetime | YES |
| `TypeSetterUserId` | int(10) | YES |
| `TypeSetterUserName` | nvarchar(400) | YES |
| `FirstAcceptanceDate` | date | YES |
| `FirstPublicationDate.JI` | date | YES |
| `COPE.IsEligible` | bit | YES |
| `COPE.IndexationStatus` | nvarchar(30) | YES |
| `COPE.Conditions.HasMoreThan12Months` | bit | YES |
| `DOAJ.IsEligible` | bit | YES |
| `DOAJ.IndexationStatus` | nvarchar(30) | YES |
| `DOAJ.Conditions.HasPublished5Articles` | bit | YES |
| `DOAJ.Conditions.HasPublished10Articles` | bit | YES |
| `DOAJ.Conditions.IsFirstPublicationOlder12M` | bit | YES |
| `DOAJ.Conditions.LowPercentagePublicationAuthoredByEbm` | bit | YES |
| `DOAJ.Conditions.LowTeAuthorRatioPerRt` | bit | YES |
| `DOAJ.MaxTeAuthorRatioPerRt` | decimal(18) | YES |
| `DOAJ.PercentagePublicationAuthoredByEbm` | decimal(18) | YES |
| `DOAJ.FirstPublicationDate` | date | YES |
| `DOAJ.DOI5` | nvarchar(50) | YES |
| `DOAJ.ArticlesCountThreshold2` | int(10) | YES |
| `PMC.IsEligible` | bit | YES |
| `PMC.IndexationStatus` | nvarchar(30) | YES |
| `PMC.Conditions.HasPublished25Articles` | bit | YES |
| `OriginalResearch.Percentage` | decimal(18) | YES |
| `Reviews.Percentage` | decimal(18) | YES |
| `CaseReports.Percentage` | decimal(18) | YES |
| `Others.Percentage` | decimal(18) | YES |
| `MED.IsEligible` | bit | YES |
| `MED.IndexationStatus` | nvarchar(30) | YES |
| `MED.Conditions.HasPublished40Articles` | bit | YES |
| `MED.Conditions.HasMoreThan12Months` | bit | YES |
| `MED.Conditions.HasPublicationsSpontaneous12MonthsOver40Percentage` | bit | YES |
| `MED.Conditions.HasPublicationsSpontaneous12MonthsUnder65Percentage` | bit | YES |
| `MED.Conditions.HasOriginalResearchCountOver60` | bit | YES |
| `MED.Conditions.HasReviewCountUnder40` | bit | YES |
| `Scopus.IsEligible` | bit | YES |
| `Scopus.IndexationStatus` | nvarchar(30) | YES |
| `Scopus.Conditions.HasPublished40Articles` | bit | YES |
| `Scopus.Conditions.HasFCE` | bit | YES |
| `Scopus.Conditions.HasMoreThan24Months` | bit | YES |
| `Scopus.Conditions.HasPublicationsAveragePerYearOver30` | bit | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### Persons

| Column | Type | Nullable |
|---|---|---|
| `PersonUserId` | bigint(19) | NO |
| `PersonUserId.Original` | bigint(19) | NO |
| `PersonId` | bigint(19) | NO |
| `Person.JournalUserId` | bigint(19) | NO |
| `Person.SpaceId` | int(10) | YES |
| `Person.UserId` | int(10) | YES |
| `Person.Email` | nvarchar(300) | YES |
| `IsPrimaryEmail` | bit | YES |
| `IsJournalUser` | bit | YES |
| `IsRegisteredUser` | bit | YES |
| `IsNonRegisteredUser` | bit | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | char(3) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | nvarchar(50) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `HighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `TopRankRosstId` | nvarchar(40) | YES |
| `HighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `HighestRankFrontiersPriority` | int(10) | YES |
| `HighestRankFrontiersPriorityBins` | nvarchar(50) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `CountryOrder` | int(10) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `OwnerEmployeeCountry13RegionsBin` | nvarchar(50) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `EditingInvitationsReceivedCount` | int(10) | YES |
| `EditingInvitationsAcceptedCount` | int(10) | YES |
| `EditingInvitationsDeclinedCount` | int(10) | YES |
| `ReviewingInvitationsReceivedCount` | int(10) | YES |
| `ReviewingInvitationsAcceptedCount` | int(10) | YES |
| `ReviewingInvitationsDeclinedCount` | int(10) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserFirstName` | nvarchar(150) | YES |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserLastName` | nvarchar(150) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserRegisterDate` | datetime | YES |
| `UserActivateDate` | datetime | YES |
| `UserModifyDate` | datetime | YES |
| `UserIsDeleted` | bit | YES |
| `UserIsActivated` | bit | YES |
| `UserStatus` | nvarchar(30) | YES |
| `UserCompletedRegistration` | bit | YES |
| `UserIsLoggedIn` | bit | YES |
| `UserIsAdmin` | bit | YES |
| `UserIsAuthor` | bit | YES |
| `UserIsEditor` | bit | YES |
| `UserIsResearchTopicEditor` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserEditorialBoardRoles` | varchar(500) | YES |
| `UserAuthorRoles` | varchar(500) | YES |
| `UserRolesNames` | varchar(500) | YES |
| `UserIsAdmin.Frontiers` | bit | YES |
| `UserIsAuthor.Frontiers` | bit | YES |
| `UserIsEditor.Frontiers` | bit | YES |
| `UserIsResearchTopicEditor.Frontiers` | bit | YES |
| `UserIsReviewer.Frontiers` | bit | YES |
| `IsUserInWatchList` | bit | YES |
| `JournalUserIsEditor` | bit | YES |
| `JournalUserIsEBM` | bit | YES |
| `JournalUserIsReviewer` | bit | YES |
| `JournalUserIsAuthor` | bit | YES |
| `JournalRoleId` | nvarchar(50) | YES |
| `JournalUserRoleId` | int(10) | YES |
| `JournalUserRole` | nvarchar(50) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `JournalRole.FirstAssigned.Date` | datetime | YES |
| `Rank.ResearchTopic` | int(10) | YES |
| `Rank.Article` | int(10) | YES |
| `JournalUserFirstTaxonomyId` | bigint(19) | YES |
| `JournalUserFirstJoinDate` | datetime | YES |
| `JournalUserOrder` | int(10) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### ResearchTopicAbstracts

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicAbstractId` | bigint(19) | NO |
| `ResearchTopicAbstractId.Original` | int(10) | NO |
| `AbstractResearchTopicId` | bigint(19) | NO |
| `AbstractTaxonomyId` | bigint(19) | YES |
| `AbstractTitle` | nvarchar | YES |
| `AbstractStage` | nvarchar(100) | YES |
| `AbstractAuthorPrimaryAffiliationCountry` | nvarchar(100) | YES |
| `AbstractAuthorEmail` | nvarchar(100) | YES |
| `Abstract.Submitted` | datetime | YES |
| `Abstract.Accepted` | datetime | YES |
| `Abstract.Rejected` | datetime | YES |
| `AbstractOrder` | bigint(19) | YES |
| `OrganizationId` | bigint(19) | YES |
| `RosstId` | nvarchar(40) | YES |
| `AbstractCountryId` | nvarchar(10) | YES |
| `AbstractCountry` | nvarchar(100) | YES |
| `AbstractContinent` | nvarchar(13) | YES |
| `AbstractCountry3RegionsBinFocus` | nvarchar(50) | YES |
| `AbstractCountry4RegionsBin` | nvarchar(50) | YES |
| `AbstractCountry5RegionsBin` | nvarchar(50) | YES |
| `AbstractCountry8RegionsBin` | nvarchar(50) | YES |
| `AbstractCountry13RegionsBin` | nvarchar(50) | YES |
| `AbstractCountry8RegionsBin-China` | nvarchar(50) | YES |
| `AbstractCountry8RegionsBin-ChinaCAS` | nvarchar(50) | YES |
| `AbstractCountryFocusRegionsBin` | nvarchar(50) | YES |
| `AbstractCountryRejectionRate` | nvarchar(50) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### ResearchTopicCoordinators

| Column | Type | Nullable |
|---|---|---|
| `CoordinatorId` | bigint(19) | NO |
| `CoordinatorSpaceId` | smallint(5) | YES |
| `CoordinatorUserId` | int(10) | NO |
| `CoordinatorPersonUserId` | bigint(19) | NO |
| `CoordinatorJournalUserId` | bigint(19) | YES |
| `CoordinatorTaxonomyId` | bigint(19) | NO |
| `CoordinatorResearchTopicId` | bigint(19) | NO |
| `IsFrontiers` | varchar(20) | YES |
| `IsQualitricsSurveyForCFP` | bit | NO |
| `IsQualitricsSurveyForClosedRT` | bit | NO |
| `CoordinatorCreateDate` | datetime | NO |
| `CoordinatorModifyDate` | datetime | YES |
| `CoordinatorOrder` | int(10) | NO |
| `CoordinatorUserOrder` | int(10) | NO |
| `KeyMetrics.CoordinatorId` | bigint(19) | YES |
| `BL Author` | int(10) | YES |
| `BL Coordinator` | int(10) | YES |
| `RT Hosted by AE` | int(10) | NO |
| `RT Hosted by AE Own Section` | int(10) | NO |
| `TE EB Max Role` | nvarchar(50) | YES |
| `TE Promotable` | int(10) | YES |
| `RT.Hosted.Count` | int(10) | YES |
| `Last.TopicHosted` | datetime | YES |
| `TimeSince.Last.TopicHosted` | int(10) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(200) | YES |
| `TenantGroup` | nvarchar(50) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `PersonUserId` | bigint(19) | YES |
| `PersonId` | bigint(19) | YES |
| `Person.UserId` | int(10) | YES |
| `Person.Email` | nvarchar(300) | YES |
| `IsPrimaryEmail` | bit | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | char(3) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | nvarchar(50) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `HighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `TopRankRosstId` | nvarchar(40) | YES |
| `HighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `HighestRankFrontiersPriority` | int(10) | YES |
| `HighestRankFrontiersPriorityBins` | nvarchar(50) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `CountryOrder` | int(10) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserFirstName` | nvarchar(150) | YES |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserLastName` | nvarchar(150) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserRegisterDate` | datetime | YES |
| `UserActivateDate` | datetime | YES |
| `UserModifyDate` | datetime | YES |
| `UserIsDeleted` | bit | YES |
| `UserIsActivated` | bit | YES |
| `UserStatus` | nvarchar(30) | YES |
| `UserCompletedRegistration` | bit | YES |
| `UserIsLoggedIn` | bit | YES |
| `UserIsAdmin` | bit | YES |
| `UserIsAuthor` | bit | YES |
| `UserIsEditor` | bit | YES |
| `UserIsResearchTopicEditor` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserEditorialBoardRoles` | varchar(500) | YES |
| `UserIsAdmin.Frontiers` | bit | YES |
| `UserIsAuthor.Frontiers` | bit | YES |
| `UserIsEditor.Frontiers` | bit | YES |
| `UserIsResearchTopicEditor.Frontiers` | bit | YES |
| `UserIsReviewer.Frontiers` | bit | YES |
| `IsUserInWatchList` | bit | YES |
| `FirstName` | nvarchar(150) | YES |
| `MiddleName` | nvarchar(50) | YES |
| `LastName` | nvarchar(150) | YES |
| `Name` | nvarchar(400) | YES |
| `Email` | nvarchar(100) | YES |
| `UserPrimaryOrganizationId` | int(10) | YES |
| `UserPrimaryRosstId` | nvarchar(40) | YES |
| `UserPrimaryOrganization` | nvarchar(200) | YES |
| `UserPrimaryOrganizationCountryId` | char(3) | YES |
| `UserPrimaryOrganizationCountry` | nvarchar(100) | YES |
| `UserPrimaryOrganizationContinentId` | char(2) | YES |
| `UserPrimaryOrganizationContinent` | nvarchar(50) | YES |
| `IsUserPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `UserOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `UserOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `Ranking` | int(10) | YES |
| `OrganizationsHighestRankWoS` | int(10) | YES |
| `HIndex Bins` | nvarchar(20) | YES |
| `Activity Bins` | nvarchar(20) | YES |
| `Connectivity Bins` | nvarchar(20) | YES |
| `Influence Bins` | nvarchar(20) | YES |
| `Productivity Bins` | nvarchar(20) | YES |
| `Frontiers Bins` | nvarchar(20) | YES |
| `Watch List Country` | bit | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `RoleId` | int(10) | NO |
| `Role` | nvarchar(50) | NO |
| `Is Editor EBM` | bit | YES |
| `Journal Responsible` | nvarchar(100) | YES |
| `Program Responsible` | nvarchar(100) | YES |
| `ResearchTopicId.Original` | int(10) | YES |
| `RT Title` | nvarchar | YES |
| `IsRTClosed` | bit | YES |
| `IsRTCompleted` | bit | YES |
| `IsRTDeleted` | bit | YES |
| `IsRTOnline` | bit | YES |
| `Is RT COVID Related?` | bit | YES |
| `ResearchTopic.OnlineDate` | datetime | YES |
| `RT Online Date` | datetime | YES |
| `ResearchTopic.CloseDate` | datetime | YES |
| `ResearchTopic.CompleteDate` | datetime | YES |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### ResearchTopicEditors

| Column | Type | Nullable |
|---|---|---|
| `EditorId` | bigint(19) | NO |
| `EditorSpaceId` | smallint(5) | YES |
| `EditorUserId` | int(10) | NO |
| `EditorPersonUserId` | bigint(19) | NO |
| `EditorJournalUserId` | bigint(19) | YES |
| `EditorTaxonomyId` | bigint(19) | NO |
| `EditorResearchTopicId` | bigint(19) | NO |
| `IsFrontiers` | varchar(20) | YES |
| `IsNotificationEnabled` | bit | NO |
| `LastNotificationSendDate` | datetime | YES |
| `EditorCreateDate` | datetime | NO |
| `EditorModifyDate` | datetime | NO |
| `EditorOrder` | bigint(19) | YES |
| `EditorUserOrder` | bigint(19) | YES |
| `KeyMetrics.EditorId` | bigint(19) | YES |
| `BL Author` | int(10) | YES |
| `BL Editor` | int(10) | YES |
| `RT Hosted by AE` | int(10) | YES |
| `RT Hosted by AE Own Section` | int(10) | YES |
| `TE EB Max Role` | nvarchar(50) | YES |
| `TE Promotable` | int(10) | YES |
| `RT.Hosted.Count` | int(10) | YES |
| `Last.TopicHosted` | datetime | YES |
| `TimeSince.Last.TopicHosted` | int(10) | YES |
| `AnalyticBins.EditorId` | bigint(19) | YES |
| `RT Hosted Bins` | nvarchar(50) | YES |
| `Time since last RT Hosted Bins` | nvarchar(50) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(200) | YES |
| `TenantGroup` | nvarchar(50) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `UserId` | int(10) | NO |
| `ResearchTopicId` | bigint(19) | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | NO |
| `UserIdOrder` | bigint(19) | YES |
| `RTs Hosted` | int(10) | YES |
| `Time Since Last Topic Hosted` | int(10) | YES |
| `PersonUserId` | bigint(19) | YES |
| `PersonId` | bigint(19) | YES |
| `Person.UserId` | int(10) | YES |
| `Person.Email` | nvarchar(300) | YES |
| `IsPrimaryEmail` | bit | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | char(3) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | nvarchar(50) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `HighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `TopRankRosstId` | nvarchar(40) | YES |
| `HighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `HighestRankFrontiersPriority` | int(10) | YES |
| `HighestRankFrontiersPriorityBins` | nvarchar(50) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `CountryOrder` | int(10) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserFirstName` | nvarchar(150) | YES |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserLastName` | nvarchar(150) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserRegisterDate` | datetime | YES |
| `UserActivateDate` | datetime | YES |
| `UserModifyDate` | datetime | YES |
| `UserIsDeleted` | bit | YES |
| `UserIsActivated` | bit | YES |
| `UserStatus` | nvarchar(30) | YES |
| `UserCompletedRegistration` | bit | YES |
| `UserIsLoggedIn` | bit | YES |
| `UserIsAdmin` | bit | YES |
| `UserIsAuthor` | bit | YES |
| `UserIsEditor` | bit | YES |
| `UserIsResearchTopicEditor` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserEditorialBoardRoles` | varchar(500) | YES |
| `UserIsAdmin.Frontiers` | bit | YES |
| `UserIsAuthor.Frontiers` | bit | YES |
| `UserIsEditor.Frontiers` | bit | YES |
| `UserIsResearchTopicEditor.Frontiers` | bit | YES |
| `UserIsReviewer.Frontiers` | bit | YES |
| `IsUserInWatchList` | bit | YES |
| `FirstName` | nvarchar(150) | YES |
| `MiddleName` | nvarchar(50) | YES |
| `LastName` | nvarchar(150) | YES |
| `Name` | nvarchar(400) | YES |
| `Email` | nvarchar(100) | YES |
| `UserPrimaryOrganizationId` | int(10) | YES |
| `UserPrimaryRosstId` | nvarchar(40) | YES |
| `UserPrimaryOrganization` | nvarchar(200) | YES |
| `UserPrimaryOrganizationCountryId` | char(3) | YES |
| `UserPrimaryOrganizationCountry` | nvarchar(100) | YES |
| `UserPrimaryOrganizationContinentId` | char(2) | YES |
| `UserPrimaryOrganizationContinent` | nvarchar(50) | YES |
| `IsUserPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `UserOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `UserOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `Ranking` | int(10) | YES |
| `OrganizationsHighestRankWoS` | int(10) | YES |
| `HIndex Bins` | nvarchar(20) | YES |
| `Activity Bins` | nvarchar(20) | YES |
| `Connectivity Bins` | nvarchar(20) | YES |
| `Influence Bins` | nvarchar(20) | YES |
| `Productivity Bins` | nvarchar(20) | YES |
| `Frontiers Bins` | nvarchar(20) | YES |
| `Watch List Country` | bit | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `RoleId` | int(10) | NO |
| `Role` | nvarchar(50) | NO |
| `Is Editor EBM` | bit | YES |
| `Journal Responsible` | nvarchar(100) | YES |
| `Program Responsible` | nvarchar(100) | YES |
| `ResearchTopicId.Original` | int(10) | YES |
| `RT Title` | nvarchar | YES |
| `IsRTClosed` | bit | YES |
| `IsRTCompleted` | bit | YES |
| `IsRTDeleted` | bit | YES |
| `IsRTOnline` | bit | YES |
| `Is RT COVID Related?` | bit | YES |
| `ResearchTopic.OnlineDate` | datetime | YES |
| `RT Online Date` | datetime | YES |
| `ResearchTopic.CloseDate` | datetime | YES |
| `ResearchTopic.CompleteDate` | datetime | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### ResearchTopics

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(100) | NO |
| `ResearchTopicId.Original` | int(10) | NO |
| `ResearchTopicTaxonomyId` | bigint(19) | NO |
| `Title` | nvarchar | NO |
| `Description` | nvarchar | YES |
| `ParticipatingJournals` | nvarchar | YES |
| `StageId` | int(10) | YES |
| `Stage` | nvarchar(30) | YES |
| `EBookId` | bigint(19) | YES |
| `EBookId.Original` | int(10) | YES |
| `EBookPublishYear` | int(10) | YES |
| `EBookStatus` | nvarchar(150) | YES |
| `URLEBookPage` | nvarchar(122) | YES |
| `IsActive` | bit | NO |
| `IsOnline` | bit | NO |
| `IsClosed` | bit | NO |
| `IsCompleted` | bit | NO |
| `IsSuggested` | bit | NO |
| `IsRejected` | bit | NO |
| `IsDeleted` | bit | NO |
| `DeletionReasonId` | int(10) | YES |
| `DeletionReason` | varchar(500) | YES |
| `URLResearchTopicPage` | nvarchar(100) | YES |
| `ShortURLResearchTopicPage` | nvarchar(50) | YES |
| `Comments` | nvarchar | YES |
| `SuggestedArticles.Count` | int(10) | YES |
| `SuggestedArticles.Count.Discarded` | int(10) | YES |
| `SuggestedArticles.Count.Invited` | int(10) | YES |
| `SuggestedArticles.Count.Accepted` | int(10) | YES |
| `SuggestedArticles.Count.Declined` | int(10) | YES |
| `SuggestedArticles.ConversionRate` | int(10) | YES |
| `IsSuggestedContributorsEnabledForTopicEditors` | bit | YES |
| `IsSuggestedManuscriptEnabledForTopicEditors` | bit | YES |
| `TopicEditorsMonitoringStartDate` | datetime | YES |
| `TopicEditorsMonitoringReminderFrequency` | int(10) | YES |
| `IsCOVIDRelated` | bit | YES |
| `IsFromACPOpportunity` | bit | YES |
| `CampaignName` | nvarchar(100) | YES |
| `ParentCampaignName` | nvarchar(100) | YES |
| `UltimateParentCampaign` | nvarchar(100) | YES |
| `IsCollectionSeries` | bit | YES |
| `IsSocietyAffiliation` | bit | YES |
| `Dates.ResearchTopicId` | bigint(19) | YES |
| `CreateDate` | datetime | YES |
| `StageDate` | datetime | YES |
| `OnlineDate` | datetime | YES |
| `DeletedDate` | datetime | YES |
| `CloseDate` | datetime | YES |
| `CompleteDate` | datetime | YES |
| `ShareEBookDate` | datetime | YES |
| `SubmissionInvitationSendDate` | datetime | YES |
| `EditorialRequestDate` | datetime | YES |
| `SubmissionDeadline` | datetime | YES |
| `AbstractSubmissionDeadline` | datetime | YES |
| `ExtendedSubmissionDeadline` | datetime | YES |
| `PublicExtendedDeadline` | datetime | YES |
| `InPreparationStageDate` | datetime | YES |
| `SuggestedStageDate` | datetime | YES |
| `RejectedStageDate` | datetime | YES |
| `DeletedStageDate` | datetime | YES |
| `InDiscussionStageDate` | datetime | YES |
| `LostStageDate` | datetime | YES |
| `Organization.ResearchTopicId` | bigint(19) | YES |
| `EditorsOrganizationsHighestRankFrontiersPriorityOrganizationId` | bigint(19) | YES |
| `EditorsOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `EditorsOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `EditorsOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `PrimaryOrganizationId` | bigint(19) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(50) | YES |
| `Continent` | nvarchar(50) | YES |
| `Country3RegionsBinFocus` | nvarchar(50) | YES |
| `Country4RegionsBin` | nvarchar(50) | YES |
| `Country5RegionsBin` | nvarchar(50) | YES |
| `Country7RegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin` | nvarchar(50) | YES |
| `Country13RegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin-China` | nvarchar(50) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(50) | YES |
| `CountryFocusRegionsBin` | nvarchar(50) | YES |
| `CountryRejectionRate` | nvarchar(50) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `OwnerEmployeeCountry13RegionsBin` | nvarchar(50) | YES |
| `Country_RegionPriority` | nvarchar(50) | YES |
| `Country8RegionsBin_RegionPriority` | nvarchar(50) | YES |
| `Country13RegionsBin_RegionPriority` | nvarchar(50) | YES |
| `Country_ContactPriority` | nvarchar(50) | YES |
| `Country8RegionsBin_ContactPriority` | nvarchar(50) | YES |
| `Country13RegionsBin_ContactPriority` | nvarchar(50) | YES |
| `KeyMetrics.ResearchTopicId` | bigint(19) | YES |
| `CountParticipatingJournals` | int(10) | YES |
| `ResearchTopicIsCrossListed` | bit | YES |
| `CountSubmissionDeadlineDates` | int(10) | YES |
| `CountExtendedSubmissionDeadlineDates` | int(10) | YES |
| `CountExpectedArticles` | int(10) | YES |
| `CountAbstractsNotRejected` | int(10) | YES |
| `CountAbstractsSubmitted` | int(10) | YES |
| `Facebook Inbound` | float(53) | YES |
| `Facebook Outbound` | float(53) | YES |
| `Twitter Inbound` | float(53) | YES |
| `Twitter Outbound` | float(53) | YES |
| `GooglePlus Inbound` | float(53) | YES |
| `GooglePlus Outbound` | float(53) | YES |
| `Linkedin Inbound` | float(53) | YES |
| `Linkedin Outbound` | float(53) | YES |
| `Others Inbound` | float(53) | YES |
| `Others Outbound` | float(53) | YES |
| `CountArticlesViews` | int(10) | YES |
| `CountArticlesDownloads` | int(10) | YES |
| `CountArticlesFrontiersViews` | int(10) | YES |
| `CountArticlesFrontiersDownloads` | int(10) | YES |
| `CountFrontiersViewsDownloads` | int(10) | YES |
| `CountArticlesCrossrefCitations` | int(10) | YES |
| `CountArticlesScopusCitations` | int(10) | YES |
| `CountArticlesPMCViews` | int(10) | YES |
| `CountArticlesPMCDownloads` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `CountArticlesCitations` | int(10) | YES |
| `CountArticlesCitationsArticles` | int(10) | YES |
| `CountSubmittedArticles` | int(10) | YES |
| `CountAcceptedArticles` | int(10) | YES |
| `CountPublishedArticles` | int(10) | YES |
| `CountRejectedArticles` | int(10) | YES |
| `CountInReviewArticles` | int(10) | YES |
| `SubmittedManuscriptsbyInvitedContributors.cfp` | int(10) | YES |
| `CountEditorialArticles` | int(10) | YES |
| `CountEditorialArticlesPublished` | int(10) | YES |
| `CountNonRejectedAbstracts` | int(10) | YES |
| `CountSubmittedAbstracts` | int(10) | YES |
| `RTEditors.Count` | int(10) | YES |
| `PublishingMetrics.ResearchTopicId` | bigint(19) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `Users.ResearchTopicId` | bigint(19) | YES |
| `Editors` | nvarchar(2000) | YES |
| `EditorIsEBM` | int(10) | YES |
| `AnyEditorIsJournalEditor` | bit | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `OwnerUserId` | int(10) | YES |
| `OwnerUserName` | nvarchar(400) | YES |
| `CreatorUserId` | int(10) | YES |
| `CreatorUserName` | nvarchar(400) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `ResearchTopicTitle` | nvarchar | NO |
| `Campaign` | nvarchar(100) | YES |
| `ParentCampaign` | nvarchar(100) | YES |
| `ResearchTopicCreateDate` | datetime | YES |
| `Organization` | nvarchar(200) | YES |
| `OrganizationId` | bigint(19) | YES |
| `RosstId` | nvarchar(40) | YES |
| `HighestRankOrganizationRejectionRateBin` | nvarchar(50) | YES |
| `HighestRankOrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `HighestRankOrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `Count.RT.Editors` | int(10) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### ReviewBoardMembers

| Column | Type | Nullable |
|---|---|---|
| `ReviewBoardMemberId` | bigint(19) | NO |
| `ReviewBoardMemberSpaceId` | smallint(5) | YES |
| `ReviewBoardMemberUserId` | int(10) | YES |
| `ReviewBoardMemberJournalUserId` | bigint(19) | YES |
| `ReviewBoardMemberPersonUserId` | bigint(19) | YES |
| `ReviewBoardMemberArticleId` | bigint(19) | YES |
| `ReviewBoardMemberTaxonomyId` | bigint(19) | YES |
| `Email` | nvarchar(100) | YES |
| `FirstName` | nvarchar(150) | YES |
| `LastName` | nvarchar(150) | YES |
| `Name` | nvarchar(400) | YES |
| `JoinDate` | datetime | YES |
| `RoleId` | int(10) | YES |
| `Role` | varchar(50) | YES |
| `RoleAbbr` | varchar(20) | YES |
| `OriginalRoleId` | int(10) | YES |
| `IsVolunteer` | bit | YES |
| `IsVolunteerExcluded` | bit | YES |
| `VolunteerExclusionReason` | nvarchar(250) | YES |
| `ReviewBoardStatusId` | tinyint(3) | YES |
| `ReviewBoardStatus` | varchar(25) | YES |
| `ReviewBoardMemberUserOrder` | int(10) | YES |
| `KeyMetrics.ReviewBoardMemberId` | bigint(19) | YES |
| `IsTopFirstAssignedRole` | bit | YES |
| `IsReviewMember` | bit | YES |
| `Reviewer.LatestInviteDate` | datetime | YES |
| `Reviewer.WithdrawDate` | datetime | YES |
| `ReviewReportDate.IndependentReviewSubmitted` | datetime | YES |
| `ReviewReportDate.FinalReportSubmitted` | datetime | YES |
| `ArticlesReviewed.Count` | int(10) | YES |
| `ArticlesEdited.Count` | int(10) | YES |
| `ArticlesEditedOrReviewed.Count` | int(10) | YES |
| `Last.Reviewer.ReviewDate` | datetime | YES |
| `Last.Reviewer.EditDate` | datetime | YES |
| `TimeSince.Last.Reviewer.EditingAssignment` | int(10) | YES |
| `TimeSince.Last.Reviewer.ReviewAssignment` | int(10) | YES |
| `TimeSince.Last.Reviewer.EditingOrReviewAssignment` | int(10) | YES |
| `ReviewReportRating` | decimal(10) | YES |
| `ArticlesReviewed.Count.Bin` | nvarchar(50) | YES |
| `ArticlesEdited.Count.Bin` | nvarchar(50) | YES |
| `ArticlesEditedOrReviewed.Count.Bin` | nvarchar(50) | YES |
| `TimeSince.Last.Reviewer.EditingAssignment.Bin` | nvarchar(50) | YES |
| `TimeSince.Last.Reviewer.ReviewAssignment.Bin` | nvarchar(50) | YES |
| `TimeSince.Last.Reviewer.EditingOrReviewAssignment.Bin` | nvarchar(50) | YES |
| `Invitation.ReviewBoardMemberId` | bigint(19) | YES |
| `ReviewBoardInvitationId` | bigint(19) | YES |
| `InviterUserId` | int(10) | YES |
| `Inviter` | nvarchar(150) | YES |
| `InviterEmail` | nvarchar(100) | YES |
| `InviteDate` | datetime | YES |
| `PersonUserId` | bigint(19) | YES |
| `PersonUserId.Original` | bigint(19) | YES |
| `PersonId` | bigint(19) | YES |
| `Person.JournalUserId` | bigint(19) | YES |
| `Person.SpaceId` | int(10) | YES |
| `Person.UserId` | int(10) | YES |
| `Person.Email` | nvarchar(300) | YES |
| `IsPrimaryEmail` | bit | YES |
| `IsJournalUser` | bit | YES |
| `IsRegisteredUser` | bit | YES |
| `IsNonRegisteredUser` | bit | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | char(3) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | nvarchar(50) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `HighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `TopRankRosstId` | nvarchar(40) | YES |
| `HighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `HighestRankFrontiersPriority` | int(10) | YES |
| `HighestRankFrontiersPriorityBins` | nvarchar(50) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `CountryOrder` | int(10) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `OwnerEmployeeCountry13RegionsBin` | nvarchar(50) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserFirstName` | nvarchar(150) | YES |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserLastName` | nvarchar(150) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserRegisterDate` | datetime | YES |
| `UserActivateDate` | datetime | YES |
| `UserModifyDate` | datetime | YES |
| `UserIsDeleted` | bit | YES |
| `UserIsActivated` | bit | YES |
| `UserStatus` | nvarchar(30) | YES |
| `UserCompletedRegistration` | bit | YES |
| `UserIsLoggedIn` | bit | YES |
| `UserIsAdmin` | bit | YES |
| `UserIsAuthor` | bit | YES |
| `UserIsEditor` | bit | YES |
| `UserIsResearchTopicEditor` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserEditorialBoardRoles` | varchar(500) | YES |
| `UserAuthorRoles` | varchar(500) | YES |
| `UserRolesNames` | varchar(500) | YES |
| `UserIsAdmin.Frontiers` | bit | YES |
| `UserIsAuthor.Frontiers` | bit | YES |
| `UserIsEditor.Frontiers` | bit | YES |
| `UserIsResearchTopicEditor.Frontiers` | bit | YES |
| `UserIsReviewer.Frontiers` | bit | YES |
| `IsUserInWatchList` | bit | YES |
| `JournalUserIsEditor` | bit | YES |
| `JournalUserIsEBM` | bit | YES |
| `JournalUserIsReviewer` | bit | YES |
| `JournalUserIsAuthor` | bit | YES |
| `JournalRoleId` | nvarchar(50) | YES |
| `JournalUserRoleId` | int(10) | YES |
| `JournalUserRole` | nvarchar(50) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `JournalRole.FirstAssigned.Date` | datetime | YES |
| `Rank.ResearchTopic` | int(10) | YES |
| `Rank.Article` | int(10) | YES |
| `JournalUserFirstTaxonomyId` | bigint(19) | YES |
| `JournalUserFirstJoinDate` | datetime | YES |
| `JournalUserOrder` | int(10) | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(200) | YES |
| `TenantGroup` | nvarchar(50) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `UserId` | int(10) | YES |
| `UserIdOrder` | int(10) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `ArticleTaxonomyId` | bigint(19) | YES |
| `ArticleDomain` | nvarchar(50) | YES |
| `ArticleDomainId` | bigint(19) | YES |
| `ArticleField` | nvarchar(150) | YES |
| `ArticleFieldId` | bigint(19) | YES |
| `ArticleSpecialtyId` | bigint(19) | YES |
| `ArticleJournal` | nvarchar(150) | YES |
| `ArticleJournalFullName` | nvarchar(300) | YES |
| `ArticleJournalTaxonomyId` | bigint(19) | YES |
| `ArticleSection` | nvarchar(100) | YES |
| `ArticleSpecialty` | nvarchar(150) | YES |
| `ArticleStageCategory` | nvarchar(30) | YES |
| `ArticleStageCategoryId` | int(10) | YES |
| `ArticleId` | bigint(19) | YES |
| `ArticleId.Original` | int(10) | YES |
| `ArticleIsAccepted` | bit | YES |
| `ArticleIsPublished` | bit | YES |
| `ArticleIsRejected` | bit | YES |
| `ArticleIsResearchTopic` | bit | YES |
| `ArticleIsSubmitted` | bit | YES |
| `ArticleStageDate.Accepted` | datetime | YES |
| `ArticleStageDate.EditorialAssignment` | datetime | YES |
| `ArticleStageDate.InIndependentReview` | datetime | YES |
| `ArticleStageDate.InInteractiveReview` | datetime | YES |
| `ArticleStageDate.ReceivedByJournal` | datetime | YES |
| `ArticleStageDate.Rejected` | datetime | YES |
| `ArticleStageDate.ReviewFinalized` | datetime | YES |
| `ArticleStageDate.Submitted` | datetime | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### Spaces

| Column | Type | Nullable |
|---|---|---|
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(200) | YES |
| `SpaceShortName` | nvarchar(20) | YES |
| `SpaceGUID` | uniqueidentifier | NO |
| `TenantGroup` | nvarchar(50) | YES |
| `WebDomain` | nvarchar(128) | NO |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### TaxonomyMetrics

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | NO |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

### UserMetrics

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `Email` | nvarchar(100) | YES |
| `FirstName` | nvarchar(150) | YES |
| `LastName` | nvarchar(150) | YES |
| `Name` | nvarchar(400) | YES |
| `Status` | nvarchar(30) | YES |
| `IsEditor` | bit | YES |
| `IsResearchTopicEditor` | bit | YES |
| `IsReviewer` | bit | YES |
| `IsDeleted` | bit | YES |
| `IsActivated` | bit | YES |
| `RegistrationDate` | datetime | YES |
| `RolesNames` | nvarchar(1000) | YES |
| `EditorialBoardRoles` | nvarchar(500) | YES |
| `AuthorRoles` | nvarchar(500) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `UserPrimaryOrganizationId` | int(10) | YES |
| `UserPrimaryRosstId` | nvarchar(40) | YES |
| `UserPrimaryOrganization` | nvarchar(200) | YES |
| `UserPrimaryOrganizationCountry` | nvarchar(100) | YES |
| `UserOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `UserOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `UserOrganizationIsTop150` | bit | YES |
| `IsUserPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `IsUserInWatchList` | bit | YES |
| `UserOrganizationRejectionRateBin` | nvarchar(50) | YES |
| `UserOrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `UserOrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |
| `ModifiedDate` | datetime2 | NO |
| `ValidUntil` | datetime2 | NO |

## [ReportingDataMart].[Shared]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### Article_Rejections

| Column | Type | Nullable |
|---|---|---|
| `Article_RejectionsId` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `Order` | bigint(19) | NO |
| `RejecterUserId` | int(10) | YES |
| `RejecterRoleId` | int(10) | YES |
| `RejecterRoleAbbr` | varchar(20) | NO |
| `RejecterJournalRoleId` | varchar(10) | YES |
| `RejectionReasonLabel` | nvarchar(50) | NO |
| `InviteDate` | datetime | NO |
| `SpaceId` | smallint(5) | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Invitation_Contributors_Status

| Column | Type | Nullable |
|---|---|---|
| `Invitation_Contributors_StatusId` | bigint(19) | NO |
| `ResearchTopicId` | bigint(19) | NO |
| `ContributorId` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ResearchTopicAbstractAcceptedDate.First` | datetime | YES |
| `IsFromResearchTopicEditorialTeam` | bit | YES |
| `HasContributorBeenInvited` | bit | YES |
| `HasContributorBeenInvited.Cfp` | bit | YES |
| `ContributorInvitationDate.logical` | datetime | YES |
| `HasConfirmedInvitation` | bit | YES |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

## [ReportingDataMart].[cdc]


### Common_Organization_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | YES |
| `Description` | nvarchar | YES |
| `Street` | nvarchar(200) | YES |
| `ZipCode` | nvarchar(30) | YES |
| `CityId` | int(10) | YES |
| `City` | nvarchar(200) | YES |
| `StateId` | int(10) | YES |
| `State` | nvarchar(150) | YES |
| `CountryId` | char(3) | YES |
| `RosstCountryId` | char(3) | YES |
| `Country` | nvarchar(100) | YES |
| `RosstCountry` | nvarchar(100) | YES |
| `ContinentId` | char(2) | YES |
| `Continent` | varchar(13) | YES |
| `ChinaClassificationId` | int(10) | YES |
| `IsCTI` | bit | YES |
| `IsCAS` | bit | YES |
| `IsCountryInWatchlist` | bit | YES |
| `Email` | nvarchar(100) | YES |
| `URL` | nvarchar(500) | YES |
| `Phone` | nvarchar(30) | YES |
| `Logo` | nvarchar(32) | YES |
| `IsDeleted` | bit | YES |
| `IsUserCreated` | bit | YES |
| `IsValidated` | bit | YES |
| `IsUnaffiliatedOption` | bit | YES |
| `Domains` | nvarchar(4000) | YES |
| `PrimaryTypeId` | int(10) | YES |
| `PrimaryType` | nvarchar(30) | YES |
| `CreateDate` | datetime | YES |
| `ModifyDate` | datetime | YES |
| `RankFrontiersPriority` | int(10) | YES |
| `AncestorsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `AncestorsTopRankRosstId` | nvarchar(40) | YES |
| `AncestorsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `AncestorsHighestRankFrontiersPriority` | int(10) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Process_EditorialBoard_Invitations_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `EditorialBoardInvitationId` | bigint(19) | YES |
| `SpaceId` | smallint(5) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `InvitationDate` | datetime | YES |
| `InvitationTypeId` | int(10) | YES |
| `InvitationType` | varchar(50) | YES |
| `InvitationSourceId` | int(10) | YES |
| `InvitationSource` | varchar(100) | YES |
| `InviterUserId` | int(10) | YES |
| `InviterEmail` | nvarchar(300) | YES |
| `InviterPersonUserId` | bigint(19) | YES |
| `InviterName` | nvarchar(400) | YES |
| `InviteeUserId` | int(10) | YES |
| `InviteeEmail` | varchar(150) | YES |
| `InviteePersonUserId` | bigint(19) | YES |
| `InviteeName` | nvarchar(452) | YES |
| `InviteeRoleId` | varchar(10) | YES |
| `InviteeRole` | varchar(50) | YES |
| `InviteeIsOnBoard` | bit | YES |
| `InvitationActivationNumber` | uniqueidentifier | YES |
| `InvitationStatusId` | int(10) | YES |
| `InvitationStatus` | varchar | YES |
| `InvitationStatusModifyDate` | datetime | YES |
| `LastReminderDate` | datetime | YES |
| `TotalReminderCount` | int(10) | YES |
| `DeclinationReasonId` | int(10) | YES |
| `DeclinationReason` | varchar(150) | YES |
| `DeclinationPersonalNote` | varchar | YES |
| `DeclinationComment` | varchar | YES |
| `InvitationReviewStatusId` | int(10) | YES |
| `InvitationReviewStatus` | nvarchar(100) | YES |
| `ReviewDecisionTypeId` | int(10) | YES |
| `ReviewDecisionType` | nvarchar(100) | YES |
| `ReviewRejectionReasonId` | int(10) | YES |
| `ReviewRejectionReason` | varchar(150) | YES |
| `ReviewInvalidReasonId` | int(10) | YES |
| `ReviewInvalidReason` | varchar(150) | YES |
| `SuggestedEditorId` | bigint(19) | YES |
| `SuggestedEditorUserId` | int(10) | YES |
| `SuggestedEditorEmail` | varchar(150) | YES |
| `SuggestedEditorPersonUserId` | bigint(19) | YES |
| `SuggestedEditorName` | nvarchar(301) | YES |
| `SuggestionMethodId` | bigint(19) | YES |
| `SuggestionMethod` | varchar(100) | YES |
| `SuggestionMethodType` | nvarchar(200) | YES |
| `SuggestionSourceId` | bigint(19) | YES |
| `SuggestionSource` | varchar(100) | YES |
| `SuggestionDiscardReasonId` | bigint(19) | YES |
| `SuggestionDiscardReason` | varchar(100) | YES |
| `SuggestionComments` | varchar(200) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_AuthorOrganizations_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `AuthorOrganizationsId` | bigint(19) | YES |
| `AuthorId` | bigint(19) | YES |
| `SpaceId` | smallint(5) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `OrganizationOrder` | int(10) | YES |
| `OrganizationSourceId` | char(1) | YES |
| `AuthorName` | nvarchar(300) | YES |
| `Organization` | nvarchar(200) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_Authors_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `AuthorId` | bigint(19) | YES |
| `AuthorUserId` | int(10) | YES |
| `AuthorJournalUserId` | bigint(19) | YES |
| `AuthorPersonUserId` | bigint(19) | YES |
| `AuthorEmail` | nvarchar(100) | YES |
| `AuthorSpaceId` | smallint(5) | YES |
| `RoleId` | int(10) | YES |
| `Role` | nvarchar(50) | YES |
| `RoleAbbr` | nvarchar(20) | YES |
| `JournalRoleId` | nvarchar(10) | YES |
| `AuthorArticleId` | bigint(19) | YES |
| `AuthorTaxonomyId` | bigint(19) | YES |
| `AuthorOrganizationId` | int(10) | YES |
| `AuthorRosstId` | nvarchar(40) | YES |
| `AuthorSource` | char(1) | YES |
| `ReviewAuthorId` | bigint(19) | YES |
| `ProductionAuthorId` | bigint(19) | YES |
| `AuthorTitle` | nvarchar(15) | YES |
| `AuthorFirstName` | nvarchar(300) | YES |
| `AuthorMiddleName` | nvarchar(100) | YES |
| `AuthorLastName` | nvarchar(300) | YES |
| `AuthorName` | nvarchar(600) | YES |
| `AuthorOriginalEmail` | nvarchar(100) | YES |
| `AuthorPrimaryEmailAddress` | nvarchar(100) | YES |
| `AuthorSuffix` | nvarchar(50) | YES |
| `AuthorOrder` | int(10) | YES |
| `IsCorrespondingAuthor` | bit | YES |
| `IsSubmittingAuthor` | bit | YES |
| `IsMainCorrespondingAuthor` | bit | YES |
| `IsLastAuthor` | bit | YES |
| `AuthorEmailOrder` | int(10) | YES |
| `ReviewerAuthorUserId` | int(10) | YES |
| `AuthorUserOrder` | int(10) | YES |
| `Dates.ArticleId` | bigint(19) | YES |
| `StageDate` | datetime | YES |
| `StageDate.InPreparation` | datetime | YES |
| `StageDate.Submitted` | datetime | YES |
| `StageDate.ReceivedByJournal` | datetime | YES |
| `StageDate.InitialValidation` | datetime | YES |
| `StageDate.JournalTransferCompleted` | datetime | YES |
| `StageDate.EditorialAssignment.Source` | datetime | YES |
| `StageDate.InReview` | datetime | YES |
| `StageDate.InIndependentReview` | datetime | YES |
| `StageDate.InInteractiveReview` | datetime | YES |
| `StageDate.ReviewFinalized` | datetime | YES |
| `StageDate.RejectionRecommended` | datetime | YES |
| `StageDate.Rejected` | datetime | YES |
| `StageDate.FinalValidation` | datetime | YES |
| `StageDate.RecommendationForRejectionRevoked` | datetime | YES |
| `StageDate.Accepted` | datetime | YES |
| `StageDate.InProduction` | datetime | YES |
| `StageDate.AuthorProof` | datetime | YES |
| `StageDate.AuthorProofApproved` | datetime | YES |
| `StageDate.Published` | datetime | YES |
| `StageDate.Deleted` | datetime | YES |
| `StageDate.Decision` | datetime | YES |
| `PartnerAcceptArticleDateTime` | datetime | YES |
| `PartnerRecommendRejectionDateTime` | datetime | YES |
| `PartnerRejectionDateTime` | datetime | YES |
| `PartnerRecommendValidationDateTime` | datetime | YES |
| `PartnerRecommendValidationApprovalDateTime` | datetime | YES |
| `PartnerPrescreeningEinCAssignedDateTime` | datetime | YES |
| `PartnerFinalizeReviewDateTime` | datetime | YES |
| `PartnerMonitorAEtoAccept/RejectDateTime` | datetime | YES |
| `PartnerAEtabnotificationDateTime` | datetime | YES |
| `PartnerAUTtabnotificationDateTime` | datetime | YES |
| `PartnerAEtab-MonitoringAUTtoreplyDateTime` | datetime | YES |
| `PartnerRe-submitManuscriptDateTime` | datetime | YES |
| `PartnerMonitorAUT_To_ResubmitReplyDateTime_Days` | datetime | YES |
| `SuggestedforResearchTopic.InviteDate` | datetime | YES |
| `SuggestedforResearchTopic.DiscardDate` | datetime | YES |
| `SuggestedforResearchTopic.AuthorAcceptDate` | datetime | YES |
| `SuggestedforResearchTopic.AuthorDeclineDate` | datetime | YES |
| `FirstPublishDate` | datetime | YES |
| `RequestforAuthortoReviseManuscriptDateTime` | datetime | YES |
| `KeyMetrics.AuthorId` | bigint(19) | YES |
| `KeyMetrics.ArticleId` | bigint(19) | YES |
| `Articles Submitted per Author` | int(10) | YES |
| `Articles Accepted per Author` | int(10) | YES |
| `First.SubmissionDate` | datetime | YES |
| `Last.Submitted` | datetime | YES |
| `Last.Accepted` | datetime | YES |
| `Last.Rejection` | datetime | YES |
| `Last.Decided` | datetime | YES |
| `Last.Decided.ArticleId` | bigint(19) | YES |
| `IsLatestArticleDecision` | bit | YES |
| `IsReturningAuthor` | bit | YES |
| `IsReturningAuthorCA` | bit | YES |
| `IsReturningAuthorSA` | bit | YES |
| `IsReturningAuthorEBM` | bit | YES |
| `IsReturningAuthorRT` | bit | YES |
| `IsReturningAuthorRTE` | bit | YES |
| `DaysSinceLastSubmission` | int(10) | YES |
| `DaysSinceLastAcceptance` | int(10) | YES |
| `DaysSinceLastRejection` | int(10) | YES |
| `DaysSinceLastDecision` | int(10) | YES |
| `DaysSinceLastPublication` | int(10) | YES |
| `LastDecidedReviewDays` | int(10) | YES |
| `ArticlesSubmitted.Count` | int(10) | YES |
| `ArticlesAccepted.Count` | int(10) | YES |
| `TimeSince.Last.Submitted.Article` | int(10) | YES |
| `TimeSince.Last.Accepted.Article` | int(10) | YES |
| `TimeSince.Last.Rejected.Article` | int(10) | YES |
| `AuthorRank` | int(10) | YES |
| `AnalyticBins.AuthorId` | bigint(19) | YES |
| `TimeSinceLastSubmission.Bin` | nvarchar(20) | YES |
| `TimeSinceLastAcceptance.Bin` | nvarchar(20) | YES |
| `TimeSinceLastRejection.Bin` | nvarchar(20) | YES |
| `TimeSinceLastDecision.Bin` | nvarchar(20) | YES |
| `TimeSinceLastPublication.Bin` | nvarchar(20) | YES |
| `PreviousReviewDecisionTime.Bin` | nvarchar(20) | YES |
| `Submitted Articles Bins` | nvarchar(50) | YES |
| `Accepted Articles Bins` | nvarchar(50) | YES |
| `Time Since Last Submitted Article Bins` | nvarchar(50) | YES |
| `Time Since Last Accepted Article Bins` | nvarchar(50) | YES |
| `Time Since Last Rejected Article Bins` | nvarchar(50) | YES |
| `Affiliations.AuthorId` | bigint(19) | YES |
| `LegacyAffiliationCountries` | nvarchar(500) | YES |
| `LegacyAffiliations` | nvarchar(4000) | YES |
| `Organization.AuthorId` | bigint(19) | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | nvarchar(10) | YES |
| `PrimaryOrganizationRosstCountryId` | nvarchar(10) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationRosstCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | nvarchar(10) | YES |
| `PrimaryOrganizationContinent` | nvarchar(13) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `AuthorOrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `AuthorOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `AuthorOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `AuthorOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(200) | YES |
| `TenantGroup` | nvarchar(50) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | datetime | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | datetime | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `ArticleId` | bigint(19) | YES |
| `Title` | nvarchar(15) | YES |
| `FirstName` | nvarchar(300) | YES |
| `MiddleName` | nvarchar(100) | YES |
| `LastName` | nvarchar(300) | YES |
| `Name` | nvarchar(600) | YES |
| `Email` | nvarchar(100) | YES |
| `Suffix` | nvarchar(50) | YES |
| `UserIdOrder` | int(10) | YES |
| `Article.StageDate.ReceivedByJournal` | datetime | YES |
| `Article.StageDate.Accepted` | datetime | YES |
| `Article.StageDate.Rejected` | datetime | YES |
| `Time Since Last Submitted Article` | int(10) | YES |
| `Time Since Last Accepted Article` | int(10) | YES |
| `Time Since Last Rejected Article` | int(10) | YES |
| `TimeSinceLast.Submission` | nvarchar(20) | YES |
| `TimeSinceLast.Acceptance` | nvarchar(20) | YES |
| `TimeSinceLast.Rejection` | nvarchar(20) | YES |
| `TimeSinceLast.Decision` | nvarchar(20) | YES |
| `ArticleId.Original` | int(10) | YES |
| `Article.IsSubmitted` | bit | YES |
| `Article.IsAccepted` | bit | YES |
| `Article.IsDeleted` | bit | YES |
| `IsFrontiers` | nvarchar(50) | YES |
| `PersonId` | bigint(19) | YES |
| `UserIsEditor.Frontiers` | bit | YES |
| `UserIsEditor` | bit | YES |
| `UserIsResearchTopicEditor.Frontiers` | bit | YES |
| `UserIsResearchTopicEditor` | bit | YES |
| `UserIsReviewer.Frontiers` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserLastName` | nvarchar(150) | YES |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserFirstName` | nvarchar(150) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `HIndex` | int(10) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `InfluencePercentile` | float(53) | YES |
| `IsAuthorInWatchlist` | bit | YES |
| `CountryId` | nvarchar(10) | YES |
| `RosstCountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `RosstCountry` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `IsAuthorFromWatchlistCountry` | bit | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `UserPrimaryOrganizationId` | int(10) | YES |
| `UserPrimaryRosstId` | nvarchar(40) | YES |
| `UserPrimaryOrganization` | nvarchar(200) | YES |
| `UserOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `UserOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `AuthorIsEBM` | bit | YES |
| `UserHIndex` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `__$command_id` | int(10) | YES |

### Reporting_CampaignMembers_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `CampaignMemberId` | char(18) | YES |
| `CampaignStatus` | nvarchar(40) | YES |
| `CampaignCRMId` | nvarchar(20) | YES |
| `CampaignName` | nvarchar(100) | YES |
| `ParentCampaignName` | nvarchar(100) | YES |
| `UltimateParentCampaignName` | nvarchar(100) | YES |
| `EmailAddress` | nvarchar(100) | YES |
| `CampaignMemberEmail` | nvarchar(200) | YES |
| `CampaignMemberUserId` | int(10) | YES |
| `CampaignMemberPersonUserId` | bigint(19) | YES |
| `CampaignMemberJournalUserId` | bigint(19) | YES |
| `CampaignMemberTaxonomyId` | bigint(19) | YES |
| `Is CM EBM` | bit | YES |
| `Is CM REV` | bit | YES |
| `JoinDate` | date | YES |
| `InviteDate` | date | YES |
| `CampaignRecordTypeCRMId` | nvarchar(20) | YES |
| `CampaignType` | nvarchar(50) | YES |
| `CampaignMemberCRMIdOrder` | int(10) | YES |
| `KeyMetrics.CampaignMemberId` | char(18) | YES |
| `Last.Reviewer.ReviewDate` | datetime | YES |
| `Last.Reviewer.EditDate` | datetime | YES |
| `LastSubmissionDate` | datetime | YES |
| `Days Since Last REV Assignment` | int(10) | YES |
| `Days Since Last Editing Assignment` | int(10) | YES |
| `Days Since Last Submission` | int(10) | YES |
| `Is Returning Author?` | bit | YES |
| `Has Hosted RT?` | bit | YES |
| `PersonUserId` | bigint(19) | YES |
| `PersonUserId.Original` | bigint(19) | YES |
| `PersonId` | bigint(19) | YES |
| `Person.JournalUserId` | bigint(19) | YES |
| `Person.SpaceId` | int(10) | YES |
| `Person.UserId` | int(10) | YES |
| `Person.Email` | nvarchar(300) | YES |
| `IsPrimaryEmail` | bit | YES |
| `IsJournalUser` | bit | YES |
| `IsRegisteredUser` | bit | YES |
| `IsNonRegisteredUser` | bit | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | char(3) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | nvarchar(50) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `HighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `TopRankRosstId` | nvarchar(40) | YES |
| `HighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `HighestRankFrontiersPriority` | int(10) | YES |
| `HighestRankFrontiersPriorityBins` | nvarchar(50) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `CountryOrder` | int(10) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `OwnerEmployeeCountry13RegionsBin` | nvarchar(50) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserFirstName` | nvarchar(150) | YES |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserLastName` | nvarchar(150) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserRegisterDate` | datetime | YES |
| `UserActivateDate` | datetime | YES |
| `UserModifyDate` | datetime | YES |
| `UserIsDeleted` | bit | YES |
| `UserIsActivated` | bit | YES |
| `UserStatus` | nvarchar(30) | YES |
| `UserCompletedRegistration` | bit | YES |
| `UserIsLoggedIn` | bit | YES |
| `UserIsAdmin` | bit | YES |
| `UserIsAuthor` | bit | YES |
| `UserIsEditor` | bit | YES |
| `UserIsResearchTopicEditor` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserEditorialBoardRoles` | varchar(500) | YES |
| `UserAuthorRoles` | varchar(500) | YES |
| `UserRolesNames` | varchar(500) | YES |
| `UserIsAdmin.Frontiers` | bit | YES |
| `UserIsAuthor.Frontiers` | bit | YES |
| `UserIsEditor.Frontiers` | bit | YES |
| `UserIsResearchTopicEditor.Frontiers` | bit | YES |
| `UserIsReviewer.Frontiers` | bit | YES |
| `IsUserInWatchList` | bit | YES |
| `JournalUserIsEditor` | bit | YES |
| `JournalUserIsEBM` | bit | YES |
| `JournalUserIsReviewer` | bit | YES |
| `JournalUserIsAuthor` | bit | YES |
| `JournalRoleId` | nvarchar(50) | YES |
| `JournalUserRoleId` | int(10) | YES |
| `JournalUserRole` | nvarchar(50) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `JournalRole.FirstAssigned.Date` | datetime | YES |
| `Rank.ResearchTopic` | int(10) | YES |
| `Rank.Article` | int(10) | YES |
| `JournalUserFirstTaxonomyId` | bigint(19) | YES |
| `JournalUserFirstJoinDate` | datetime | YES |
| `JournalUserOrder` | int(10) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `Campaign Name` | nvarchar(100) | YES |
| `Campaign Status` | nvarchar(40) | YES |
| `CampaignMemberCRMId` | char(18) | YES |
| `Campaign Type` | nvarchar(50) | YES |
| `UserId` | int(10) | YES |
| `UserPrimaryEmail` | nvarchar(100) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | YES |
| `OrganizationsHighestRank` | int(10) | YES |
| `Role` | nvarchar(50) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_Contributors_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `ContributorId` | bigint(19) | YES |
| `ContributorId.Original` | int(10) | YES |
| `ContributorSpaceId` | smallint(5) | YES |
| `ContributorUserId` | int(10) | YES |
| `ContributorJournalUserId` | bigint(19) | YES |
| `ContributorPersonUserId` | bigint(19) | YES |
| `ContributorResearchTopicId` | bigint(19) | YES |
| `ContributorResearchTopicId.Original` | bigint(19) | YES |
| `ContributorTaxonomyId` | bigint(19) | YES |
| `ContributorTheme` | nvarchar(500) | YES |
| `ContributorCreatorUserTypeRoleId` | int(10) | YES |
| `ContributorCreatorUserTypeRole` | nvarchar(100) | YES |
| `ContributorEmail` | nvarchar(100) | YES |
| `Email` | nvarchar(100) | YES |
| `ContributorName` | nvarchar(400) | YES |
| `ContributorFirstName` | nvarchar(200) | YES |
| `ContributorMiddleName` | nvarchar(200) | YES |
| `ContributorLastName` | nvarchar(200) | YES |
| `ContributorSourceId` | int(10) | YES |
| `ContributorSource` | nvarchar(100) | YES |
| `ContributorSecondarySourceId` | int(10) | YES |
| `ContributorSecondarySource` | nvarchar(50) | YES |
| `ContributorCreateDate` | datetime | YES |
| `SalesForceMessageCreateDate` | datetime | YES |
| `ContributorSortOrder` | bigint(19) | YES |
| `CountExpectedArticles` | int(10) | YES |
| `KeyMetrics.ContributorId` | bigint(19) | YES |
| `ResearchTopicAbstractAcceptedDate.First` | datetime | YES |
| `SuggestedContributorUploadTypeId` | int(10) | YES |
| `SuggestedContributorAlgorithmTypeId` | int(10) | YES |
| `SuggestedContributorAlgorithmType` | nvarchar(100) | YES |
| `First.RT.SubmissionDate` | datetime | YES |
| `Reminders.Count.InvitationtoConfirmation` | int(10) | YES |
| `Reminders.Count.ConfirmationtoSubmission` | int(10) | YES |
| `Reminders.Count.Total` | int(10) | YES |
| `HasContributorBeenInvited` | bit | YES |
| `HasContributorBeenInvited.Cfp` | bit | YES |
| `ContributorInvitationDate.Logical` | datetime | YES |
| `HasConfirmedInvitation` | bit | YES |
| `ContributorIsSuggested` | bit | YES |
| `First.Author.SubmissionDate` | datetime | YES |
| `ContributorIsRTEditor` | bit | YES |
| `IsConfirmedContributor` | bit | YES |
| `IsSpontaneousSubmission` | bit | YES |
| `Invitation.ContributorId` | bigint(19) | YES |
| `InviteDate` | datetime | YES |
| `InviterUserId` | int(10) | YES |
| `ConfirmedDate` | datetime | YES |
| `ExpectedSubmissionDate` | datetime | YES |
| `InvitationInitiatorRoleId` | int(10) | YES |
| `InvitationInitiatorRole` | nvarchar(50) | YES |
| `InvitationStatusId` | int(10) | YES |
| `InvitationStatus` | nvarchar(50) | YES |
| `InvitationStatusDate` | datetime | YES |
| `InvitationSentRemindersCount` | int(10) | YES |
| `InvitationLastReminderDate` | datetime | YES |
| `InvitationActivationNumber` | uniqueidentifier | YES |
| `ActivationLink` | nvarchar(251) | YES |
| `InvitationStatusDate.Confirmed.First` | datetime | YES |
| `InvitationStatusDate.Confirmed.Last` | datetime | YES |
| `Invitation.InitiationDate` | datetime | YES |
| `DeclinationOtherReason` | nvarchar(200) | YES |
| `DeclinationReason` | nvarchar(200) | YES |
| `DeclinationCreateDate` | datetime | YES |
| `DeclinationReasons` | nvarchar(50) | YES |
| `PersonUserId` | bigint(19) | YES |
| `PersonUserId.Original` | bigint(19) | YES |
| `PersonId` | bigint(19) | YES |
| `Person.JournalUserId` | bigint(19) | YES |
| `Person.SpaceId` | int(10) | YES |
| `Person.UserId` | int(10) | YES |
| `Person.Email` | nvarchar(300) | YES |
| `IsPrimaryEmail` | bit | YES |
| `IsJournalUser` | bit | YES |
| `IsRegisteredUser` | bit | YES |
| `IsNonRegisteredUser` | bit | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | char(3) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | nvarchar(50) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `HighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `TopRankRosstId` | nvarchar(40) | YES |
| `HighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `HighestRankFrontiersPriority` | int(10) | YES |
| `HighestRankFrontiersPriorityBins` | nvarchar(50) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `CountryOrder` | int(10) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `OwnerEmployeeCountry13RegionsBin` | nvarchar(50) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserFirstName` | nvarchar(150) | YES |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserLastName` | nvarchar(150) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserRegisterDate` | datetime | YES |
| `UserActivateDate` | datetime | YES |
| `UserModifyDate` | datetime | YES |
| `UserIsDeleted` | bit | YES |
| `UserIsActivated` | bit | YES |
| `UserStatus` | nvarchar(30) | YES |
| `UserCompletedRegistration` | bit | YES |
| `UserIsLoggedIn` | bit | YES |
| `UserIsAdmin` | bit | YES |
| `UserIsAuthor` | bit | YES |
| `UserIsEditor` | bit | YES |
| `UserIsResearchTopicEditor` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserEditorialBoardRoles` | varchar(500) | YES |
| `UserAuthorRoles` | varchar(500) | YES |
| `UserRolesNames` | varchar(500) | YES |
| `UserIsAdmin.Frontiers` | bit | YES |
| `UserIsAuthor.Frontiers` | bit | YES |
| `UserIsEditor.Frontiers` | bit | YES |
| `UserIsResearchTopicEditor.Frontiers` | bit | YES |
| `UserIsReviewer.Frontiers` | bit | YES |
| `IsUserInWatchList` | bit | YES |
| `JournalUserIsEditor` | bit | YES |
| `JournalUserIsEBM` | bit | YES |
| `JournalUserIsReviewer` | bit | YES |
| `JournalUserIsAuthor` | bit | YES |
| `JournalRoleId` | nvarchar(50) | YES |
| `JournalUserRoleId` | int(10) | YES |
| `JournalUserRole` | nvarchar(50) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `JournalRole.FirstAssigned.Date` | datetime | YES |
| `Rank.ResearchTopic` | int(10) | YES |
| `Rank.Article` | int(10) | YES |
| `JournalUserFirstTaxonomyId` | bigint(19) | YES |
| `JournalUserFirstJoinDate` | datetime | YES |
| `JournalUserOrder` | int(10) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(200) | YES |
| `TenantGroup` | nvarchar(50) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `FirstName` | nvarchar(200) | YES |
| `MiddleName` | nvarchar(200) | YES |
| `LastName` | nvarchar(200) | YES |
| `Name` | nvarchar(400) | YES |
| `ResearchTopicId` | bigint(19) | YES |
| `ResearchTopicId.Original` | bigint(19) | YES |
| `Contributor.Creator.UserTypeRoleId` | int(10) | YES |
| `Contributor.Creator.UserTypeRole` | nvarchar(100) | YES |
| `UserId` | int(10) | YES |
| `CreateDate` | datetime | YES |
| `SortOrder` | bigint(19) | YES |
| `Theme` | nvarchar(500) | YES |
| `ContributorExpectedArticles.Count` | int(10) | YES |
| `ContributorInvitationDate` | datetime | YES |
| `ContributorConfirmedDate` | datetime | YES |
| `ContributorExpectedSubmissionDate` | datetime | YES |
| `ContributorInvitationStatusId` | int(10) | YES |
| `ContributorInvitationStatus` | nvarchar(50) | YES |
| `ContributorInvitationStatusDate` | datetime | YES |
| `ContributorInvitationActivationNumber` | uniqueidentifier | YES |
| `ContributorDeclinationOtherReason` | nvarchar(200) | YES |
| `ContributorDeclinationReason` | nvarchar(200) | YES |
| `ContributorDeclinationCreateDate` | datetime | YES |
| `ContributorInvitationSentRemindersCount` | int(10) | YES |
| `Invitation.Initiator.RoleId` | int(10) | YES |
| `Invitation.Initiator.Role` | nvarchar(50) | YES |
| `ContributorInvitationLastReminderDate` | datetime | YES |
| `Organization` | nvarchar(200) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `UserPrimaryEmail` | nvarchar(100) | YES |
| `UserOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `ContributorOrganizationsHighestRankWoS` | int(10) | YES |
| `ContributorOrganizationId` | int(10) | YES |
| `ContributorRosstId` | nvarchar(40) | YES |
| `ContributorOrganization` | nvarchar(200) | YES |
| `ContributorCountryId` | nvarchar(10) | YES |
| `ContributorCountry` | nvarchar(100) | YES |
| `ContributorCountinent` | nvarchar(100) | YES |
| `ContributorCountryRejectionRate` | nvarchar(100) | YES |
| `IsUserEditor` | bit | YES |
| `IsUserResearchTopicEditor` | bit | YES |
| `IsResearchTopicEditor` | bit | YES |
| `IsUserReviewer` | bit | YES |
| `ContributorActivityPercentile` | float(53) | YES |
| `ContributorConnectivityPercentile` | float(53) | YES |
| `ContributorInfluencePercentile` | float(53) | YES |
| `ContributorProductivityPercentile` | float(53) | YES |
| `ContributorHIndexBins` | nvarchar(20) | YES |
| `ContributorActivityBins` | nvarchar(20) | YES |
| `ContributorConnectivityBins` | nvarchar(20) | YES |
| `ContributorInfluenceBins` | nvarchar(20) | YES |
| `ContributorProductivityBins` | nvarchar(20) | YES |
| `ContributorFrontiersBins` | nvarchar(20) | YES |
| `ContributorOrganizationRejectionRateBin` | nvarchar(50) | YES |
| `ContributorOrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `ContributorOrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `ContributorCountry3RegionsBinFocus` | nvarchar(100) | YES |
| `ContributorCountry4RegionsBin` | nvarchar(100) | YES |
| `ContributorCountry5RegionsBin` | nvarchar(100) | YES |
| `ContributorCountry7RegionsBin` | nvarchar(100) | YES |
| `ContributorCountry8RegionsBin` | nvarchar(100) | YES |
| `ContributorCountry13RegionsBin` | nvarchar(100) | YES |
| `ContributorCountryFocusRegionsBin` | nvarchar(100) | YES |
| `ContributorCountry8RegionsBin-China` | nvarchar(100) | YES |
| `ContributorCountry8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `ContributorHIndex` | int(10) | YES |
| `ContributorIsEBM` | bit | YES |
| `ContributorIsEditor` | bit | YES |
| `IsJournalEditor` | bit | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_CountryMetrics_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `CountryId` | nvarchar(3) | YES |
| `Country` | nvarchar(50) | YES |
| `ContinentId` | nvarchar(3) | YES |
| `Continent` | nvarchar(50) | YES |
| `3RegionsBinFocus` | nvarchar(50) | YES |
| `4RegionsBin` | nvarchar(50) | YES |
| `5RegionsBin` | nvarchar(50) | YES |
| `7RegionsBin` | nvarchar(50) | YES |
| `8RegionsBin` | nvarchar(50) | YES |
| `13RegionsBin` | nvarchar(50) | YES |
| `IsFocusRegion` | bit | YES |
| `FocusRegionsBin` | nvarchar(50) | YES |
| `RejectionRate` | nvarchar(50) | YES |
| `CountrySortOrder` | int(10) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_EditorialBoardMembers_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `EditorialBoardMemberId` | bigint(19) | YES |
| `EditorialBoardMemberSpaceId` | smallint(5) | YES |
| `EditorialBoardMemberUserId` | int(10) | YES |
| `EditorialBoardMemberJournalUserId` | bigint(19) | YES |
| `EditorialBoardMemberPersonUserId` | bigint(19) | YES |
| `EditorialBoardMemberTaxonomyId` | bigint(19) | YES |
| `RoleJoinOrder` | int(10) | YES |
| `IsFirstJoinedRole` | bit | YES |
| `RoleLevelOrder` | int(10) | YES |
| `IsTopFirstRole` | bit | YES |
| `RoleId` | int(10) | YES |
| `Role` | varchar(50) | YES |
| `RoleAbbr` | varchar(20) | YES |
| `RoleLevel` | varchar(9) | YES |
| `JoinDate` | datetime | YES |
| `EndDate` | datetime | YES |
| `IsActive` | bit | YES |
| `ModifyDate` | datetime | YES |
| `IsFirstTaxonomyRole` | bit | YES |
| `TaxonomyRoleOrder` | int(10) | YES |
| `InauguralArticleStage` | nvarchar(40) | YES |
| `EditorialBoardMemberUserOrder` | bigint(19) | YES |
| `EndReasonId` | int(10) | YES |
| `EndReason` | nvarchar(50) | YES |
| `EndReasonRoleChangeFlag` | int(10) | YES |
| `KeyMetrics.EditorialBoardMemberId` | bigint(19) | YES |
| `CountPublicationsConfirmed` | int(10) | YES |
| `CrossListedFields` | nvarchar(4000) | YES |
| `ActiveModifyDate` | datetime | YES |
| `MinJoinDate` | datetime | YES |
| `MinStartDate` | datetime | YES |
| `MaxEndDate` | datetime | YES |
| `SectionJoinDate` | datetime | YES |
| `SectionEndDate` | datetime | YES |
| `FirstTaxonomyRoleId` | int(10) | YES |
| `CountofTaxonomyRoles` | int(10) | YES |
| `ActiveEditorialBoards` | int(10) | YES |
| `HasOpportunity` | bit | YES |
| `Invitation.EditorialBoardMemberId` | bigint(19) | YES |
| `EditorialBoardInvitationId` | bigint(19) | YES |
| `InviterUserId` | int(10) | YES |
| `Inviter` | nvarchar(400) | YES |
| `InviteDate` | datetime | YES |
| `InvitationSourceId` | int(10) | YES |
| `InvitationSource` | nvarchar(100) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(200) | YES |
| `TenantGroup` | nvarchar(50) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `UserId` | int(10) | YES |
| `UserIdOrder` | bigint(19) | YES |
| `PersonId` | bigint(19) | YES |
| `UserIsEBM` | bit | YES |
| `UserIsEditor` | bit | YES |
| `JournalRoleId` | varchar(10) | YES |
| `Email` | nvarchar(100) | YES |
| `FirstName` | nvarchar(150) | YES |
| `LastName` | nvarchar(150) | YES |
| `Name` | nvarchar(400) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `UserOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `UserOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | YES |
| `OrganizationsHighestRankWoS` | int(10) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserPrimaryOrganizationId` | int(10) | YES |
| `UserPrimaryRosstId` | nvarchar(40) | YES |
| `UserPrimaryOrganization` | nvarchar(200) | YES |
| `UserPrimaryOrganizationCountry` | nvarchar(100) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | varchar(13) | YES |
| `PrimaryOrganizationCountry` | nvarchar(50) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `EditingInvitationsReceivedCount` | int(10) | YES |
| `EditingInvitationsAcceptedCount` | int(10) | YES |
| `EditingInvitationsDeclinedCount` | int(10) | YES |
| `ReviewingInvitationsReceivedCount` | int(10) | YES |
| `ReviewingInvitationsAcceptedCount` | int(10) | YES |
| `ReviewingInvitationsDeclinedCount` | int(10) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_EmailMetrics_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `Email` | nvarchar(300) | YES |
| `UserId` | int(10) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `UserPrimaryOrganizationId` | int(10) | YES |
| `UserPrimaryRosstId` | nvarchar(40) | YES |
| `UserPrimaryOrganization` | nvarchar(200) | YES |
| `UserOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `UserOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `UserOrganizationIsTop150` | bit | YES |
| `IsUserPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `IsUserInWatchlist` | bit | YES |
| `UserOrganizationRejectionRateBin` | nvarchar(50) | YES |
| `UserOrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `UserOrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `HIndex` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | varchar(14) | YES |
| `ActivityBins` | varchar(14) | YES |
| `ConnectivityBins` | varchar(14) | YES |
| `InfluenceBins` | varchar(14) | YES |
| `ProductivityBins` | varchar(14) | YES |
| `FrontiersBins` | varchar(14) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_JournalRole_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `JournalRoleId` | nvarchar(10) | YES |
| `RoleId` | int(10) | YES |
| `Role` | varchar(50) | YES |
| `RoleGroup` | nvarchar(50) | YES |
| `IsAdminOfficeRole` | bit | YES |
| `IsJournalEditorialBoardRole` | bit | YES |
| `IsResearchTopicEditorRole` | bit | YES |
| `IsArticleReviewBoardRole` | bit | YES |
| `IsArticleAuthorsRole` | bit | YES |
| `Rank.ResearchTopic` | smallint(5) | YES |
| `Rank.Article` | smallint(5) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_JournalUserMetrics_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `UserId` | int(10) | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(100) | YES |
| `TenantGroup` | varchar(20) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserIsEditor` | bit | YES |
| `UserIsEBM` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserIsAuthor` | bit | YES |
| `UserOrder` | bigint(19) | YES |
| `RoleId` | int(10) | YES |
| `Role` | nvarchar(50) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `JournalRole.FirstAssigned.Date` | datetime | YES |
| `Rank.ResearchTopic` | int(10) | YES |
| `Rank.Article` | int(10) | YES |
| `JoinDate` | datetime | YES |
| `RegistrationDate` | datetime | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `Program` | nvarchar(50) | YES |
| `Domain` | nvarchar(50) | YES |
| `Field` | nvarchar(150) | YES |
| `Journal` | nvarchar(150) | YES |
| `Specialty` | nvarchar(150) | YES |
| `Section` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `OrganizationsHighestRankWoS` | int(10) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | YES |
| `IsUserPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `IsUserInWatchlist` | bit | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_Journals_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `SpaceId` | smallint(5) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `TaxonomyLevel` | varchar(9) | YES |
| `JournalLevel` | nvarchar(20) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalDevelopment.SeniorJournalManager` | nvarchar(100) | YES |
| `JournalSpecialist.Count` | int(10) | YES |
| `JournalSegmentId` | nvarchar(30) | YES |
| `JournalSegment` | nvarchar(100) | YES |
| `JournalSegmentId.Previous` | nvarchar(30) | YES |
| `JournalSegment.Previous` | nvarchar(100) | YES |
| `SegmentId` | nvarchar(30) | YES |
| `Segment` | nvarchar(100) | YES |
| `SegmentId.Previous` | nvarchar(30) | YES |
| `Segment.Previous` | nvarchar(100) | YES |
| `SegmentBonusId` | nvarchar(30) | YES |
| `SegmentBonus` | nvarchar(100) | YES |
| `JournalDevelopment.SegmentManager` | nvarchar(100) | YES |
| `PortfolioId` | nvarchar(32) | YES |
| `Portfolio` | nvarchar(128) | YES |
| `JournalDevelopment.PortfolioManager` | nvarchar(400) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `FullName` | nvarchar(200) | YES |
| `Abbreviation` | nvarchar(100) | YES |
| `ParentTaxonomyId` | bigint(19) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `TypeId` | int(10) | YES |
| `Type` | nvarchar(30) | YES |
| `ISSN` | nvarchar(30) | YES |
| `StatusId` | int(10) | YES |
| `Status` | varchar(7) | YES |
| `IsOnline` | bit | YES |
| `IsDeleted` | bit | YES |
| `IsOpenForSubmission` | bit | YES |
| `SubmissionStatus` | varchar(6) | YES |
| `MissionStatement` | nvarchar | YES |
| `PublishDate` | datetime | YES |
| `ModifyDate` | datetime | YES |
| `TypeSetterUserId` | int(10) | YES |
| `TypeSetterUserName` | nvarchar(400) | YES |
| `FirstAcceptanceDate` | date | YES |
| `FirstPublicationDate.JI` | date | YES |
| `COPE.IsEligible` | bit | YES |
| `COPE.IndexationStatus` | nvarchar(30) | YES |
| `COPE.Conditions.HasMoreThan12Months` | bit | YES |
| `DOAJ.IsEligible` | bit | YES |
| `DOAJ.IndexationStatus` | nvarchar(30) | YES |
| `DOAJ.Conditions.HasPublished5Articles` | bit | YES |
| `DOAJ.Conditions.HasPublished10Articles` | bit | YES |
| `DOAJ.Conditions.IsFirstPublicationOlder12M` | bit | YES |
| `DOAJ.Conditions.LowPercentagePublicationAuthoredByEbm` | bit | YES |
| `DOAJ.Conditions.LowTeAuthorRatioPerRt` | bit | YES |
| `DOAJ.MaxTeAuthorRatioPerRt` | decimal(18) | YES |
| `DOAJ.PercentagePublicationAuthoredByEbm` | decimal(18) | YES |
| `DOAJ.FirstPublicationDate` | date | YES |
| `DOAJ.DOI5` | nvarchar(50) | YES |
| `DOAJ.ArticlesCountThreshold2` | int(10) | YES |
| `PMC.IsEligible` | bit | YES |
| `PMC.IndexationStatus` | nvarchar(30) | YES |
| `PMC.Conditions.HasPublished25Articles` | bit | YES |
| `OriginalResearch.Percentage` | decimal(18) | YES |
| `Reviews.Percentage` | decimal(18) | YES |
| `CaseReports.Percentage` | decimal(18) | YES |
| `Others.Percentage` | decimal(18) | YES |
| `MED.IsEligible` | bit | YES |
| `MED.IndexationStatus` | nvarchar(30) | YES |
| `MED.Conditions.HasPublished40Articles` | bit | YES |
| `MED.Conditions.HasMoreThan12Months` | bit | YES |
| `MED.Conditions.HasPublicationsSpontaneous12MonthsOver40Percentage` | bit | YES |
| `MED.Conditions.HasPublicationsSpontaneous12MonthsUnder65Percentage` | bit | YES |
| `MED.Conditions.HasOriginalResearchCountOver60` | bit | YES |
| `MED.Conditions.HasReviewCountUnder40` | bit | YES |
| `Scopus.IsEligible` | bit | YES |
| `Scopus.IndexationStatus` | nvarchar(30) | YES |
| `Scopus.Conditions.HasPublished40Articles` | bit | YES |
| `Scopus.Conditions.HasFCE` | bit | YES |
| `Scopus.Conditions.HasMoreThan24Months` | bit | YES |
| `Scopus.Conditions.HasPublicationsAveragePerYearOver30` | bit | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_Persons_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `PersonUserId` | bigint(19) | YES |
| `PersonUserId.Original` | bigint(19) | YES |
| `PersonId` | bigint(19) | YES |
| `Person.JournalUserId` | bigint(19) | YES |
| `Person.SpaceId` | int(10) | YES |
| `Person.UserId` | int(10) | YES |
| `Person.Email` | nvarchar(300) | YES |
| `IsPrimaryEmail` | bit | YES |
| `IsJournalUser` | bit | YES |
| `IsRegisteredUser` | bit | YES |
| `IsNonRegisteredUser` | bit | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | char(3) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | nvarchar(50) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `HighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `TopRankRosstId` | nvarchar(40) | YES |
| `HighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `HighestRankFrontiersPriority` | int(10) | YES |
| `HighestRankFrontiersPriorityBins` | nvarchar(50) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `CountryOrder` | int(10) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `OwnerEmployeeCountry13RegionsBin` | nvarchar(50) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `EditingInvitationsReceivedCount` | int(10) | YES |
| `EditingInvitationsAcceptedCount` | int(10) | YES |
| `EditingInvitationsDeclinedCount` | int(10) | YES |
| `ReviewingInvitationsReceivedCount` | int(10) | YES |
| `ReviewingInvitationsAcceptedCount` | int(10) | YES |
| `ReviewingInvitationsDeclinedCount` | int(10) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserFirstName` | nvarchar(150) | YES |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserLastName` | nvarchar(150) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserRegisterDate` | datetime | YES |
| `UserActivateDate` | datetime | YES |
| `UserModifyDate` | datetime | YES |
| `UserIsDeleted` | bit | YES |
| `UserIsActivated` | bit | YES |
| `UserStatus` | nvarchar(30) | YES |
| `UserCompletedRegistration` | bit | YES |
| `UserIsLoggedIn` | bit | YES |
| `UserIsAdmin` | bit | YES |
| `UserIsAuthor` | bit | YES |
| `UserIsEditor` | bit | YES |
| `UserIsResearchTopicEditor` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserEditorialBoardRoles` | varchar(500) | YES |
| `UserAuthorRoles` | varchar(500) | YES |
| `UserRolesNames` | varchar(500) | YES |
| `UserIsAdmin.Frontiers` | bit | YES |
| `UserIsAuthor.Frontiers` | bit | YES |
| `UserIsEditor.Frontiers` | bit | YES |
| `UserIsResearchTopicEditor.Frontiers` | bit | YES |
| `UserIsReviewer.Frontiers` | bit | YES |
| `IsUserInWatchList` | bit | YES |
| `JournalUserIsEditor` | bit | YES |
| `JournalUserIsEBM` | bit | YES |
| `JournalUserIsReviewer` | bit | YES |
| `JournalUserIsAuthor` | bit | YES |
| `JournalRoleId` | nvarchar(50) | YES |
| `JournalUserRoleId` | int(10) | YES |
| `JournalUserRole` | nvarchar(50) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `JournalRole.FirstAssigned.Date` | datetime | YES |
| `Rank.ResearchTopic` | int(10) | YES |
| `Rank.Article` | int(10) | YES |
| `JournalUserFirstTaxonomyId` | bigint(19) | YES |
| `JournalUserFirstJoinDate` | datetime | YES |
| `JournalUserOrder` | int(10) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_ResearchTopicAbstracts_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `ResearchTopicAbstractId` | bigint(19) | YES |
| `ResearchTopicAbstractId.Original` | int(10) | YES |
| `AbstractResearchTopicId` | bigint(19) | YES |
| `AbstractTaxonomyId` | bigint(19) | YES |
| `AbstractTitle` | nvarchar | YES |
| `AbstractStage` | nvarchar(100) | YES |
| `AbstractAuthorPrimaryAffiliationCountry` | nvarchar(100) | YES |
| `AbstractAuthorEmail` | nvarchar(100) | YES |
| `Abstract.Submitted` | datetime | YES |
| `Abstract.Accepted` | datetime | YES |
| `Abstract.Rejected` | datetime | YES |
| `AbstractOrder` | bigint(19) | YES |
| `OrganizationId` | bigint(19) | YES |
| `RosstId` | nvarchar(40) | YES |
| `AbstractCountryId` | nvarchar(10) | YES |
| `AbstractCountry` | nvarchar(100) | YES |
| `AbstractContinent` | nvarchar(13) | YES |
| `AbstractCountry3RegionsBinFocus` | nvarchar(50) | YES |
| `AbstractCountry4RegionsBin` | nvarchar(50) | YES |
| `AbstractCountry5RegionsBin` | nvarchar(50) | YES |
| `AbstractCountry8RegionsBin` | nvarchar(50) | YES |
| `AbstractCountry13RegionsBin` | nvarchar(50) | YES |
| `AbstractCountry8RegionsBin-China` | nvarchar(50) | YES |
| `AbstractCountry8RegionsBin-ChinaCAS` | nvarchar(50) | YES |
| `AbstractCountryFocusRegionsBin` | nvarchar(50) | YES |
| `AbstractCountryRejectionRate` | nvarchar(50) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_ResearchTopicCoordinators_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `CoordinatorId` | bigint(19) | YES |
| `CoordinatorSpaceId` | smallint(5) | YES |
| `CoordinatorUserId` | int(10) | YES |
| `CoordinatorPersonUserId` | bigint(19) | YES |
| `CoordinatorJournalUserId` | bigint(19) | YES |
| `CoordinatorTaxonomyId` | bigint(19) | YES |
| `CoordinatorResearchTopicId` | bigint(19) | YES |
| `IsFrontiers` | varchar(20) | YES |
| `IsQualitricsSurveyForCFP` | bit | YES |
| `IsQualitricsSurveyForClosedRT` | bit | YES |
| `CoordinatorCreateDate` | datetime | YES |
| `CoordinatorModifyDate` | datetime | YES |
| `CoordinatorOrder` | int(10) | YES |
| `CoordinatorUserOrder` | int(10) | YES |
| `KeyMetrics.CoordinatorId` | bigint(19) | YES |
| `BL Author` | int(10) | YES |
| `BL Coordinator` | int(10) | YES |
| `RT Hosted by AE` | int(10) | YES |
| `RT Hosted by AE Own Section` | int(10) | YES |
| `TE EB Max Role` | nvarchar(50) | YES |
| `TE Promotable` | int(10) | YES |
| `RT.Hosted.Count` | int(10) | YES |
| `Last.TopicHosted` | datetime | YES |
| `TimeSince.Last.TopicHosted` | int(10) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(200) | YES |
| `TenantGroup` | nvarchar(50) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `PersonUserId` | bigint(19) | YES |
| `PersonId` | bigint(19) | YES |
| `Person.UserId` | int(10) | YES |
| `Person.Email` | nvarchar(300) | YES |
| `IsPrimaryEmail` | bit | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | char(3) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | nvarchar(50) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `HighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `TopRankRosstId` | nvarchar(40) | YES |
| `HighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `HighestRankFrontiersPriority` | int(10) | YES |
| `HighestRankFrontiersPriorityBins` | nvarchar(50) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `CountryOrder` | int(10) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserFirstName` | nvarchar(150) | YES |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserLastName` | nvarchar(150) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserRegisterDate` | datetime | YES |
| `UserActivateDate` | datetime | YES |
| `UserModifyDate` | datetime | YES |
| `UserIsDeleted` | bit | YES |
| `UserIsActivated` | bit | YES |
| `UserStatus` | nvarchar(30) | YES |
| `UserCompletedRegistration` | bit | YES |
| `UserIsLoggedIn` | bit | YES |
| `UserIsAdmin` | bit | YES |
| `UserIsAuthor` | bit | YES |
| `UserIsEditor` | bit | YES |
| `UserIsResearchTopicEditor` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserEditorialBoardRoles` | varchar(500) | YES |
| `UserIsAdmin.Frontiers` | bit | YES |
| `UserIsAuthor.Frontiers` | bit | YES |
| `UserIsEditor.Frontiers` | bit | YES |
| `UserIsResearchTopicEditor.Frontiers` | bit | YES |
| `UserIsReviewer.Frontiers` | bit | YES |
| `IsUserInWatchList` | bit | YES |
| `FirstName` | nvarchar(150) | YES |
| `MiddleName` | nvarchar(50) | YES |
| `LastName` | nvarchar(150) | YES |
| `Name` | nvarchar(400) | YES |
| `Email` | nvarchar(100) | YES |
| `UserPrimaryOrganizationId` | int(10) | YES |
| `UserPrimaryRosstId` | nvarchar(40) | YES |
| `UserPrimaryOrganization` | nvarchar(200) | YES |
| `UserPrimaryOrganizationCountryId` | char(3) | YES |
| `UserPrimaryOrganizationCountry` | nvarchar(100) | YES |
| `UserPrimaryOrganizationContinentId` | char(2) | YES |
| `UserPrimaryOrganizationContinent` | nvarchar(50) | YES |
| `IsUserPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `UserOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `UserOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `Ranking` | int(10) | YES |
| `OrganizationsHighestRankWoS` | int(10) | YES |
| `HIndex Bins` | nvarchar(20) | YES |
| `Activity Bins` | nvarchar(20) | YES |
| `Connectivity Bins` | nvarchar(20) | YES |
| `Influence Bins` | nvarchar(20) | YES |
| `Productivity Bins` | nvarchar(20) | YES |
| `Frontiers Bins` | nvarchar(20) | YES |
| `Watch List Country` | bit | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `RoleId` | int(10) | YES |
| `Role` | nvarchar(50) | YES |
| `Is Editor EBM` | bit | YES |
| `Journal Responsible` | nvarchar(100) | YES |
| `Program Responsible` | nvarchar(100) | YES |
| `ResearchTopicId.Original` | int(10) | YES |
| `RT Title` | nvarchar | YES |
| `IsRTClosed` | bit | YES |
| `IsRTCompleted` | bit | YES |
| `IsRTDeleted` | bit | YES |
| `IsRTOnline` | bit | YES |
| `Is RT COVID Related?` | bit | YES |
| `ResearchTopic.OnlineDate` | datetime | YES |
| `RT Online Date` | datetime | YES |
| `ResearchTopic.CloseDate` | datetime | YES |
| `ResearchTopic.CompleteDate` | datetime | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_ResearchTopicEditors_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `EditorId` | bigint(19) | YES |
| `EditorSpaceId` | smallint(5) | YES |
| `EditorUserId` | int(10) | YES |
| `EditorPersonUserId` | bigint(19) | YES |
| `EditorJournalUserId` | bigint(19) | YES |
| `EditorTaxonomyId` | bigint(19) | YES |
| `EditorResearchTopicId` | bigint(19) | YES |
| `IsFrontiers` | varchar(20) | YES |
| `IsNotificationEnabled` | bit | YES |
| `LastNotificationSendDate` | datetime | YES |
| `EditorCreateDate` | datetime | YES |
| `EditorModifyDate` | datetime | YES |
| `EditorOrder` | bigint(19) | YES |
| `EditorUserOrder` | bigint(19) | YES |
| `KeyMetrics.EditorId` | bigint(19) | YES |
| `BL Author` | int(10) | YES |
| `BL Editor` | int(10) | YES |
| `RT Hosted by AE` | int(10) | YES |
| `RT Hosted by AE Own Section` | int(10) | YES |
| `TE EB Max Role` | nvarchar(50) | YES |
| `TE Promotable` | int(10) | YES |
| `RT.Hosted.Count` | int(10) | YES |
| `Last.TopicHosted` | datetime | YES |
| `TimeSince.Last.TopicHosted` | int(10) | YES |
| `AnalyticBins.EditorId` | bigint(19) | YES |
| `RT Hosted Bins` | nvarchar(50) | YES |
| `Time since last RT Hosted Bins` | nvarchar(50) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(200) | YES |
| `TenantGroup` | nvarchar(50) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `UserId` | int(10) | YES |
| `ResearchTopicId` | bigint(19) | YES |
| `CreateDate` | datetime | YES |
| `ModifyDate` | datetime | YES |
| `UserIdOrder` | bigint(19) | YES |
| `RTs Hosted` | int(10) | YES |
| `Time Since Last Topic Hosted` | int(10) | YES |
| `PersonUserId` | bigint(19) | YES |
| `PersonId` | bigint(19) | YES |
| `Person.UserId` | int(10) | YES |
| `Person.Email` | nvarchar(300) | YES |
| `IsPrimaryEmail` | bit | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | char(3) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | nvarchar(50) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `HighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `TopRankRosstId` | nvarchar(40) | YES |
| `HighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `HighestRankFrontiersPriority` | int(10) | YES |
| `HighestRankFrontiersPriorityBins` | nvarchar(50) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `CountryOrder` | int(10) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserFirstName` | nvarchar(150) | YES |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserLastName` | nvarchar(150) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserRegisterDate` | datetime | YES |
| `UserActivateDate` | datetime | YES |
| `UserModifyDate` | datetime | YES |
| `UserIsDeleted` | bit | YES |
| `UserIsActivated` | bit | YES |
| `UserStatus` | nvarchar(30) | YES |
| `UserCompletedRegistration` | bit | YES |
| `UserIsLoggedIn` | bit | YES |
| `UserIsAdmin` | bit | YES |
| `UserIsAuthor` | bit | YES |
| `UserIsEditor` | bit | YES |
| `UserIsResearchTopicEditor` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserEditorialBoardRoles` | varchar(500) | YES |
| `UserIsAdmin.Frontiers` | bit | YES |
| `UserIsAuthor.Frontiers` | bit | YES |
| `UserIsEditor.Frontiers` | bit | YES |
| `UserIsResearchTopicEditor.Frontiers` | bit | YES |
| `UserIsReviewer.Frontiers` | bit | YES |
| `IsUserInWatchList` | bit | YES |
| `FirstName` | nvarchar(150) | YES |
| `MiddleName` | nvarchar(50) | YES |
| `LastName` | nvarchar(150) | YES |
| `Name` | nvarchar(400) | YES |
| `Email` | nvarchar(100) | YES |
| `UserPrimaryOrganizationId` | int(10) | YES |
| `UserPrimaryRosstId` | nvarchar(40) | YES |
| `UserPrimaryOrganization` | nvarchar(200) | YES |
| `UserPrimaryOrganizationCountryId` | char(3) | YES |
| `UserPrimaryOrganizationCountry` | nvarchar(100) | YES |
| `UserPrimaryOrganizationContinentId` | char(2) | YES |
| `UserPrimaryOrganizationContinent` | nvarchar(50) | YES |
| `IsUserPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `UserOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `UserOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `Ranking` | int(10) | YES |
| `OrganizationsHighestRankWoS` | int(10) | YES |
| `HIndex Bins` | nvarchar(20) | YES |
| `Activity Bins` | nvarchar(20) | YES |
| `Connectivity Bins` | nvarchar(20) | YES |
| `Influence Bins` | nvarchar(20) | YES |
| `Productivity Bins` | nvarchar(20) | YES |
| `Frontiers Bins` | nvarchar(20) | YES |
| `Watch List Country` | bit | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `RoleId` | int(10) | YES |
| `Role` | nvarchar(50) | YES |
| `Is Editor EBM` | bit | YES |
| `Journal Responsible` | nvarchar(100) | YES |
| `Program Responsible` | nvarchar(100) | YES |
| `ResearchTopicId.Original` | int(10) | YES |
| `RT Title` | nvarchar | YES |
| `IsRTClosed` | bit | YES |
| `IsRTCompleted` | bit | YES |
| `IsRTDeleted` | bit | YES |
| `IsRTOnline` | bit | YES |
| `Is RT COVID Related?` | bit | YES |
| `ResearchTopic.OnlineDate` | datetime | YES |
| `RT Online Date` | datetime | YES |
| `ResearchTopic.CloseDate` | datetime | YES |
| `ResearchTopic.CompleteDate` | datetime | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_ResearchTopics_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `ResearchTopicId` | bigint(19) | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(100) | YES |
| `ResearchTopicId.Original` | int(10) | YES |
| `ResearchTopicTaxonomyId` | bigint(19) | YES |
| `Title` | nvarchar | YES |
| `Description` | nvarchar | YES |
| `ParticipatingJournals` | nvarchar | YES |
| `StageId` | int(10) | YES |
| `Stage` | nvarchar(30) | YES |
| `EBookId` | bigint(19) | YES |
| `EBookId.Original` | int(10) | YES |
| `EBookPublishYear` | int(10) | YES |
| `EBookStatus` | nvarchar(150) | YES |
| `URLEBookPage` | nvarchar(122) | YES |
| `IsActive` | bit | YES |
| `IsOnline` | bit | YES |
| `IsClosed` | bit | YES |
| `IsCompleted` | bit | YES |
| `IsSuggested` | bit | YES |
| `IsRejected` | bit | YES |
| `IsDeleted` | bit | YES |
| `DeletionReasonId` | int(10) | YES |
| `DeletionReason` | varchar(500) | YES |
| `URLResearchTopicPage` | nvarchar(100) | YES |
| `ShortURLResearchTopicPage` | nvarchar(50) | YES |
| `Comments` | nvarchar | YES |
| `SuggestedArticles.Count` | int(10) | YES |
| `SuggestedArticles.Count.Discarded` | int(10) | YES |
| `SuggestedArticles.Count.Invited` | int(10) | YES |
| `SuggestedArticles.Count.Accepted` | int(10) | YES |
| `SuggestedArticles.Count.Declined` | int(10) | YES |
| `SuggestedArticles.ConversionRate` | int(10) | YES |
| `IsSuggestedContributorsEnabledForTopicEditors` | bit | YES |
| `IsSuggestedManuscriptEnabledForTopicEditors` | bit | YES |
| `TopicEditorsMonitoringStartDate` | datetime | YES |
| `TopicEditorsMonitoringReminderFrequency` | int(10) | YES |
| `IsCOVIDRelated` | bit | YES |
| `IsFromACPOpportunity` | bit | YES |
| `CampaignName` | nvarchar(100) | YES |
| `ParentCampaignName` | nvarchar(100) | YES |
| `UltimateParentCampaign` | nvarchar(100) | YES |
| `IsCollectionSeries` | bit | YES |
| `IsSocietyAffiliation` | bit | YES |
| `Dates.ResearchTopicId` | bigint(19) | YES |
| `CreateDate` | datetime | YES |
| `StageDate` | datetime | YES |
| `OnlineDate` | datetime | YES |
| `DeletedDate` | datetime | YES |
| `CloseDate` | datetime | YES |
| `CompleteDate` | datetime | YES |
| `ShareEBookDate` | datetime | YES |
| `SubmissionInvitationSendDate` | datetime | YES |
| `EditorialRequestDate` | datetime | YES |
| `SubmissionDeadline` | datetime | YES |
| `AbstractSubmissionDeadline` | datetime | YES |
| `ExtendedSubmissionDeadline` | datetime | YES |
| `PublicExtendedDeadline` | datetime | YES |
| `InPreparationStageDate` | datetime | YES |
| `SuggestedStageDate` | datetime | YES |
| `RejectedStageDate` | datetime | YES |
| `DeletedStageDate` | datetime | YES |
| `InDiscussionStageDate` | datetime | YES |
| `LostStageDate` | datetime | YES |
| `Organization.ResearchTopicId` | bigint(19) | YES |
| `EditorsOrganizationsHighestRankFrontiersPriorityOrganizationId` | bigint(19) | YES |
| `EditorsOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `EditorsOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `EditorsOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `PrimaryOrganizationId` | bigint(19) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(50) | YES |
| `Continent` | nvarchar(50) | YES |
| `Country3RegionsBinFocus` | nvarchar(50) | YES |
| `Country4RegionsBin` | nvarchar(50) | YES |
| `Country5RegionsBin` | nvarchar(50) | YES |
| `Country7RegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin` | nvarchar(50) | YES |
| `Country13RegionsBin` | nvarchar(50) | YES |
| `Country8RegionsBin-China` | nvarchar(50) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(50) | YES |
| `CountryFocusRegionsBin` | nvarchar(50) | YES |
| `CountryRejectionRate` | nvarchar(50) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `OwnerEmployeeCountry13RegionsBin` | nvarchar(50) | YES |
| `Country_RegionPriority` | nvarchar(50) | YES |
| `Country8RegionsBin_RegionPriority` | nvarchar(50) | YES |
| `Country13RegionsBin_RegionPriority` | nvarchar(50) | YES |
| `Country_ContactPriority` | nvarchar(50) | YES |
| `Country8RegionsBin_ContactPriority` | nvarchar(50) | YES |
| `Country13RegionsBin_ContactPriority` | nvarchar(50) | YES |
| `KeyMetrics.ResearchTopicId` | bigint(19) | YES |
| `CountParticipatingJournals` | int(10) | YES |
| `ResearchTopicIsCrossListed` | bit | YES |
| `CountSubmissionDeadlineDates` | int(10) | YES |
| `CountExtendedSubmissionDeadlineDates` | int(10) | YES |
| `CountExpectedArticles` | int(10) | YES |
| `CountAbstractsNotRejected` | int(10) | YES |
| `CountAbstractsSubmitted` | int(10) | YES |
| `Facebook Inbound` | float(53) | YES |
| `Facebook Outbound` | float(53) | YES |
| `Twitter Inbound` | float(53) | YES |
| `Twitter Outbound` | float(53) | YES |
| `GooglePlus Inbound` | float(53) | YES |
| `GooglePlus Outbound` | float(53) | YES |
| `Linkedin Inbound` | float(53) | YES |
| `Linkedin Outbound` | float(53) | YES |
| `Others Inbound` | float(53) | YES |
| `Others Outbound` | float(53) | YES |
| `CountArticlesViews` | int(10) | YES |
| `CountArticlesDownloads` | int(10) | YES |
| `CountArticlesFrontiersViews` | int(10) | YES |
| `CountArticlesFrontiersDownloads` | int(10) | YES |
| `CountFrontiersViewsDownloads` | int(10) | YES |
| `CountArticlesCrossrefCitations` | int(10) | YES |
| `CountArticlesScopusCitations` | int(10) | YES |
| `CountArticlesPMCViews` | int(10) | YES |
| `CountArticlesPMCDownloads` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `CountArticlesCitations` | int(10) | YES |
| `CountArticlesCitationsArticles` | int(10) | YES |
| `CountSubmittedArticles` | int(10) | YES |
| `CountAcceptedArticles` | int(10) | YES |
| `CountPublishedArticles` | int(10) | YES |
| `CountRejectedArticles` | int(10) | YES |
| `CountInReviewArticles` | int(10) | YES |
| `SubmittedManuscriptsbyInvitedContributors.cfp` | int(10) | YES |
| `CountEditorialArticles` | int(10) | YES |
| `CountEditorialArticlesPublished` | int(10) | YES |
| `CountNonRejectedAbstracts` | int(10) | YES |
| `CountSubmittedAbstracts` | int(10) | YES |
| `RTEditors.Count` | int(10) | YES |
| `PublishingMetrics.ResearchTopicId` | bigint(19) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `Users.ResearchTopicId` | bigint(19) | YES |
| `Editors` | nvarchar(2000) | YES |
| `EditorIsEBM` | int(10) | YES |
| `AnyEditorIsJournalEditor` | bit | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `OwnerUserId` | int(10) | YES |
| `OwnerUserName` | nvarchar(400) | YES |
| `CreatorUserId` | int(10) | YES |
| `CreatorUserName` | nvarchar(400) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `ResearchTopicTitle` | nvarchar | YES |
| `Campaign` | nvarchar(100) | YES |
| `ParentCampaign` | nvarchar(100) | YES |
| `ResearchTopicCreateDate` | datetime | YES |
| `Organization` | nvarchar(200) | YES |
| `OrganizationId` | bigint(19) | YES |
| `RosstId` | nvarchar(40) | YES |
| `HighestRankOrganizationRejectionRateBin` | nvarchar(50) | YES |
| `HighestRankOrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `HighestRankOrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `Count.RT.Editors` | int(10) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_ReviewBoardMembers_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `ReviewBoardMemberId` | bigint(19) | YES |
| `ReviewBoardMemberSpaceId` | smallint(5) | YES |
| `ReviewBoardMemberUserId` | int(10) | YES |
| `ReviewBoardMemberJournalUserId` | bigint(19) | YES |
| `ReviewBoardMemberPersonUserId` | bigint(19) | YES |
| `ReviewBoardMemberArticleId` | bigint(19) | YES |
| `ReviewBoardMemberTaxonomyId` | bigint(19) | YES |
| `Email` | nvarchar(100) | YES |
| `FirstName` | nvarchar(150) | YES |
| `LastName` | nvarchar(150) | YES |
| `Name` | nvarchar(400) | YES |
| `JoinDate` | datetime | YES |
| `RoleId` | int(10) | YES |
| `Role` | varchar(50) | YES |
| `RoleAbbr` | varchar(20) | YES |
| `OriginalRoleId` | int(10) | YES |
| `IsVolunteer` | bit | YES |
| `IsVolunteerExcluded` | bit | YES |
| `VolunteerExclusionReason` | nvarchar(250) | YES |
| `ReviewBoardStatusId` | tinyint(3) | YES |
| `ReviewBoardStatus` | varchar(25) | YES |
| `ReviewBoardMemberUserOrder` | int(10) | YES |
| `KeyMetrics.ReviewBoardMemberId` | bigint(19) | YES |
| `IsTopFirstAssignedRole` | bit | YES |
| `IsReviewMember` | bit | YES |
| `Reviewer.LatestInviteDate` | datetime | YES |
| `Reviewer.WithdrawDate` | datetime | YES |
| `ReviewReportDate.IndependentReviewSubmitted` | datetime | YES |
| `ReviewReportDate.FinalReportSubmitted` | datetime | YES |
| `ArticlesReviewed.Count` | int(10) | YES |
| `ArticlesEdited.Count` | int(10) | YES |
| `ArticlesEditedOrReviewed.Count` | int(10) | YES |
| `Last.Reviewer.ReviewDate` | datetime | YES |
| `Last.Reviewer.EditDate` | datetime | YES |
| `TimeSince.Last.Reviewer.EditingAssignment` | int(10) | YES |
| `TimeSince.Last.Reviewer.ReviewAssignment` | int(10) | YES |
| `TimeSince.Last.Reviewer.EditingOrReviewAssignment` | int(10) | YES |
| `ReviewReportRating` | decimal(10) | YES |
| `ArticlesReviewed.Count.Bin` | nvarchar(50) | YES |
| `ArticlesEdited.Count.Bin` | nvarchar(50) | YES |
| `ArticlesEditedOrReviewed.Count.Bin` | nvarchar(50) | YES |
| `TimeSince.Last.Reviewer.EditingAssignment.Bin` | nvarchar(50) | YES |
| `TimeSince.Last.Reviewer.ReviewAssignment.Bin` | nvarchar(50) | YES |
| `TimeSince.Last.Reviewer.EditingOrReviewAssignment.Bin` | nvarchar(50) | YES |
| `Invitation.ReviewBoardMemberId` | bigint(19) | YES |
| `ReviewBoardInvitationId` | bigint(19) | YES |
| `InviterUserId` | int(10) | YES |
| `Inviter` | nvarchar(150) | YES |
| `InviterEmail` | nvarchar(100) | YES |
| `InviteDate` | datetime | YES |
| `PersonUserId` | bigint(19) | YES |
| `PersonUserId.Original` | bigint(19) | YES |
| `PersonId` | bigint(19) | YES |
| `Person.JournalUserId` | bigint(19) | YES |
| `Person.SpaceId` | int(10) | YES |
| `Person.UserId` | int(10) | YES |
| `Person.Email` | nvarchar(300) | YES |
| `IsPrimaryEmail` | bit | YES |
| `IsJournalUser` | bit | YES |
| `IsRegisteredUser` | bit | YES |
| `IsNonRegisteredUser` | bit | YES |
| `PrimaryOrganizationId` | int(10) | YES |
| `PrimaryRosstId` | nvarchar(40) | YES |
| `PrimaryOrganization` | nvarchar(200) | YES |
| `PrimaryOrganizationCountryId` | char(3) | YES |
| `PrimaryOrganizationCountry` | nvarchar(100) | YES |
| `PrimaryOrganizationContinentId` | char(2) | YES |
| `PrimaryOrganizationContinent` | nvarchar(50) | YES |
| `PrimaryOrganizationCityId` | int(10) | YES |
| `PrimaryOrganizationCity` | nvarchar(200) | YES |
| `IsPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `HighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `TopRankRosstId` | nvarchar(40) | YES |
| `HighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `HighestRankFrontiersPriority` | int(10) | YES |
| `HighestRankFrontiersPriorityBins` | nvarchar(50) | YES |
| `OrganizationIsTop150` | bit | YES |
| `OrganizationRejectionRateBin` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `OrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `CountryOrder` | int(10) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `OwnerEmployeeCountry13RegionsBin` | nvarchar(50) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `CountConfirmedPublications` | int(10) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `UserPrimaryEmailAddress` | nvarchar(100) | YES |
| `UserFirstName` | nvarchar(150) | YES |
| `UserMiddleName` | nvarchar(50) | YES |
| `UserLastName` | nvarchar(150) | YES |
| `UserName` | nvarchar(400) | YES |
| `UserRegisterDate` | datetime | YES |
| `UserActivateDate` | datetime | YES |
| `UserModifyDate` | datetime | YES |
| `UserIsDeleted` | bit | YES |
| `UserIsActivated` | bit | YES |
| `UserStatus` | nvarchar(30) | YES |
| `UserCompletedRegistration` | bit | YES |
| `UserIsLoggedIn` | bit | YES |
| `UserIsAdmin` | bit | YES |
| `UserIsAuthor` | bit | YES |
| `UserIsEditor` | bit | YES |
| `UserIsResearchTopicEditor` | bit | YES |
| `UserIsReviewer` | bit | YES |
| `UserEditorialBoardRoles` | varchar(500) | YES |
| `UserAuthorRoles` | varchar(500) | YES |
| `UserRolesNames` | varchar(500) | YES |
| `UserIsAdmin.Frontiers` | bit | YES |
| `UserIsAuthor.Frontiers` | bit | YES |
| `UserIsEditor.Frontiers` | bit | YES |
| `UserIsResearchTopicEditor.Frontiers` | bit | YES |
| `UserIsReviewer.Frontiers` | bit | YES |
| `IsUserInWatchList` | bit | YES |
| `JournalUserIsEditor` | bit | YES |
| `JournalUserIsEBM` | bit | YES |
| `JournalUserIsReviewer` | bit | YES |
| `JournalUserIsAuthor` | bit | YES |
| `JournalRoleId` | nvarchar(50) | YES |
| `JournalUserRoleId` | int(10) | YES |
| `JournalUserRole` | nvarchar(50) | YES |
| `JournalHighestRoleId.ResearchTopic` | nvarchar(10) | YES |
| `JournalHighestRole.ResearchTopic` | nvarchar(50) | YES |
| `JournalHighestRoleId.Article` | nvarchar(10) | YES |
| `JournalHighestRole.Article` | nvarchar(50) | YES |
| `JournalRole.FirstAssigned.Date` | datetime | YES |
| `Rank.ResearchTopic` | int(10) | YES |
| `Rank.Article` | int(10) | YES |
| `JournalUserFirstTaxonomyId` | bigint(19) | YES |
| `JournalUserFirstJoinDate` | datetime | YES |
| `JournalUserOrder` | int(10) | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(200) | YES |
| `TenantGroup` | nvarchar(50) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `UserId` | int(10) | YES |
| `UserIdOrder` | int(10) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `ArticleTaxonomyId` | bigint(19) | YES |
| `ArticleDomain` | nvarchar(50) | YES |
| `ArticleDomainId` | bigint(19) | YES |
| `ArticleField` | nvarchar(150) | YES |
| `ArticleFieldId` | bigint(19) | YES |
| `ArticleSpecialtyId` | bigint(19) | YES |
| `ArticleJournal` | nvarchar(150) | YES |
| `ArticleJournalFullName` | nvarchar(300) | YES |
| `ArticleJournalTaxonomyId` | bigint(19) | YES |
| `ArticleSection` | nvarchar(100) | YES |
| `ArticleSpecialty` | nvarchar(150) | YES |
| `ArticleStageCategory` | nvarchar(30) | YES |
| `ArticleStageCategoryId` | int(10) | YES |
| `ArticleId` | bigint(19) | YES |
| `ArticleId.Original` | int(10) | YES |
| `ArticleIsAccepted` | bit | YES |
| `ArticleIsPublished` | bit | YES |
| `ArticleIsRejected` | bit | YES |
| `ArticleIsResearchTopic` | bit | YES |
| `ArticleIsSubmitted` | bit | YES |
| `ArticleStageDate.Accepted` | datetime | YES |
| `ArticleStageDate.EditorialAssignment` | datetime | YES |
| `ArticleStageDate.InIndependentReview` | datetime | YES |
| `ArticleStageDate.InInteractiveReview` | datetime | YES |
| `ArticleStageDate.ReceivedByJournal` | datetime | YES |
| `ArticleStageDate.Rejected` | datetime | YES |
| `ArticleStageDate.ReviewFinalized` | datetime | YES |
| `ArticleStageDate.Submitted` | datetime | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_Spaces_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `SpaceId` | smallint(5) | YES |
| `Space` | nvarchar(200) | YES |
| `SpaceShortName` | nvarchar(20) | YES |
| `SpaceGUID` | uniqueidentifier | YES |
| `TenantGroup` | nvarchar(50) | YES |
| `WebDomain` | nvarchar(128) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_TaxonomyMetrics_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `Taxonomy` | nvarchar(200) | YES |
| `ProgramId` | int(10) | YES |
| `Program` | nvarchar(50) | YES |
| `DomainId` | bigint(19) | YES |
| `Domain` | nvarchar(50) | YES |
| `FieldId` | bigint(19) | YES |
| `Field` | nvarchar(150) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `Specialty` | nvarchar(150) | YES |
| `JournalId` | int(10) | YES |
| `Journal` | nvarchar(150) | YES |
| `SectionId` | int(10) | YES |
| `Section` | nvarchar(100) | YES |
| `DefaultTaxonomyId` | bigint(19) | YES |
| `JournalDevelopment.ProgramManager` | nvarchar(100) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `JournalFullName` | nvarchar(300) | YES |
| `JournalAbbreviation` | nvarchar(100) | YES |
| `JournalLaunchDate` | datetime | YES |
| `JournalMaturity` | nvarchar(50) | YES |
| `JournalISSN` | nvarchar(30) | YES |
| `IsOpenForSubmission` | bit | YES |
| `JournalPublishDate` | datetime | YES |
| `JournalFirstArticlePublishDate` | datetime | YES |
| `JCR.ImpactFactor.First` | real(24) | YES |
| `JCR.Year.First` | smallint(5) | YES |
| `JCR.ImpactFactor.Last` | real(24) | YES |
| `JCR.ImpactFactor.Last.Bin` | nvarchar(50) | YES |
| `JCR.ImpactFactor.Previous` | real(24) | YES |
| `JCR.ImpactFactor.TwoPrevious` | real(24) | YES |
| `JournalIsESCI` | bit | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### Reporting_UserMetrics_CT

| Column | Type | Nullable |
|---|---|---|
| `__$start_lsn` | binary(10) | NO |
| `__$end_lsn` | binary(10) | YES |
| `__$seqval` | binary(10) | NO |
| `__$operation` | int(10) | NO |
| `__$update_mask` | varbinary(128) | YES |
| `UserId` | int(10) | YES |
| `Email` | nvarchar(100) | YES |
| `FirstName` | nvarchar(150) | YES |
| `LastName` | nvarchar(150) | YES |
| `Name` | nvarchar(400) | YES |
| `Status` | nvarchar(30) | YES |
| `IsEditor` | bit | YES |
| `IsResearchTopicEditor` | bit | YES |
| `IsReviewer` | bit | YES |
| `IsDeleted` | bit | YES |
| `IsActivated` | bit | YES |
| `RegistrationDate` | datetime | YES |
| `RolesNames` | nvarchar(1000) | YES |
| `EditorialBoardRoles` | nvarchar(500) | YES |
| `AuthorRoles` | nvarchar(500) | YES |
| `CountPageViews` | int(10) | YES |
| `HIndex` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `ActivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `HIndexBins` | nvarchar(20) | YES |
| `ActivityBins` | nvarchar(20) | YES |
| `ConnectivityBins` | nvarchar(20) | YES |
| `InfluenceBins` | nvarchar(20) | YES |
| `ProductivityBins` | nvarchar(20) | YES |
| `FrontiersBins` | nvarchar(20) | YES |
| `CountryId` | nvarchar(10) | YES |
| `Country` | nvarchar(100) | YES |
| `Continent` | nvarchar(100) | YES |
| `Country3RegionsBinFocus` | nvarchar(100) | YES |
| `Country4RegionsBin` | nvarchar(100) | YES |
| `Country5RegionsBin` | nvarchar(100) | YES |
| `Country7RegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin` | nvarchar(100) | YES |
| `Country13RegionsBin` | nvarchar(100) | YES |
| `CountryFocusRegionsBin` | nvarchar(100) | YES |
| `Country8RegionsBin-China` | nvarchar(100) | YES |
| `Country8RegionsBin-ChinaCAS` | nvarchar(100) | YES |
| `CountryRejectionRate` | nvarchar(100) | YES |
| `UserPrimaryOrganizationId` | int(10) | YES |
| `UserPrimaryRosstId` | nvarchar(40) | YES |
| `UserPrimaryOrganization` | nvarchar(200) | YES |
| `UserPrimaryOrganizationCountry` | nvarchar(100) | YES |
| `UserOrganizationsHighestRankFrontiersPriority` | int(10) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganizationId` | int(10) | YES |
| `UserOrganizationsTopRankRosstId` | nvarchar(40) | YES |
| `UserOrganizationsHighestRankFrontiersPriorityOrganization` | nvarchar(200) | YES |
| `UserOrganizationIsTop150` | bit | YES |
| `IsUserPrimaryOrganizationCountryInWatchlist` | bit | YES |
| `IsUserInWatchList` | bit | YES |
| `UserOrganizationRejectionRateBin` | nvarchar(50) | YES |
| `UserOrganizationRejectionRateBin3` | nvarchar(50) | YES |
| `UserOrganizationRejectionRateBin10` | nvarchar(50) | YES |
| `OwnerEmployeeCountry` | nvarchar(50) | YES |
| `OwnerEmployeeCountry8RegionsBin` | nvarchar(50) | YES |
| `ThisYearStart` | date | YES |
| `ThisYearEnd` | date | YES |
| `LastYearStart` | date | YES |
| `LastYearEnd` | date | YES |
| `ThisYear` | int(10) | YES |
| `LastYear` | int(10) | YES |
| `Checksum` | bigint(19) | YES |
| `RowVersion` | binary(8) | YES |
| `ModifiedDate` | datetime2 | YES |
| `ValidUntil` | datetime2 | YES |
| `__$command_id` | int(10) | YES |

### captured_columns

| Column | Type | Nullable |
|---|---|---|
| `object_id` | int(10) | NO |
| `column_name` | nvarchar(128) | NO |
| `column_id` | int(10) | YES |
| `column_type` | nvarchar(128) | NO |
| `column_ordinal` | int(10) | NO |
| `is_computed` | bit | YES |
| `masking_function` | nvarchar(4000) | YES |

### change_tables

| Column | Type | Nullable |
|---|---|---|
| `object_id` | int(10) | NO |
| `version` | int(10) | YES |
| `source_object_id` | int(10) | YES |
| `capture_instance` | nvarchar(128) | NO |
| `start_lsn` | binary(10) | YES |
| `end_lsn` | binary(10) | YES |
| `supports_net_changes` | bit | YES |
| `has_drop_pending` | bit | YES |
| `role_name` | nvarchar(128) | YES |
| `index_name` | nvarchar(128) | YES |
| `filegroup_name` | nvarchar(128) | YES |
| `create_date` | datetime | YES |
| `partition_switch` | bit | NO |

### ddl_history

| Column | Type | Nullable |
|---|---|---|
| `source_object_id` | int(10) | YES |
| `object_id` | int(10) | NO |
| `required_column_update` | bit | YES |
| `ddl_command` | nvarchar | YES |
| `ddl_lsn` | binary(10) | NO |
| `ddl_time` | datetime | YES |

### index_columns

| Column | Type | Nullable |
|---|---|---|
| `object_id` | int(10) | NO |
| `column_name` | nvarchar(128) | NO |
| `index_ordinal` | tinyint(3) | NO |
| `column_id` | int(10) | NO |

### lsn_time_mapping

| Column | Type | Nullable |
|---|---|---|
| `start_lsn` | binary(10) | NO |
| `tran_begin_time` | datetime | YES |
| `tran_end_time` | datetime | YES |
| `tran_id` | varbinary(10) | YES |
| `tran_begin_lsn` | binary(10) | YES |

## [ReportingDataMart].[dbo]


### __RefactorLog

| Column | Type | Nullable |
|---|---|---|
| `OperationKey` | uniqueidentifier | NO |

### systranschemas

| Column | Type | Nullable |
|---|---|---|
| `tabid` | int(10) | NO |
| `startlsn` | binary(10) | NO |
| `endlsn` | binary(10) | NO |
| `typeid` | int(10) | NO |

## [TenantsDataMarts].[Accounting]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### Currencies

| Column | Type | Nullable |
|---|---|---|
| `CurrencyId` | int(10) | NO |
| `CurrencyCode` | nvarchar(10) | YES |
| `RowVersion` | timestamp | NO |

### CurrencyRates

| Column | Type | Nullable |
|---|---|---|
| `CurrencyCode` | nvarchar(3) | NO |
| `Year` | int(10) | NO |
| `ExchangeRate.USD` | float(53) | YES |
| `ExchangeRate.CHF` | float(53) | YES |
| `VAT` | float(53) | YES |

### DiscountCategories

| Column | Type | Nullable |
|---|---|---|
| `DiscountCategoryCode` | nvarchar(10) | NO |
| `DiscountCategoryName` | nvarchar(200) | YES |
| `RowVersion` | timestamp | NO |

### DiscountTypes

| Column | Type | Nullable |
|---|---|---|
| `DiscountTypeCode` | nvarchar(10) | NO |
| `DiscountTypeName` | nvarchar(200) | YES |
| `RowVersion` | timestamp | NO |

### InstitutionalMembership.ArticleFunding

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `InstitutionId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `MatchingReasonId` | int(10) | YES |
| `FundingDecisionId` | int(10) | YES |
| `DecideDate` | datetime | YES |
| `DeclinationReasonId` | int(10) | YES |
| `DeclinationReasonComment` | nvarchar(500) | YES |
| `DeclinationComment` | nvarchar(1000) | YES |
| `BillingReference` | nvarchar(2000) | YES |
| `InvoiceId` | bigint(19) | YES |
| `IsMembershipDiscountApplied` | bit | NO |
| `IsFundingCapApplied` | bit | NO |
| `RowVersion` | timestamp | NO |

### InstitutionalMembership.ArticleFundingHistory

| Column | Type | Nullable |
|---|---|---|
| `HistoryId` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `InstitutionId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `IsActive` | bit | NO |
| `MatchingReasonId` | int(10) | YES |
| `FundingDecisionId` | int(10) | YES |
| `DecideDate` | datetime | YES |
| `DeclinationReasonId` | int(10) | YES |
| `DeclinationReasonComment` | nvarchar(500) | YES |
| `DeclinationComment` | nvarchar(1000) | YES |
| `BillingReference` | nvarchar(2000) | YES |
| `CreateDate` | datetime | NO |
| `CreatorUserId` | int(10) | YES |
| `ModifyDate` | datetime | YES |
| `ModifierUserId` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### InstitutionalMembership.ArticleInstitutionMatches

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `ArticleId.Original` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `InstitutionId` | bigint(19) | NO |
| `IsActive` | bit | NO |
| `IsDisplayed` | bit | NO |
| `MatchingReasonId` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### InstitutionalMembership.BillingStatus

| Column | Type | Nullable |
|---|---|---|
| `BillingStatusId` | int(10) | NO |
| `BillingStatus` | nvarchar(50) | YES |
| `RowVersion` | timestamp | NO |

### InstitutionalMembership.DeclinationReason

| Column | Type | Nullable |
|---|---|---|
| `DeclinationReasonId` | int(10) | NO |
| `DeclinationReason` | nvarchar(500) | YES |
| `Description` | nvarchar(100) | YES |
| `RowVersion` | timestamp | NO |

### InstitutionalMembership.FundingDecision

| Column | Type | Nullable |
|---|---|---|
| `FundingDecisionId` | int(10) | NO |
| `FundingDecision` | nvarchar(50) | YES |
| `RowVersion` | timestamp | NO |

### InstitutionalMembership.Institution

| Column | Type | Nullable |
|---|---|---|
| `InstitutionId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `InstitutionId.Original` | int(10) | NO |
| `InstitutionName` | nvarchar(255) | NO |
| `CreateDate` | date | YES |
| `TerminateDate` | date | YES |
| `BillingStatusId` | int(10) | YES |
| `InstitutionTypeId` | int(10) | YES |
| `MembershipTypeId` | int(10) | YES |
| `MembershipBillingTypeId` | int(10) | YES |
| `APCCoverageRatio` | decimal(5) | YES |
| `MembershipDiscountRatio` | decimal(5) | YES |
| `CapLimitAmount` | decimal(18) | YES |
| `CapLimitCurrencyId` | int(10) | YES |
| `InstitutionHandlerUserId` | int(10) | NO |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `ConsortiumInstitutionId.Original` | bigint(19) | YES |
| `ConsortiumInstitutionId` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |

### InstitutionalMembership.InstitutionType

| Column | Type | Nullable |
|---|---|---|
| `InstitutionTypeId` | int(10) | NO |
| `InstitutionType` | nvarchar(50) | YES |
| `RowVersion` | timestamp | NO |

### InstitutionalMembership.MatchingReason

| Column | Type | Nullable |
|---|---|---|
| `MatchingReasonId` | int(10) | NO |
| `MatchingReason` | nvarchar(50) | YES |
| `Description` | nvarchar(100) | YES |
| `RowVersion` | timestamp | NO |

### InstitutionalMembership.MembershipBillingType

| Column | Type | Nullable |
|---|---|---|
| `MembershipBillingTypeId` | int(10) | NO |
| `MembershipBillingType` | nvarchar(50) | YES |
| `RowVersion` | timestamp | NO |

### InstitutionalMembership.MembershipType

| Column | Type | Nullable |
|---|---|---|
| `MembershipTypeId` | int(10) | NO |
| `MembershipType` | nvarchar(50) | YES |
| `RowVersion` | timestamp | NO |

### InvoiceItems

| Column | Type | Nullable |
|---|---|---|
| `InvoiceItemId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `InvoiceId` | bigint(19) | NO |
| `ItemName` | nvarchar(400) | NO |
| `ItemAmount` | numeric(18) | YES |
| `RevenueItemId` | bigint(19) | NO |
| `Quantity` | int(10) | YES |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### InvoiceItems_Discounts

| Column | Type | Nullable |
|---|---|---|
| `DiscountId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `InvoiceItemId` | bigint(19) | NO |
| `DiscountName` | nvarchar(100) | NO |
| `DiscountAmount` | numeric(18) | YES |
| `RevenueItemDiscountId` | bigint(19) | YES |
| `Quantity` | int(10) | YES |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### Invoices

| Column | Type | Nullable |
|---|---|---|
| `InvoiceId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(100) | NO |
| `InvoiceId.Original` | int(10) | NO |
| `ArticleId` | bigint(19) | YES |
| `ArticleId.Original` | int(10) | YES |
| `RevenueId` | int(10) | YES |
| `InvoiceNo` | int(10) | NO |
| `InvoiceNoDisplay` | nvarchar(50) | YES |
| `DueAmount` | numeric(18) | YES |
| `AmountOutstanding` | numeric(18) | YES |
| `CurrencyId` | int(10) | YES |
| `InvoiceDate` | datetime | YES |
| `InvoiceDueDate` | datetime | YES |
| `InvoiceDiscountCode` | nvarchar(500) | YES |
| `StatusId` | tinyint(3) | YES |
| `ValidityId` | tinyint(3) | YES |
| `VAT` | numeric(21) | YES |
| `CreateDate` | datetime | NO |
| `CreatorUserId` | int(10) | YES |
| `ModifyDate` | datetime | YES |
| `ModifierUserId` | int(10) | YES |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |
| `Checksum` | bigint(19) | NO |

### Invoices.Transactions

| Column | Type | Nullable |
|---|---|---|
| `TransactionId` | bigint(19) | NO |
| `InvoiceId` | bigint(19) | NO |
| `InvoiceItemId` | bigint(19) | NO |
| `InvoiceItemDiscountId` | bigint(19) | YES |
| `DiscountMappingId` | int(10) | YES |
| `PaymentId` | bigint(19) | YES |
| `SpaceId` | smallint(5) | NO |
| `Amount` | numeric(19) | YES |
| `VATRate` | numeric(9) | YES |
| `ExchangeRate` | numeric(9) | YES |
| `TransactionTypeId` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Invoices_History

| Column | Type | Nullable |
|---|---|---|
| `InvoiceId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `InvoiceId.Original` | int(10) | NO |
| `ArticleId` | bigint(19) | YES |
| `JournalId` | int(10) | YES |
| `RevenueId` | int(10) | YES |
| `InvoiceNo` | int(10) | NO |
| `InvoiceNoDisplay` | nvarchar(50) | YES |
| `Version` | int(10) | YES |
| `DueAmount` | numeric(18) | YES |
| `AmountOutstanding` | numeric(18) | YES |
| `CurrencyId` | int(10) | YES |
| `InvoiceDate` | datetime | YES |
| `InvoiceDueDate` | datetime | YES |
| `InvoiceDiscountCode` | nvarchar(500) | YES |
| `StatusId` | tinyint(3) | YES |
| `ValidityId` | tinyint(3) | YES |
| `VAT` | numeric(21) | YES |
| `VATRate` | numeric(9) | YES |
| `InvoiceIsLatest` | bit | NO |
| `InvoiceId.Latest` | bigint(19) | NO |
| `InvoiceVersion.Latest` | bigint(19) | YES |
| `IsLastInvoiceInDate` | bit | NO |
| `CreateDate` | datetime | NO |
| `CreatorUserId` | int(10) | NO |
| `ModifyDate` | datetime | YES |
| `ModifierUserId` | int(10) | YES |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### Invoices_PayerType

| Column | Type | Nullable |
|---|---|---|
| `PayerTypeId` | int(10) | NO |
| `PayerType` | nvarchar(30) | NO |

### Invoices_Payers

| Column | Type | Nullable |
|---|---|---|
| `PayerId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `InvoiceId` | bigint(19) | NO |
| `Email` | nvarchar(100) | YES |
| `FirstName` | nvarchar(400) | YES |
| `MiddleName` | nvarchar(500) | YES |
| `LastName` | nvarchar(200) | YES |
| `Name` | nvarchar(400) | YES |
| `PayerUserId` | int(10) | YES |
| `PayerTypeId` | int(10) | NO |
| `PayerInstitutionOrganizationId` | int(10) | YES |
| `PayerInstitutionRosstId` | nvarchar(40) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `LegacyOrganization` | nvarchar(700) | YES |
| `LegacyDepartment` | nvarchar(800) | YES |
| `LegacyLaboratory` | nvarchar(400) | YES |
| `Address` | nvarchar(500) | YES |
| `City` | nvarchar(50) | YES |
| `PostalCode` | nvarchar(50) | YES |
| `State` | nvarchar(50) | YES |
| `CountryId` | char(3) | YES |
| `PhoneNumber` | nvarchar(30) | YES |
| `UserReference` | nvarchar | YES |
| `Comments` | nvarchar(500) | YES |
| `Attention` | nvarchar(350) | YES |
| `AttentionEmail` | nvarchar(150) | YES |
| `AttentionIsPayer` | bit | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### Invoices_Status

| Column | Type | Nullable |
|---|---|---|
| `StatusId` | tinyint(3) | NO |
| `Status` | varchar(9) | NO |
| `RowVersion` | timestamp | NO |

### Invoices_Validity

| Column | Type | Nullable |
|---|---|---|
| `ValidityId` | tinyint(3) | NO |
| `Validity` | varchar(9) | NO |
| `RowVersion` | timestamp | NO |

### Payments

| Column | Type | Nullable |
|---|---|---|
| `PaymentId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId` | bigint(19) | YES |
| `InvoiceId` | bigint(19) | YES |
| `Amount` | numeric(18) | NO |
| `CurrencyId` | int(10) | YES |
| `TypeId` | int(10) | YES |
| `AccountId` | bigint(19) | YES |
| `PayerUserId` | int(10) | YES |
| `PayerEmail` | nvarchar(100) | YES |
| `Description` | nvarchar(100) | YES |
| `BankReferenceId` | nvarchar(30) | YES |
| `CreateDate` | datetime | NO |
| `PayDate` | datetime | YES |
| `IsVisible` | bit | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### Payments_Account

| Column | Type | Nullable |
|---|---|---|
| `AccountId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `AccountKey` | nvarchar(10) | YES |
| `Account` | nvarchar(50) | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### Payments_Type

| Column | Type | Nullable |
|---|---|---|
| `TypeId` | int(10) | NO |
| `Type` | nvarchar(50) | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### Revenue

| Column | Type | Nullable |
|---|---|---|
| `RevenueId` | int(10) | NO |
| `Revenue` | nvarchar(100) | NO |
| `Description` | nvarchar(100) | YES |
| `RowVersion` | timestamp | NO |

### RevenueItems

| Column | Type | Nullable |
|---|---|---|
| `RevenueItemId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `RevenueId` | int(10) | NO |
| `RevenueItem` | nvarchar(100) | NO |
| `Description` | nvarchar(500) | YES |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### RevenueItems_DiscountCategory

| Column | Type | Nullable |
|---|---|---|
| `DiscountCategoryId` | int(10) | NO |
| `DiscountCategory` | nvarchar(255) | NO |

### RevenueItems_DiscountMapping

| Column | Type | Nullable |
|---|---|---|
| `DiscountMappingId` | int(10) | NO |
| `RevenueItemDiscountId` | bigint(19) | YES |
| `DiscountName` | nvarchar(255) | NO |
| `DiscountTypeId` | int(10) | NO |
| `DiscountCategoryId` | int(10) | NO |
| `IsHidden` | bit | NO |
| `IsAggregated` | bit | NO |
| `IsPublisherDiscount` | bit | NO |

### RevenueItems_DiscountType

| Column | Type | Nullable |
|---|---|---|
| `DiscountTypeId` | int(10) | NO |
| `DiscountType` | nvarchar(255) | NO |

### RevenueItems_Discounts

| Column | Type | Nullable |
|---|---|---|
| `DiscountId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `RevenueItemId` | bigint(19) | NO |
| `Discount` | nvarchar(100) | NO |
| `Type` | nvarchar(50) | YES |
| `Description` | nvarchar(500) | YES |
| `IsDeleted` | bit | NO |
| `IsHidden` | bit | NO |
| `DiscountCategoryCode` | nvarchar(10) | NO |
| `DiscountTypeCode` | nvarchar(10) | YES |
| `RowVersion` | timestamp | NO |

### RevenueItems_FrontiersRevenue.History

| Column | Type | Nullable |
|---|---|---|
| `SplitRevenueOceanId` | nvarchar(50) | YES |
| `TaxonomyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleTypeId` | bigint(19) | NO |
| `CurrencyId` | int(10) | YES |
| `CurrencyCode` | nvarchar(10) | YES |
| `FrontiersRevenue` | decimal(18) | YES |
| `StartDate` | datetime | NO |
| `EndDate` | datetime | YES |
| `RowVersion` | timestamp | NO |
| `Checksum` | bigint(19) | NO |

### RevenueItems_Revenues

| Column | Type | Nullable |
|---|---|---|
| `SpaceId` | smallint(5) | NO |
| `Journal` | nvarchar(200) | NO |
| `ArticleType` | nvarchar(100) | NO |
| `FrontiersRevenue` | numeric(18) | NO |
| `JournalCurrency` | nvarchar(3) | NO |

## [TenantsDataMarts].[Analytics]


### IndividualTargetValues

| Column | Type | Nullable |
|---|---|---|
| `MeasureId` | int(10) | NO |
| `TargetTypeId` | int(10) | NO |
| `JournalTaxonomyId` | bigint(19) | NO |
| `JournalId` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `JobProfileId` | nvarchar(8) | NO |
| `TargetPeriodType` | char(1) | NO |
| `RegionBinId` | int(10) | NO |
| `WorkdayEmployeeId` | varchar(12) | NO |
| `Date` | datetime | NO |
| `Value` | float(53) | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |

### Measures

| Column | Type | Nullable |
|---|---|---|
| `MeasureId` | int(10) | NO |
| `MeasureCode` | varchar(100) | NO |
| `WorkdayMeasure` | nvarchar(400) | YES |
| `Order` | int(10) | NO |
| `Measure` | nvarchar(100) | NO |
| `Unit` | nvarchar(10) | NO |
| `DecimalScale` | int(10) | NO |
| `Definition` | nvarchar(400) | YES |
| `ComputedFormula` | varchar(100) | YES |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |

### MeasuresMapping

| Column | Type | Nullable |
|---|---|---|
| `MeasureId.Original` | int(10) | NO |
| `TargetGranularityId` | int(10) | NO |
| `MeasureId.Final` | int(10) | NO |
| `StartDate` | date | NO |
| `EndDate` | date | NO |
| `IsVisible` | bit | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |

### SourceTargetValues

| Column | Type | Nullable |
|---|---|---|
| `MeasureId` | int(10) | NO |
| `TargetTypeId` | int(10) | NO |
| `TaxonomyId` | bigint(19) | NO |
| `Date` | datetime | NO |
| `TargetPeriodType` | char(1) | NO |
| `TargetGranularityId` | int(10) | NO |
| `RegionBinId` | int(10) | NO |
| `RegionId` | char(3) | NO |
| `Value` | float(53) | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |

### TargetGranularities

| Column | Type | Nullable |
|---|---|---|
| `TargetGranularityId` | int(10) | NO |
| `TargetGranularity` | nvarchar(30) | NO |
| `Description` | nvarchar(400) | YES |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |

### TargetTypes

| Column | Type | Nullable |
|---|---|---|
| `TargetTypeId` | int(10) | NO |
| `TargetType` | nvarchar(30) | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |

## [TenantsDataMarts].[CRM]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### Campaigns

| Column | Type | Nullable |
|---|---|---|
| `CampaignCRMId` | char(18) | NO |
| `Name` | nvarchar(200) | NO |
| `CampaignOwnerUserId` | int(10) | YES |
| `ParentCampaignCRMId` | char(18) | YES |
| `UltimateParentCampaignCRMId` | char(18) | YES |
| `RecordTypeCRMId` | char(18) | NO |
| `TaxonomyId` | bigint(19) | YES |
| `MessagingMethod` | nvarchar(255) | YES |
| `IsPerfectEmailEnabled` | bit | YES |
| `StartDate` | datetime | YES |
| `EndDate` | datetime | YES |
| `Status` | nvarchar(128) | YES |
| `ModifyDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### CampaignsMembers

| Column | Type | Nullable |
|---|---|---|
| `CampaignMemberCRMId` | char(18) | NO |
| `RecordTypeCRMId` | char(18) | NO |
| `CampaignCRMId` | char(18) | NO |
| `CampaignRecordTypeCRMId` | char(18) | NO |
| `Status` | nvarchar(40) | YES |
| `UserId` | int(10) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `EmailAddress` | nvarchar(80) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `InviteDate` | date | YES |
| `ModifyDate` | datetime | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### ChatTranscript

| Column | Type | Nullable |
|---|---|---|
| `ChatTranscriptId` | nvarchar(18) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId` | bigint(19) | YES |
| `ArticleId.Original` | int(10) | YES |
| `Owner.UserId` | int(10) | YES |
| `Requester.UserId` | int(10) | YES |
| `Requester.RoleId` | int(10) | YES |
| `Request.CreateDate` | datetime | YES |
| `ChatTranscript.StartDate` | datetime | YES |
| `ChatTranscript.EndDate` | datetime | YES |
| `CountryId` | char(3) | YES |
| `LocationString` | nvarchar(50) | YES |
| `IsChatbotSession` | bit | NO |
| `Requester.Browser` | nvarchar(200) | YES |
| `Requester.BrowserLanguage` | nvarchar(200) | YES |
| `Requester.Platform` | nvarchar(200) | YES |
| `RecordTypeCRMId` | char(18) | YES |
| `IsDeleted` | bit | NO |

### Contacts

| Column | Type | Nullable |
|---|---|---|
| `ContactId` | nvarchar(18) | NO |
| `Email` | nvarchar(128) | YES |
| `UserId` | int(10) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `CreateDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### Contracts

| Column | Type | Nullable |
|---|---|---|
| `CRMContractId` | nvarchar(18) | NO |
| `RosstId` | nvarchar(40) | YES |
| `StartDate` | datetime | NO |
| `EndDate` | datetime | YES |
| `MembershipType` | nvarchar(60) | YES |
| `Currency` | nvarchar(3) | YES |
| `ContractedAmount` | int(10) | YES |
| `RecordTypeId` | nvarchar(18) | YES |

### Discounts

| Column | Type | Nullable |
|---|---|---|
| `DiscountCodeCRMId` | char(18) | NO |
| `DiscountName` | nvarchar(80) | NO |
| `DiscountTypeCode` | nvarchar(10) | YES |
| `DiscountCategoryCode` | nvarchar(10) | YES |
| `CurrencyId` | int(10) | YES |
| `ApplicationDate` | date | YES |
| `SpaceId` | smallint(5) | YES |
| `ArticleId` | bigint(19) | YES |
| `ArticleId.Original` | int(10) | YES |
| `DecisionStatus` | nvarchar(255) | YES |
| `ExpirationDate` | date | NO |
| `InvoiceNo` | nvarchar(50) | YES |
| `InitialFee` | decimal(18) | YES |
| `DiscountPercent` | decimal(18) | YES |
| `Referrer.UserId` | int(10) | YES |
| `Referrer.Email` | nvarchar(150) | YES |
| `ResearchTopicId` | bigint(19) | YES |
| `ResearchTopicId.Original` | int(10) | YES |
| `JournalTaxonomyId` | bigint(19) | YES |
| `CreateDate` | datetime | NO |
| `IsDeleted` | bit | NO |
| `ModifyDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### EmployeeRole

| Column | Type | Nullable |
|---|---|---|
| `EmployeeRoleId` | nvarchar(18) | NO |
| `EmployeeRole` | nvarchar(250) | YES |
| `Description` | nvarchar(250) | YES |
| `ModifiedDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### Employees

| Column | Type | Nullable |
|---|---|---|
| `UserCRMId` | char(18) | NO |
| `Email` | nvarchar(128) | YES |
| `UserId` | int(10) | YES |
| `Firstname` | nvarchar(40) | YES |
| `Lastname` | nvarchar(80) | YES |
| `EmploymentCountryId` | char(3) | YES |
| `EmployeeRoleId` | nvarchar(18) | YES |
| `CreateDate` | datetime | YES |
| `ModifiedDate` | datetime | YES |
| `IsActive` | bit | YES |
| `RowVersion` | timestamp | NO |

### Opportunities

| Column | Type | Nullable |
|---|---|---|
| `OpportunityCRMId` | char(18) | NO |
| `Name` | nvarchar(250) | NO |
| `RecordTypeCRMId` | char(18) | NO |
| `ParentOpportunityCRMId` | char(18) | YES |
| `CampaignCRMId` | char(18) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `ResearchTopicId` | bigint(19) | YES |
| `ResearchTopicId.Original` | int(10) | YES |
| `ContactUserId` | int(10) | YES |
| `ContactEmailAddress` | nvarchar(80) | YES |
| `ContactOrganizationId` | int(10) | YES |
| `ContactRosstId` | nvarchar(40) | YES |
| `OwnerUserId` | int(10) | YES |
| `Stage` | nvarchar(40) | NO |
| `PartOfACP` | bit | YES |
| `CloseDate` | datetime | YES |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### OpportunitiesContactsRoles

| Column | Type | Nullable |
|---|---|---|
| `OpportunityContactRoleCRMId` | char(18) | NO |
| `OpportunityCRMId` | char(18) | NO |
| `ContactUserId` | int(10) | YES |
| `ContactEmailAddress` | nvarchar(80) | YES |
| `ContactRole` | nvarchar(255) | YES |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### OpportunitiesStages

| Column | Type | Nullable |
|---|---|---|
| `OpportunityStageCRMId` | char(18) | NO |
| `OpportunityCRMId` | char(18) | NO |
| `StageOrder` | int(10) | NO |
| `IsCurrent` | bit | NO |
| `Stage.Previous` | nvarchar(40) | YES |
| `Stage` | nvarchar(40) | NO |
| `Stage.Next` | nvarchar(40) | YES |
| `CreateDate` | datetime | NO |
| `Duration` | datetime | YES |
| `RowVersion` | timestamp | NO |

### RecordType

| Column | Type | Nullable |
|---|---|---|
| `RecordTypeCRMId` | char(18) | NO |
| `RecordType` | nvarchar(80) | NO |
| `Description` | nvarchar(255) | YES |
| `SObjectType` | nvarchar(40) | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopicsEvents

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicId` | bigint(19) | NO |
| `ResearchTopicId.Original` | int(10) | YES |
| `SpaceId` | smallint(5) | NO |
| `ResearchTopicCRMId` | nvarchar(18) | YES |
| `EventCreatorUserId` | int(10) | YES |
| `EventType` | nvarchar(255) | NO |
| `StartDate` | datetime | NO |
| `EndDate` | datetime | YES |
| `Id` | int(10) | YES |
| `Name` | nvarchar(255) | YES |

## [TenantsDataMarts].[Common]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### Calendar

| Column | Type | Nullable |
|---|---|---|
| `Date` | date | NO |
| `Year` | smallint(5) | NO |
| `Quarter` | tinyint(3) | NO |
| `Month` | tinyint(3) | NO |
| `Week` | tinyint(3) | NO |
| `Day` | tinyint(3) | NO |
| `DayOfWeek` | tinyint(3) | NO |
| `DayOfQuarter` | tinyint(3) | NO |
| `DayOfYear` | smallint(5) | NO |
| `MonthName` | varchar(10) | NO |
| `MonthShortName` | char(3) | NO |
| `WeekDayName` | varchar(10) | NO |
| `WeekDayShortName` | char(3) | NO |
| `DateString` | char(10) | NO |
| `ShortDateString` | char(11) | NO |
| `LongDateString` | varchar(30) | NO |
| `FirstDayOfYear` | date | NO |
| `FirstDayOfQuarter` | date | NO |
| `FirstDayOfMonth` | date | NO |
| `FirstDayOfweek` | date | NO |
| `LastDayOfYear` | date | NO |
| `LastDayOfQuarter` | date | NO |
| `LastDayOfMonth` | date | NO |
| `LastDayOfweek` | date | NO |
| `IsFirstDayOfYear` | bit | NO |
| `IsFirstDayOfQuarter` | bit | NO |
| `IsFirstDayOfMonth` | bit | NO |
| `IsFirstDayOfWeek` | bit | NO |
| `IsFirstMonthOfYear` | bit | NO |
| `IsFirstMonthOfQuarter` | bit | NO |
| `IsLastDayOfYear` | bit | NO |
| `IsLastDayOfQuarter` | bit | NO |
| `IsLastDayOfMonth` | bit | NO |
| `IsLastDayOfWeek` | bit | NO |
| `IsLastMonthOfYear` | bit | NO |
| `IsLastMonthOfQuarter` | bit | NO |
| `IsLeapYear` | bit | NO |
| `IsPreviousYearLeapYear` | bit | NO |
| `DaysInYear` | smallint(5) | NO |
| `DaysInQuarter` | tinyint(3) | NO |
| `DaysInMonth` | tinyint(3) | NO |
| `DaysLeftInYear` | smallint(5) | NO |
| `DaysLeftInQuarter` | tinyint(3) | NO |
| `DaysLeftInMonth` | tinyint(3) | NO |

### Cities

| Column | Type | Nullable |
|---|---|---|
| `CityId` | int(10) | NO |
| `Name` | nvarchar(200) | NO |
| `StateId` | int(10) | YES |
| `CountryId` | char(3) | YES |
| `RowVersion` | timestamp | NO |

### Continents

| Column | Type | Nullable |
|---|---|---|
| `ContinentId` | char(2) | NO |
| `Continent` | varchar(13) | NO |
| `RowVersion` | timestamp | NO |

### CostCenters

| Column | Type | Nullable |
|---|---|---|
| `CostCenterId` | nvarchar(50) | NO |
| `CostCenterName` | nvarchar(255) | NO |
| `CostCenterDescription` | nvarchar(255) | NO |
| `RowVersion` | timestamp | NO |

### Countries

| Column | Type | Nullable |
|---|---|---|
| `CountryId` | char(3) | NO |
| `Country` | nvarchar(100) | NO |
| `EnglishShortName` | nvarchar(255) | YES |
| `Alpha2Code` | char(2) | YES |
| `Numeric` | char(3) | YES |
| `ccTLD` | char(3) | YES |
| `ContinentId` | char(2) | YES |
| `Latitude` | decimal(10) | YES |
| `Longitude` | decimal(10) | YES |
| `RowVersion` | timestamp | NO |

### Countries_Flag

| Column | Type | Nullable |
|---|---|---|
| `FlagId` | int(10) | NO |
| `Name` | nvarchar(20) | NO |
| `Description` | nvarchar(100) | YES |
| `RowVersion` | timestamp | NO |

### Countries_Flags

| Column | Type | Nullable |
|---|---|---|
| `CountryId` | char(3) | NO |
| `FlagId` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Countries_Names

| Column | Type | Nullable |
|---|---|---|
| `CountryName` | nvarchar(100) | NO |
| `CountryId` | char(3) | NO |
| `Source` | nvarchar(100) | YES |
| `Comments` | nvarchar(4000) | YES |
| `CreateDate` | datetime | NO |
| `ModifyHistory` | xml | YES |
| `RowVersion` | timestamp | NO |

### Countries_Regions

| Column | Type | Nullable |
|---|---|---|
| `CountryId` | char(3) | NO |
| `Country` | nvarchar(128) | YES |
| `Region3Bin` | nvarchar(128) | YES |
| `Region4Bin` | nvarchar(128) | YES |
| `Region5Bin` | nvarchar(128) | YES |
| `Region7Bin` | nvarchar(128) | YES |
| `Region8Bin` | nvarchar(128) | YES |
| `Region13Bin` | nvarchar(128) | YES |
| `IsFocusRegion` | bit | YES |
| `RowVersion` | timestamp | NO |

### EmailDomains

| Column | Type | Nullable |
|---|---|---|
| `DomainPattern` | nvarchar(100) | NO |
| `DomainType` | nvarchar(50) | NO |

### Impacts_Action

| Column | Type | Nullable |
|---|---|---|
| `ActionId` | int(10) | NO |
| `Action` | varchar(40) | NO |
| `RowVersion` | timestamp | NO |

### Impacts_Aggregation

| Column | Type | Nullable |
|---|---|---|
| `AggregationId` | int(10) | NO |
| `Aggregation` | varchar(150) | NO |
| `RowVersion` | timestamp | NO |

### Impacts_Provider

| Column | Type | Nullable |
|---|---|---|
| `ProviderId` | int(10) | NO |
| `Provider` | nvarchar(50) | YES |
| `RowVersion` | timestamp | NO |

### JobProfiles

| Column | Type | Nullable |
|---|---|---|
| `JobProfileId` | nvarchar(8) | NO |
| `JobProfile` | nvarchar(255) | NO |
| `RowVersion` | timestamp | NO |

### Languages

| Column | Type | Nullable |
|---|---|---|
| `LanguageId` | nchar(2) | NO |
| `LanguageName` | nvarchar(50) | NO |
| `RowVersion` | timestamp | NO |

### Organizations

| Column | Type | Nullable |
|---|---|---|
| `OrganizationId` | int(10) | NO |
| `MergedToOrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(200) | NO |
| `Description` | nvarchar | YES |
| `Logo` | nvarchar(32) | YES |
| `OriginId` | smallint(5) | NO |
| `URL` | nvarchar(500) | YES |
| `Phone` | nvarchar(30) | YES |
| `Email` | nvarchar(100) | YES |
| `Latitude` | float(53) | YES |
| `Longitude` | float(53) | YES |
| `IsDeleted` | bit | NO |
| `IsUserCreated` | bit | NO |
| `IsValidated` | bit | NO |
| `IsUnaffiliatedOption` | bit | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### Organizations_Addresses

| Column | Type | Nullable |
|---|---|---|
| `AddressId` | int(10) | NO |
| `Street` | nvarchar(200) | YES |
| `ZipCode` | nvarchar(30) | YES |
| `CityId` | int(10) | NO |
| `OrganizationId` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Organizations_Aliases

| Column | Type | Nullable |
|---|---|---|
| `AliasId` | int(10) | NO |
| `OrganizationId` | int(10) | NO |
| `Alias` | nvarchar(200) | NO |
| `RowVersion` | timestamp | NO |

### Organizations_EmailDomains

| Column | Type | Nullable |
|---|---|---|
| `EmailDomainId` | int(10) | NO |
| `Domain` | nvarchar(100) | NO |
| `IsPrimary` | bit | NO |
| `OrganizationId` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Organizations_Flag

| Column | Type | Nullable |
|---|---|---|
| `FlagId` | int(10) | NO |
| `Name` | nvarchar(20) | NO |
| `RowVersion` | timestamp | NO |

### Organizations_Flags

| Column | Type | Nullable |
|---|---|---|
| `OrganizationId` | int(10) | NO |
| `FlagId` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Organizations_Hierarchy

| Column | Type | Nullable |
|---|---|---|
| `ParentOrganizationId` | int(10) | NO |
| `ChildOrganizationId` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Organizations_HierarchyAllLevelChilds

| Column | Type | Nullable |
|---|---|---|
| `OrganizationHierarchyId` | numeric(20) | NO |
| `OrganizationId` | int(10) | NO |
| `Organization` | nvarchar(200) | NO |
| `ChildOrganizationId` | int(10) | YES |
| `ChildOrganization` | nvarchar(200) | YES |
| `ConnectionLevel` | int(10) | NO |
| `HasDescendant` | bit | NO |
| `RowVersion` | timestamp | NO |
| `Checksum` | bigint(19) | NO |

### Organizations_HierarchyAllLevelParents

| Column | Type | Nullable |
|---|---|---|
| `OrganizationHierarchyId` | numeric(20) | NO |
| `OrganizationId` | int(10) | NO |
| `Organization` | nvarchar(200) | NO |
| `ParentOrganizationId` | int(10) | YES |
| `ParentOrganization` | nvarchar(200) | YES |
| `ConnectionLevel` | int(10) | NO |
| `HasAncestor` | bit | NO |
| `RowVersion` | timestamp | NO |
| `Checksum` | bigint(19) | NO |

### Organizations_Origin

| Column | Type | Nullable |
|---|---|---|
| `OriginId` | smallint(5) | NO |
| `Origin` | nvarchar(100) | NO |
| `RowVersion` | timestamp | NO |

### Organizations_Ranking

| Column | Type | Nullable |
|---|---|---|
| `RankingId` | int(10) | NO |
| `Name` | nvarchar(100) | NO |
| `Length` | int(10) | YES |
| `Year` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Organizations_Rankings

| Column | Type | Nullable |
|---|---|---|
| `OrganizationId` | int(10) | NO |
| `RankingId` | int(10) | NO |
| `Position` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Organizations_Source

| Column | Type | Nullable |
|---|---|---|
| `OrganizationSourceId` | char(1) | NO |
| `OrganizationSource` | nvarchar(40) | NO |
| `RowVersion` | timestamp | NO |

### Organizations_Type

| Column | Type | Nullable |
|---|---|---|
| `TypeId` | int(10) | NO |
| `Type` | nvarchar(30) | NO |
| `RowVersion` | timestamp | NO |

### Organizations_Types

| Column | Type | Nullable |
|---|---|---|
| `OrganizationId` | int(10) | NO |
| `TypeId` | int(10) | NO |
| `IsPrimary` | bit | NO |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### RegionBins

| Column | Type | Nullable |
|---|---|---|
| `RegionBinId` | int(10) | NO |
| `RegionBin` | nvarchar(255) | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### Regions

| Column | Type | Nullable |
|---|---|---|
| `RegionId` | char(3) | NO |
| `Region` | nvarchar(255) | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### ResearchOrganizations

| Column | Type | Nullable |
|---|---|---|
| `RosstId` | nvarchar(40) | NO |
| `Organization` | nvarchar(250) | NO |
| `OrganizationTypeId` | int(10) | NO |
| `CreatedDate` | datetime | NO |

### ResearchOrganizations_Addresses

| Column | Type | Nullable |
|---|---|---|
| `RosstId` | nvarchar(40) | NO |
| `City` | nvarchar(150) | NO |
| `CountryIsoCode2` | char(2) | NO |
| `CreatedDate` | datetime | NO |

### ResearchOrganizations_ConsortiumMembership

| Column | Type | Nullable |
|---|---|---|
| `RosstId` | nvarchar(40) | NO |
| `ConsortiumRosstId` | nvarchar(40) | NO |
| `CreatedDate` | datetime | NO |

### ResearchOrganizations_Hierarchies

| Column | Type | Nullable |
|---|---|---|
| `RosstId` | nvarchar(40) | NO |
| `ParentRosstId` | nvarchar(40) | NO |
| `HierarchicalOrder` | int(10) | NO |
| `HierarchyId` | int(10) | NO |
| `UltimateParentOrganizationTypeId` | int(10) | NO |
| `CreatedDate` | datetime | NO |

### ResearchOrganizations_Mapping

| Column | Type | Nullable |
|---|---|---|
| `RosstId` | nvarchar(40) | NO |
| `UgaritId` | int(10) | NO |
| `CreatedDate` | datetime | NO |

### ResearchOrganizations_Type

| Column | Type | Nullable |
|---|---|---|
| `OrganizationTypeId` | int(10) | NO |
| `OrganizationType` | nvarchar(200) | NO |
| `Description` | nvarchar(1000) | NO |
| `CreatedDate` | datetime | NO |

### Role

| Column | Type | Nullable |
|---|---|---|
| `RoleId` | int(10) | NO |
| `Role` | varchar(50) | NO |
| `RoleAbbr` | varchar(20) | NO |
| `IsAdmin` | bit | NO |
| `RowVersion` | timestamp | NO |

### SocialCounts_Source

| Column | Type | Nullable |
|---|---|---|
| `SourceId` | int(10) | NO |
| `Source` | varchar(19) | NO |
| `RowVersion` | timestamp | NO |

### Spaces

| Column | Type | Nullable |
|---|---|---|
| `SpaceId` | smallint(5) | NO |
| `SODSEnvironmentId` | char(4) | NO |
| `Space` | nvarchar(100) | NO |
| `SpaceShortName` | nvarchar(20) | NO |
| `SpaceInstanceName` | nvarchar(100) | NO |
| `SpaceGUID` | uniqueidentifier | NO |
| `TenantGroup` | nvarchar(20) | NO |
| `WebDomain` | nvarchar(128) | NO |
| `WebDomainShort` | nvarchar(128) | YES |
| `RowVersion` | timestamp | NO |

### States

| Column | Type | Nullable |
|---|---|---|
| `StateId` | int(10) | NO |
| `Name` | nvarchar(150) | NO |
| `CountryId` | char(3) | NO |
| `RowVersion` | timestamp | NO |

### SurveyTypes

| Column | Type | Nullable |
|---|---|---|
| `SurveyTypeId` | int(10) | NO |
| `Survey` | nvarchar(128) | NO |

### Taxonomy

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `DomainId` | bigint(19) | NO |
| `FieldId` | bigint(19) | YES |
| `SpecialtyId` | bigint(19) | YES |
| `ParentTaxonomyId` | bigint(19) | YES |
| `DefaultTaxonomyId` | bigint(19) | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### Taxonomy_Domains

| Column | Type | Nullable |
|---|---|---|
| `DomainId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Domain` | nvarchar(50) | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### Taxonomy_Fields

| Column | Type | Nullable |
|---|---|---|
| `FieldId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Field` | nvarchar(150) | NO |
| `RowVersion` | timestamp | NO |

### Taxonomy_Relationships

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `AssociatedTaxonomyId` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Taxonomy_Specialties

| Column | Type | Nullable |
|---|---|---|
| `SpecialtyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Specialty` | nvarchar(150) | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

## [TenantsDataMarts].[Journal]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### Articles

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId.Original` | int(10) | NO |
| `TypeId` | bigint(19) | NO |
| `TaxonomyId` | bigint(19) | NO |
| `ResearchTopicId` | bigint(19) | YES |
| `ResearchTopicId.Original` | int(10) | YES |
| `SuggestedforResearchTopic.InviteDate` | datetime | YES |
| `SuggestedforResearchTopic.DiscardDate` | datetime | YES |
| `SuggestedforResearchTopic.AuthorAcceptDate` | datetime | YES |
| `SuggestedforResearchTopic.AuthorDeclineDate` | datetime | YES |
| `SuggestedforResearchTopic.StatusId` | int(10) | YES |
| `DOI` | nvarchar(50) | YES |
| `Title` | nvarchar(1000) | NO |
| `TitlePlainText` | nvarchar | NO |
| `Abstract` | nvarchar | YES |
| `BodyText` | nvarchar | YES |
| `CoverLetter` | nvarchar | YES |
| `FundingStatement` | nvarchar | YES |
| `JournalVolume` | int(10) | YES |
| `HasSupplementaryMaterials` | bit | NO |
| `SubmissionCountWordsAbstract` | int(10) | NO |
| `SubmissionCountWordsBodyText` | int(10) | NO |
| `SubmissionCountWordsCOI` | int(10) | NO |
| `SubmissionCountFigures` | int(10) | NO |
| `SubmissionCountTables` | int(10) | NO |
| `IsReviewFastForward` | bit | NO |
| `IsDirectCommission` | bit | NO |
| `IsRTIC` | bit | YES |
| `StageId` | int(10) | NO |
| `RequestedRevisionLevelId` | int(10) | YES |
| `IsControversial` | bit | NO |
| `ControversialityReason` | nvarchar(30) | YES |
| `EOfComments` | nvarchar | YES |
| `EOfPOfComments` | nvarchar | YES |
| `JournalTeamComments` | nvarchar | YES |
| `TypeSetterUserId` | int(10) | YES |
| `CreatorUserId` | int(10) | NO |
| `ReviewOperations.Owner.UserId` | int(10) | YES |
| `ReviewOperations.Owner.Email` | nvarchar(128) | YES |
| `ReviewOperations.Owner.FirstName` | nvarchar(40) | YES |
| `ReviewOperations.Owner.LastName` | nvarchar(80) | YES |
| `ResearchIntegrity.Owner.UserId` | int(10) | YES |
| `ResearchIntegrity.Owner.Email` | nvarchar(128) | YES |
| `ResearchIntegrity.Owner.FirstName` | nvarchar(40) | YES |
| `ResearchIntegrity.Owner.LastName` | nvarchar(80) | YES |
| `OpportunityOwner.UserId` | int(10) | YES |
| `CreateDate` | datetime | NO |
| `WSSContentSiteId` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### Articles_AIRA

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `OriginalResourceId` | int(10) | NO |
| `StatusId` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### Articles_AIRAActionType

| Column | Type | Nullable |
|---|---|---|
| `ActionTypeId` | int(10) | NO |
| `ActionTypeCode` | nvarchar(10) | NO |
| `ActionType` | nvarchar(50) | NO |
| `Description` | nvarchar(50) | YES |
| `Version` | int(10) | NO |
| `IsCurrent` | bit | NO |
| `RowVersion` | timestamp | NO |

### Articles_AIRAActions

| Column | Type | Nullable |
|---|---|---|
| `ActionId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ActionTypeId` | int(10) | NO |
| `ArticleId` | bigint(19) | NO |
| `TriggerId` | bigint(19) | NO |
| `ReportId` | bigint(19) | NO |
| `ArticleStageId` | int(10) | YES |
| `IsConditionsValid` | bit | NO |
| `IsEndpointCallSuccessful` | bit | NO |
| `Message` | nvarchar | YES |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### Articles_AIRACategories

| Column | Type | Nullable |
|---|---|---|
| `CategoryId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `CategoryTypeId` | int(10) | NO |
| `ArticleId` | bigint(19) | NO |
| `TriggerId` | bigint(19) | NO |
| `ReportId` | bigint(19) | NO |
| `CategoryStatusId` | int(10) | NO |
| `Version` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### Articles_AIRACategoryStatus

| Column | Type | Nullable |
|---|---|---|
| `CategoryStatusId` | int(10) | NO |
| `CategoryStatus` | nvarchar(30) | NO |
| `Description` | nvarchar(100) | YES |
| `RowVersion` | timestamp | NO |

### Articles_AIRACategoryType

| Column | Type | Nullable |
|---|---|---|
| `CategoryTypeId` | int(10) | NO |
| `CategoryTypeCode` | nvarchar(40) | NO |
| `CategoryType` | nvarchar(40) | NO |
| `Description` | nvarchar(40) | YES |
| `Version` | int(10) | NO |
| `Priority` | int(10) | NO |
| `State` | nvarchar(20) | NO |
| `StateDescription` | nvarchar(40) | YES |
| `RowVersion` | timestamp | NO |

### Articles_AIRAIndicatorGroupStatus

| Column | Type | Nullable |
|---|---|---|
| `IndicatorGroupStatusId` | int(10) | NO |
| `IndicatorGroupStatus` | nvarchar(30) | NO |
| `Description` | nvarchar(150) | YES |
| `DisplayOrder` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### Articles_AIRAIndicatorGroupType

| Column | Type | Nullable |
|---|---|---|
| `IndicatorGroupTypeId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `IndicatorGroupTypeCode` | nvarchar(10) | NO |
| `IndicatorGroupType` | nvarchar(150) | NO |
| `Description` | nvarchar(400) | YES |
| `Version` | int(10) | NO |
| `Priority` | int(10) | NO |
| `IsCurrent` | bit | NO |
| `IsTrusted` | bit | NO |
| `RowVersion` | timestamp | NO |

### Articles_AIRAIndicatorGroups

| Column | Type | Nullable |
|---|---|---|
| `IndicatorGroupId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `IndicatorGroupTypeId` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `TriggerId` | bigint(19) | NO |
| `ReportId` | bigint(19) | NO |
| `CategoryId` | bigint(19) | NO |
| `Version` | int(10) | NO |
| `IndicatorGroupStatusId` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `Message` | nvarchar(150) | YES |
| `DisplayOrder` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### Articles_AIRAIndicatorScenarioType

| Column | Type | Nullable |
|---|---|---|
| `IndicatorScenarioTypeId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `IndicatorScenarioTypeCode` | nvarchar(30) | NO |
| `InternalDefinition` | nvarchar(200) | YES |
| `Description` | nvarchar(150) | YES |
| `FeedbackInstructionMessage` | nvarchar(150) | YES |
| `IsEnabled` | bit | NO |
| `ParentIndicatorScenarioTypeId` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |

### Articles_AIRAIndicatorScenarios

| Column | Type | Nullable |
|---|---|---|
| `IndicatorScenarioId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `IndicatorId` | bigint(19) | NO |
| `IndicatorScenarioTypeId` | bigint(19) | NO |
| `FeedbackMessage` | nvarchar | YES |
| `IsEnabled` | bit | NO |
| `EnableDate` | datetime | NO |
| `EnablerUserId` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Articles_AIRAIndicatorStatus

| Column | Type | Nullable |
|---|---|---|
| `IndicatorStatusId` | int(10) | NO |
| `IndicatorStatus` | nvarchar(30) | NO |
| `Description` | nvarchar(150) | YES |
| `DisplayOrder` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### Articles_AIRAIndicatorType

| Column | Type | Nullable |
|---|---|---|
| `IndicatorTypeId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `IndicatorTypeCode` | nvarchar(100) | NO |
| `IndicatorType` | nvarchar(200) | NO |
| `Description` | nvarchar(1000) | YES |
| `Version` | int(10) | NO |
| `Priority` | int(10) | NO |
| `IsCurrent` | bit | NO |
| `IsTrusted` | bit | NO |
| `RowVersion` | timestamp | NO |

### Articles_AIRAIndicators

| Column | Type | Nullable |
|---|---|---|
| `IndicatorId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `IndicatorTypeId` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `TriggerId` | bigint(19) | NO |
| `ReportId` | bigint(19) | NO |
| `CategoryId` | bigint(19) | NO |
| `IndicatorGroupId` | bigint(19) | NO |
| `Version` | int(10) | NO |
| `IndicatorStatusId` | int(10) | NO |
| `IsProcessed` | bit | NO |
| `IsScenariosEnabled` | bit | NO |
| `CreateDate` | datetime | NO |
| `Message` | nvarchar | YES |
| `Links` | nvarchar | YES |
| `RevertedBackToAIRAInterpretationBy` | int(10) | YES |
| `RevertedBackToAIRAInterpretationDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### Articles_AIRARIProcessState

| Column | Type | Nullable |
|---|---|---|
| `RIProcessStateId` | int(10) | NO |
| `RIProcessState` | nvarchar(40) | NO |
| `Description` | nvarchar(100) | YES |
| `IsVisible` | bit | NO |
| `Priority` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Articles_AIRAReportType

| Column | Type | Nullable |
|---|---|---|
| `ReportTypeId` | int(10) | NO |
| `ReportTypeCode` | nvarchar(20) | NO |
| `ReportType` | nvarchar(20) | NO |
| `Description` | nvarchar(20) | YES |
| `Version` | int(10) | NO |
| `IsCurrent` | bit | NO |
| `RowVersion` | timestamp | NO |

### Articles_AIRAReports

| Column | Type | Nullable |
|---|---|---|
| `ReportId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ReportTypeId` | int(10) | NO |
| `ArticleId` | bigint(19) | NO |
| `TriggerId` | bigint(19) | NO |
| `Version` | int(10) | NO |
| `RIProcessStateId` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### Articles_AIRAServiceLevels

| Column | Type | Nullable |
|---|---|---|
| `AIRAServiceLevelId` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId.Original` | int(10) | NO |
| `Version` | smallint(5) | NO |
| `IsLatest` | bit | NO |
| `GlobalScore` | decimal(5) | NO |
| `ServiceLevel` | tinyint(3) | NO |
| `RowVersion` | timestamp | NO |

### Articles_AIRAStatus

| Column | Type | Nullable |
|---|---|---|
| `StatusId` | int(10) | NO |
| `Status` | nvarchar(20) | NO |
| `Description` | nvarchar(150) | YES |
| `RowVersion` | timestamp | NO |

### Articles_AIRATriggerStatus

| Column | Type | Nullable |
|---|---|---|
| `TriggerStatusId` | int(10) | NO |
| `TriggerStatus` | nvarchar(20) | NO |
| `Description` | nvarchar(150) | YES |
| `RowVersion` | timestamp | NO |

### Articles_AIRATriggerType

| Column | Type | Nullable |
|---|---|---|
| `TriggerTypeId` | int(10) | NO |
| `TriggerTypeCode` | nvarchar(100) | NO |
| `TriggerType` | nvarchar(200) | NO |
| `Description` | nvarchar(200) | YES |
| `RowVersion` | timestamp | NO |

### Articles_AIRATriggers

| Column | Type | Nullable |
|---|---|---|
| `TriggerId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `TriggerTypeId` | int(10) | NO |
| `ArticleId` | bigint(19) | NO |
| `TriggerStatusId` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### Articles_Activities

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(100) | NO |
| `ArticleId.Original` | int(10) | NO |
| `CountViews` | int(10) | NO |
| `CountDownloads` | int(10) | NO |
| `CountCitations` | int(10) | NO |
| `CountArticleCitations` | int(10) | NO |
| `CountFrontiersViews` | int(10) | YES |
| `CountFrontiersDownloads` | int(10) | YES |
| `CountPMCViews` | int(10) | YES |
| `CountPMCDownloads` | int(10) | YES |
| `RowVersion` | timestamp | NO |
| `Checksum` | bigint(19) | NO |

### Articles_Affiliations_Legacy

| Column | Type | Nullable |
|---|---|---|
| `AffiliationId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `Organization` | nvarchar(800) | YES |
| `City` | nvarchar(200) | YES |
| `State` | nvarchar(100) | YES |
| `CountryId` | char(3) | YES |
| `RowVersion` | timestamp | NO |

### Articles_Authors

| Column | Type | Nullable |
|---|---|---|
| `AuthorId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId` | bigint(19) | NO |
| `ArticleId.Original` | int(10) | YES |
| `AuthorOrder` | int(10) | NO |
| `AuthorSource` | char(1) | NO |
| `ReviewAuthorId` | bigint(19) | YES |
| `ProductionAuthorId` | bigint(19) | YES |
| `POFAuthorId` | bigint(19) | YES |
| `TitleId` | int(10) | NO |
| `Email` | nvarchar(100) | YES |
| `FirstName` | nvarchar(150) | YES |
| `MiddleName` | nvarchar(100) | YES |
| `LastName` | nvarchar(300) | NO |
| `Name` | nvarchar(600) | NO |
| `Suffix` | nvarchar(50) | YES |
| `RoleId` | int(10) | NO |
| `JournalRoleId` | varchar(10) | YES |
| `IsCorrespondingAuthor` | bit | NO |
| `IsSubmittingAuthor` | bit | NO |
| `AuthorUserId` | int(10) | YES |
| `PersonId` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |

### Articles_Authors.Concatenated

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(100) | NO |
| `ArticleId.Original` | int(10) | YES |
| `Authors` | nvarchar | YES |
| `AuthorsEmails` | nvarchar | YES |
| `AuthorsAffiliations` | nvarchar | YES |
| `CorrespondingAuthors` | nvarchar | YES |
| `CorrespondingAuthorsEmails` | nvarchar | YES |
| `CorrespondingAuthorsAffiliations` | nvarchar | YES |
| `RowVersion` | timestamp | NO |

### Articles_Authors.Production

| Column | Type | Nullable |
|---|---|---|
| `ProductionAuthorId` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId.Original` | int(10) | NO |
| `ReviewAuthorId` | bigint(19) | YES |
| `AuthorOrder` | int(10) | NO |
| `IsCorrespondingAuthor` | bit | NO |
| `FirstName` | nvarchar(300) | YES |
| `MiddleName` | nvarchar(100) | YES |
| `LastName` | nvarchar(300) | YES |
| `Name` | nvarchar(400) | YES |
| `Email` | nvarchar(200) | YES |
| `IsEmailPersonalDomain` | bit | NO |
| `UserId` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### Articles_Authors.Review

| Column | Type | Nullable |
|---|---|---|
| `ReviewAuthorId` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId.Original` | int(10) | NO |
| `ReviewAuthorId.Original` | int(10) | NO |
| `AuthorOrder` | int(10) | YES |
| `IsCorrespondingAuthor` | bit | NO |
| `FirstName` | nvarchar(150) | YES |
| `MiddleName` | nvarchar(50) | YES |
| `LastName` | nvarchar(150) | YES |
| `Name` | nvarchar(400) | YES |
| `Email` | nvarchar(150) | YES |
| `IsEmailPersonalDomain` | bit | NO |
| `UserId` | int(10) | YES |
| `PersonId` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |

### Articles_AuthorsAffiliations

| Column | Type | Nullable |
|---|---|---|
| `AuthorAffiliationId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `AuthorId` | bigint(19) | NO |
| `AffiliationId` | bigint(19) | NO |
| `AuthorAffiliationOrder` | int(10) | NO |
| `AffiliationSource` | varchar(1) | NO |
| `ReviewAffiliationId` | int(10) | NO |
| `ProductionAffiliationId` | int(10) | NO |
| `POFAffiliationId` | int(10) | NO |
| `OriginalOrder` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Articles_AuthorsOrganizations

| Column | Type | Nullable |
|---|---|---|
| `AuthorId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `OrganizationId` | int(10) | NO |
| `RosstId` | nvarchar(40) | YES |
| `OrganizationOrder` | int(10) | NO |
| `OrganizationSourceId` | char(1) | NO |
| `RowVersion` | timestamp | NO |

### Articles_AuthorsOrganizations.Production

| Column | Type | Nullable |
|---|---|---|
| `AuthorId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `OrganizationId` | int(10) | NO |
| `RosstId` | nvarchar(40) | YES |
| `OrganizationOrder` | int(10) | NO |
| `OrganizationSourceId` | char(1) | NO |
| `RowVersion` | timestamp | NO |

### Articles_AuthorsOrganizations.Review

| Column | Type | Nullable |
|---|---|---|
| `AuthorId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `OrganizationId` | int(10) | NO |
| `RosstId` | nvarchar(40) | YES |
| `OrganizationOrder` | int(10) | NO |
| `OrganizationSourceId` | char(1) | NO |
| `RowVersion` | timestamp | NO |

### Articles_AuthorsSuggestedReviewer.SuggestionType

| Column | Type | Nullable |
|---|---|---|
| `SuggestionTypeId` | int(10) | NO |
| `SuggestionTypeCode` | nchar(1) | NO |
| `SuggestionType` | nvarchar(100) | YES |

### Articles_AuthorsSuggestedReviewers

| Column | Type | Nullable |
|---|---|---|
| `SuggestedReviewerId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId` | bigint(19) | NO |
| `AuthorUserId` | int(10) | NO |
| `ReviewerUserId` | int(10) | YES |
| `Email` | nvarchar(150) | YES |
| `FirstName` | nvarchar(150) | YES |
| `MiddleName` | nvarchar(50) | YES |
| `LastName` | nvarchar(150) | YES |
| `SuggestionTypeId` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `CreatorUserId` | int(10) | NO |
| `ModifierUserId` | int(10) | YES |
| `IsValidated` | bit | YES |
| `RowVersion` | timestamp | NO |

### Articles_Citations

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId.Original` | int(10) | NO |
| `ImpactActionId` | int(10) | NO |
| `ImpactAggregationId` | int(10) | NO |
| `Date` | date | NO |
| `Total.Value` | int(10) | NO |
| `Articles.Value` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Articles_DiscoverFeedback

| Column | Type | Nullable |
|---|---|---|
| `ArticleFeedbackId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | YES |
| `UserId` | int(10) | YES |
| `IsDeleted` | bit | NO |
| `ArticleId` | bigint(19) | YES |
| `ArticleFeedbackTypeId` | int(10) | YES |
| `CreateDate` | datetime | YES |
| `ModifyDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### Articles_DiscoverFeedbackType

| Column | Type | Nullable |
|---|---|---|
| `ArticleFeedbackTypeId` | int(10) | NO |
| `ArticleFeedbackType` | nvarchar(120) | YES |
| `RowVersion` | timestamp | NO |

### Articles_Funder

| Column | Type | Nullable |
|---|---|---|
| `FunderId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Funder` | nvarchar(400) | NO |
| `OriginalId` | nvarchar(500) | YES |
| `DOI` | nvarchar(500) | YES |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### Articles_Funding

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `FunderId` | bigint(19) | NO |
| `Awards` | nvarchar(4000) | YES |
| `APCCoverage` | bit | NO |
| `RowVersion` | timestamp | NO |

### Articles_Inaugurals

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `UserId` | int(10) | NO |
| `RoleId` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Articles_JournalTransfers

| Column | Type | Nullable |
|---|---|---|
| `TransferId` | uniqueidentifier | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId` | bigint(19) | NO |
| `ArticleId.Original` | int(10) | YES |
| `Status` | varchar(100) | NO |
| `LastEvent` | varchar(100) | NO |
| `CreateDate` | date | NO |
| `ModifyDate` | datetime | YES |
| `InitialArticleStageId` | int(10) | YES |
| `InitiatorUserId` | int(10) | NO |
| `InitiatorRoleId` | int(10) | NO |
| `InitiatorJournalRoleId` | varchar(10) | YES |
| `IsValidated` | bit | NO |
| `ValidatorUserId` | int(10) | YES |
| `ValidatorRoleId` | int(10) | YES |
| `ValidatorJournalRoleId` | varchar(10) | YES |
| `IsConfirmed` | bit | NO |
| `ConfirmationExpirationDate` | datetime | YES |
| `IsAuthorConfirmationBypassed` | bit | NO |
| `ConfirmerUserId` | int(10) | YES |
| `ConfirmerRoleId` | int(10) | YES |
| `ConfirmerJournalRoleId` | varchar(10) | YES |
| `ConfirmationCancellerUserId` | int(10) | YES |
| `ConfirmationCancellerRoleId` | int(10) | YES |
| `ConfirmationCancellerJournalRoleId` | varchar(10) | YES |
| `ConfirmationCancellationReason` | varchar | YES |
| `SourceTaxonomyId` | bigint(19) | YES |
| `SourceResearchTopicId` | bigint(19) | YES |
| `DestinationTaxonomyId` | bigint(19) | YES |
| `DestinationResearchTopicId` | bigint(19) | YES |
| `TransferReason` | varchar | NO |
| `TransferDeclinationReason` | varchar | YES |
| `RowVersion` | timestamp | NO |

### Articles_Keywords

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `SortOrder` | tinyint(3) | NO |
| `KeywordId` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Articles_Keywords.Concatenated

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(100) | NO |
| `ArticleId.Original` | int(10) | YES |
| `Keywords` | nvarchar | NO |
| `RowVersion` | timestamp | NO |

### Articles_RelatedArticle

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `RelatedArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `RelationshipTypeId` | tinyint(3) | NO |
| `RowVersion` | timestamp | NO |

### Articles_RelatedArticleType

| Column | Type | Nullable |
|---|---|---|
| `RelationshipTypeId` | tinyint(3) | NO |
| `Relationship` | nvarchar(100) | NO |
| `RowVersion` | timestamp | NO |

### Articles_RequestedRevisionLevel

| Column | Type | Nullable |
|---|---|---|
| `RequestedRevisionLevelId` | int(10) | NO |
| `RequestedRevisionLevel` | nvarchar(20) | YES |
| `RowVersion` | timestamp | NO |

### Articles_Review.Event

| Column | Type | Nullable |
|---|---|---|
| `ReviewEventId` | int(10) | NO |
| `Event` | nvarchar(150) | NO |
| `Description` | nvarchar(1500) | NO |
| `RelatedTable` | nvarchar(150) | NO |
| `Source` | nvarchar(300) | NO |

### Articles_Review.Events

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ReviewEventId` | int(10) | NO |
| `EventDatetime` | datetime | NO |
| `EventDate` | date | NO |
| `CreatorUserId` | int(10) | NO |
| `CreatorRoleId` | int(10) | YES |
| `RecipientUserId` | int(10) | YES |
| `RecipientRoleId` | int(10) | YES |
| `ExtensionDays` | smallint(5) | YES |
| `WorkflowId` | int(10) | YES |
| `WorkflowStatusId` | int(10) | YES |
| `Comments` | nvarchar(255) | YES |
| `RowVersion` | timestamp | NO |

### Articles_ReviewActionReason

| Column | Type | Nullable |
|---|---|---|
| `ReviewActionReasonId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ReviewActionReasonId.Original` | int(10) | NO |
| `ReviewActionReason` | nvarchar(300) | NO |
| `ReviewActionReasonLabel` | nvarchar(50) | NO |
| `ReviewActionReasonType` | nvarchar(30) | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewActionReasons

| Column | Type | Nullable |
|---|---|---|
| `ReviewBoardInvitationId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `CreateDate` | datetime | YES |
| `ReviewActionReasonId` | bigint(19) | NO |
| `Comments` | nvarchar | YES |
| `RowVersion` | timestamp | NO |

### Articles_ReviewActionSubReason

| Column | Type | Nullable |
|---|---|---|
| `ReviewActionSubReasonId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ReviewActionSubReasonId.Original` | int(10) | NO |
| `ReviewActionSubReason` | nvarchar | NO |
| `ReviewActionSubReasonLabel` | nvarchar(200) | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewArticleRejectionReasons

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ReviewActionReasonId` | bigint(19) | NO |
| `ReviewActionSubReasonId` | bigint(19) | YES |
| `Comments` | nvarchar | YES |
| `RejecterUserId` | int(10) | NO |
| `RejecterRoleId` | int(10) | NO |
| `IsDeleted` | bit | NO |
| `CreateDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardConflictOfInterests

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `UserId` | int(10) | NO |
| `ConflictOfInterestsQuestionId` | int(10) | NO |
| `Answer` | nchar(5) | YES |
| `CreateDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardConflictOfInterestsQuestion

| Column | Type | Nullable |
|---|---|---|
| `ConflictOfInterestsQuestionId` | int(10) | NO |
| `ConflictOfInterestsQuestion` | nvarchar | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardDiscoverVolunteers

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `ReviewBoardMemberId` | bigint(19) | YES |
| `SpaceId` | smallint(5) | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `CreatorUserId` | int(10) | YES |
| `ModifierUserId` | int(10) | YES |
| `UserId` | int(10) | NO |
| `IsAssigned` | bit | YES |
| `AssignmentDecision` | nvarchar(200) | YES |
| `IsDeleted` | bit | NO |
| `Source` | nvarchar(20) | NO |
| `ReferrerSourceId` | smallint(5) | YES |
| `Campaign` | nvarchar(200) | YES |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardDiscoverVolunteers.ExclusionReason

| Column | Type | Nullable |
|---|---|---|
| `ReviewBoardVolunteerExclusionReasonId` | int(10) | NO |
| `ExclusionReason` | nvarchar(250) | YES |
| `CreateDate` | datetime | NO |
| `CreatorUserId` | int(10) | YES |
| `ModifyDate` | datetime | YES |
| `ModifierUserId` | int(10) | YES |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardDiscoverVolunteers.Exclusions

| Column | Type | Nullable |
|---|---|---|
| `ReviewBoardVolunteerExclusionId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId` | bigint(19) | NO |
| `UserId` | int(10) | YES |
| `ReviewBoardMemberId` | bigint(19) | YES |
| `StageId` | int(10) | NO |
| `ReviewBoardVolunteerExclusionReasonId` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `CreatorUserId` | int(10) | YES |
| `ModifyDate` | datetime | YES |
| `ModifierUserId` | int(10) | YES |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardDiscoverVolunteers.ReferrerSource

| Column | Type | Nullable |
|---|---|---|
| `ReferrerSourceId` | smallint(5) | NO |
| `ReferrerSource` | nvarchar(200) | YES |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardInvitationAlgorithmType

| Column | Type | Nullable |
|---|---|---|
| `AlgorithmTypeId` | int(10) | NO |
| `AlgorithmType` | nvarchar(50) | NO |

### Articles_ReviewBoardInvitationAudienceGroup

| Column | Type | Nullable |
|---|---|---|
| `AudienceGroupId` | int(10) | NO |
| `AudienceGroup` | nvarchar(50) | NO |

### Articles_ReviewBoardInvitationMethod

| Column | Type | Nullable |
|---|---|---|
| `ReviewBoardInvitationMethodId` | int(10) | NO |
| `ReviewBoardInvitationMethod` | nvarchar(50) | NO |
| `Description` | nvarchar | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardInvitationStatus

| Column | Type | Nullable |
|---|---|---|
| `ReviewBoardInvitationStatusId` | int(10) | NO |
| `ReviewBoardInvitationStatus` | nvarchar(40) | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardInvitations

| Column | Type | Nullable |
|---|---|---|
| `ReviewBoardInvitationId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId` | bigint(19) | NO |
| `ArticleId.Original` | int(10) | YES |
| `PersonId.Original` | bigint(19) | YES |
| `PersonId` | bigint(19) | YES |
| `UserId` | int(10) | YES |
| `Email` | nvarchar(150) | NO |
| `FirstName` | nvarchar(150) | YES |
| `MiddleName` | nvarchar(50) | YES |
| `LastName` | nvarchar(150) | YES |
| `Name` | nvarchar(400) | YES |
| `RoleId` | int(10) | YES |
| `JournalRoleId` | varchar(10) | YES |
| `OriginalRoleId` | int(10) | YES |
| `WorkflowId` | int(10) | YES |
| `WorkflowEmailId` | bigint(19) | YES |
| `WorkflowMessageTypeId` | int(10) | YES |
| `WorkflowPipelineStageId` | int(10) | YES |
| `ScheduledInvitationId` | bigint(19) | YES |
| `InvitationWorkflowId` | int(10) | YES |
| `InvitationWorkflowEmailId` | bigint(19) | YES |
| `InvitationStatusId` | int(10) | YES |
| `IsAutomaticInvitation` | bit | NO |
| `InvitationMethodId` | int(10) | YES |
| `InvitationBatch` | int(10) | YES |
| `InvitationAlgorithmTypeId` | int(10) | YES |
| `InvitationAudienceGroupId` | int(10) | YES |
| `InvitationRelevancyScore` | float(53) | YES |
| `ManuscriptContextPromptVersion` | nvarchar(50) | YES |
| `ManuscriptContextModel` | nvarchar(100) | YES |
| `PerfectEmailPromptVersion` | nvarchar(50) | YES |
| `PerfectEmailModel` | nvarchar(100) | YES |
| `ExplainabilityPromptVersion` | nvarchar(50) | YES |
| `ExplainabilityModel` | nvarchar(100) | YES |
| `IsMatch` | bit | YES |
| `InvitationActivationNumber` | uniqueidentifier | YES |
| `InvitationRank` | int(10) | YES |
| `IsClosed` | bit | NO |
| `CreatorUserId` | int(10) | NO |
| `CreatorRoleId` | int(10) | YES |
| `CreatorJournalRoleId` | varchar(10) | YES |
| `CreatorOriginalRoleId` | int(10) | YES |
| `InviteDate` | datetime | NO |
| `InvitationStatusDate` | datetime | YES |
| `AuthorReviewerSuggestionTypeId` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardInvitationsHistory

| Column | Type | Nullable |
|---|---|---|
| `ReviewBoardInvitationsHistoryId` | bigint(19) | NO |
| `ReviewBoardInvitationId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId` | bigint(19) | NO |
| `UserId` | int(10) | YES |
| `Email` | nvarchar(150) | NO |
| `FirstName` | nvarchar(150) | YES |
| `MiddleName` | nvarchar(50) | YES |
| `LastName` | nvarchar(150) | YES |
| `Name` | nvarchar(400) | YES |
| `RoleId` | int(10) | YES |
| `JournalRoleId` | varchar(10) | YES |
| `OriginalRoleId` | int(10) | YES |
| `WorkflowId` | int(10) | YES |
| `WorkflowEmailId` | bigint(19) | YES |
| `WorkflowMessageTypeId` | int(10) | YES |
| `WorkflowPipelineStageId` | int(10) | YES |
| `InvitationStatusId` | int(10) | YES |
| `InvitationActivationNumber` | uniqueidentifier | YES |
| `CreatorUserId` | int(10) | NO |
| `CreatorRoleId` | int(10) | YES |
| `CreatorJournalRoleId` | varchar(10) | YES |
| `CreatorOriginalRoleId` | int(10) | YES |
| `InviteDate` | datetime | NO |
| `InvitationStatusDate` | datetime | YES |
| `AuthorReviewerSuggestionTypeId` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardInvitationsScheduled

| Column | Type | Nullable |
|---|---|---|
| `ScheduledInvitationId` | bigint(19) | NO |
| `ScheduledInvitationId.Original` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `ArticleId.Original` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `BatchSequence` | int(10) | NO |
| `BatchExpectedSize` | int(10) | NO |
| `ProcessDefinition` | nvarchar(100) | NO |
| `StatusId` | int(10) | NO |
| `MethodId` | int(10) | NO |
| `WorkflowId` | int(10) | NO |
| `ScheduledDate` | datetime | YES |
| `SenderUserId` | int(10) | YES |
| `DiscarderUserId` | int(10) | YES |
| `DiscardReasonId` | int(10) | YES |
| `Invitee.UserId` | int(10) | YES |
| `Invitee.Name` | nvarchar(250) | YES |
| `Invitee.Email` | nvarchar(200) | YES |
| `Invitee.RoleId` | int(10) | YES |
| `Invitee.RelevancyScore` | float(53) | YES |
| `Invitee.AudienceRank` | int(10) | YES |
| `Invitee.AudienceTypeId` | int(10) | YES |
| `Invitee.DeclinationReasonId` | int(10) | YES |
| `Invitee.DeclinationReasonText` | nvarchar(255) | YES |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardInvitationsScheduled.AudienceType

| Column | Type | Nullable |
|---|---|---|
| `AudienceTypeId` | int(10) | NO |
| `AudienceType` | nvarchar(50) | NO |
| `Description` | nvarchar(100) | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardInvitationsScheduled.DeclinationReason

| Column | Type | Nullable |
|---|---|---|
| `DeclinationReasonId` | int(10) | NO |
| `DeclinationReason` | nvarchar(50) | NO |
| `Description` | nvarchar(100) | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardInvitationsScheduled.DiscardReason

| Column | Type | Nullable |
|---|---|---|
| `DiscardReasonId` | int(10) | NO |
| `DiscardReason` | nvarchar(50) | NO |
| `Description` | nvarchar(100) | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardInvitationsScheduled.Method

| Column | Type | Nullable |
|---|---|---|
| `MethodId` | int(10) | NO |
| `Method` | nvarchar(50) | NO |
| `Description` | nvarchar(100) | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardInvitationsScheduled.Status

| Column | Type | Nullable |
|---|---|---|
| `StatusId` | int(10) | NO |
| `Status` | nvarchar(50) | NO |
| `Description` | nvarchar(100) | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardMembers

| Column | Type | Nullable |
|---|---|---|
| `ReviewBoardMemberId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId` | bigint(19) | NO |
| `ArticleId.Original` | int(10) | YES |
| `UserId` | int(10) | NO |
| `RoleId` | int(10) | NO |
| `JournalRoleId` | varchar(10) | YES |
| `OriginalRoleId` | int(10) | NO |
| `ReviewBoardStatusId` | tinyint(3) | YES |
| `ReviewBoardInvitationId` | bigint(19) | YES |
| `InviterUserId` | int(10) | YES |
| `InviteDate` | datetime | YES |
| `JoinDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardStatus

| Column | Type | Nullable |
|---|---|---|
| `ReviewBoardStatusId` | tinyint(3) | NO |
| `ReviewBoardStatus` | varchar(25) | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewBoardWithdrawals

| Column | Type | Nullable |
|---|---|---|
| `WithdrawlId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId` | bigint(19) | YES |
| `StageId` | int(10) | YES |
| `UserId` | int(10) | YES |
| `LoggedInUserId` | int(10) | YES |
| `RoleId` | int(10) | YES |
| `ReasonId` | bigint(19) | YES |
| `Comments` | varchar | YES |
| `CreateDate` | datetime | YES |
| `ModifyDate` | datetime | YES |
| `IsDeleted` | bit | YES |
| `RowVersion` | timestamp | NO |

### Articles_ReviewIndependentReports

| Column | Type | Nullable |
|---|---|---|
| `ReviewBoardMemberId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId` | bigint(19) | NO |
| `ArticleId.Original` | int(10) | YES |
| `WordCount` | int(10) | NO |
| `WordCountThreshold` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewPlagiarismCheck

| Column | Type | Nullable |
|---|---|---|
| `PlagiarismCheckId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId` | bigint(19) | NO |
| `IThenticateId` | int(10) | YES |
| `Status` | varchar(15) | YES |
| `SimilarityIndex` | int(10) | YES |
| `ReportURL` | varchar(100) | YES |
| `CreateDate` | datetime | YES |
| `ModifyDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### Articles_ReviewReportAnswerType

| Column | Type | Nullable |
|---|---|---|
| `AnswerTypeId` | int(10) | NO |
| `AnswerType` | nvarchar(40) | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewReportAnswers

| Column | Type | Nullable |
|---|---|---|
| `AnswerId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ReviewReportId` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `ReviewBoardMemberId` | bigint(19) | NO |
| `ArticleStageId` | int(10) | YES |
| `QuestionId` | bigint(19) | NO |
| `SubQuestionId` | bigint(19) | YES |
| `AnswerTypeId` | int(10) | NO |
| `Answer` | nvarchar | YES |
| `ModifyDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewReportDiscussions

| Column | Type | Nullable |
|---|---|---|
| `DiscussionId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ReviewReportId` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `UserId` | int(10) | NO |
| `RoleId` | int(10) | NO |
| `JournalRoleId` | varchar(10) | YES |
| `OriginalRoleId` | int(10) | NO |
| `ReviewBoardMemberId` | bigint(19) | NO |
| `ArticleStageId` | int(10) | YES |
| `QuestionId` | bigint(19) | NO |
| `Discussion` | nvarchar | NO |
| `ParentDiscussionId` | bigint(19) | YES |
| `Level` | int(10) | YES |
| `IsDraft` | bit | NO |
| `DraftComment` | nvarchar | YES |
| `SubmitDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewReportQuestions

| Column | Type | Nullable |
|---|---|---|
| `QuestionId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleTypeId` | bigint(19) | NO |
| `Area` | nvarchar(20) | YES |
| `HeaderId` | int(10) | NO |
| `Header` | nvarchar(50) | YES |
| `HeaderOrder` | int(10) | YES |
| `SubHeaderId` | int(10) | YES |
| `SubHeader` | nvarchar(50) | YES |
| `SubHeaderOrder` | int(10) | YES |
| `Question` | nvarchar(2000) | YES |
| `QuestionOrder` | int(10) | NO |
| `StartDate` | datetime | YES |
| `EndDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewReportRatings

| Column | Type | Nullable |
|---|---|---|
| `ReviewReportRatingId` | uniqueidentifier | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId` | bigint(19) | NO |
| `ArticleId.Original` | int(10) | NO |
| `ReviewerUserId` | int(10) | NO |
| `ReviewBoardMemberId` | bigint(19) | YES |
| `Rating` | int(10) | NO |
| `RatingDate` | datetime | NO |
| `EvaluatorUserId` | int(10) | NO |
| `EvaluatorRoleId` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewReportSubQuestions

| Column | Type | Nullable |
|---|---|---|
| `SubQuestionId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `QuestionId` | bigint(19) | NO |
| `AnswerTypeId` | int(10) | NO |
| `SubQuestion` | varchar | NO |
| `SubQuestionOrder` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Articles_ReviewReports

| Column | Type | Nullable |
|---|---|---|
| `ReviewReportId` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId.Original` | int(10) | NO |
| `ReviewBoardMemberId` | bigint(19) | NO |
| `ArticleStageId` | int(10) | NO |
| `StageStatusId` | int(10) | YES |
| `StartDate` | datetime | YES |
| `EndDate` | datetime | YES |
| `Rating.Average` | decimal(5) | YES |
| `CreatorUserId` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### Articles_Stage

| Column | Type | Nullable |
|---|---|---|
| `StageId` | int(10) | NO |
| `Sequence` | int(10) | NO |
| `Stage` | nvarchar(100) | NO |
| `StageCategoryId` | int(10) | YES |
| `StageCategory` | nvarchar(30) | YES |
| `IsSubmitted` | bit | NO |
| `IsDeleted` | bit | NO |
| `IsRejected` | bit | NO |
| `IsAccepted` | bit | NO |
| `IsPublished` | bit | NO |
| `RowVersion` | timestamp | NO |

### Articles_StageDates.Pivot

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(100) | NO |
| `ArticleId.Original` | int(10) | YES |
| `CurrentStage` | datetime | YES |
| `InPreparation` | datetime | YES |
| `Submitted` | datetime | YES |
| `InitialValidation` | datetime | YES |
| `JournalTransferCompleted` | datetime | YES |
| `ReceivedByJournal` | datetime | YES |
| `EditorialAssignment` | datetime | YES |
| `InReview` | datetime | YES |
| `InIndependentReview` | datetime | YES |
| `InInteractiveReview` | datetime | YES |
| `ReviewFinalized` | datetime | YES |
| `RejectionRecommended` | datetime | YES |
| `Rejected` | datetime | YES |
| `FinalValidation` | datetime | YES |
| `RecommendationForRejectionRevoked` | datetime | YES |
| `Accepted` | datetime | YES |
| `InProduction` | datetime | YES |
| `AuthorProof` | datetime | YES |
| `AuthorProofApproved` | datetime | YES |
| `PublisherProof` | datetime | YES |
| `PublisherProofApproved` | datetime | YES |
| `Published` | datetime | YES |
| `Deposited` | datetime | YES |
| `Deleted` | datetime | YES |
| `RowVersion` | timestamp | NO |
| `Checksum` | bigint(19) | NO |

### Articles_StageStatus

| Column | Type | Nullable |
|---|---|---|
| `StageStatusId` | int(10) | NO |
| `StageStatus` | nvarchar(20) | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### Articles_Stages

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId.Original` | int(10) | NO |
| `StageId` | int(10) | NO |
| `StageDate` | datetime | NO |
| `StageDateTime` | datetime | NO |
| `ModifierUserId` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### Articles_StagesHistory

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleStagesHistoryId` | bigint(19) | NO |
| `StageId` | int(10) | NO |
| `StageDate` | datetime | NO |
| `StageDateTime` | datetime | NO |
| `ModifierUserId` | int(10) | YES |
| `IsCurrent` | bit | NO |
| `RowVersion` | timestamp | NO |

### Articles_SubmissionHistory

| Column | Type | Nullable |
|---|---|---|
| `SubmissionHistoryId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId` | bigint(19) | NO |
| `ArticleId.Original` | int(10) | YES |
| `Version` | int(10) | NO |
| `SubmitDate` | datetime | NO |
| `SubmittingUserId` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Articles_SubmissionStatementAnswers

| Column | Type | Nullable |
|---|---|---|
| `SubmissionStatementId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `QuestionId` | nvarchar(40) | NO |
| `QuestionCode` | nvarchar(20) | NO |
| `QuestionVersion` | int(10) | NO |
| `Answer` | nvarchar | YES |
| `RowVersion` | timestamp | NO |

### Articles_SubmissionStatementQuestion

| Column | Type | Nullable |
|---|---|---|
| `QuestionId` | nvarchar(40) | NO |
| `SpaceId` | smallint(5) | NO |
| `QuestionCode` | nvarchar(20) | NO |
| `QuestionVersion` | int(10) | NO |
| `Question` | nvarchar | YES |
| `RowVersion` | timestamp | NO |

### Articles_SubmissionStatements

| Column | Type | Nullable |
|---|---|---|
| `SubmissionStatementId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId` | bigint(19) | NO |
| `ArticleId.Original` | int(10) | YES |
| `StatementCode` | nvarchar(20) | NO |
| `StatementVersion` | int(10) | NO |
| `Statement` | nvarchar | YES |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### Articles_Surveys.NetPromoterScore

| Column | Type | Nullable |
|---|---|---|
| `SurveyResponseId` | int(10) | NO |
| `SourceResponseId` | nvarchar(100) | NO |
| `ArticleId` | bigint(19) | NO |
| `TaxonomyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `StartDate` | datetime | NO |
| `EndDate` | datetime | YES |
| `UserId` | int(10) | NO |
| `ParticipantRoleId` | int(10) | YES |
| `CountryId` | char(3) | YES |
| `NetPromoterScore` | int(10) | YES |
| `FinalDecision` | nvarchar(50) | YES |
| `SurveyTypeId` | int(10) | NO |
| `RowVersion` | timestamp | NO |
| `Checksum` | bigint(19) | NO |

### Articles_Translations

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `LanguageId` | nchar(2) | NO |
| `LanguagePublicationDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### Articles_Type

| Column | Type | Nullable |
|---|---|---|
| `TypeId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Type` | nvarchar(50) | NO |
| `TypeCategory` | nvarchar(10) | YES |
| `ArticleTypeId.Original` | int(10) | NO |
| `ArticleSequenceNumber.Original` | int(10) | NO |
| `Description` | nvarchar | YES |
| `SortOrder` | int(10) | NO |
| `IsActive` | bit | NO |
| `IsPayingArticleType` | bit | NO |
| `ArticleCategoryId` | int(10) | NO |
| `ArticleCategory` | nvarchar(15) | NO |
| `RequiredIndependentReviewReportsCount` | int(10) | YES |
| `RequiredReviewersCount` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### Articles_ViewsAndDownloads

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId.Original` | int(10) | NO |
| `ImpactActionId` | int(10) | NO |
| `ImpactAggregationId` | int(10) | NO |
| `ProviderId` | int(10) | NO |
| `Date` | date | NO |
| `Human.Value` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### EBooks

| Column | Type | Nullable |
|---|---|---|
| `EBookId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `EBookId.Original` | int(10) | NO |
| `Title` | nvarchar(400) | NO |
| `PublishYear` | int(10) | YES |
| `StatusId` | int(10) | YES |
| `ResearchTopicId` | bigint(19) | YES |
| `ResearchTopicId.Original` | int(10) | YES |
| `Edition` | int(10) | YES |
| `IsLatestEdition` | bit | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### EBooks_Status

| Column | Type | Nullable |
|---|---|---|
| `StatusId` | int(10) | NO |
| `Status` | nvarchar(20) | NO |
| `RowVersion` | timestamp | NO |

### EditorialBoard.Activities

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(100) | NO |
| `TaxonomyId` | bigint(19) | NO |
| `CountArticleAssignments` | int(10) | NO |
| `CountArticleAssignmentsEditing` | int(10) | NO |
| `CountArticleAssignmentsReview` | int(10) | NO |
| `CountJournalReviewEditorsInvited` | int(10) | NO |
| `CountJournalReviewEditorsAppointed` | int(10) | NO |
| `CountJournalReviewEditorsAccepted` | int(10) | NO |
| `CountJournalReviewEditorsAssigned` | int(10) | NO |
| `CountArticleReviewersInvited` | int(10) | NO |
| `CountArticleReviewersAppointed` | int(10) | NO |
| `CountArticleReviewersAccepted` | int(10) | NO |
| `CountArticleReviewersAssigned` | int(10) | NO |
| `CountResearchTopics` | int(10) | NO |
| `RowVersion` | timestamp | NO |
| `Checksum` | bigint(19) | NO |

### EditorialBoard.AlgorithmSource

| Column | Type | Nullable |
|---|---|---|
| `AlgorithmSourceId` | int(10) | NO |
| `AlgorithmSourceType` | varchar(200) | NO |
| `AlgorithmSourceDescription` | varchar(200) | YES |
| `RowVersion` | timestamp | NO |

### EditorialBoard.Appointments

| Column | Type | Nullable |
|---|---|---|
| `AppointmentId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `InvitationId` | bigint(19) | YES |
| `UserId` | int(10) | NO |
| `TaxonomyId` | bigint(19) | NO |
| `RoleId` | int(10) | NO |
| `JournalRoleId` | varchar(10) | NO |
| `CreatorUserId` | int(10) | YES |
| `CreateDate` | datetime | YES |
| `ModifierUserId` | int(10) | YES |
| `ModifyDate` | datetime | YES |
| `OnboardingStatusId` | int(10) | YES |
| `IsOnboardingRunning` | bit | NO |
| `StartDate` | datetime | YES |
| `EndDate` | datetime | YES |
| `EndReasonId` | int(10) | YES |
| `RemoveReasonId` | int(10) | YES |
| `RemoverUserId` | int(10) | YES |
| `RemoveCreateDate` | datetime | YES |
| `IsActive` | bit | NO |
| `OnboardingReminderDate.Last` | datetime | YES |
| `OnboardingReminderDate.Next` | datetime | YES |
| `OnboardingReminders.Next.Count` | int(10) | YES |
| `OnboardingReminders.Total.Count` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### EditorialBoard.InvitationReviewDecisionType

| Column | Type | Nullable |
|---|---|---|
| `InvitationReviewDecisionTypeId` | int(10) | NO |
| `InvitationReviewDecisionType` | nvarchar(100) | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### EditorialBoard.InvitationReviewStatus

| Column | Type | Nullable |
|---|---|---|
| `InvitationReviewStatusId` | int(10) | NO |
| `InvitationReviewStatus` | nvarchar(100) | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### EditorialBoard.InvitationSource

| Column | Type | Nullable |
|---|---|---|
| `InvitationSourceId` | int(10) | NO |
| `InvitationSource` | varchar(100) | NO |
| `RowVersion` | timestamp | NO |

### EditorialBoard.InvitationStatus

| Column | Type | Nullable |
|---|---|---|
| `InvitationStatusId` | int(10) | NO |
| `InvitationStatus` | varchar | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### EditorialBoard.InvitationType

| Column | Type | Nullable |
|---|---|---|
| `InvitationTypeId` | int(10) | NO |
| `InvitationType` | varchar(50) | NO |
| `RowVersion` | timestamp | NO |

### EditorialBoard.Invitations

| Column | Type | Nullable |
|---|---|---|
| `InvitationId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `InvitationTypeId` | int(10) | NO |
| `InvitationSourceId` | int(10) | YES |
| `InviterUserId` | int(10) | YES |
| `TaxonomyId` | bigint(19) | NO |
| `JournalRoleId` | varchar(10) | NO |
| `SuggestedEditorId` | bigint(19) | YES |
| `InviteeUserId` | int(10) | YES |
| `InviteeEmail` | varchar(150) | NO |
| `InviteeFirstName` | nvarchar(150) | YES |
| `InviteeMiddleName` | nvarchar(150) | YES |
| `InviteeLastName` | nvarchar(150) | YES |
| `InviteeAffiliation` | nvarchar(2000) | YES |
| `InvitationStatusId` | int(10) | YES |
| `InvitationStatusModifyDate` | datetime | YES |
| `InviteDate` | datetime | NO |
| `DeclinationReasonId` | int(10) | YES |
| `DeclinationPersonalNote` | varchar | YES |
| `DeclinationComment` | varchar | YES |
| `ReminderDate.Last` | datetime | YES |
| `Reminders.Total.Count` | int(10) | YES |
| `InvitationReviewDecisionTypeId` | int(10) | YES |
| `InvitationReviewRejectionReasonId` | int(10) | YES |
| `InvitationReviewStatusId` | int(10) | YES |
| `InvitationReviewStatusModificationDate` | datetime | YES |
| `InvitationReviewInvalidReasonId` | int(10) | YES |
| `InvitationReviewInfluenceScoreSnapshot` | decimal(5) | YES |
| `InvitationReviewHIndexSnapshot` | decimal(5) | YES |
| `InvitationActivationNumber` | uniqueidentifier | NO |
| `RowVersion` | timestamp | NO |

### EditorialBoard.Invitations.Blocked

| Column | Type | Nullable |
|---|---|---|
| `BlockedInvitationId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `InviterUserId` | int(10) | NO |
| `TaxonomyId` | bigint(19) | YES |
| `InviteeUserId` | int(10) | YES |
| `InviteeEmail` | nvarchar(150) | NO |
| `InviteeFirstName` | nvarchar(150) | YES |
| `InviteeMiddleName` | nvarchar(150) | YES |
| `InviteeLastName` | nvarchar(150) | YES |
| `InviteeAffiliationId` | int(10) | YES |
| `InviteeRosstId` | nvarchar(40) | YES |
| `InviteeAffiliation` | nvarchar(2000) | YES |
| `InfluenceScoreSnapshot` | decimal(5) | YES |
| `HIndex` | decimal(5) | YES |
| `CreatorUserId` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### EditorialBoard.OnboardingStatus

| Column | Type | Nullable |
|---|---|---|
| `StatusId` | int(10) | NO |
| `Status` | varchar(50) | NO |
| `RowVersion` | timestamp | NO |

### EditorialBoard.Reason

| Column | Type | Nullable |
|---|---|---|
| `ReasonId` | int(10) | NO |
| `Reason` | nvarchar(150) | NO |
| `RowVersion` | timestamp | NO |

### EditorialBoard.SuggestedEditors

| Column | Type | Nullable |
|---|---|---|
| `SuggestedEditorId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `SuggestedEditorId.Original` | int(10) | NO |
| `UserId` | int(10) | YES |
| `FirstName` | nvarchar(150) | YES |
| `LastName` | nvarchar(150) | YES |
| `Email` | varchar(150) | YES |
| `Affiliation` | nvarchar(2000) | YES |
| `HIndex` | int(10) | YES |
| `InfluenceScoreSnapshot` | decimal(5) | YES |
| `CitationsCount` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `AlgorithmSourceId` | int(10) | YES |
| `AlgorithmSuggestedTaxonomyId` | bigint(19) | YES |
| `TaxonomyId` | bigint(19) | NO |
| `RoleId` | int(10) | YES |
| `JournalRoleId` | varchar(10) | YES |
| `SuggesterUserId` | int(10) | YES |
| `SuggesterFirstName` | nvarchar(150) | YES |
| `SuggesterMiddleName` | nvarchar(150) | YES |
| `SuggesterLastName` | nvarchar(150) | YES |
| `SuggesterEmail` | nvarchar(150) | YES |
| `SuggesterAffiliation` | nvarchar(2000) | YES |
| `SuggestionRecipientUserId` | int(10) | YES |
| `MethodId` | bigint(19) | NO |
| `SourceId` | bigint(19) | YES |
| `StatusId` | int(10) | NO |
| `DiscardReasonId` | bigint(19) | YES |
| `Comments` | varchar(200) | YES |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### EditorialBoard.SuggestedEditors.DiscardReason

| Column | Type | Nullable |
|---|---|---|
| `DiscardReasonId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `DiscardReasonId.Original` | int(10) | NO |
| `DiscardReason` | varchar(100) | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### EditorialBoard.SuggestedEditors.Method

| Column | Type | Nullable |
|---|---|---|
| `MethodId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `MethodId.Original` | int(10) | NO |
| `Method` | varchar(100) | NO |
| `CreateDate` | datetime | NO |
| `MethodType` | nvarchar(200) | YES |
| `RowVersion` | timestamp | NO |

### EditorialBoard.SuggestedEditors.Source

| Column | Type | Nullable |
|---|---|---|
| `SourceId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `SourceId.Original` | int(10) | NO |
| `Source` | varchar(100) | NO |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### EditorialBoard.SuggestedEditors.Status

| Column | Type | Nullable |
|---|---|---|
| `StatusId` | int(10) | NO |
| `Status` | varchar(100) | NO |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### EditorialOffice_ArticlesPrograms

| Column | Type | Nullable |
|---|---|---|
| `ArticleId` | bigint(19) | NO |
| `ProgramId` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### EditorialOffice_Journals

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `ProgramId` | int(10) | YES |
| `JournalDevelopment.JournalManager` | nvarchar(100) | YES |
| `JournalDevelopment.SeniorJournalManager` | nvarchar(100) | YES |
| `JournalSpecialist.Count` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### EditorialOffice_Journals_Archive

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `ProgramId` | int(10) | YES |
| `ResponsibleName` | nvarchar(100) | YES |
| `RowVersion` | timestamp | NO |

### EditorialOffice_Journals_History_Archive

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyHistoryId` | decimal(25) | NO |
| `StartDate` | date | NO |
| `EndDate` | date | YES |
| `TaxonomyId` | bigint(19) | NO |
| `HistoryOrder` | int(10) | NO |
| `ProgramHistoryId` | int(10) | YES |
| `ResponsibleName` | nvarchar(100) | YES |
| `IsCurrent` | bit | NO |
| `RowVersion` | timestamp | NO |

### EditorialOffice_Programs

| Column | Type | Nullable |
|---|---|---|
| `ProgramId` | int(10) | NO |
| `Program` | nvarchar(50) | NO |
| `ResponsibleName` | nvarchar(100) | YES |
| `IsActive` | bit | NO |
| `RowVersion` | timestamp | NO |

### EditorialOffice_Programs_Archive

| Column | Type | Nullable |
|---|---|---|
| `ProgramId` | int(10) | NO |
| `Program` | nvarchar(50) | NO |
| `ResponsibleName` | nvarchar(100) | YES |
| `IsActive` | bit | NO |
| `RowVersion` | timestamp | NO |

### EditorialOffice_Programs_History_Archive

| Column | Type | Nullable |
|---|---|---|
| `ProgramHistoryId` | decimal(17) | NO |
| `StartDate` | date | NO |
| `EndDate` | date | YES |
| `ProgramId` | int(10) | NO |
| `HistoryOrder` | int(10) | NO |
| `Program` | nvarchar(50) | NO |
| `ResponsibleName` | nvarchar(100) | YES |
| `IsCurrent` | bit | NO |
| `RowVersion` | timestamp | NO |

### EditorialOffice_Roles

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `ProgramId` | int(10) | YES |
| `ProjectRoleDescription` | nvarchar(120) | NO |
| `ResponsibleName` | nvarchar(50) | NO |
| `RowVersion` | timestamp | NO |

### EditorialOffice_Segment

| Column | Type | Nullable |
|---|---|---|
| `SegmentId` | nvarchar(30) | NO |
| `Segment` | nvarchar(50) | NO |
| `ResponsibleName` | nvarchar(100) | YES |
| `RowVersion` | timestamp | NO |

### EditorialOffice_SegmentsHistory

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `ReferenceYear` | smallint(5) | NO |
| `SegmentType` | nvarchar(20) | NO |
| `SegmentId` | nvarchar(30) | NO |
| `Segment` | nvarchar(50) | NO |
| `RowVersion` | timestamp | NO |

### JCREditions

| Column | Type | Nullable |
|---|---|---|
| `JCREditionId` | nvarchar(10) | NO |
| `JCREdition` | nvarchar(80) | NO |

### JournalRole

| Column | Type | Nullable |
|---|---|---|
| `JournalRoleId` | varchar(10) | NO |
| `RoleId` | int(10) | NO |
| `Role` | varchar(50) | NO |
| `RoleGroup` | nvarchar(50) | NO |
| `IsAdminOfficeRole` | bit | NO |
| `IsJournalEditorialBoardRole` | bit | NO |
| `IsResearchTopicEditorRole` | bit | NO |
| `IsArticleReviewBoardRole` | bit | NO |
| `IsArticleAuthorsRole` | bit | NO |
| `Rank.ResearchTopic` | smallint(5) | YES |
| `Rank.Article` | smallint(5) | YES |
| `RowVersion` | timestamp | NO |

### JournalsIndexing.Eligibility

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `JournalId` | int(10) | NO |
| `FirstAcceptanceDate` | date | YES |
| `FirstAcceptanceDOI` | nvarchar(50) | YES |
| `FirstPublicationDate` | date | YES |
| `FirstPublicationDOI` | nvarchar(50) | YES |
| `JournalAgeMonths` | int(10) | YES |
| `Publications.Count` | int(10) | YES |
| `AveragePublicationsYear` | decimal(18) | YES |
| `CurrentFCE.Count` | int(10) | YES |
| `PublicationsYTD.Count` | int(10) | YES |
| `Publications2FullYears.Count` | int(10) | YES |
| `Publications12Months.Count` | int(10) | YES |
| `PublicationsSpontaneous12Months.Count` | int(10) | YES |
| `PublicationsSpontaneous12Months.Percentage` | decimal(18) | YES |
| `PublicationsSpontaneousAcceptance12Months.Percentage` | decimal(18) | YES |
| `OriginalResearch.Count` | int(10) | YES |
| `OriginalResearch.Percentage` | decimal(18) | YES |
| `Reviews.Count` | int(10) | YES |
| `Reviews.Percentage` | decimal(18) | YES |
| `CaseReports.Count` | int(10) | YES |
| `CaseReports.Percentage` | decimal(18) | YES |
| `Others.Count` | int(10) | YES |
| `Others.Percentage` | decimal(18) | YES |
| `PublicationsAuthoredByEBM24months.Percentage` | decimal(18) | YES |
| `NArticles40ArticlesPublicationDate` | date | YES |
| `NArticles50ArticlesPublicationDate` | date | YES |
| `NArticles25ArticlesPublicationDate` | date | YES |
| `NArticles5ArticlesPublicationDate` | date | YES |
| `NArticles10ArticlesPublicationDate` | date | YES |
| `DOAJ.ArticlesCountThreshold` | int(10) | YES |
| `DOAJ.DOI5` | nvarchar(50) | YES |
| `DOAJ.ArticlesCountThreshold2` | int(10) | YES |
| `DOAJ.DOI10` | nvarchar(50) | YES |
| `DOAJ.FirstPublicationDate` | date | YES |
| `DOAJ.PercentagePublicationAuthoredByEbm` | decimal(18) | YES |
| `DOAJ.MaxTeAuthorRatioPerRt` | decimal(18) | YES |
| `DOAJ.Conditions.HasPublished5Articles` | bit | YES |
| `DOAJ.Conditions.HasPublished10Articles` | bit | YES |
| `DOAJ.Conditions.IsFirstPublicationOlder12M` | bit | YES |
| `DOAJ.Conditions.LowPercentagePublicationAuthoredByEbm` | bit | YES |
| `DOAJ.Conditions.LowTeAuthorRatioPerRt` | bit | YES |
| `DOAJ.IsEligible` | bit | YES |
| `DOAJ.ApplicationDate` | date | YES |
| `DOAJ.AcceptanceDate` | date | YES |
| `DOAJ.ContentStartDate` | date | YES |
| `DOAJ.ContentEndDate` | date | YES |
| `DOAJ.RejectionDate` | date | YES |
| `DOAJ.OutOfScopeDate` | date | YES |
| `DOAJ.OnHoldDate` | date | YES |
| `DOAJ.LastRelevantDate` | date | YES |
| `DOAJ.IndexationStatus` | nvarchar(30) | YES |
| `PMC.ArticlesCountThreshold` | int(10) | YES |
| `PMC.DOI25` | nvarchar(50) | YES |
| `PMC.Conditions.HasPublished25Articles` | bit | YES |
| `PMC.IsEligible` | bit | YES |
| `PMC.ApplicationDate` | date | YES |
| `PMC.AcceptanceDate` | date | YES |
| `PMC.ContentStartDate` | date | YES |
| `PMC.ContentEndDate` | date | YES |
| `PMC.RejectionDate` | date | YES |
| `PMC.OutOfScopeDate` | date | YES |
| `PMC.OnHoldDate` | date | YES |
| `PMC.LastRelevantDate` | date | YES |
| `PMC.IndexationStatus` | nvarchar(30) | YES |
| `MED.ArticlesCountThreshold` | int(10) | YES |
| `MED.JournalMinimumAgeMonths` | int(10) | YES |
| `MED.DOI40` | nvarchar(50) | YES |
| `MED.ReachedDate` | date | YES |
| `MED.LatestReached` | nvarchar(30) | YES |
| `MED.Conditions.HasPublished40Articles` | bit | YES |
| `MED.Conditions.HasMoreThan12Months` | bit | YES |
| `MED.Conditions.HasPublicationsSpontaneous12MonthsOver40Percentage` | bit | YES |
| `MED.Conditions.HasPublicationsSpontaneous12MonthsUnder65Percentage` | bit | YES |
| `MED.Conditions.HasOriginalResearchCountOver60` | bit | YES |
| `MED.Conditions.HasReviewCountUnder40` | bit | YES |
| `MED.IsEligible` | bit | YES |
| `MED.ApplicationDate` | date | YES |
| `MED.AcceptanceDate` | date | YES |
| `MED.ContentStartDate` | date | YES |
| `MED.ContentEndDate` | date | YES |
| `MED.RejectionDate` | date | YES |
| `MED.OutOfScopeDate` | date | YES |
| `MED.OnHoldDate` | date | YES |
| `MED.LastRelevantDate` | date | YES |
| `MED.IndexationStatus` | nvarchar(30) | YES |
| `Scopus.ArticlesCountThreshold` | bigint(19) | YES |
| `Scopus.JournalMinimumAgeMonths` | bigint(19) | YES |
| `Scopus.PublicationsAveragePerYear.Minimum` | bigint(19) | YES |
| `Scopus.DOI40` | nvarchar(50) | YES |
| `Scopus.ReachedDate` | date | YES |
| `Scopus.LatestReached` | nvarchar(30) | YES |
| `Scopus.Conditions.HasPublished40Articles` | bit | YES |
| `Scopus.Conditions.HasPublicationsAveragePerYearOver30` | bit | YES |
| `Scopus.Conditions.HasFCE` | bit | YES |
| `Scopus.Conditions.HasMoreThan24Months` | bit | YES |
| `Scopus.IsEligible` | bit | YES |
| `Scopus.ApplicationDate` | date | YES |
| `Scopus.AcceptanceDate` | date | YES |
| `Scopus.ContentStartDate` | date | YES |
| `Scopus.ContentEndDate` | date | YES |
| `Scopus.RejectionDate` | date | YES |
| `Scopus.OutOfScopeDate` | date | YES |
| `Scopus.OnHoldDate` | date | YES |
| `Scopus.LastRelevantDate` | date | YES |
| `Scopus.IndexationStatus` | nvarchar(30) | YES |
| `COPE.JournalMinimumAgeMonths` | int(10) | YES |
| `COPE.Conditions.HasMoreThan12Months` | bit | YES |
| `COPE.IsEligible` | bit | YES |
| `COPE.ApplicationDate` | date | YES |
| `COPE.AcceptanceDate` | date | YES |
| `COPE.ContentStartDate` | date | YES |
| `COPE.ContentEndDate` | date | YES |
| `COPE.RejectionDate` | date | YES |
| `COPE.OutOfScopeDate` | date | YES |
| `COPE.OnHoldDate` | date | YES |
| `COPE.LastRelevantDate` | date | YES |
| `COPE.IndexationStatus` | nvarchar(30) | YES |

### JournalsIndexing.Journals

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `IndexingServiceId` | int(10) | NO |
| `ContentDateStart` | date | YES |
| `ContentDateEnd` | date | YES |
| `ApplicationDate` | date | YES |
| `AcceptanceDate` | date | YES |
| `RejectionDate` | date | YES |
| `OutOfScopeDate` | date | YES |
| `OnHoldDate` | date | YES |
| `RowVersion` | timestamp | NO |

### JournalsIndexing.Services

| Column | Type | Nullable |
|---|---|---|
| `IndexingServiceId` | int(10) | NO |
| `Name` | nvarchar(150) | NO |
| `ShortName` | nvarchar(20) | YES |
| `Provider` | nvarchar(150) | YES |
| `ValidDateStart` | date | NO |
| `ValidDateEnd` | date | YES |
| `HomePage` | nvarchar(100) | YES |
| `Comment` | nvarchar(255) | YES |
| `RowVersion` | timestamp | NO |

### Journals_ArticleTypes

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleTypeId` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### Journals_CostCenters

| Column | Type | Nullable |
|---|---|---|
| `SpaceId` | smallint(5) | NO |
| `JournalId` | int(10) | NO |
| `CostCenterId` | nvarchar(50) | YES |
| `RowVersion` | timestamp | NO |

### Journals_Details

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `JournalId` | int(10) | NO |
| `TypeId` | int(10) | YES |
| `Journal` | nvarchar(150) | NO |
| `ShortName` | nvarchar(50) | YES |
| `Abbreviation` | nvarchar(100) | YES |
| `ISSNElectronic` | nvarchar(30) | YES |
| `MissionStatement` | nvarchar | YES |
| `CreateDate` | datetime | NO |
| `PublishDate.Original` | datetime | YES |
| `PublishDate` | datetime | NO |
| `EnabledSmartInvitationAE` | bit | NO |
| `EnabledSmartInvitationRE` | bit | NO |
| `TypeSetterUserId` | int(10) | YES |
| `ImpactFactor` | numeric(10) | YES |
| `IsDeleted` | bit | NO |
| `ModifyDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### Journals_DetailsTaxonomy

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `JournalId` | int(10) | NO |
| `SectionId` | int(10) | YES |
| `IsOnline` | bit | NO |
| `IsOpenForSubmission` | bit | NO |
| `CreateDate` | datetime | YES |
| `ModifyDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### Journals_ImpactFactorHistory

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `JournalId` | int(10) | NO |
| `Year` | int(10) | NO |
| `ImpactFactor` | numeric(10) | NO |
| `OrderAsc` | int(10) | NO |
| `OrderDesc` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Journals_JCREditions

| Column | Type | Nullable |
|---|---|---|
| `TaxonomyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `JournalId` | int(10) | NO |
| `Year` | nvarchar(10) | NO |
| `EditionId` | nvarchar(10) | NO |
| `OrderAsc` | smallint(5) | YES |
| `OrderDesc` | smallint(5) | YES |

### Journals_Type

| Column | Type | Nullable |
|---|---|---|
| `TypeId` | int(10) | NO |
| `Type` | nvarchar(30) | YES |
| `JournalLevel` | nvarchar(20) | NO |
| `TaxonomyLevel` | nvarchar(20) | YES |
| `RowVersion` | timestamp | NO |

### Keywords

| Column | Type | Nullable |
|---|---|---|
| `KeywordId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Keyword` | nvarchar(256) | NO |
| `RowVersion` | timestamp | NO |

### LaunchResearchTopics

| Column | Type | Nullable |
|---|---|---|
| `TopicId` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `TopicTitle` | nvarchar(1250) | YES |
| `TaxonomyId` | bigint(19) | NO |
| `SourceId` | int(10) | YES |
| `GroupId` | int(10) | YES |
| `ThemeId` | int(10) | YES |
| `CampaignId` | char(18) | YES |
| `CreatedBy` | int(10) | YES |
| `CreatedDate` | datetime | NO |
| `TotalReactions` | int(10) | YES |
| `NegativeReactions` | int(10) | YES |
| `PositiveReactions` | int(10) | YES |

### LaunchResearchTopics_Comments

| Column | Type | Nullable |
|---|---|---|
| `TopicId` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `CommentedByUserId` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `Comments` | nvarchar | YES |

### LaunchResearchTopics_Editors

| Column | Type | Nullable |
|---|---|---|
| `TopicId` | int(10) | NO |
| `PersonId` | bigint(19) | NO |
| `Rank` | int(10) | YES |
| `LastAuthor.Count` | int(10) | YES |
| `FirstAuthor.Count` | int(10) | YES |
| `ProfilingState` | int(10) | YES |
| `LastPublicationDate` | datetime | YES |
| `PapersAuthored` | int(10) | YES |

### LaunchResearchTopics_Feedback

| Column | Type | Nullable |
|---|---|---|
| `TopicId` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `FeedbackTypeId` | int(10) | NO |
| `Reasons` | nvarchar(500) | YES |
| `SubmittedByUserId` | int(10) | NO |
| `SubmittedDate` | datetime | NO |
| `Enhancements` | nvarchar | YES |
| `FurtherDetails` | nvarchar | YES |
| `RecommendedResearchers` | nvarchar | YES |

### LaunchResearchTopics_FeedbackType

| Column | Type | Nullable |
|---|---|---|
| `FeedbackTypeId` | int(10) | NO |
| `FeedbackType` | nvarchar(200) | NO |

### LaunchResearchTopics_Group

| Column | Type | Nullable |
|---|---|---|
| `GroupId` | int(10) | NO |
| `Group` | nvarchar(200) | YES |

### LaunchResearchTopics_InvalidationReasons

| Column | Type | Nullable |
|---|---|---|
| `ReasonId` | int(10) | NO |
| `Reason` | nvarchar(200) | NO |

### LaunchResearchTopics_Invalidations

| Column | Type | Nullable |
|---|---|---|
| `TopicId` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `ReasonId` | int(10) | NO |
| `InvalidatedByUserId` | int(10) | YES |
| `InvalidationDate` | datetime | NO |
| `Comments` | nvarchar | YES |

### LaunchResearchTopics_Merges

| Column | Type | Nullable |
|---|---|---|
| `MergedToTopicId` | int(10) | NO |
| `DeletedTopicId` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `MergedByUserId` | int(10) | YES |
| `MergeDate` | datetime | YES |

### LaunchResearchTopics_Source

| Column | Type | Nullable |
|---|---|---|
| `SourceId` | int(10) | NO |
| `Source` | nvarchar(200) | YES |

### LaunchResearchTopics_Stage

| Column | Type | Nullable |
|---|---|---|
| `StageId` | int(10) | NO |
| `Stage` | nvarchar(200) | YES |
| `Stage.Label.ACP` | nvarchar(200) | YES |
| `Stage.Label.Trendy` | nvarchar(200) | YES |
| `StageOrder` | int(10) | YES |

### LaunchResearchTopics_Theme

| Column | Type | Nullable |
|---|---|---|
| `ThemeId` | int(10) | NO |
| `Theme` | nvarchar(400) | YES |

### LaunchResearchTopics_TransferHistory

| Column | Type | Nullable |
|---|---|---|
| `TopicId` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `TaxonomyId` | bigint(19) | NO |
| `InitiatedBy` | int(10) | YES |
| `InitiatedDate` | datetime | NO |

### LaunchResearchTopics_WorkflowHistory

| Column | Type | Nullable |
|---|---|---|
| `TopicId` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `StageId` | int(10) | YES |
| `StartedBy` | int(10) | YES |
| `StartDate` | datetime | NO |
| `EndDate` | datetime | YES |

### Recognition.Editors

| Column | Type | Nullable |
|---|---|---|
| `RecognitionEditorsId` | nvarchar(50) | NO |
| `SpaceID` | smallint(5) | NO |
| `RecognitionEditorsId.Original` | nvarchar(50) | NO |
| `CreateDate` | datetime | NO |
| `Event` | nvarchar(100) | NO |
| `UserId` | int(10) | NO |
| `Discriminator` | nvarchar(50) | NO |
| `PointsDebit` | int(10) | YES |
| `ExpiryDate` | datetime | YES |
| `PointsPendingToRedeem` | int(10) | YES |
| `ArticleId` | bigint(19) | YES |
| `PointsCredit` | int(10) | YES |
| `VoucherId` | nvarchar(50) | YES |
| `Discount.Percentage` | decimal(18) | YES |
| `PointsPending` | int(10) | YES |
| `SenderPersonalMessage` | nvarchar(500) | YES |
| `PointsFromShareTransactionCredit` | int(10) | YES |
| `PointsFromShareTransactionPendingToRedeem` | int(10) | YES |
| `ReferredUserId` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### ResearchTopicAbstracts

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicAbstractId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `TaxonomyId` | bigint(19) | NO |
| `ResearchTopicId` | bigint(19) | NO |
| `ResearchTopicId.Original` | int(10) | YES |
| `Title` | nvarchar | YES |
| `Abstract` | nvarchar | YES |
| `Interests` | tinyint(3) | YES |
| `StageId` | int(10) | YES |
| `CreatorUserId` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopicAbstracts_Affiliations

| Column | Type | Nullable |
|---|---|---|
| `AffiliationId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Organization` | nvarchar(700) | YES |
| `State` | nvarchar(100) | YES |
| `City` | nvarchar(200) | YES |
| `CountryId` | char(3) | YES |
| `RowVersion` | timestamp | NO |

### ResearchTopicAbstracts_Authors

| Column | Type | Nullable |
|---|---|---|
| `AuthorId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ResearchTopicAbstractId` | bigint(19) | NO |
| `AuthorOrder` | int(10) | YES |
| `TitleId` | int(10) | NO |
| `Email` | nvarchar(100) | NO |
| `FirstName` | nvarchar(100) | NO |
| `MiddleName` | nvarchar(50) | YES |
| `LastName` | nvarchar(100) | NO |
| `Name` | nvarchar(150) | YES |
| `Suffix` | nvarchar(50) | YES |
| `RoleId` | int(10) | NO |
| `JournalRoleId` | varchar(10) | YES |
| `IsCorrespondingAuthor` | bit | NO |
| `AuthorUserId` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### ResearchTopicAbstracts_AuthorsAffiliations

| Column | Type | Nullable |
|---|---|---|
| `AuthorAffiliationId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `AuthorId` | bigint(19) | NO |
| `AuthorAffiliationOrder` | int(10) | YES |
| `AffiliationId` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopicAbstracts_Stage

| Column | Type | Nullable |
|---|---|---|
| `StageId` | int(10) | NO |
| `Stage` | nvarchar(100) | NO |
| `StageCategoryId` | int(10) | YES |
| `StageCategory` | nvarchar(30) | YES |
| `IsSubmitted` | bit | NO |
| `IsDeleted` | bit | NO |
| `IsRejected` | bit | NO |
| `IsAccepted` | bit | NO |
| `IsPublished` | bit | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopicAbstracts_Stages

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicAbstractId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `StageId` | int(10) | NO |
| `StageDate` | datetime | YES |
| `ModifierUserId` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### ResearchTopicSuggestedContributors

| Column | Type | Nullable |
|---|---|---|
| `SuggestedContributorId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ResearchTopicId` | bigint(19) | NO |
| `ResearchTopicId.Original` | int(10) | YES |
| `UserId` | int(10) | YES |
| `RoleId` | int(10) | YES |
| `ContributorId` | bigint(19) | YES |
| `FirstName` | nvarchar(150) | NO |
| `MiddleName` | nvarchar(50) | YES |
| `LastName` | nvarchar(100) | NO |
| `Email` | nvarchar(100) | NO |
| `NessieVersionId` | int(10) | YES |
| `ExtractDate` | datetime | NO |
| `Score` | numeric(38) | NO |
| `HIndex` | int(10) | YES |
| `TotalCitations` | int(10) | YES |
| `ActivityYears` | int(10) | YES |
| `EstimatedPublicationCount` | int(10) | YES |
| `EOfDecisionReasonId` | int(10) | YES |
| `TEDecisionReasonId` | int(10) | YES |
| `EOfEvaluationStatusId` | int(10) | YES |
| `TEEvaluationStatusId` | int(10) | YES |
| `TEHideReasonId` | int(10) | YES |
| `EOFEvaluationDate` | datetime | YES |
| `TEEvaluationDate` | datetime | YES |
| `UploadTypeId` | int(10) | YES |
| `AlgorithmTypeId` | int(10) | YES |
| `CreateUserId` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `ModifyUserId` | int(10) | YES |
| `ModifyDate` | datetime | YES |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopicSuggestedContributors_Action

| Column | Type | Nullable |
|---|---|---|
| `ActionId` | int(10) | NO |
| `Type` | varchar(11) | NO |
| `Source` | varchar(3) | NO |
| `OriginalId` | int(10) | NO |
| `Label` | nvarchar(30) | NO |
| `IsDeleted` | bit | NO |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopicSuggestedContributors_AlgorithmType

| Column | Type | Nullable |
|---|---|---|
| `AlgorithmTypeId` | int(10) | NO |
| `AlgorithmType` | nvarchar(100) | NO |

### ResearchTopicSuggestedContributors_NessieVersion

| Column | Type | Nullable |
|---|---|---|
| `NessieVersionId` | int(10) | NO |
| `NessieVersion` | nvarchar(20) | NO |

### ResearchTopicSuggestedContributors_UploadType

| Column | Type | Nullable |
|---|---|---|
| `UploadTypeId` | int(10) | NO |
| `UploadType` | nvarchar(15) | NO |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopic_SuggestedArticleStatus

| Column | Type | Nullable |
|---|---|---|
| `SuggestedforResearchTopic.StatusId` | int(10) | NO |
| `Status` | nvarchar(50) | NO |
| `Description` | nvarchar(100) | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ResearchTopicId.Original` | int(10) | NO |
| `TaxonomyId` | bigint(19) | NO |
| `Title` | nvarchar(1100) | NO |
| `Description` | nvarchar | YES |
| `SubmissionDeadline` | datetime | YES |
| `CreateDate` | datetime | NO |
| `CreatorUserId` | int(10) | NO |
| `OwnerUserId` | int(10) | YES |
| `AbstractSubmissionDeadline` | datetime | YES |
| `ExtendedSubmissionDeadline` | datetime | YES |
| `PublicExtendedDeadline` | datetime | YES |
| `StageId` | int(10) | NO |
| `IsOnline` | bit | NO |
| `IsClosed` | bit | NO |
| `IsCompleted` | bit | NO |
| `IsSuggested` | bit | NO |
| `IsRejected` | bit | NO |
| `IsDeleted` | bit | NO |
| `DeletionReasonId` | int(10) | YES |
| `ResearchTopicStep` | nvarchar(255) | YES |
| `ResearchTopicStepHealthStatus` | nvarchar(255) | YES |
| `SuggestedArticles.Count` | int(10) | YES |
| `SuggestedArticles.Count.Discarded` | int(10) | YES |
| `SuggestedArticles.Count.Invited` | int(10) | YES |
| `SuggestedArticles.Count.Accepted` | int(10) | YES |
| `SuggestedArticles.Count.Declined` | int(10) | YES |
| `SuggestedArticles.ConversionRate` | decimal(4) | YES |
| `SubmissionInvitationSendDate` | datetime | YES |
| `EditorialRequestDate` | datetime | YES |
| `Comments` | nvarchar | YES |
| `CountSubmissionDeadlineDates` | int(10) | NO |
| `CountExtendedSubmissionDeadlineDates` | int(10) | NO |
| `IsSuggestedContributorsEnabledForTopicEditors` | bit | NO |
| `IsSuggestedManuscriptEnabledForTopicEditors` | bit | NO |
| `TopicEditorsMonitoringStartDate` | datetime | YES |
| `TopicEditorsMonitoringReminderFrequency` | int(10) | YES |
| `ShareEBookDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### ResearchTopics_ArticlesAssignments

| Column | Type | Nullable |
|---|---|---|
| `AssignmentHistoryId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ResearchTopicId` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `AssignmentTypeId` | smallint(5) | NO |
| `AssignmentDate` | datetime | NO |
| `IsDeleted` | bit | YES |
| `CreatorUserId` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `ModifierUserId` | int(10) | YES |
| `ModifyDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### ResearchTopics_ContributorReferralSource

| Column | Type | Nullable |
|---|---|---|
| `SourceId` | int(10) | NO |
| `Source` | nvarchar(40) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_ContributorReferralStatus

| Column | Type | Nullable |
|---|---|---|
| `StatusId` | int(10) | NO |
| `Status` | nvarchar(30) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_ContributorReferrals

| Column | Type | Nullable |
|---|---|---|
| `ContributorReferralId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ResearchTopicId` | bigint(19) | NO |
| `ResearchTopicId.Original` | int(10) | YES |
| `SourceId` | int(10) | NO |
| `ContributorId` | bigint(19) | YES |
| `FullName` | nvarchar(150) | NO |
| `UserId` | int(10) | YES |
| `IsEditorialBoardMember` | bit | NO |
| `Affiliation` | nvarchar | YES |
| `AffiliationCountry` | nvarchar(60) | YES |
| `Email` | nvarchar(100) | NO |
| `HIndex` | int(10) | YES |
| `YearsofActivityCount` | int(10) | YES |
| `EstimatedPublicationsCount` | int(10) | YES |
| `EstimatedCitationsCount` | int(10) | YES |
| `InboundLeadReferralId` | bigint(19) | YES |
| `StatusId` | int(10) | NO |
| `IsAccepted` | bit | NO |
| `CreatorUserId` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `ModifierUserId` | int(10) | YES |
| `ModifyDate` | datetime | YES |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_ContributorTracking

| Column | Type | Nullable |
|---|---|---|
| `ContributorTrackingId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ContributorTrackingId.Original` | int(10) | NO |
| `ContributorId` | bigint(19) | NO |
| `TrackingEvent` | int(10) | NO |
| `URL` | nvarchar(1000) | NO |
| `ReferrerURL` | nvarchar(1000) | YES |
| `VisitDate` | datetime | YES |
| `ReferrerEmailType` | nvarchar(250) | YES |
| `Source` | nvarchar(128) | YES |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_Contributors

| Column | Type | Nullable |
|---|---|---|
| `ContributorId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ContributorId.Original` | bigint(19) | NO |
| `ResearchTopicId` | bigint(19) | NO |
| `ResearchTopicId.Original` | int(10) | NO |
| `SortOrder` | bigint(19) | NO |
| `UserId` | int(10) | YES |
| `Email` | nvarchar(100) | NO |
| `ContributorSourceId` | int(10) | NO |
| `ContributorSecondarySourceId` | int(10) | YES |
| `FirstName` | nvarchar(150) | NO |
| `MiddleName` | nvarchar(50) | YES |
| `LastName` | nvarchar(150) | NO |
| `Name` | nvarchar(400) | YES |
| `Theme` | nvarchar(500) | YES |
| `SalesForceMessageCreateDate` | datetime | YES |
| `Invitation.InitiationDate` | datetime | YES |
| `InviteDate` | datetime | YES |
| `InviteDate_2` | datetime | YES |
| `InviterUserId` | int(10) | YES |
| `Invitation.Initiator.RoleId` | int(10) | YES |
| `Contributor.Creator.UserTypeRoleId` | int(10) | YES |
| `CreateDate` | datetime | NO |
| `ContributorCreatedDate` | datetime | YES |
| `InvitationStatusId` | int(10) | NO |
| `InvitationStatusDate` | datetime | YES |
| `InvitationStatusDate.Confirmed.First` | datetime | YES |
| `InvitationStatusDate.Confirmed.Last` | datetime | YES |
| `InvitationSentRemindersCount` | int(10) | NO |
| `InvitationLastReminderDate` | datetime | YES |
| `InvitationActivationNumber` | uniqueidentifier | YES |
| `IsContributorEngaged` | bit | NO |
| `CountExpectedArticles` | int(10) | NO |
| `PersonalSubmissionDeadline` | datetime | YES |
| `IsFromResearchTopicEditorialTeam` | bit | YES |
| `CfPJourney` | nvarchar(120) | YES |
| `CfPJourneyLastEmailReceived` | nvarchar(120) | YES |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_Contributors.Aggregated

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Space` | nvarchar(100) | NO |
| `ResearchTopicId.Original` | int(10) | YES |
| `ContributorsConfirmed.Count` | int(10) | YES |
| `ContributorsToBeContacted.Count` | int(10) | YES |
| `ContributorsPending.Count` | int(10) | YES |
| `ContributorsDeclined.Count` | int(10) | YES |
| `ContributorsAbstractCoauthor.Count` | int(10) | YES |
| `ContributorsUnresponsive.Count` | int(10) | YES |
| `ContributorsWithdrawn.Count` | int(10) | YES |
| `ContributorsInvited.Count` | int(10) | YES |
| `ContributorsPotential.Count` | int(10) | YES |
| `Contributors.Count` | int(10) | YES |
| `Contributors.Overview` | varchar(17) | NO |
| `SuggestedContributors.Count` | int(10) | YES |
| `SuggestedContributorsInvited.Count` | int(10) | YES |
| `SuggestedContributorsUploadedByEditorialOffice.Count` | int(10) | YES |
| `SuggestedContributorsDiscardedByEditorialOffice.Count` | int(10) | YES |
| `SuggestedContributorsApprovedByTopicEditor.Count` | int(10) | YES |
| `SuggestedContributorsDiscardedByTopicEditor.Count` | int(10) | YES |
| `SuggestedContributorsPendingByTopicEditor.Count` | int(10) | YES |
| `IsUsingPC2TE` | bit | NO |
| `RowVersion` | timestamp | NO |
| `Checksum` | bigint(19) | NO |

### ResearchTopics_Contributors.SecondarySource

| Column | Type | Nullable |
|---|---|---|
| `ContributorSecondarySourceId` | int(10) | NO |
| `ContributorSecondarySource` | nvarchar(50) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_Contributors.UserTypeRoles

| Column | Type | Nullable |
|---|---|---|
| `UserTypeRoleId` | int(10) | NO |
| `UserTypeRole` | nvarchar(20) | NO |

### ResearchTopics_ContributorsArticles

| Column | Type | Nullable |
|---|---|---|
| `ContributorId` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ArticleId.Original` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### ResearchTopics_ContributorsArticlesDuplicates

| Column | Type | Nullable |
|---|---|---|
| `ContributorId` | bigint(19) | NO |
| `ArticleAuthorId` | bigint(19) | NO |
| `ArticleId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ContributorId.Original` | int(10) | NO |
| `ArticleAuthorId.Original` | int(10) | NO |
| `ArticleId.Original` | int(10) | NO |
| `DuplicatedContributorId` | bigint(19) | YES |
| `DuplicatedContributorId.Original` | int(10) | YES |
| `CreatedDate` | datetime | NO |

### ResearchTopics_ContributorsDeclinations

| Column | Type | Nullable |
|---|---|---|
| `ContributorId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `DeclinationReasonId` | int(10) | NO |
| `DeclinationReasonRank` | int(10) | NO |
| `OtherReason` | varchar(200) | YES |
| `SuggestedContributors` | varchar(3500) | YES |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_ContributorsEvent

| Column | Type | Nullable |
|---|---|---|
| `EventId` | int(10) | NO |
| `Event` | nvarchar(200) | YES |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_ContributorsEventTriggerType

| Column | Type | Nullable |
|---|---|---|
| `TriggerTypeId` | int(10) | NO |
| `TriggerType` | nvarchar(100) | YES |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_ContributorsEvents.Reminders

| Column | Type | Nullable |
|---|---|---|
| `ContributorEventId` | bigint(19) | NO |
| `ResearchTopicId` | bigint(19) | NO |
| `ResearchTopicId.Original` | int(10) | NO |
| `ContributorId` | bigint(19) | NO |
| `ContributorId.Original` | bigint(19) | NO |
| `TriggerTypeId` | int(10) | NO |
| `EventId` | int(10) | NO |
| `EventDatetime` | datetime | YES |

### ResearchTopics_ContributorsInvitationABTests

| Column | Type | Nullable |
|---|---|---|
| `InvitationABTestId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ContributorId` | bigint(19) | NO |
| `SenderUserId` | int(10) | NO |
| `MessageTemplateCode` | nvarchar(20) | YES |
| `CreatorUserId` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_ContributorsSource

| Column | Type | Nullable |
|---|---|---|
| `ContributorSourceId` | int(10) | NO |
| `ContributorSource` | nvarchar(100) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_DeclinationReason

| Column | Type | Nullable |
|---|---|---|
| `DeclinationReasonId` | int(10) | NO |
| `DeclinationReason` | varchar(150) | NO |
| `Description` | nvarchar(400) | YES |
| `CreateDate` | datetime | NO |
| `IsDeleted` | bit | NO |
| `Rank` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### ResearchTopics_DeletionReason

| Column | Type | Nullable |
|---|---|---|
| `DeletionReasonId` | int(10) | NO |
| `DeletionReason` | varchar(500) | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_Editors

| Column | Type | Nullable |
|---|---|---|
| `EditorId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ResearchTopicId` | bigint(19) | NO |
| `ResearchTopicId.Original` | int(10) | NO |
| `EditorUserId` | int(10) | YES |
| `IsNotificationEnabled` | bit | NO |
| `LastNotificationSendDate` | datetime | YES |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_InvitationStatus

| Column | Type | Nullable |
|---|---|---|
| `InvitationStatusId` | int(10) | NO |
| `InvitationStatus` | nvarchar(30) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_Keywords

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicKeywordId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ResearchTopicId` | bigint(19) | NO |
| `Keyword` | nvarchar(256) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_ParticipatingJournals

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `TaxonomyId` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_SocialCounts

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `CreateDate` | datetime | NO |
| `SocialCountSourceId` | int(10) | NO |
| `Value` | float(53) | YES |
| `Cumulative` | float(53) | YES |
| `RowVersion` | timestamp | NO |

### ResearchTopics_Stage

| Column | Type | Nullable |
|---|---|---|
| `StageId` | int(10) | NO |
| `Stage` | nvarchar(30) | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_Stages

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ResearchTopicId.Original` | int(10) | NO |
| `StageId` | int(10) | NO |
| `StageDate` | datetime | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_Surveys.NetPromoterScore

| Column | Type | Nullable |
|---|---|---|
| `SurveyResponseId` | int(10) | NO |
| `SourceResponseId` | nvarchar(100) | NO |
| `ResearchTopicId` | bigint(19) | NO |
| `TaxonomyId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `StartDate` | datetime | NO |
| `EndDate` | datetime | YES |
| `UserId` | int(10) | NO |
| `ParticipantRoleId` | int(10) | YES |
| `CountryId` | char(3) | YES |
| `NetPromoterScore` | int(10) | YES |
| `SurveyTypeId` | int(10) | NO |
| `RowVersion` | timestamp | NO |
| `Checksum` | bigint(19) | NO |

### ResearchTopics_TopicCoordinators

| Column | Type | Nullable |
|---|---|---|
| `Id` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ResearchTopicId` | bigint(19) | NO |
| `ResearchTopicId.Original` | int(10) | NO |
| `UserId` | int(10) | NO |
| `LoginUserId` | int(10) | NO |
| `CreatorUserid` | int(10) | NO |
| `CreatedDate` | datetime | NO |
| `ModifierUserId` | int(10) | YES |
| `ModifiedDate` | datetime | YES |
| `SequenceId` | int(10) | YES |
| `IsDeleted` | bit | NO |
| `IsQualitricsSurveyForCFP` | bit | NO |
| `IsQualitricsSurveyForClosedRT` | bit | NO |
| `RowVersion` | timestamp | NO |

### ResearchTopics_ViewsAndDownloads

| Column | Type | Nullable |
|---|---|---|
| `ResearchTopicId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ResearchTopicId.Original` | int(10) | NO |
| `ImpactActionId` | int(10) | NO |
| `ImpactAggregationId` | int(10) | NO |
| `ProviderId` | int(10) | NO |
| `Date` | date | NO |
| `Human.Value` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### Researchtopics_ArticlesAssignments.AssignmentType

| Column | Type | Nullable |
|---|---|---|
| `AssignmentTypeId` | smallint(5) | NO |
| `AssignmentType` | nvarchar(30) | NO |
| `RowVersion` | timestamp | NO |

### Submissions

| Column | Type | Nullable |
|---|---|---|
| `SubmissionId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `SubmissionId.Original` | int(10) | NO |
| `ArticleId` | bigint(19) | YES |
| `ArticleId.Original` | int(10) | YES |
| `IsProvided.Files.Manuscript` | bit | NO |
| `ManuscriptId` | bigint(19) | NO |
| `ManuscriptId.Original` | int(10) | NO |
| `IsProvided.Files.Figures` | bit | NO |
| `IsProvided.Files.Supplementary` | bit | NO |
| `ManuscriptTables.Count` | int(10) | NO |
| `IsResubmission` | bit | NO |
| `ArticleTitle` | nvarchar(800) | YES |
| `ArticleRunningTitle` | nvarchar(800) | YES |
| `Keywords` | nvarchar | YES |
| `IsProvided.Abstract` | bit | NO |
| `IsProvided.BodyText` | bit | NO |
| `HasConflictOfInterest` | bit | NO |
| `IsProvided.EthicsStatement` | bit | NO |
| `IsProvided.DataAvailability` | bit | NO |
| `IsProvided.ContributionStatement` | bit | NO |
| `IsProvided.ContributionToField` | bit | NO |
| `IsProvided.ProductDetails` | bit | NO |
| `ArticleTypeId` | bigint(19) | YES |
| `TaxonomyId` | bigint(19) | YES |
| `ResearchTopicId` | bigint(19) | YES |
| `ResearchTopicId.Original` | int(10) | YES |
| `SourceId` | char(1) | NO |
| `SourceTypeId` | int(10) | YES |
| `IsTransferredFromExternalPartner` | bit | NO |
| `TransferredFromExternalPartner.ExternalPartnerId` | int(10) | YES |
| `TransferredFromExternalPartner.CreateDate` | datetime | YES |
| `TransferredFromExternalPartner.IsCompleted` | bit | NO |
| `TransferredFromExternalPartner.CompleteDate` | datetime | YES |
| `StageId` | int(10) | YES |
| `StatusId` | int(10) | YES |
| `IsSubmitted` | bit | NO |
| `PreferredEditorId` | int(10) | YES |
| `IsProvided.ReviewersRecommended` | bit | NO |
| `IsProvided.ReviewersExcluded` | bit | NO |
| `LoginUserId` | int(10) | YES |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `CreatorUserId` | int(10) | YES |
| `CreatorEmail` | nvarchar(150) | YES |
| `Visits.Count` | int(10) | YES |
| `ModifierUserId` | int(10) | YES |
| `IsProvided.FunderInformation` | bit | NO |
| `IsProvided.FundingStatement` | bit | NO |
| `DiscountCode` | nvarchar(300) | YES |
| `InvoicePayer` | nvarchar(500) | YES |
| `InvoiceRecipient` | nvarchar(250) | YES |
| `IsPreliminaryFeePaid` | bit | NO |
| `RowVersion` | timestamp | NO |

### Submissions.ExternalPartners

| Column | Type | Nullable |
|---|---|---|
| `ExternalPartnerId` | int(10) | NO |
| `ExternalPartner` | nvarchar(100) | NO |

### Submissions_Authors

| Column | Type | Nullable |
|---|---|---|
| `AuthorId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `SubmissionId` | bigint(19) | NO |
| `SubmissionId.Original` | int(10) | YES |
| `AuthorOrder` | int(10) | NO |
| `TitleId` | int(10) | YES |
| `FirstName` | nvarchar(200) | YES |
| `MiddleName` | nvarchar(50) | YES |
| `LastName` | nvarchar(200) | YES |
| `Name` | nvarchar(400) | YES |
| `Suffix` | nvarchar(50) | YES |
| `Email` | nvarchar(120) | YES |
| `IsSubmittingAuthor` | bit | NO |
| `IsCorrespondingAuthor` | bit | NO |
| `LoginUserId` | int(10) | YES |
| `AuthorAffiliationId` | int(10) | YES |
| `AuthorRosstId` | nvarchar(40) | YES |
| `IsDeleted` | bit | NO |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `CreatorUserId` | int(10) | NO |
| `ModifierUserId` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### Submissions_Source

| Column | Type | Nullable |
|---|---|---|
| `SourceId` | char(1) | NO |
| `Source` | nvarchar(32) | NO |
| `IsResubmission` | bit | NO |
| `RowVersion` | timestamp | NO |

### Submissions_SourceType

| Column | Type | Nullable |
|---|---|---|
| `TypeId` | int(10) | NO |
| `TypeCode` | varchar(50) | NO |
| `TypeName` | varchar(150) | NO |
| `RowVersion` | timestamp | NO |

### Submissions_Status

| Column | Type | Nullable |
|---|---|---|
| `StatusId` | int(10) | NO |
| `Status` | varchar(9) | NO |
| `RowVersion` | timestamp | NO |

### Users

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `JournalRole.FirstAssigned.JournalRoleId` | varchar(10) | NO |
| `JournalRole.FirstAssigned.Date` | datetime | YES |
| `JournalRole.FirstAssigned.TaxonomyId` | bigint(19) | NO |
| `JournalRole.HighestRankResearchTopic.FirstAssigned.JournalRoleId` | varchar(10) | NO |
| `JournalRole.HighestRankResearchTopic.FirstAssigned.Date` | datetime | YES |
| `JournalRole.HighestRankResearchTopic.FirstAssigned.TaxonomyId` | bigint(19) | NO |
| `JournalRole.HighestRankArticle.FirstAssigned.JournalRoleId` | varchar(10) | NO |
| `JournalRole.HighestRankArticle.FirstAssigned.Date` | datetime | YES |
| `JournalRole.HighestRankArticle.FirstAssigned.TaxonomyId` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |
| `Checksum` | bigint(19) | NO |

### Users_JournalRoles

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `JournalRoleId` | varchar(10) | NO |
| `JournalRole.FirstAssigned.Date` | datetime | YES |
| `JournalRole.FirstAssigned.TaxonomyId` | bigint(19) | NO |
| `JournalRole.LastAssigned.Date` | datetime | YES |
| `JournalRole.LastAssigned.TaxonomyId` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |
| `Checksum` | bigint(19) | NO |

### Workflows

| Column | Type | Nullable |
|---|---|---|
| `WorkflowId` | int(10) | NO |
| `PipelineStageId` | int(10) | NO |
| `Workflow` | nvarchar(200) | NO |
| `WorkflowNo` | nvarchar(10) | NO |
| `ProcessTimeoutDuration` | numeric(25) | YES |
| `EOfPOfWorkflow` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Workflows_Emails

| Column | Type | Nullable |
|---|---|---|
| `EmailId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `WorkflowId` | int(10) | NO |
| `EmailNo` | nvarchar(10) | NO |
| `EmailKeyText` | varchar(50) | YES |
| `EmailSortOrder` | bigint(19) | YES |
| `MessageTypeId` | int(10) | NO |
| `TimeoutId` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |

### Workflows_MessageType

| Column | Type | Nullable |
|---|---|---|
| `MessageTypeId` | int(10) | NO |
| `MessageType` | nvarchar(30) | NO |
| `RowVersion` | timestamp | NO |

### Workflows_Module

| Column | Type | Nullable |
|---|---|---|
| `ModuleId` | int(10) | NO |
| `Module` | nvarchar(40) | NO |
| `RowVersion` | timestamp | NO |

### Workflows_NotificationSalutation

| Column | Type | Nullable |
|---|---|---|
| `SalutationId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Salutation` | varchar(30) | NO |
| `RowVersion` | timestamp | NO |

### Workflows_NotificationTemplates

| Column | Type | Nullable |
|---|---|---|
| `NotificationId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `Type` | nvarchar(50) | NO |
| `Message` | ntext(1073741823) | NO |
| `KeyText` | varchar(50) | NO |
| `Subject` | varchar(150) | NO |
| `SalutationId` | bigint(19) | YES |
| `RowVersion` | timestamp | NO |

### Workflows_PipelineStage

| Column | Type | Nullable |
|---|---|---|
| `PipelineStageId` | int(10) | NO |
| `ModuleId` | int(10) | YES |
| `PipelineStage` | nvarchar(100) | NO |
| `RowVersion` | timestamp | NO |

### Workflows_Status

| Column | Type | Nullable |
|---|---|---|
| `StatusId` | int(10) | NO |
| `Status` | nvarchar(30) | NO |
| `RowVersion` | timestamp | NO |

### Workflows_Tasks

| Column | Type | Nullable |
|---|---|---|
| `WorkflowTaskId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `ModuleId` | int(10) | YES |
| `ModuleItemId` | int(10) | YES |
| `ArticleId` | bigint(19) | YES |
| `InvoiceId` | bigint(19) | YES |
| `InvoiceNo` | int(10) | YES |
| `UserId` | int(10) | YES |
| `WorkflowId` | int(10) | NO |
| `WorkflowStatusId` | int(10) | NO |
| `LastUsedTimeoutId` | bigint(19) | YES |
| `LastUsedTimeoutEndDate` | datetime | YES |
| `NextTimeoutId` | bigint(19) | YES |
| `NextScheduledDate` | datetime | YES |
| `CreateDate` | datetime | NO |
| `ModifyDate` | datetime | YES |
| `RowVersion` | timestamp | NO |

### Workflows_Timeouts

| Column | Type | Nullable |
|---|---|---|
| `TimeoutId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `WorkflowId` | int(10) | NO |
| `Timeout` | nchar(10) | YES |
| `TimeoutDuration` | numeric(25) | YES |
| `RowVersion` | timestamp | NO |

## [TenantsDataMarts].[Network]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### Employees

| Column | Type | Nullable |
|---|---|---|
| `WorkdayEmployeeId` | varchar(12) | NO |
| `LoopUserId` | int(10) | YES |
| `SalesforceUserId` | char(18) | YES |
| `CurrentJobProfileId` | nvarchar(8) | YES |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### Users

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `FirstName` | nvarchar(150) | NO |
| `MiddleName` | nvarchar(50) | YES |
| `LastName` | nvarchar(150) | NO |
| `Name` | nvarchar(400) | NO |
| `PrimaryEmailAddress` | nvarchar(100) | NO |
| `Degree` | nvarchar(50) | YES |
| `Biography` | nvarchar | YES |
| `RegisterDate` | datetime | YES |
| `ActivateDate` | datetime | YES |
| `ModifyDate` | datetime | YES |
| `IsDeleted` | bit | NO |
| `CompletedRegistration` | bit | NO |
| `IsActivated` | bit | NO |
| `LoggedIn` | bit | NO |
| `HasProfilePicture` | bit | NO |
| `IsProfilePublic` | bit | NO |
| `RowVersion` | timestamp | NO |

### Users.Recognition

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `HasMadeInitialVisit` | bit | NO |
| `PointsBalance` | int(10) | NO |
| `IsDeleted` | bit | NO |
| `EnrollmentDate` | datetime | YES |
| `EnrollmentJournalId` | int(10) | YES |
| `EnrollmentSectionId` | int(10) | YES |
| `EnrollmentArticleId` | bigint(19) | YES |
| `EnrollmentEntityType` | nvarchar(10) | YES |
| `EnrollmentEvent` | nvarchar(40) | YES |
| `EnrollmentReasonType` | nvarchar(20) | YES |
| `EnrollmentRole` | nvarchar(20) | YES |
| `RowVersion` | timestamp | NO |

### Users_AIRA

| Column | Type | Nullable |
|---|---|---|
| `PersonId` | bigint(19) | NO |
| `UserId` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### Users_Addresses

| Column | Type | Nullable |
|---|---|---|
| `AddressId` | int(10) | NO |
| `UserId` | int(10) | NO |
| `SortOrder` | bigint(19) | YES |
| `CountryId` | char(3) | YES |
| `State` | nvarchar(150) | YES |
| `City` | nvarchar(200) | YES |
| `OrganizationTypeId` | int(10) | YES |
| `Organization` | nvarchar(200) | YES |
| `RowVersion` | timestamp | NO |

### Users_Degree

| Column | Type | Nullable |
|---|---|---|
| `DegreeId` | int(10) | NO |
| `Degree` | nvarchar(50) | NO |
| `RowVersion` | timestamp | NO |

### Users_Educations

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `SortOrder` | bigint(19) | NO |
| `IsCurrent` | bit | NO |
| `DegreeId` | int(10) | YES |
| `FieldOfStudy` | nvarchar(50) | YES |
| `StartDate` | datetime | YES |
| `EndDate` | datetime | YES |
| `Organization` | nvarchar(250) | YES |
| `RowVersion` | timestamp | NO |

### Users_Emails

| Column | Type | Nullable |
|---|---|---|
| `EmailId` | int(10) | NO |
| `UserId` | int(10) | NO |
| `Email` | nvarchar(100) | NO |
| `IsPrimary` | bit | NO |
| `IsVerified` | bit | NO |
| `ModifyDate` | datetime | YES |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### Users_Experiences

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `SortOrder` | bigint(19) | NO |
| `IsCurrent` | bit | NO |
| `PositionId` | int(10) | YES |
| `StartDate` | datetime | YES |
| `EndDate` | datetime | YES |
| `AddressId` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### Users_OrganizationType

| Column | Type | Nullable |
|---|---|---|
| `OrganizationTypeId` | int(10) | NO |
| `OrganizationType` | nvarchar(30) | NO |
| `RowVersion` | timestamp | NO |

### Users_Organizations

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `OrganizationId` | int(10) | NO |
| `RosstId` | nvarchar(40) | YES |
| `IsPrimary` | bit | NO |
| `IsCurrent` | bit | NO |
| `RowVersion` | timestamp | NO |

### Users_Position

| Column | Type | Nullable |
|---|---|---|
| `PositionId` | int(10) | NO |
| `Position` | nvarchar(100) | NO |
| `RowVersion` | timestamp | NO |

### Users_ProfileMetrics

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `Impact.Views.Total.Count` | int(10) | NO |
| `Publications.Count` | int(10) | NO |
| `Network.Followers.Count` | int(10) | NO |
| `Network.Following.Count` | int(10) | NO |
| `Network.CoAuthors.Count` | int(10) | NO |
| `Network.Connections.Count` | int(10) | NO |
| `ModifyDate.Impact` | datetime | YES |
| `ModifyDate.Publications` | datetime | YES |
| `ModifyDate.Network` | datetime | YES |
| `RowVersion` | timestamp | NO |

### Users_Roles

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `SpaceId` | smallint(5) | NO |
| `RoleId` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `RowVersion` | timestamp | NO |

### Users_Title

| Column | Type | Nullable |
|---|---|---|
| `TitleId` | int(10) | NO |
| `Title` | nvarchar(15) | YES |
| `RowVersion` | timestamp | NO |

### Users_Titles

| Column | Type | Nullable |
|---|---|---|
| `UserId` | int(10) | NO |
| `TitleId` | int(10) | NO |
| `RowVersion` | timestamp | NO |

## [TenantsDataMarts].[Person]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### Emails

| Column | Type | Nullable |
|---|---|---|
| `Email` | nvarchar(300) | NO |
| `IsPrimary` | bit | NO |
| `PersonId` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

### FieldStudies

| Column | Type | Nullable |
|---|---|---|
| `PersonId` | bigint(19) | NO |
| `FieldStudyId` | bigint(19) | NO |
| `Rank` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### FieldStudy

| Column | Type | Nullable |
|---|---|---|
| `FieldStudyId` | bigint(19) | NO |
| `FieldStudy` | nvarchar(200) | YES |
| `RowVersion` | timestamp | NO |

### Metrics

| Column | Type | Nullable |
|---|---|---|
| `PersonId` | bigint(19) | NO |
| `CountryId` | char(3) | YES |
| `HIndex` | int(10) | YES |
| `YearsOfActivity` | int(10) | YES |
| `PublicationsCount` | int(10) | YES |
| `PublicationsCount.OpenAccess` | int(10) | YES |
| `PublicationsCount.AsFirstAuthor` | int(10) | YES |
| `PublicationsCount.AsLastAuthor` | int(10) | YES |
| `CitationsCount` | int(10) | YES |
| `CoAuthorsCount` | int(10) | YES |
| `InfluencePercentile` | float(53) | YES |
| `ActivityPercentile` | float(53) | YES |
| `TrendinessPercentile` | float(53) | YES |
| `ProductivityPercentile` | float(53) | YES |
| `ConnectivityPercentile` | float(53) | YES |
| `OrganizationId` | int(10) | YES |
| `RosstId` | nvarchar(40) | YES |
| `RowVersion` | timestamp | NO |

### Persons

| Column | Type | Nullable |
|---|---|---|
| `PersonId` | bigint(19) | NO |

### Users

| Column | Type | Nullable |
|---|---|---|
| `PersonUserId` | int(10) | NO |
| `PersonId` | bigint(19) | NO |
| `UserId` | int(10) | NO |
| `Email` | nvarchar(150) | NO |
| `Loop.IsPrimaryEmail` | bit | NO |
| `Aira.IsPrimaryEmail` | bit | NO |
| `IsPrimaryEmail` | bit | NO |
| `UserEmailOrder` | int(10) | NO |
| `EmailOrder` | int(10) | NO |
| `UserOrder` | int(10) | NO |
| `PersonIdHasMetrics` | bit | NO |
| `Checksum` | bigint(19) | NO |
| `RowVersion` | timestamp | NO |

## [TenantsDataMarts].[Subscription]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### Category

| Column | Type | Nullable |
|---|---|---|
| `CategoryId` | int(10) | NO |
| `Category` | nvarchar(100) | NO |
| `Description` | nvarchar(500) | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### OperationalType

| Column | Type | Nullable |
|---|---|---|
| `OperationalTypeId` | int(10) | NO |
| `OperationalType` | nvarchar(50) | YES |
| `RowVersion` | timestamp | NO |

### Subscribers

| Column | Type | Nullable |
|---|---|---|
| `Id` | int(10) | NO |
| `SubscriberId` | int(10) | NO |
| `UserId` | int(10) | YES |
| `Email` | nvarchar(200) | YES |
| `IsGloballyUnsubscribed` | bit | NO |
| `GloballyUnsubscribedDate` | datetime | YES |
| `GloballyUnsubscribedSpaceId` | smallint(5) | YES |
| `CreateDate` | datetime | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### Subscriptions

| Column | Type | Nullable |
|---|---|---|
| `SubscriptionId` | int(10) | NO |
| `SubscriberId` | int(10) | NO |
| `SubscriptionTypeId` | int(10) | NO |
| `StartDate` | datetime | YES |
| `EndDate` | datetime | YES |
| `CreateDate` | datetime | NO |
| `IsDeleted` | bit | NO |
| `RowVersion` | timestamp | NO |

### Type

| Column | Type | Nullable |
|---|---|---|
| `SubscriptionTypeId` | int(10) | NO |
| `SubscriptionType` | nvarchar(100) | NO |
| `Subscription` | nvarchar(255) | NO |
| `Description` | nvarchar(500) | NO |
| `CategoryId` | int(10) | NO |
| `CreateDate` | datetime | NO |
| `IsDeleted` | bit | NO |
| `OperationalTypeId` | int(10) | YES |
| `SpaceId` | smallint(5) | NO |
| `RowVersion` | timestamp | NO |

## [TenantsDataMarts].[TransferZone]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### TransferOpportunity

| Column | Type | Nullable |
|---|---|---|
| `OpportunityId` | int(10) | NO |
| `SourceSpaceId` | smallint(5) | NO |
| `SourceArticleId.Original` | int(10) | NO |
| `SourceArticleId` | bigint(19) | NO |
| `DestinationSpaceId` | smallint(5) | NO |
| `DestinationArticleId.Original` | int(10) | YES |
| `DestinationArticleId` | bigint(19) | YES |
| `StatusId` | int(10) | NO |
| `SourceJournalId` | int(10) | YES |
| `DestinationJournalId.Recommendation` | int(10) | YES |
| `DestinationJournalId` | int(10) | YES |
| `RowVersion` | timestamp | NO |

### TransferOpportunityHistory

| Column | Type | Nullable |
|---|---|---|
| `OpportunityHistoryId` | int(10) | NO |
| `OpportunityId` | int(10) | NO |
| `StatusId` | int(10) | NO |
| `EventDatetime` | datetime | NO |
| `EventDate` | date | NO |
| `RowVersion` | timestamp | NO |

### TransferOpportunityStatus

| Column | Type | Nullable |
|---|---|---|
| `StatusId` | int(10) | NO |
| `Status` | varchar(150) | NO |
| `RowVersion` | timestamp | NO |

## [TenantsDataMarts].[Watchlist]


### @ContentsSummary

| Column | Type | Nullable |
|---|---|---|
| `TableName` | nvarchar(256) | NO |
| `SpaceId` | smallint(5) | NO |
| `ExecutionDate` | datetime | YES |
| `UpdateDate` | datetime | YES |
| `IncrementalValues` | xml | YES |

### Persons

| Column | Type | Nullable |
|---|---|---|
| `PersonId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `FirstName` | nvarchar(100) | YES |
| `MiddleName` | nvarchar(100) | YES |
| `LastName` | nvarchar(100) | YES |
| `LoopUserId` | int(10) | YES |
| `PeopleId` | int(10) | YES |
| `ScopusId` | varchar(20) | YES |
| `MAGId` | bigint(19) | YES |
| `ORCId` | nvarchar(50) | YES |
| `RowVersion` | timestamp | NO |

### Persons_Emails

| Column | Type | Nullable |
|---|---|---|
| `EmailId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `PersonId` | bigint(19) | NO |
| `Email` | nvarchar(100) | NO |
| `RowVersion` | timestamp | NO |

### Persons_Watchlisting

| Column | Type | Nullable |
|---|---|---|
| `WatchlistingId` | bigint(19) | NO |
| `SpaceId` | smallint(5) | NO |
| `PersonId` | bigint(19) | NO |
| `WatchlistingReasonId` | int(10) | NO |
| `WatchlistingRoleId` | int(10) | NO |
| `Comments` | nvarchar | YES |
| `CreateDate` | date | NO |
| `RowVersion` | timestamp | NO |

### WatchlistingReason

| Column | Type | Nullable |
|---|---|---|
| `WatchlistingReasonId` | int(10) | NO |
| `WatchlistingReason` | nvarchar(100) | NO |
| `CategoryId` | int(10) | NO |
| `RowVersion` | timestamp | NO |

### WatchlistingReason_Category

| Column | Type | Nullable |
|---|---|---|
| `CategoryId` | int(10) | NO |
| `Category` | nvarchar(50) | NO |
| `RowVersion` | timestamp | NO |

### WatchlistingRole

| Column | Type | Nullable |
|---|---|---|
| `WatchlistingRoleId` | int(10) | NO |
| `WatchlistingRole` | nvarchar(20) | NO |
| `RowVersion` | timestamp | NO |

---

## Foreign Key Relationships

Found 933 foreign key relationships across 3 databases.


### [FrontiersReports] Relationships

| FK Name | From Table | From Column | To Table | To Key |
|---|---|---|---|---|
| `FK_Reporting.FactOKR_Base(DateId)` | [Reporting].[FactJournalAnalytics_Base] | `DateID` | [Reporting].[DimDate_Base] | `PK_Reporting.DimDate_Base` |
| `FK_Reporting.FactOKR_Base(MeasureId)` | [Reporting].[FactJournalAnalytics_Base] | `MeasureID` | [Reporting].[DimMeasure_Base] | `PK_Reporting.DimMeasure_Stage_Base` |
| `FK_Reporting.FactOKR_Base(ScenarioId)` | [Reporting].[FactJournalAnalytics_Base] | `ScenarioID` | [Reporting].[DimScenario_Base] | `PK_Reporting.Scenario` |
| `FK_Reporting.FactOKR_Base(TaxonomyId)` | [Reporting].[FactJournalAnalytics_Base] | `TaxonomyID` | [Reporting].[DimTaxonomy_Base] | `PK_Reporting.DimTaxonomy_Base` |
| `FK_Reporting.FactOKR_Drillthrough_Base(DateId)` | [Reporting].[FactJournalAnalytics_Drillthrough_Base] | `DateID` | [Reporting].[DimDate_Base] | `PK_Reporting.DimDate_Base` |
| `FK_Reporting.FactOKR_Drillthrough_Base(MeasureId)` | [Reporting].[FactJournalAnalytics_Drillthrough_Base] | `MeasureID` | [Reporting].[DimMeasure_Base] | `PK_Reporting.DimMeasure_Stage_Base` |
| `FK_Reporting.FactOKR_Drillthrough_Base(TaxonomyID)` | [Reporting].[FactJournalAnalytics_Drillthrough_Base] | `TaxonomyID` | [Reporting].[DimTaxonomy_Base] | `PK_Reporting.DimTaxonomy_Base` |
| `FK_Reporting.FactOKR_Static(DateId)` | [Reporting].[FactJournalAnalytics_Static] | `DateID` | [Reporting].[DimDate_Base] | `PK_Reporting.DimDate_Base` |
| `FK_Reporting.FactOKR_Static(MeasureId)` | [Reporting].[FactJournalAnalytics_Static] | `MeasureID` | [Reporting].[DimMeasure_Base] | `PK_Reporting.DimMeasure_Stage_Base` |
| `FK_Reporting.FactOKR_Static(ScenarioId)` | [Reporting].[FactJournalAnalytics_Static] | `ScenarioID` | [Reporting].[DimScenario_Base] | `PK_Reporting.Scenario` |
| `FK_Reporting.FactOKR_Static(TaxonomyId)` | [Reporting].[FactJournalAnalytics_Static] | `TaxonomyID` | [Reporting].[DimTaxonomy_Base] | `PK_Reporting.DimTaxonomy_Base` |
| `FK_Reporting.FactMGMT_Base(MeasureId)` | [Reporting].[FactManagementDashboard_Base] | `MeasureID` | [Reporting].[DimMeasure_Base] | `PK_Reporting.DimMeasure_Stage_Base` |
| `FK_FactSectionAnalytics_Base(DateId)` | [Reporting].[FactSectionAnalytics_Base] | `DateID` | [Reporting].[DimDate_Base] | `PK_Reporting.DimDate_Base` |
| `FK_FactSectionAnalytics_Base(MeasureId)` | [Reporting].[FactSectionAnalytics_Base] | `MeasureID` | [Reporting].[DimMeasure_Base] | `PK_Reporting.DimMeasure_Stage_Base` |
| `FK_FactSectionAnalytics_Base(ScenarioId)` | [Reporting].[FactSectionAnalytics_Base] | `ScenarioID` | [Reporting].[DimScenario_Base] | `PK_Reporting.Scenario` |
| `FK_FactSectionAnalytics_Base(TaxonomyId)` | [Reporting].[FactSectionAnalytics_Base] | `TaxonomyID` | [Reporting].[DimTaxonomySection_Base] | `PK_Reporting.DimTaxonomySection_Base` |
| `FK_Reporting.FactSectionAnalytics_Drillthrough_Base(DateId)` | [Reporting].[FactSectionAnalytics_Drillthrough_Base] | `DateID` | [Reporting].[DimDate_Base] | `PK_Reporting.DimDate_Base` |
| `FK_Reporting.FactSectionAnalytics_Drillthrough_Base(MeasureId)` | [Reporting].[FactSectionAnalytics_Drillthrough_Base] | `MeasureID` | [Reporting].[DimMeasure_Base] | `PK_Reporting.DimMeasure_Stage_Base` |
| `FK_Reporting.FactSectionAnalytics_Drillthrough_Base(TaxonomyID)` | [Reporting].[FactSectionAnalytics_Drillthrough_Base] | `TaxonomyID` | [Reporting].[DimTaxonomySection_Base] | `PK_Reporting.DimTaxonomySection_Base` |

### [ReportingDataMart] Relationships

| FK Name | From Table | From Column | To Table | To Key |
|---|---|---|---|---|
| `FK-Reporting.Articles(ArticleResearchTopicId)` | [Reporting].[Articles] | `ArticleResearchTopicId` | [Reporting].[ResearchTopics] | `PK-Reporting.ResearchTopics` |
| `FK-Reporting.Articles(ArticleTaxonomyId)` | [Reporting].[Articles] | `ArticleTaxonomyId` | [Reporting].[TaxonomyMetrics] | `PK-Reporting.TaxonomyMetrics` |
| `FK-Reporting.AuthorOrganizations(AuthorId)` | [Reporting].[AuthorOrganizations] | `AuthorId` | [Reporting].[Authors] | `PK-Reporting.Authors` |
| `FK-Reporting.AuthorOrganizations(SpaceId)` | [Reporting].[AuthorOrganizations] | `SpaceId` | [Reporting].[Spaces] | `PK-Reporting.Spaces` |
| `FK-Reporting.Authors(AuthorArticleId)` | [Reporting].[Authors] | `AuthorArticleId` | [Reporting].[Articles] | `PK-Reporting.Articles` |
| `FK-Reporting.Authors(AuthorPersonUserId)` | [Reporting].[Authors] | `AuthorPersonUserId` | [Reporting].[Persons] | `PK-Reporting.Persons` |
| `FK-Reporting.Authors(AuthorSpaceId)` | [Reporting].[Authors] | `AuthorSpaceId` | [Reporting].[Spaces] | `PK-Reporting.Spaces` |
| `FK-Reporting.Authors(AuthorTaxonomyId)` | [Reporting].[Authors] | `AuthorTaxonomyId` | [Reporting].[TaxonomyMetrics] | `PK-Reporting.TaxonomyMetrics` |
| `FK-Reporting.Authors(JournalRoleId)` | [Reporting].[Authors] | `JournalRoleId` | [Reporting].[JournalRole] | `PK-Reporting.JournalRole` |
| `FK_Reporting.CampaignMembers(CampaignMemberPersonUserId)` | [Reporting].[CampaignMembers] | `CampaignMemberPersonUserId` | [Reporting].[Persons] | `PK-Reporting.Persons` |
| `FK_Reporting.CampaignMembers(CampaignMemberTaxonomyId)` | [Reporting].[CampaignMembers] | `CampaignMemberTaxonomyId` | [Reporting].[TaxonomyMetrics] | `PK-Reporting.TaxonomyMetrics` |
| `FK-Reporting.CampaignMembers(CampaignMemberPersonUserId)` | [Reporting].[CampaignMembers] | `CampaignMemberPersonUserId` | [Reporting].[Persons] | `PK-Reporting.Persons` |
| `FK-Reporting.CampaignMembers(CampaignMemberTaxonomyId)` | [Reporting].[CampaignMembers] | `CampaignMemberTaxonomyId` | [Reporting].[TaxonomyMetrics] | `PK-Reporting.TaxonomyMetrics` |
| `FK-Reporting.Contributors(ContributorPersonUserId)` | [Reporting].[Contributors] | `ContributorPersonUserId` | [Reporting].[Persons] | `PK-Reporting.Persons` |
| `FK-Reporting.Contributors(ContributorResearchTopicId)` | [Reporting].[Contributors] | `ContributorResearchTopicId` | [Reporting].[ResearchTopics] | `PK-Reporting.ResearchTopics` |
| `FK-Reporting.Contributors(ContributorSpaceId)` | [Reporting].[Contributors] | `ContributorSpaceId` | [Reporting].[Spaces] | `PK-Reporting.Spaces` |
| `FK-Reporting.Contributors(ContributorTaxonomyId)` | [Reporting].[Contributors] | `ContributorTaxonomyId` | [Reporting].[TaxonomyMetrics] | `PK-Reporting.TaxonomyMetrics` |
| `FK-Reporting.EditorialBoardMembers(EditorialBoardMemberPersonUserId)` | [Reporting].[EditorialBoardMembers] | `EditorialBoardMemberPersonUserId` | [Reporting].[Persons] | `PK-Reporting.Persons` |
| `FK-Reporting.EditorialBoardMembers(EditorialBoardMemberSpaceId)` | [Reporting].[EditorialBoardMembers] | `EditorialBoardMemberSpaceId` | [Reporting].[Spaces] | `PK-Reporting.Spaces` |
| `FK-Reporting.EditorialBoardMembers(EditorialBoardMemberTaxonomyId)` | [Reporting].[EditorialBoardMembers] | `EditorialBoardMemberTaxonomyId` | [Reporting].[Journals] | `PK-Reporting.Journals` |
| `FK-Reporting.Journals(JournalTaxonomyId)` | [Reporting].[Journals] | `JournalTaxonomyId` | [Reporting].[TaxonomyMetrics] | `PK-Reporting.TaxonomyMetrics` |
| `FK-Reporting.ResearchTopicAbstracts(AbstractResearchTopicId)` | [Reporting].[ResearchTopicAbstracts] | `AbstractResearchTopicId` | [Reporting].[ResearchTopics] | `PK-Reporting.ResearchTopics` |
| `FK-Reporting.ResearchTopicAbstracts(AbstractTaxonomyId)` | [Reporting].[ResearchTopicAbstracts] | `AbstractTaxonomyId` | [Reporting].[TaxonomyMetrics] | `PK-Reporting.TaxonomyMetrics` |
| `FK-Reporting.ResearchTopicCoordinators(CoordinatorPersonUserId)` | [Reporting].[ResearchTopicCoordinators] | `CoordinatorPersonUserId` | [Reporting].[Persons] | `PK-Reporting.Persons` |
| `FK-Reporting.ResearchTopicCoordinators(CoordinatorResearchTopicId)` | [Reporting].[ResearchTopicCoordinators] | `CoordinatorResearchTopicId` | [Reporting].[ResearchTopics] | `PK-Reporting.ResearchTopics` |
| `FK-Reporting.ResearchTopicCoordinators(CoordinatorSpaceId)` | [Reporting].[ResearchTopicCoordinators] | `CoordinatorSpaceId` | [Reporting].[Spaces] | `PK-Reporting.Spaces` |
| `FK-Reporting.ResearchTopicCoordinators(CoordinatorTaxonomyId)` | [Reporting].[ResearchTopicCoordinators] | `CoordinatorTaxonomyId` | [Reporting].[TaxonomyMetrics] | `PK-Reporting.TaxonomyMetrics` |
| `FK-Reporting.ResearchTopicEditors(EditorPersonUserId)` | [Reporting].[ResearchTopicEditors] | `EditorPersonUserId` | [Reporting].[Persons] | `PK-Reporting.Persons` |
| `FK-Reporting.ResearchTopicEditors(EditorResearchTopicId)` | [Reporting].[ResearchTopicEditors] | `EditorResearchTopicId` | [Reporting].[ResearchTopics] | `PK-Reporting.ResearchTopics` |
| `FK-Reporting.ResearchTopicEditors(EditorSpaceId)` | [Reporting].[ResearchTopicEditors] | `EditorSpaceId` | [Reporting].[Spaces] | `PK-Reporting.Spaces` |
| `FK-Reporting.ResearchTopicEditors(EditorTaxonomyId)` | [Reporting].[ResearchTopicEditors] | `EditorTaxonomyId` | [Reporting].[TaxonomyMetrics] | `PK-Reporting.TaxonomyMetrics` |
| `FK-Reporting.ResearchTopics(ResearchTopicTaxonomyId)` | [Reporting].[ResearchTopics] | `ResearchTopicTaxonomyId` | [Reporting].[TaxonomyMetrics] | `PK-Reporting.TaxonomyMetrics` |
| `FK-Reporting.ReviewBoardMembers(ReviewBoardMemberArticleId)` | [Reporting].[ReviewBoardMembers] | `ReviewBoardMemberArticleId` | [Reporting].[Articles] | `PK-Reporting.Articles` |
| `FK-Reporting.ReviewBoardMembers(ReviewBoardMemberPersonUserId)` | [Reporting].[ReviewBoardMembers] | `ReviewBoardMemberPersonUserId` | [Reporting].[Persons] | `PK-Reporting.Persons` |
| `FK-Reporting.ReviewBoardMembers(ReviewBoardMemberSpaceId)` | [Reporting].[ReviewBoardMembers] | `ReviewBoardMemberSpaceId` | [Reporting].[Spaces] | `PK-Reporting.Spaces` |
| `FK-Reporting.ReviewBoardMembers(ReviewBoardMemberTaxonomyId)` | [Reporting].[ReviewBoardMembers] | `ReviewBoardMemberTaxonomyId` | [Reporting].[TaxonomyMetrics] | `PK-Reporting.TaxonomyMetrics` |

### [TenantsDataMarts] Relationships

| FK Name | From Table | From Column | To Table | To Key |
|---|---|---|---|---|
| `FK-Accounting.InstitutionalMembership.ArticleFunding(ArticleId)` | [Accounting].[InstitutionalMembership.ArticleFunding] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Accounting.InstitutionalMembership.ArticleFunding(DeclinationReasonId)` | [Accounting].[InstitutionalMembership.ArticleFunding] | `DeclinationReasonId` | [Accounting].[InstitutionalMembership.DeclinationReason] | `PK-Accounting.InstitutionalMembership.DeclinationReason` |
| `FK-Accounting.InstitutionalMembership.ArticleFunding(FundingDecisionId)` | [Accounting].[InstitutionalMembership.ArticleFunding] | `FundingDecisionId` | [Accounting].[InstitutionalMembership.FundingDecision] | `PK-Accounting.InstitutionalMembership.FundingDecision` |
| `FK-Accounting.InstitutionalMembership.ArticleFunding(InstitutionId)` | [Accounting].[InstitutionalMembership.ArticleFunding] | `InstitutionId` | [Accounting].[InstitutionalMembership.Institution] | `PK-Accounting.InstitutionalMembership.Institution` |
| `FK-Accounting.InstitutionalMembership.ArticleFunding(InvoiceId)` | [Accounting].[InstitutionalMembership.ArticleFunding] | `InvoiceId` | [Accounting].[Invoices_History] | `PK-Accounting.Invoices_History` |
| `FK-Accounting.InstitutionalMembership.ArticleFunding(MatchingReasonId)` | [Accounting].[InstitutionalMembership.ArticleFunding] | `MatchingReasonId` | [Accounting].[InstitutionalMembership.MatchingReason] | `PK-Accounting.InstitutionalMembership.MatchingReason` |
| `FK-Accounting.InstitutionalMembership.ArticleFunding(SpaceId)` | [Accounting].[InstitutionalMembership.ArticleFunding] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Accounting.InstitutionalMembership.ArticleFundingHistory(ArticleId)` | [Accounting].[InstitutionalMembership.ArticleFundingHistory] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Accounting.InstitutionalMembership.ArticleFundingHistory(CreatorUserId)` | [Accounting].[InstitutionalMembership.ArticleFundingHistory] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Accounting.InstitutionalMembership.ArticleFundingHistory(DeclinationReasonId)` | [Accounting].[InstitutionalMembership.ArticleFundingHistory] | `DeclinationReasonId` | [Accounting].[InstitutionalMembership.DeclinationReason] | `PK-Accounting.InstitutionalMembership.DeclinationReason` |
| `FK-Accounting.InstitutionalMembership.ArticleFundingHistory(FundingDecisionId)` | [Accounting].[InstitutionalMembership.ArticleFundingHistory] | `FundingDecisionId` | [Accounting].[InstitutionalMembership.FundingDecision] | `PK-Accounting.InstitutionalMembership.FundingDecision` |
| `FK-Accounting.InstitutionalMembership.ArticleFundingHistory(InstitutionId)` | [Accounting].[InstitutionalMembership.ArticleFundingHistory] | `InstitutionId` | [Accounting].[InstitutionalMembership.Institution] | `PK-Accounting.InstitutionalMembership.Institution` |
| `FK-Accounting.InstitutionalMembership.ArticleFundingHistory(MatchingReasonId)` | [Accounting].[InstitutionalMembership.ArticleFundingHistory] | `MatchingReasonId` | [Accounting].[InstitutionalMembership.MatchingReason] | `PK-Accounting.InstitutionalMembership.MatchingReason` |
| `FK-Accounting.InstitutionalMembership.ArticleFundingHistory(ModifierUserId)` | [Accounting].[InstitutionalMembership.ArticleFundingHistory] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Accounting.InstitutionalMembership.ArticleFundingHistory(SpaceId)` | [Accounting].[InstitutionalMembership.ArticleFundingHistory] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Accounting.InstitutionalMembership.ArticleInstitutionMatches(ArticleId)` | [Accounting].[InstitutionalMembership.ArticleInstitutionMatches] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Accounting.InstitutionalMembership.ArticleInstitutionMatches(InstitutionId)` | [Accounting].[InstitutionalMembership.ArticleInstitutionMatches] | `InstitutionId` | [Accounting].[InstitutionalMembership.Institution] | `PK-Accounting.InstitutionalMembership.Institution` |
| `FK-Accounting.InstitutionalMembership.ArticleInstitutionMatches(MatchingReasonId)` | [Accounting].[InstitutionalMembership.ArticleInstitutionMatches] | `MatchingReasonId` | [Accounting].[InstitutionalMembership.MatchingReason] | `PK-Accounting.InstitutionalMembership.MatchingReason` |
| `FK-Accounting.InstitutionalMembership.ArticleInstitutionMatches(SpaceId)` | [Accounting].[InstitutionalMembership.ArticleInstitutionMatches] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Accounting.InstitutionalMembership.Institution(BillingStatusId)` | [Accounting].[InstitutionalMembership.Institution] | `BillingStatusId` | [Accounting].[InstitutionalMembership.BillingStatus] | `PK-Accounting.InstitutionalMembership.BillingStatus` |
| `FK-Accounting.InstitutionalMembership.Institution(CapLimitCurrencyId)` | [Accounting].[InstitutionalMembership.Institution] | `CapLimitCurrencyId` | [Accounting].[Currencies] | `PK-Accounting.Currencies` |
| `FK-Accounting.InstitutionalMembership.Institution(ConsortiumInstitutionId)` | [Accounting].[InstitutionalMembership.Institution] | `ConsortiumInstitutionId` | [Accounting].[InstitutionalMembership.Institution] | `PK-Accounting.InstitutionalMembership.Institution` |
| `FK-Accounting.InstitutionalMembership.Institution(InstitutionHandlerUserId)` | [Accounting].[InstitutionalMembership.Institution] | `InstitutionHandlerUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Accounting.InstitutionalMembership.Institution(InstitutionTypeId)` | [Accounting].[InstitutionalMembership.Institution] | `InstitutionTypeId` | [Accounting].[InstitutionalMembership.InstitutionType] | `PK-Accounting.InstitutionalMembership.InstitutionType` |
| `FK-Accounting.InstitutionalMembership.Institution(MembershipBillingTypeId)` | [Accounting].[InstitutionalMembership.Institution] | `MembershipBillingTypeId` | [Accounting].[InstitutionalMembership.MembershipBillingType] | `PK-Accounting.InstitutionalMembership.MembershipBillingType` |
| `FK-Accounting.InstitutionalMembership.Institution(MembershipTypeId)` | [Accounting].[InstitutionalMembership.Institution] | `MembershipTypeId` | [Accounting].[InstitutionalMembership.MembershipType] | `PK-Accounting.InstitutionalMembership.MembershipType` |
| `FK-Accounting.InstitutionalMembership.Institution(OrganizationId)` | [Accounting].[InstitutionalMembership.Institution] | `OrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Accounting.InstitutionalMembership.Institution(RosstId)` | [Accounting].[InstitutionalMembership.Institution] | `RosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Accounting.InstitutionalMembership.Institution(SpaceId)` | [Accounting].[InstitutionalMembership.Institution] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Accounting.InvoiceItems(InvoiceId)` | [Accounting].[InvoiceItems] | `InvoiceId` | [Accounting].[Invoices_History] | `PK-Accounting.Invoices_History` |
| `FK-Accounting.InvoiceItems(RevenueItemId)` | [Accounting].[InvoiceItems] | `RevenueItemId` | [Accounting].[RevenueItems] | `PK-Accounting.RevenueItems` |
| `FK-Accounting.InvoiceItems(SpaceId)` | [Accounting].[InvoiceItems] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Accounting.InvoiceItems_Discounts(InvoiceItemId)` | [Accounting].[InvoiceItems_Discounts] | `InvoiceItemId` | [Accounting].[InvoiceItems] | `PK-Accounting.InvoiceItems` |
| `FK-Accounting.InvoiceItems_Discounts(RevenueItemDiscountId)` | [Accounting].[InvoiceItems_Discounts] | `RevenueItemDiscountId` | [Accounting].[RevenueItems_Discounts] | `PK-Accounting.RevenueItems_Discounts` |
| `FK-Accounting.InvoiceItems_Discounts(SpaceId)` | [Accounting].[InvoiceItems_Discounts] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Accounting.Invoices(ArticleId)` | [Accounting].[Invoices] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Accounting.Invoices(CreatorUserId)` | [Accounting].[Invoices] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Accounting.Invoices(CurrencyId)` | [Accounting].[Invoices] | `CurrencyId` | [Accounting].[Currencies] | `PK-Accounting.Currencies` |
| `FK-Accounting.Invoices(ModifierUserId)` | [Accounting].[Invoices] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Accounting.Invoices(RevenueId)` | [Accounting].[Invoices] | `RevenueId` | [Accounting].[Revenue] | `PK-Accounting.Revenue` |
| `FK-Accounting.Invoices(SpaceId)` | [Accounting].[Invoices] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Accounting.Invoices(StatusId)` | [Accounting].[Invoices] | `StatusId` | [Accounting].[Invoices_Status] | `PK-Accounting.Invoices_Status` |
| `FK-Accounting.Invoices(ValidityId)` | [Accounting].[Invoices] | `ValidityId` | [Accounting].[Invoices_Validity] | `PK-Accounting.Invoices_Validity` |
| `FK-Accounting.Invoices.Transactions(DiscountMappingId)` | [Accounting].[Invoices.Transactions] | `DiscountMappingId` | [Accounting].[RevenueItems_DiscountMapping] | `PK-Accounting.RevenueItems_DiscountMapping` |
| `FK-Accounting.Invoices.Transactions(InvoiceId)` | [Accounting].[Invoices.Transactions] | `InvoiceId` | [Accounting].[Invoices_History] | `PK-Accounting.Invoices_History` |
| `FK-Accounting.Invoices.Transactions(InvoiceItemDiscountId)` | [Accounting].[Invoices.Transactions] | `InvoiceItemDiscountId` | [Accounting].[InvoiceItems_Discounts] | `PK-Accounting.InvoiceItems_Discounts` |
| `FK-Accounting.Invoices.Transactions(InvoiceItemId)` | [Accounting].[Invoices.Transactions] | `InvoiceItemId` | [Accounting].[InvoiceItems] | `PK-Accounting.InvoiceItems` |
| `FK-Accounting.Invoices.Transactions(PaymentId)` | [Accounting].[Invoices.Transactions] | `PaymentId` | [Accounting].[Payments] | `PK-Accounting.Payments` |
| `FK-Accounting.Invoices.Transactions(SpaceId)` | [Accounting].[Invoices.Transactions] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Accounting.Invoices_History(ArticleId)` | [Accounting].[Invoices_History] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Accounting.Invoices_History(CreatorUserId)` | [Accounting].[Invoices_History] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Accounting.Invoices_History(CurrencyId)` | [Accounting].[Invoices_History] | `CurrencyId` | [Accounting].[Currencies] | `PK-Accounting.Currencies` |
| `FK-Accounting.Invoices_History(ModifierUserId)` | [Accounting].[Invoices_History] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Accounting.Invoices_History(RevenueId)` | [Accounting].[Invoices_History] | `RevenueId` | [Accounting].[Revenue] | `PK-Accounting.Revenue` |
| `FK-Accounting.Invoices_History(SpaceId)` | [Accounting].[Invoices_History] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Accounting.Invoices_History(StatusId)` | [Accounting].[Invoices_History] | `StatusId` | [Accounting].[Invoices_Status] | `PK-Accounting.Invoices_Status` |
| `FK-Accounting.Invoices_History(ValidityId)` | [Accounting].[Invoices_History] | `ValidityId` | [Accounting].[Invoices_Validity] | `PK-Accounting.Invoices_Validity` |
| `FK-Accounting.Invoices_Payers(CountryId)` | [Accounting].[Invoices_Payers] | `CountryId` | [Common].[Countries] | `PK-Common.Countries` |
| `FK-Accounting.Invoices_Payers(InvoiceId)` | [Accounting].[Invoices_Payers] | `InvoiceId` | [Accounting].[Invoices_History] | `PK-Accounting.Invoices_History` |
| `FK-Accounting.Invoices_Payers(OrganizationId)` | [Accounting].[Invoices_Payers] | `OrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Accounting.Invoices_Payers(PayerInstitutionOrganizationId)` | [Accounting].[Invoices_Payers] | `PayerInstitutionOrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Accounting.Invoices_Payers(PayerInstitutionRosstId)` | [Accounting].[Invoices_Payers] | `PayerInstitutionRosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Accounting.Invoices_Payers(PayerTypeId)` | [Accounting].[Invoices_Payers] | `PayerTypeId` | [Accounting].[Invoices_PayerType] | `PK-Accounting.Invoices_PayerType` |
| `FK-Accounting.Invoices_Payers(PayerUserId)` | [Accounting].[Invoices_Payers] | `PayerUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Accounting.Invoices_Payers(RosstId)` | [Accounting].[Invoices_Payers] | `RosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Accounting.Invoices_Payers(SpaceId)` | [Accounting].[Invoices_Payers] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Accounting.Payments(AccountId)` | [Accounting].[Payments] | `AccountId` | [Accounting].[Payments_Account] | `PK-Accounting.Payments_Account` |
| `FK-Accounting.Payments(ArticleId)` | [Accounting].[Payments] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Accounting.Payments(CurrencyId)` | [Accounting].[Payments] | `CurrencyId` | [Accounting].[Currencies] | `PK-Accounting.Currencies` |
| `FK-Accounting.Payments(InvoiceId)` | [Accounting].[Payments] | `InvoiceId` | [Accounting].[Invoices_History] | `PK-Accounting.Invoices_History` |
| `FK-Accounting.Payments(PayerUserId)` | [Accounting].[Payments] | `PayerUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Accounting.Payments(SpaceId)` | [Accounting].[Payments] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Accounting.Payments(TypeId)` | [Accounting].[Payments] | `TypeId` | [Accounting].[Payments_Type] | `PK-Accounting.Payments_Type` |
| `FK-Accounting.Payments_Account(SpaceId)` | [Accounting].[Payments_Account] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Accounting.RevenueItems(RevenueId)` | [Accounting].[RevenueItems] | `RevenueId` | [Accounting].[Revenue] | `PK-Accounting.Revenue` |
| `FK-Accounting.RevenueItems(SpaceId)` | [Accounting].[RevenueItems] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Accounting.RevenueItems_DiscountMapping(DiscountCategoryId)` | [Accounting].[RevenueItems_DiscountMapping] | `DiscountCategoryId` | [Accounting].[RevenueItems_DiscountCategory] | `PK-Accounting.RevenueItems_DiscountCategory` |
| `FK-Accounting.RevenueItems_DiscountMapping(DiscountTypeId)` | [Accounting].[RevenueItems_DiscountMapping] | `DiscountTypeId` | [Accounting].[RevenueItems_DiscountType] | `PK-Accounting.RevenueItems_DiscountType` |
| `FK-Accounting.RevenueItems_DiscountMapping(RevenueItemDiscountId)` | [Accounting].[RevenueItems_DiscountMapping] | `RevenueItemDiscountId` | [Accounting].[RevenueItems_Discounts] | `PK-Accounting.RevenueItems_Discounts` |
| `FK-Accounting.RevenueItems_Discounts(DiscountCategoryCode)` | [Accounting].[RevenueItems_Discounts] | `DiscountCategoryCode` | [Accounting].[DiscountCategories] | `PK-Accounting.DiscountCategories` |
| `FK-Accounting.RevenueItems_Discounts(DiscountTypeCode)` | [Accounting].[RevenueItems_Discounts] | `DiscountTypeCode` | [Accounting].[DiscountTypes] | `PK-Accounting.DiscountTypes` |
| `FK-Accounting.RevenueItems_Discounts(RevenueItemId)` | [Accounting].[RevenueItems_Discounts] | `RevenueItemId` | [Accounting].[RevenueItems] | `PK-Accounting.RevenueItems` |
| `FK-Accounting.RevenueItems_Discounts(SpaceId)` | [Accounting].[RevenueItems_Discounts] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Accounting.RevenueItems_FrontiersRevenue.History(ArticleTypeId)` | [Accounting].[RevenueItems_FrontiersRevenue.History] | `ArticleTypeId` | [Journal].[Articles_Type] | `PK-Journal.Articles_Type` |
| `FK-Accounting.RevenueItems_FrontiersRevenue.History(CurrencyId)` | [Accounting].[RevenueItems_FrontiersRevenue.History] | `CurrencyId` | [Accounting].[Currencies] | `PK-Accounting.Currencies` |
| `FK-Accounting.RevenueItems_FrontiersRevenue.History(SpaceId)` | [Accounting].[RevenueItems_FrontiersRevenue.History] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Accounting.RevenueItems_FrontiersRevenue.History(TaxonomyId)` | [Accounting].[RevenueItems_FrontiersRevenue.History] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Accounting.RevenueItems_Revenues(SpaceId)` | [Accounting].[RevenueItems_Revenues] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Analytics.IndividualTargetValues(JobProfileId)` | [Analytics].[IndividualTargetValues] | `JobProfileId` | [Common].[JobProfiles] | `PK-Common.JobProfiles` |
| `FK-Analytics.IndividualTargetValues(JournalTaxonomyId)` | [Analytics].[IndividualTargetValues] | `JournalTaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Analytics.IndividualTargetValues(MeasureId)` | [Analytics].[IndividualTargetValues] | `MeasureId` | [Analytics].[Measures] | `PK-Analytics.Measures` |
| `FK-Analytics.IndividualTargetValues(RegionBinId)` | [Analytics].[IndividualTargetValues] | `RegionBinId` | [Common].[RegionBins] | `PK-Common.RegionBins` |
| `FK-Analytics.IndividualTargetValues(SpaceId)` | [Analytics].[IndividualTargetValues] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Analytics.IndividualTargetValues(TargetTypeId)` | [Analytics].[IndividualTargetValues] | `TargetTypeId` | [Analytics].[TargetTypes] | `PK-Analytics.TargetTypes` |
| `FK-Analytics.IndividualTargetValues(WorkdayEmployeeId)` | [Analytics].[IndividualTargetValues] | `WorkdayEmployeeId` | [Network].[Employees] | `PK-Network.Employees` |
| `FK-Analytics.MeasuresMapping(MeasureId.Final)` | [Analytics].[MeasuresMapping] | `MeasureId.Final` | [Analytics].[Measures] | `PK-Analytics.Measures` |
| `FK-Analytics.MeasuresMapping(MeasureId.Original)` | [Analytics].[MeasuresMapping] | `MeasureId.Original` | [Analytics].[Measures] | `PK-Analytics.Measures` |
| `FK-Analytics.MeasuresMapping(TargetGranularityId)` | [Analytics].[MeasuresMapping] | `TargetGranularityId` | [Analytics].[TargetGranularities] | `PK-Analytics.TargetGranularities` |
| `FK-Analytics.SourceTargetValues(MeasureId)` | [Analytics].[SourceTargetValues] | `MeasureId` | [Analytics].[Measures] | `PK-Analytics.Measures` |
| `FK-Analytics.SourceTargetValues(RegionBinId)` | [Analytics].[SourceTargetValues] | `RegionBinId` | [Common].[RegionBins] | `PK-Common.RegionBins` |
| `FK-Analytics.SourceTargetValues(RegionId)` | [Analytics].[SourceTargetValues] | `RegionId` | [Common].[Regions] | `PK-Common.Regions` |
| `FK-Analytics.SourceTargetValues(TargetGranularityId)` | [Analytics].[SourceTargetValues] | `TargetGranularityId` | [Analytics].[TargetGranularities] | `PK-Analytics.TargetGranularities` |
| `FK-Analytics.SourceTargetValues(TargetTypeId)` | [Analytics].[SourceTargetValues] | `TargetTypeId` | [Analytics].[TargetTypes] | `PK-Analytics.TargetTypes` |
| `FK-Analytics.SourceTargetValues(TaxonomyId)` | [Analytics].[SourceTargetValues] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Common.Cities(CountryId)` | [Common].[Cities] | `CountryId` | [Common].[Countries] | `PK-Common.Countries` |
| `FK-Common.Cities(StateId)` | [Common].[Cities] | `StateId` | [Common].[States] | `PK-Common.States` |
| `FK-Common.Countries(ContinentId)` | [Common].[Countries] | `ContinentId` | [Common].[Continents] | `PK-Common.Continents` |
| `FK-Common.Countries_Flags(CountryId)` | [Common].[Countries_Flags] | `CountryId` | [Common].[Countries] | `PK-Common.Countries` |
| `FK-Common.Countries_Flags(FlagId)` | [Common].[Countries_Flags] | `FlagId` | [Common].[Countries_Flag] | `PK-Common.Countries_Flag` |
| `FK-Common.Countries_Names(CountryId)` | [Common].[Countries_Names] | `CountryId` | [Common].[Countries] | `PK-Common.Countries` |
| `FK-Common.Countries_Regions(CountryId)` | [Common].[Countries_Regions] | `CountryId` | [Common].[Countries] | `PK-Common.Countries` |
| `FK-Common.Organizations(MergedToOrganizationId)` | [Common].[Organizations] | `MergedToOrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Common.Organizations(OriginId)` | [Common].[Organizations] | `OriginId` | [Common].[Organizations_Origin] | `PK-Common.Organizations_Origin` |
| `FK-Common.Organizations(RosstId)` | [Common].[Organizations] | `RosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Common.Organizations_Addresses(CityId)` | [Common].[Organizations_Addresses] | `CityId` | [Common].[Cities] | `PK-Common.Cities` |
| `FK-Common.Organizations_Addresses(OrganizationId)` | [Common].[Organizations_Addresses] | `OrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Common.Organizations_Aliases(OrganizationId)` | [Common].[Organizations_Aliases] | `OrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Common.Organizations_EmailDomains(OrganizationId)` | [Common].[Organizations_EmailDomains] | `OrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Common.Organizations_Flags(FlagId)` | [Common].[Organizations_Flags] | `FlagId` | [Common].[Organizations_Flag] | `PK-Common.Organizations_Flag` |
| `FK-Common.Organizations_Flags(OrganizationId)` | [Common].[Organizations_Flags] | `OrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Common.Organizations_Hierarchy(ChildOrganizationId)` | [Common].[Organizations_Hierarchy] | `ChildOrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Common.Organizations_Hierarchy(ParentOrganizationId)` | [Common].[Organizations_Hierarchy] | `ParentOrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Common.Organizations_HierarchyAllLevelChilds(ChildOrganizationId)` | [Common].[Organizations_HierarchyAllLevelChilds] | `ChildOrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Common.Organizations_HierarchyAllLevelChilds(OrganizationId)` | [Common].[Organizations_HierarchyAllLevelChilds] | `OrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Common.Organizations_HierarchyAllLevelParents(OrganizationId)` | [Common].[Organizations_HierarchyAllLevelParents] | `OrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Common.Organizations_HierarchyAllLevelParents(ParentOrganizationId)` | [Common].[Organizations_HierarchyAllLevelParents] | `ParentOrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Common.Organizations_Rankings(OrganizationId)` | [Common].[Organizations_Rankings] | `OrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Common.Organizations_Rankings(RankingId)` | [Common].[Organizations_Rankings] | `RankingId` | [Common].[Organizations_Ranking] | `PK-Common.Organizations_Ranking` |
| `FK-Common.Organizations_Types(OrganizationId)` | [Common].[Organizations_Types] | `OrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Common.Organizations_Types(TypeId)` | [Common].[Organizations_Types] | `TypeId` | [Common].[Organizations_Type] | `PK-Common.Organizations_Type` |
| `FK-Common.ResearchOrganizations_Addresses(RosstId)` | [Common].[ResearchOrganizations_Addresses] | `RosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Common.ResearchOrganizations_ConsortiumMembership(ConsortiumRosstId)` | [Common].[ResearchOrganizations_ConsortiumMembership] | `ConsortiumRosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Common.ResearchOrganizations_ConsortiumMembership(RosstId)` | [Common].[ResearchOrganizations_ConsortiumMembership] | `RosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Common.ResearchOrganizations_Hierarchies(ParentRosstId)` | [Common].[ResearchOrganizations_Hierarchies] | `ParentRosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Common.ResearchOrganizations_Hierarchies(RosstId)` | [Common].[ResearchOrganizations_Hierarchies] | `RosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Common.ResearchOrganizations_Hierarchies(UltimateParentOrganizationTypeId)` | [Common].[ResearchOrganizations_Hierarchies] | `UltimateParentOrganizationTypeId` | [Common].[ResearchOrganizations_Type] | `PK-Common.ResearchOrganizations_Type` |
| `FK-Common.ResearchOrganizations_Mapping(RosstId)` | [Common].[ResearchOrganizations_Mapping] | `RosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Common.ResearchOrganizations_Mapping(UgaritId)` | [Common].[ResearchOrganizations_Mapping] | `UgaritId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Common.States(CountryId)` | [Common].[States] | `CountryId` | [Common].[Countries] | `PK-Common.Countries` |
| `FK-Common.Taxonomy(DefaultTaxonomyId)` | [Common].[Taxonomy] | `DefaultTaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Common.Taxonomy(DomainId)` | [Common].[Taxonomy] | `DomainId` | [Common].[Taxonomy_Domains] | `PK-Common.Taxonomy_Domains` |
| `FK-Common.Taxonomy(FieldId)` | [Common].[Taxonomy] | `FieldId` | [Common].[Taxonomy_Fields] | `PK-Common.Taxonomy_Fields` |
| `FK-Common.Taxonomy(ParentTaxonomyId)` | [Common].[Taxonomy] | `ParentTaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Common.Taxonomy(SpaceId)` | [Common].[Taxonomy] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Common.Taxonomy(SpecialtyId)` | [Common].[Taxonomy] | `SpecialtyId` | [Common].[Taxonomy_Specialties] | `PK-Common.Taxonomy_Specialties` |
| `FK-Common.Taxonomy_Domains(SpaceId)` | [Common].[Taxonomy_Domains] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Common.Taxonomy_Fields(SpaceId)` | [Common].[Taxonomy_Fields] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Common.Taxonomy_Relationships(AssociatedTaxonomyId)` | [Common].[Taxonomy_Relationships] | `AssociatedTaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Common.Taxonomy_Relationships(SpaceId)` | [Common].[Taxonomy_Relationships] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Common.Taxonomy_Relationships(TaxonomyId)` | [Common].[Taxonomy_Relationships] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Common.Taxonomy_Specialties(SpaceId)` | [Common].[Taxonomy_Specialties] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-CRM.Campaigns(ParentCampaignCRMId)` | [CRM].[Campaigns] | `ParentCampaignCRMId` | [CRM].[Campaigns] | `PK-CRM.Campaigns` |
| `FK-CRM.Campaigns(RecordTypeCRMId)` | [CRM].[Campaigns] | `RecordTypeCRMId` | [CRM].[RecordType] | `PK-CRM.RecordType` |
| `FK-CRM.Campaigns(TaxonomyId)` | [CRM].[Campaigns] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-CRM.Campaigns(UltimateParentCampaignCRMId)` | [CRM].[Campaigns] | `UltimateParentCampaignCRMId` | [CRM].[Campaigns] | `PK-CRM.Campaigns` |
| `FK-CRM.CampaignsMembers(CampaignCRMId)` | [CRM].[CampaignsMembers] | `CampaignCRMId` | [CRM].[Campaigns] | `PK-CRM.Campaigns` |
| `FK-CRM.CampaignsMembers(CampaignRecordTypeCRMId)` | [CRM].[CampaignsMembers] | `CampaignRecordTypeCRMId` | [CRM].[RecordType] | `PK-CRM.RecordType` |
| `FK-CRM.CampaignsMembers(OrganizationId)` | [CRM].[CampaignsMembers] | `OrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-CRM.CampaignsMembers(RecordTypeCRMId)` | [CRM].[CampaignsMembers] | `RecordTypeCRMId` | [CRM].[RecordType] | `PK-CRM.RecordType` |
| `FK-CRM.CampaignsMembers(RosstId)` | [CRM].[CampaignsMembers] | `RosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-CRM.CampaignsMembers(TaxonomyId)` | [CRM].[CampaignsMembers] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-CRM.CampaignsMembers(UserId)` | [CRM].[CampaignsMembers] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-CRM.ChatTranscript(ArticleId)` | [CRM].[ChatTranscript] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-CRM.ChatTranscript(CountryId)` | [CRM].[ChatTranscript] | `CountryId` | [Common].[Countries] | `PK-Common.Countries` |
| `FK-CRM.ChatTranscript(Owner.UserId)` | [CRM].[ChatTranscript] | `Owner.UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-CRM.ChatTranscript(RecordTypeCRMId)` | [CRM].[ChatTranscript] | `RecordTypeCRMId` | [CRM].[RecordType] | `PK-CRM.RecordType` |
| `FK-CRM.ChatTranscript(Requester.RoleId)` | [CRM].[ChatTranscript] | `Requester.RoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-CRM.ChatTranscript(Requester.UserId)` | [CRM].[ChatTranscript] | `Requester.UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-CRM.ChatTranscript(SpaceId)` | [CRM].[ChatTranscript] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-CRM.Contracts(RosstId)` | [CRM].[Contracts] | `RosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-CRM.Discounts(ArticleId)` | [CRM].[Discounts] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-CRM.Discounts(CurrencyId)` | [CRM].[Discounts] | `CurrencyId` | [Accounting].[Currencies] | `PK-Accounting.Currencies` |
| `FK-CRM.Discounts(DiscountCategoryCode)` | [CRM].[Discounts] | `DiscountCategoryCode` | [Accounting].[DiscountCategories] | `PK-Accounting.DiscountCategories` |
| `FK-CRM.Discounts(DiscountTypeCode)` | [CRM].[Discounts] | `DiscountTypeCode` | [Accounting].[DiscountTypes] | `PK-Accounting.DiscountTypes` |
| `FK-CRM.Discounts(JournalTaxonomyId)` | [CRM].[Discounts] | `JournalTaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-CRM.Discounts(Referrer.UserId)` | [CRM].[Discounts] | `Referrer.UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-CRM.Discounts(ResearchTopicId)` | [CRM].[Discounts] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-CRM.Discounts(SpaceId)` | [CRM].[Discounts] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-CRM.Employees(EmployeeRoleId)` | [CRM].[Employees] | `EmployeeRoleId` | [CRM].[EmployeeRole] | `PK-CRM.EmployeeRole` |
| `FK-CRM.Employees(EmploymentCountryId)` | [CRM].[Employees] | `EmploymentCountryId` | [Common].[Countries] | `PK-Common.Countries` |
| `FK-CRM.Employees(UserId)` | [CRM].[Employees] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-CRM.Opportunities(CampaignCRMId)` | [CRM].[Opportunities] | `CampaignCRMId` | [CRM].[Campaigns] | `PK-CRM.Campaigns` |
| `FK-CRM.Opportunities(ContactOrganizationId)` | [CRM].[Opportunities] | `ContactOrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-CRM.Opportunities(ContactRosstId)` | [CRM].[Opportunities] | `ContactRosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-CRM.Opportunities(ContactUserId)` | [CRM].[Opportunities] | `ContactUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-CRM.Opportunities(OwnerUserId)` | [CRM].[Opportunities] | `OwnerUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-CRM.Opportunities(ParentOpportunityCRMId)` | [CRM].[Opportunities] | `ParentOpportunityCRMId` | [CRM].[Opportunities] | `PK-CRM.Opportunities` |
| `FK-CRM.Opportunities(RecordTypeCRMId)` | [CRM].[Opportunities] | `RecordTypeCRMId` | [CRM].[RecordType] | `PK-CRM.RecordType` |
| `FK-CRM.Opportunities(ResearchTopicId)` | [CRM].[Opportunities] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-CRM.Opportunities(TaxonomyId)` | [CRM].[Opportunities] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-CRM.OpportunitiesContactsRoles(ContactUserId)` | [CRM].[OpportunitiesContactsRoles] | `ContactUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-CRM.OpportunitiesContactsRoles(OpportunityCRMId)` | [CRM].[OpportunitiesContactsRoles] | `OpportunityCRMId` | [CRM].[Opportunities] | `PK-CRM.Opportunities` |
| `FK-CRM.OpportunitiesStages(OpportunityCRMId)` | [CRM].[OpportunitiesStages] | `OpportunityCRMId` | [CRM].[Opportunities] | `PK-CRM.Opportunities` |
| `FK-CRM.ResearchTopicsEvents(EventCreatorUserId)` | [CRM].[ResearchTopicsEvents] | `EventCreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-CRM.ResearchTopicsEvents(ResearchTopicId)` | [CRM].[ResearchTopicsEvents] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-CRM.ResearchTopicsEvents(SpaceId)` | [CRM].[ResearchTopicsEvents] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles(CreatorUserId)` | [Journal].[Articles] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles(RequestedRevisionLevelId)` | [Journal].[Articles] | `RequestedRevisionLevelId` | [Journal].[Articles_RequestedRevisionLevel] | `PK-Journal.Articles_RequestedRevisionLevel` |
| `FK-Journal.Articles(ResearchIntegrity.Owner.UserId)` | [Journal].[Articles] | `ResearchIntegrity.Owner.UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles(ResearchTopicId)` | [Journal].[Articles] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.Articles(ReviewOperations.Owner.UserId)` | [Journal].[Articles] | `ReviewOperations.Owner.UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles(SpaceId)` | [Journal].[Articles] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles(StageId)` | [Journal].[Articles] | `StageId` | [Journal].[Articles_Stage] | `PK-Journal.Articles_Stage` |
| `FK-Journal.Articles(SuggestedforResearchTopic.StatusId)` | [Journal].[Articles] | `SuggestedforResearchTopic.StatusId` | [Journal].[ResearchTopic_SuggestedArticleStatus] | `PK-Journal.ResearchTopic_SuggestedArticleStatus` |
| `FK-Journal.Articles(TaxonomyId)` | [Journal].[Articles] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.Articles(TypeId)` | [Journal].[Articles] | `TypeId` | [Journal].[Articles_Type] | `PK-Journal.Articles_Type` |
| `FK-Journal.Articles(TypeSetterUserId)` | [Journal].[Articles] | `TypeSetterUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_Activities(ArticleId)` | [Journal].[Articles_Activities] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_Activities(SpaceId)` | [Journal].[Articles_Activities] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Affiliations_Legacy(CountryId)` | [Journal].[Articles_Affiliations_Legacy] | `CountryId` | [Common].[Countries] | `PK-Common.Countries` |
| `FK-Journal.Articles_Affiliations_Legacy(RosstId)` | [Journal].[Articles_Affiliations_Legacy] | `RosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Journal.Articles_Affiliations_Legacy(SpaceId)` | [Journal].[Articles_Affiliations_Legacy] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AIRA(ArticleId)` | [Journal].[Articles_AIRA] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_AIRA(SpaceId)` | [Journal].[Articles_AIRA] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AIRA(StatusId)` | [Journal].[Articles_AIRA] | `StatusId` | [Journal].[Articles_AIRAStatus] | `PK-Journal.Articles_AIRAStatus` |
| `FK-Journal.Articles_AIRAActions(ActionTypeId)` | [Journal].[Articles_AIRAActions] | `ActionTypeId` | [Journal].[Articles_AIRAActionType] | `PK-Journal.Articles_AIRAActionType` |
| `FK-Journal.Articles_AIRAActions(ArticleId)` | [Journal].[Articles_AIRAActions] | `ArticleId` | [Journal].[Articles_AIRA] | `PK-Journal.Articles_AIRA` |
| `FK-Journal.Articles_AIRAActions(ArticleStageId)` | [Journal].[Articles_AIRAActions] | `ArticleStageId` | [Journal].[Articles_Stage] | `PK-Journal.Articles_Stage` |
| `FK-Journal.Articles_AIRAActions(ReportId)` | [Journal].[Articles_AIRAActions] | `ReportId` | [Journal].[Articles_AIRAReports] | `PK-Journal.Articles_AIRAReports` |
| `FK-Journal.Articles_AIRAActions(SpaceId)` | [Journal].[Articles_AIRAActions] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AIRAActions(TriggerId)` | [Journal].[Articles_AIRAActions] | `TriggerId` | [Journal].[Articles_AIRATriggers] | `PK-Journal.Articles_AIRATriggers` |
| `FK-Journal.Articles_AIRACategories(ArticleId)` | [Journal].[Articles_AIRACategories] | `ArticleId` | [Journal].[Articles_AIRA] | `PK-Journal.Articles_AIRA` |
| `FK-Journal.Articles_AIRACategories(CategoryStatusId)` | [Journal].[Articles_AIRACategories] | `CategoryStatusId` | [Journal].[Articles_AIRACategoryStatus] | `PK-Journal.Articles_AIRACategoryStatus` |
| `FK-Journal.Articles_AIRACategories(CategoryTypeId)` | [Journal].[Articles_AIRACategories] | `CategoryTypeId` | [Journal].[Articles_AIRACategoryType] | `PK-Journal.Articles_AIRACategoryType` |
| `FK-Journal.Articles_AIRACategories(ReportId)` | [Journal].[Articles_AIRACategories] | `ReportId` | [Journal].[Articles_AIRAReports] | `PK-Journal.Articles_AIRAReports` |
| `FK-Journal.Articles_AIRACategories(SpaceId)` | [Journal].[Articles_AIRACategories] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AIRACategories(TriggerId)` | [Journal].[Articles_AIRACategories] | `TriggerId` | [Journal].[Articles_AIRATriggers] | `PK-Journal.Articles_AIRATriggers` |
| `FK-Journal.Articles_AIRAIndicatorGroups(ArticleId)` | [Journal].[Articles_AIRAIndicatorGroups] | `ArticleId` | [Journal].[Articles_AIRA] | `PK-Journal.Articles_AIRA` |
| `FK-Journal.Articles_AIRAIndicatorGroups(CategoryId)` | [Journal].[Articles_AIRAIndicatorGroups] | `CategoryId` | [Journal].[Articles_AIRACategories] | `PK-Journal.Articles_AIRACategories` |
| `FK-Journal.Articles_AIRAIndicatorGroups(IndicatorGroupStatusId)` | [Journal].[Articles_AIRAIndicatorGroups] | `IndicatorGroupStatusId` | [Journal].[Articles_AIRAIndicatorGroupStatus] | `PK-Journal.Articles_AIRAIndicatorGroupStatus` |
| `FK-Journal.Articles_AIRAIndicatorGroups(IndicatorGroupTypeId)` | [Journal].[Articles_AIRAIndicatorGroups] | `IndicatorGroupTypeId` | [Journal].[Articles_AIRAIndicatorGroupType] | `PK-Journal.Articles_AIRAIndicatorGroupType` |
| `FK-Journal.Articles_AIRAIndicatorGroups(ReportId)` | [Journal].[Articles_AIRAIndicatorGroups] | `ReportId` | [Journal].[Articles_AIRAReports] | `PK-Journal.Articles_AIRAReports` |
| `FK-Journal.Articles_AIRAIndicatorGroups(SpaceId)` | [Journal].[Articles_AIRAIndicatorGroups] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AIRAIndicatorGroups(TriggerId)` | [Journal].[Articles_AIRAIndicatorGroups] | `TriggerId` | [Journal].[Articles_AIRATriggers] | `PK-Journal.Articles_AIRATriggers` |
| `FK-Journal.Articles_AIRAIndicatorGroupType(SpaceId)` | [Journal].[Articles_AIRAIndicatorGroupType] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AIRAIndicators(ArticleId)` | [Journal].[Articles_AIRAIndicators] | `ArticleId` | [Journal].[Articles_AIRA] | `PK-Journal.Articles_AIRA` |
| `FK-Journal.Articles_AIRAIndicators(CategoryId)` | [Journal].[Articles_AIRAIndicators] | `CategoryId` | [Journal].[Articles_AIRACategories] | `PK-Journal.Articles_AIRACategories` |
| `FK-Journal.Articles_AIRAIndicators(IndicatorGroupId)` | [Journal].[Articles_AIRAIndicators] | `IndicatorGroupId` | [Journal].[Articles_AIRAIndicatorGroups] | `PK-Journal.Articles_AIRAIndicatorGroups` |
| `FK-Journal.Articles_AIRAIndicators(IndicatorStatusId)` | [Journal].[Articles_AIRAIndicators] | `IndicatorStatusId` | [Journal].[Articles_AIRAIndicatorStatus] | `PK-Journal.Articles_AIRAIndicatorStatus` |
| `FK-Journal.Articles_AIRAIndicators(IndicatorTypeId)` | [Journal].[Articles_AIRAIndicators] | `IndicatorTypeId` | [Journal].[Articles_AIRAIndicatorType] | `PK-Journal.Articles_AIRAIndicatorType` |
| `FK-Journal.Articles_AIRAIndicators(ReportId)` | [Journal].[Articles_AIRAIndicators] | `ReportId` | [Journal].[Articles_AIRAReports] | `PK-Journal.Articles_AIRAReports` |
| `FK-Journal.Articles_AIRAIndicators(SpaceId)` | [Journal].[Articles_AIRAIndicators] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AIRAIndicators(TriggerId)` | [Journal].[Articles_AIRAIndicators] | `TriggerId` | [Journal].[Articles_AIRATriggers] | `PK-Journal.Articles_AIRATriggers` |
| `FK-Journal.Articles_AIRAIndicatorScenarios(IndicatorId)` | [Journal].[Articles_AIRAIndicatorScenarios] | `IndicatorId` | [Journal].[Articles_AIRAIndicators] | `PK-Journal.Articles_AIRAIndicators` |
| `FK-Journal.Articles_AIRAIndicatorScenarios(IndicatorScenarioTypeId)` | [Journal].[Articles_AIRAIndicatorScenarios] | `IndicatorScenarioTypeId` | [Journal].[Articles_AIRAIndicatorScenarioType] | `PK-Journal.Articles_AIRAIndicatorScenarioType` |
| `FK-Journal.Articles_AIRAIndicatorScenarios(SpaceId)` | [Journal].[Articles_AIRAIndicatorScenarios] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AIRAIndicatorScenarioType(ParentIndicatorScenarioTypeId)` | [Journal].[Articles_AIRAIndicatorScenarioType] | `ParentIndicatorScenarioTypeId` | [Journal].[Articles_AIRAIndicatorScenarioType] | `PK-Journal.Articles_AIRAIndicatorScenarioType` |
| `FK-Journal.Articles_AIRAIndicatorScenarioType(SpaceId)` | [Journal].[Articles_AIRAIndicatorScenarioType] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AIRAIndicatorType(SpaceId)` | [Journal].[Articles_AIRAIndicatorType] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AIRAReports(ArticleId)` | [Journal].[Articles_AIRAReports] | `ArticleId` | [Journal].[Articles_AIRA] | `PK-Journal.Articles_AIRA` |
| `FK-Journal.Articles_AIRAReports(ReportTypeId)` | [Journal].[Articles_AIRAReports] | `ReportTypeId` | [Journal].[Articles_AIRAReportType] | `PK-Journal.Articles_AIRAReportType` |
| `FK-Journal.Articles_AIRAReports(RIProcessStateId)` | [Journal].[Articles_AIRAReports] | `RIProcessStateId` | [Journal].[Articles_AIRARIProcessState] | `PK-Journal.Articles_AIRARIProcessState` |
| `FK-Journal.Articles_AIRAReports(SpaceId)` | [Journal].[Articles_AIRAReports] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AIRAReports(TriggerId)` | [Journal].[Articles_AIRAReports] | `TriggerId` | [Journal].[Articles_AIRATriggers] | `PK-Journal.Articles_AIRATriggers` |
| `FK-Journal.Articles_AIRAServiceLevels(ArticleId)` | [Journal].[Articles_AIRAServiceLevels] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_AIRAServiceLevels(SpaceId)` | [Journal].[Articles_AIRAServiceLevels] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AIRATriggers(ArticleId)` | [Journal].[Articles_AIRATriggers] | `ArticleId` | [Journal].[Articles_AIRA] | `PK-Journal.Articles_AIRA` |
| `FK-Journal.Articles_AIRATriggers(SpaceId)` | [Journal].[Articles_AIRATriggers] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AIRATriggers(TriggerStatusId)` | [Journal].[Articles_AIRATriggers] | `TriggerStatusId` | [Journal].[Articles_AIRATriggerStatus] | `PK-Journal.Articles_AIRATriggerStatus` |
| `FK-Journal.Articles_AIRATriggers(TriggerTypeId)` | [Journal].[Articles_AIRATriggers] | `TriggerTypeId` | [Journal].[Articles_AIRATriggerType] | `PK-Journal.Articles_AIRATriggerType` |
| `FK-Journal.Articles_Authors(ArticleId)` | [Journal].[Articles_Authors] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_Authors(AuthorUserId)` | [Journal].[Articles_Authors] | `AuthorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_Authors(JournalRoleId)` | [Journal].[Articles_Authors] | `JournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.Articles_Authors(PersonId)` | [Journal].[Articles_Authors] | `PersonId` | [Person].[Persons] | `PK-Person.Persons` |
| `FK-Journal.Articles_Authors(RoleId)` | [Journal].[Articles_Authors] | `RoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_Authors(SpaceId)` | [Journal].[Articles_Authors] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Authors(TitleId)` | [Journal].[Articles_Authors] | `TitleId` | [Network].[Users_Title] | `PK-Network.Users_Title` |
| `FK-Journal.Articles_Authors.Concatenated(ArticleId)` | [Journal].[Articles_Authors.Concatenated] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_Authors.Concatenated(SpaceId)` | [Journal].[Articles_Authors.Concatenated] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Authors.Production(ArticleId)` | [Journal].[Articles_Authors.Production] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_Authors.Production(SpaceId)` | [Journal].[Articles_Authors.Production] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Authors.Production(UserId)` | [Journal].[Articles_Authors.Production] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_Authors.Review(ArticleId)` | [Journal].[Articles_Authors.Review] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_Authors.Review(PersonId)` | [Journal].[Articles_Authors.Review] | `PersonId` | [Person].[Persons] | `PK-Person.Persons` |
| `FK-Journal.Articles_Authors.Review(SpaceId)` | [Journal].[Articles_Authors.Review] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Authors.Review(UserId)` | [Journal].[Articles_Authors.Review] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_AuthorsAffiliations(AffiliationId)` | [Journal].[Articles_AuthorsAffiliations] | `AffiliationId` | [Journal].[Articles_Affiliations_Legacy] | `PK-Journal.Articles_Affiliations_Legacy` |
| `FK-Journal.Articles_AuthorsAffiliations(AuthorId)` | [Journal].[Articles_AuthorsAffiliations] | `AuthorId` | [Journal].[Articles_Authors] | `PK-Journal.Articles_Authors` |
| `FK-Journal.Articles_AuthorsAffiliations(SpaceId)` | [Journal].[Articles_AuthorsAffiliations] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AuthorsOrganizations(AuthorId)` | [Journal].[Articles_AuthorsOrganizations] | `AuthorId` | [Journal].[Articles_Authors] | `PK-Journal.Articles_Authors` |
| `FK-Journal.Articles_AuthorsOrganizations(OrganizationId)` | [Journal].[Articles_AuthorsOrganizations] | `OrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Journal.Articles_AuthorsOrganizations(OrganizationSourceId)` | [Journal].[Articles_AuthorsOrganizations] | `OrganizationSourceId` | [Common].[Organizations_Source] | `PK-Common.Organizations_Source` |
| `FK-Journal.Articles_AuthorsOrganizations(RosstId)` | [Journal].[Articles_AuthorsOrganizations] | `RosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Journal.Articles_AuthorsOrganizations(SpaceId)` | [Journal].[Articles_AuthorsOrganizations] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AuthorsOrganizations.Production(AuthorId)` | [Journal].[Articles_AuthorsOrganizations.Production] | `AuthorId` | [Journal].[Articles_Authors] | `PK-Journal.Articles_Authors` |
| `FK-Journal.Articles_AuthorsOrganizations.Production(OrganizationSourceId)` | [Journal].[Articles_AuthorsOrganizations.Production] | `OrganizationSourceId` | [Common].[Organizations_Source] | `PK-Common.Organizations_Source` |
| `FK-Journal.Articles_AuthorsOrganizations.Production(RosstId)` | [Journal].[Articles_AuthorsOrganizations.Production] | `RosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Journal.Articles_AuthorsOrganizations.Production(SpaceId)` | [Journal].[Articles_AuthorsOrganizations.Production] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AuthorsOrganizations.Review(AuthorId)` | [Journal].[Articles_AuthorsOrganizations.Review] | `AuthorId` | [Journal].[Articles_Authors] | `PK-Journal.Articles_Authors` |
| `FK-Journal.Articles_AuthorsOrganizations.Review(OrganizationSourceId)` | [Journal].[Articles_AuthorsOrganizations.Review] | `OrganizationSourceId` | [Common].[Organizations_Source] | `PK-Common.Organizations_Source` |
| `FK-Journal.Articles_AuthorsOrganizations.Review(RosstId)` | [Journal].[Articles_AuthorsOrganizations.Review] | `RosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Journal.Articles_AuthorsOrganizations.Review(SpaceId)` | [Journal].[Articles_AuthorsOrganizations.Review] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_AuthorsSuggestedReviewers(ArticleId)` | [Journal].[Articles_AuthorsSuggestedReviewers] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_AuthorsSuggestedReviewers(AuthorUserId)` | [Journal].[Articles_AuthorsSuggestedReviewers] | `AuthorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_AuthorsSuggestedReviewers(CreatorUserId)` | [Journal].[Articles_AuthorsSuggestedReviewers] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_AuthorsSuggestedReviewers(ModifierUserId)` | [Journal].[Articles_AuthorsSuggestedReviewers] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_AuthorsSuggestedReviewers(ReviewerUserId)` | [Journal].[Articles_AuthorsSuggestedReviewers] | `ReviewerUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_AuthorsSuggestedReviewers(SpaceId)` | [Journal].[Articles_AuthorsSuggestedReviewers] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Citations(ArticleId)` | [Journal].[Articles_Citations] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_Citations(ImpactActionId)` | [Journal].[Articles_Citations] | `ImpactActionId` | [Common].[Impacts_Action] | `PK-Common.Impacts_Action` |
| `FK-Journal.Articles_Citations(ImpactAggregationId)` | [Journal].[Articles_Citations] | `ImpactAggregationId` | [Common].[Impacts_Aggregation] | `PK-Common.Impacts_Aggregation` |
| `FK-Journal.Articles_Citations(SpaceId)` | [Journal].[Articles_Citations] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_DiscoverFeedback(ArticleFeedbackTypeId)` | [Journal].[Articles_DiscoverFeedback] | `ArticleFeedbackTypeId` | [Journal].[Articles_DiscoverFeedbackType] | `PK-Journal.Articles_DiscoverFeedbackType` |
| `FK-Journal.Articles_DiscoverFeedback(ArticleId)` | [Journal].[Articles_DiscoverFeedback] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_DiscoverFeedback(SpaceId)` | [Journal].[Articles_DiscoverFeedback] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_DiscoverFeedback(UserId)` | [Journal].[Articles_DiscoverFeedback] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_Funder(SpaceId)` | [Journal].[Articles_Funder] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Funding(ArticleId)` | [Journal].[Articles_Funding] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_Funding(FunderId)` | [Journal].[Articles_Funding] | `FunderId` | [Journal].[Articles_Funder] | `PK-Journal.Articles_Funder` |
| `FK-Journal.Articles_Funding(SpaceId)` | [Journal].[Articles_Funding] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Inaugurals(ArticleId)` | [Journal].[Articles_Inaugurals] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_Inaugurals(RoleId)` | [Journal].[Articles_Inaugurals] | `RoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_Inaugurals(SpaceId)` | [Journal].[Articles_Inaugurals] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Inaugurals(UserId)` | [Journal].[Articles_Inaugurals] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_JournalTransfers(ArticleId)` | [Journal].[Articles_JournalTransfers] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_JournalTransfers(ConfirmationCancellerJournalRoleId)` | [Journal].[Articles_JournalTransfers] | `ConfirmationCancellerJournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.Articles_JournalTransfers(ConfirmationCancellerRoleId)` | [Journal].[Articles_JournalTransfers] | `ConfirmationCancellerRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_JournalTransfers(ConfirmationCancellerUserId)` | [Journal].[Articles_JournalTransfers] | `ConfirmationCancellerUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_JournalTransfers(ConfirmerJournalRoleId)` | [Journal].[Articles_JournalTransfers] | `ConfirmerJournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.Articles_JournalTransfers(ConfirmerRoleId)` | [Journal].[Articles_JournalTransfers] | `ConfirmerRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_JournalTransfers(ConfirmerUserId)` | [Journal].[Articles_JournalTransfers] | `ConfirmerUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_JournalTransfers(DestinationResearchTopicId)` | [Journal].[Articles_JournalTransfers] | `DestinationResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.Articles_JournalTransfers(DestinationTaxonomyId)` | [Journal].[Articles_JournalTransfers] | `DestinationTaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.Articles_JournalTransfers(InitialArticleStageId)` | [Journal].[Articles_JournalTransfers] | `InitialArticleStageId` | [Journal].[Articles_Stage] | `PK-Journal.Articles_Stage` |
| `FK-Journal.Articles_JournalTransfers(InitiatorJournalRoleId)` | [Journal].[Articles_JournalTransfers] | `InitiatorJournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.Articles_JournalTransfers(InitiatorRoleId)` | [Journal].[Articles_JournalTransfers] | `InitiatorRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_JournalTransfers(InitiatorUserId)` | [Journal].[Articles_JournalTransfers] | `InitiatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_JournalTransfers(SourceResearchTopicId)` | [Journal].[Articles_JournalTransfers] | `SourceResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.Articles_JournalTransfers(SourceTaxonomyId)` | [Journal].[Articles_JournalTransfers] | `SourceTaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.Articles_JournalTransfers(SpaceId)` | [Journal].[Articles_JournalTransfers] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_JournalTransfers(ValidatorJournalRoleId)` | [Journal].[Articles_JournalTransfers] | `ValidatorJournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.Articles_JournalTransfers(ValidatorRoleId)` | [Journal].[Articles_JournalTransfers] | `ValidatorRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_JournalTransfers(ValidatorUserId)` | [Journal].[Articles_JournalTransfers] | `ValidatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_Keywords(ArticleId)` | [Journal].[Articles_Keywords] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_Keywords(KeywordId)` | [Journal].[Articles_Keywords] | `KeywordId` | [Journal].[Keywords] | `PK-Journal.Keywords` |
| `FK-Journal.Articles_Keywords(SpaceId)` | [Journal].[Articles_Keywords] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Keywords.Concatenated(ArticleId)` | [Journal].[Articles_Keywords.Concatenated] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_Keywords.Concatenated(SpaceId)` | [Journal].[Articles_Keywords.Concatenated] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_RelatedArticle(ArticleId)` | [Journal].[Articles_RelatedArticle] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_RelatedArticle(RelatedArticleId)` | [Journal].[Articles_RelatedArticle] | `RelatedArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_RelatedArticle(RelationshipTypeId)` | [Journal].[Articles_RelatedArticle] | `RelationshipTypeId` | [Journal].[Articles_RelatedArticleType] | `PK-Journal.Articles_RelatedArticleType` |
| `FK-Journal.Articles_RelatedArticle(SpaceId)` | [Journal].[Articles_RelatedArticle] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Review.Events(ArticleId)` | [Journal].[Articles_Review.Events] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_Review.Events(CreatorRoleId)` | [Journal].[Articles_Review.Events] | `CreatorRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_Review.Events(CreatorUserId)` | [Journal].[Articles_Review.Events] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_Review.Events(RecipientRoleId)` | [Journal].[Articles_Review.Events] | `RecipientRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_Review.Events(RecipientUserId)` | [Journal].[Articles_Review.Events] | `RecipientUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_Review.Events(ReviewEventId)` | [Journal].[Articles_Review.Events] | `ReviewEventId` | [Journal].[Articles_Review.Event] | `PK-Journal.Articles_Review.Event` |
| `FK-Journal.Articles_Review.Events(SpaceId)` | [Journal].[Articles_Review.Events] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Review.Events(WorkflowId)` | [Journal].[Articles_Review.Events] | `WorkflowId` | [Journal].[Workflows] | `PK-Journal.Workflows` |
| `FK-Journal.Articles_Review.Events(WorkflowStatusId)` | [Journal].[Articles_Review.Events] | `WorkflowStatusId` | [Journal].[Workflows_Status] | `PK-Journal.Workflows_Status` |
| `FK-Journal.Articles_ReviewActionReason(SpaceId)` | [Journal].[Articles_ReviewActionReason] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewActionReasons(ReviewActionReasonId)` | [Journal].[Articles_ReviewActionReasons] | `ReviewActionReasonId` | [Journal].[Articles_ReviewActionReason] | `PK-Journal.Articles_ReviewActionReason` |
| `FK-Journal.Articles_ReviewActionReasons(ReviewBoardInvitationId)` | [Journal].[Articles_ReviewActionReasons] | `ReviewBoardInvitationId` | [Journal].[Articles_ReviewBoardInvitations] | `PK-Journal.Articles_ReviewBoardInvitations` |
| `FK-Journal.Articles_ReviewActionReasons(SpaceId)` | [Journal].[Articles_ReviewActionReasons] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewActionSubReason(SpaceId)` | [Journal].[Articles_ReviewActionSubReason] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewArticleRejectionReasons(ArticleId)` | [Journal].[Articles_ReviewArticleRejectionReasons] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ReviewArticleRejectionReasons(ReviewActionReasonId)` | [Journal].[Articles_ReviewArticleRejectionReasons] | `ReviewActionReasonId` | [Journal].[Articles_ReviewActionReason] | `PK-Journal.Articles_ReviewActionReason` |
| `FK-Journal.Articles_ReviewArticleRejectionReasons(ReviewActionSubReasonId)` | [Journal].[Articles_ReviewArticleRejectionReasons] | `ReviewActionSubReasonId` | [Journal].[Articles_ReviewActionSubReason] | `PK-Journal.Articles_ReviewActionSubReason` |
| `FK-Journal.Articles_ReviewArticleRejectionReasons(SpaceId)` | [Journal].[Articles_ReviewArticleRejectionReasons] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewBoardConflictOfInterests(ArticleId)` | [Journal].[Articles_ReviewBoardConflictOfInterests] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ReviewBoardConflictOfInterests(ConflictOfInterestsQuestionId)` | [Journal].[Articles_ReviewBoardConflictOfInterests] | `ConflictOfInterestsQuestionId` | [Journal].[Articles_ReviewBoardConflictOfInterestsQuestion] | `PK-Journal.Articles_ReviewBoardConflictOfInterestsQuestion` |
| `FK-Journal.Articles_ReviewBoardConflictOfInterests(SpaceId)` | [Journal].[Articles_ReviewBoardConflictOfInterests] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewBoardConflictOfInterests(UserId)` | [Journal].[Articles_ReviewBoardConflictOfInterests] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers(ArticleId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers(CreatorUserId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers(ModifierUserId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers(ReviewBoardMemberId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers] | `ReviewBoardMemberId` | [Journal].[Articles_ReviewBoardMembers] | `PK-Journal.Articles_ReviewBoardMembers` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers(SpaceId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers(UserId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers.ExclusionReason(CreatorUserId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers.ExclusionReason] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers.ExclusionReason(ModifierUserId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers.ExclusionReason] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers.Exclusions(ArticleId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers.Exclusions] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers.Exclusions(CreatorUserId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers.Exclusions] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers.Exclusions(ModifierUserId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers.Exclusions] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers.Exclusions(ReviewBoardMemberId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers.Exclusions] | `ReviewBoardMemberId` | [Journal].[Articles_ReviewBoardMembers] | `PK-Journal.Articles_ReviewBoardMembers` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers.Exclusions(ReviewBoardVolunteerExclusionReasonId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers.Exclusions] | `ReviewBoardVolunteerExclusionReasonId` | [Journal].[Articles_ReviewBoardDiscoverVolunteers.ExclusionReason] | `PK-Journal.Articles_ReviewBoardDiscoverVolunteers.ExclusionReason` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers.Exclusions(SpaceId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers.Exclusions] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers.Exclusions(StageId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers.Exclusions] | `StageId` | [Journal].[Articles_Stage] | `PK-Journal.Articles_Stage` |
| `FK-Journal.Articles_ReviewBoardDiscoverVolunteers.Exclusions(UserId)` | [Journal].[Articles_ReviewBoardDiscoverVolunteers.Exclusions] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardInvitations(ArticleId)` | [Journal].[Articles_ReviewBoardInvitations] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ReviewBoardInvitations(AuthorReviewerSuggestionTypeId)` | [Journal].[Articles_ReviewBoardInvitations] | `AuthorReviewerSuggestionTypeId` | [Journal].[Articles_AuthorsSuggestedReviewer.SuggestionType] | `PK-Journal.Articles_AuthorsSuggestedReviewer.SuggestionType` |
| `FK-Journal.Articles_ReviewBoardInvitations(CreatorJournalRoleId)` | [Journal].[Articles_ReviewBoardInvitations] | `CreatorJournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.Articles_ReviewBoardInvitations(CreatorOriginalRoleId)` | [Journal].[Articles_ReviewBoardInvitations] | `CreatorOriginalRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_ReviewBoardInvitations(CreatorRoleId)` | [Journal].[Articles_ReviewBoardInvitations] | `CreatorRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_ReviewBoardInvitations(CreatorUserId)` | [Journal].[Articles_ReviewBoardInvitations] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardInvitations(InvitationAlgorithmTypeId)` | [Journal].[Articles_ReviewBoardInvitations] | `InvitationAlgorithmTypeId` | [Journal].[Articles_ReviewBoardInvitationAlgorithmType] | `PK-Journal.Articles_ReviewBoardInvitationAlgorithmType` |
| `FK-Journal.Articles_ReviewBoardInvitations(InvitationAudienceGroupId)` | [Journal].[Articles_ReviewBoardInvitations] | `InvitationAudienceGroupId` | [Journal].[Articles_ReviewBoardInvitationAudienceGroup] | `PK-Journal.Articles_ReviewBoardInvitationAudienceGroup` |
| `FK-Journal.Articles_ReviewBoardInvitations(InvitationMethodId)` | [Journal].[Articles_ReviewBoardInvitations] | `InvitationMethodId` | [Journal].[Articles_ReviewBoardInvitationMethod] | `PK-Journal.Articles_ReviewBoardInvitationMethod` |
| `FK-Journal.Articles_ReviewBoardInvitations(InvitationStatusId)` | [Journal].[Articles_ReviewBoardInvitations] | `InvitationStatusId` | [Journal].[Articles_ReviewBoardInvitationStatus] | `PK-Journal.Articles_ReviewBoardInvitationStatus` |
| `FK-Journal.Articles_ReviewBoardInvitations(InvitationWorkflowEmailId)` | [Journal].[Articles_ReviewBoardInvitations] | `InvitationWorkflowEmailId` | [Journal].[Workflows_Emails] | `PK-Journal.Workflows_Emails` |
| `FK-Journal.Articles_ReviewBoardInvitations(InvitationWorkflowId)` | [Journal].[Articles_ReviewBoardInvitations] | `InvitationWorkflowId` | [Journal].[Workflows] | `PK-Journal.Workflows` |
| `FK-Journal.Articles_ReviewBoardInvitations(JournalRoleId)` | [Journal].[Articles_ReviewBoardInvitations] | `JournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.Articles_ReviewBoardInvitations(OriginalRoleId)` | [Journal].[Articles_ReviewBoardInvitations] | `OriginalRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_ReviewBoardInvitations(PersonId)` | [Journal].[Articles_ReviewBoardInvitations] | `PersonId` | [Person].[Persons] | `PK-Person.Persons` |
| `FK-Journal.Articles_ReviewBoardInvitations(PersonId.Original)` | [Journal].[Articles_ReviewBoardInvitations] | `PersonId.Original` | [Person].[Persons] | `PK-Person.Persons` |
| `FK-Journal.Articles_ReviewBoardInvitations(RoleId)` | [Journal].[Articles_ReviewBoardInvitations] | `RoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_ReviewBoardInvitations(ScheduledInvitationId)` | [Journal].[Articles_ReviewBoardInvitations] | `ScheduledInvitationId` | [Journal].[Articles_ReviewBoardInvitationsScheduled] | `PK-Journal.Articles_ReviewBoardInvitationsScheduled` |
| `FK-Journal.Articles_ReviewBoardInvitations(SpaceId)` | [Journal].[Articles_ReviewBoardInvitations] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewBoardInvitations(UserId)` | [Journal].[Articles_ReviewBoardInvitations] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardInvitations(WorkflowEmailId)` | [Journal].[Articles_ReviewBoardInvitations] | `WorkflowEmailId` | [Journal].[Workflows_Emails] | `PK-Journal.Workflows_Emails` |
| `FK-Journal.Articles_ReviewBoardInvitations(WorkflowId)` | [Journal].[Articles_ReviewBoardInvitations] | `WorkflowId` | [Journal].[Workflows] | `PK-Journal.Workflows` |
| `FK-Journal.Articles_ReviewBoardInvitations(WorkflowMessageTypeId)` | [Journal].[Articles_ReviewBoardInvitations] | `WorkflowMessageTypeId` | [Journal].[Workflows_MessageType] | `PK-Journal.Workflows_MessageType` |
| `FK-Journal.Articles_ReviewBoardInvitations(WorkflowPipelineStageId)` | [Journal].[Articles_ReviewBoardInvitations] | `WorkflowPipelineStageId` | [Journal].[Workflows_PipelineStage] | `PK-Journal.Workflows_PipelineStage` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(ArticleId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(AuthorReviewerSuggestionTypeId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `AuthorReviewerSuggestionTypeId` | [Journal].[Articles_AuthorsSuggestedReviewer.SuggestionType] | `PK-Journal.Articles_AuthorsSuggestedReviewer.SuggestionType` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(CreatorJournalRoleId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `CreatorJournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(CreatorOriginalRoleId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `CreatorOriginalRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(CreatorRoleId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `CreatorRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(CreatorUserId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(InvitationStatusId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `InvitationStatusId` | [Journal].[Articles_ReviewBoardInvitationStatus] | `PK-Journal.Articles_ReviewBoardInvitationStatus` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(JournalRoleId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `JournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(OriginalRoleId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `OriginalRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(RoleId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `RoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(SpaceId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(UserId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(WorkflowEmailId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `WorkflowEmailId` | [Journal].[Workflows_Emails] | `PK-Journal.Workflows_Emails` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(WorkflowId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `WorkflowId` | [Journal].[Workflows] | `PK-Journal.Workflows` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(WorkflowMessageTypeId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `WorkflowMessageTypeId` | [Journal].[Workflows_MessageType] | `PK-Journal.Workflows_MessageType` |
| `FK-Journal.Articles_ReviewBoardInvitationsHistory(WorkflowPipelineStageId)` | [Journal].[Articles_ReviewBoardInvitationsHistory] | `WorkflowPipelineStageId` | [Journal].[Workflows_PipelineStage] | `PK-Journal.Workflows_PipelineStage` |
| `FK-Journal.Articles_ReviewBoardInvitationsScheduled(ArticleId)` | [Journal].[Articles_ReviewBoardInvitationsScheduled] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ReviewBoardInvitationsScheduled(DiscarderUserId)` | [Journal].[Articles_ReviewBoardInvitationsScheduled] | `DiscarderUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardInvitationsScheduled(DiscardReasonId)` | [Journal].[Articles_ReviewBoardInvitationsScheduled] | `DiscardReasonId` | [Journal].[Articles_ReviewBoardInvitationsScheduled.DiscardReason] | `PK-Journal.Articles_ReviewBoardInvitationsScheduled.DiscardReason` |
| `FK-Journal.Articles_ReviewBoardInvitationsScheduled(Invitee.AudienceTypeId)` | [Journal].[Articles_ReviewBoardInvitationsScheduled] | `Invitee.AudienceTypeId` | [Journal].[Articles_ReviewBoardInvitationsScheduled.AudienceType] | `PK-Journal.Articles_ReviewBoardInvitationsScheduled.AudienceType` |
| `FK-Journal.Articles_ReviewBoardInvitationsScheduled(Invitee.DeclinationReasonId)` | [Journal].[Articles_ReviewBoardInvitationsScheduled] | `Invitee.DeclinationReasonId` | [Journal].[Articles_ReviewBoardInvitationsScheduled.DeclinationReason] | `PK-Journal.Articles_ReviewBoardInvitationsScheduled.DeclinationReason` |
| `FK-Journal.Articles_ReviewBoardInvitationsScheduled(Invitee.RoleId)` | [Journal].[Articles_ReviewBoardInvitationsScheduled] | `Invitee.RoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_ReviewBoardInvitationsScheduled(Invitee.UserId)` | [Journal].[Articles_ReviewBoardInvitationsScheduled] | `Invitee.UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardInvitationsScheduled(MethodId)` | [Journal].[Articles_ReviewBoardInvitationsScheduled] | `MethodId` | [Journal].[Articles_ReviewBoardInvitationsScheduled.Method] | `PK-Journal.Articles_ReviewBoardInvitationsScheduled.Method` |
| `FK-Journal.Articles_ReviewBoardInvitationsScheduled(SenderUserId)` | [Journal].[Articles_ReviewBoardInvitationsScheduled] | `SenderUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardInvitationsScheduled(SpaceId)` | [Journal].[Articles_ReviewBoardInvitationsScheduled] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewBoardInvitationsScheduled(StatusId)` | [Journal].[Articles_ReviewBoardInvitationsScheduled] | `StatusId` | [Journal].[Articles_ReviewBoardInvitationsScheduled.Status] | `PK-Journal.Articles_ReviewBoardInvitationsScheduled.Status` |
| `FK-Journal.Articles_ReviewBoardInvitationsScheduled(WorkflowId)` | [Journal].[Articles_ReviewBoardInvitationsScheduled] | `WorkflowId` | [Journal].[Workflows] | `PK-Journal.Workflows` |
| `FK-Journal.Articles_ReviewBoardMembers(ArticleId)` | [Journal].[Articles_ReviewBoardMembers] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ReviewBoardMembers(InviterUserId)` | [Journal].[Articles_ReviewBoardMembers] | `InviterUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardMembers(JournalRoleId)` | [Journal].[Articles_ReviewBoardMembers] | `JournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.Articles_ReviewBoardMembers(OriginalRoleId)` | [Journal].[Articles_ReviewBoardMembers] | `OriginalRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_ReviewBoardMembers(ReviewBoardInvitationId)` | [Journal].[Articles_ReviewBoardMembers] | `ReviewBoardInvitationId` | [Journal].[Articles_ReviewBoardInvitations] | `PK-Journal.Articles_ReviewBoardInvitations` |
| `FK-Journal.Articles_ReviewBoardMembers(ReviewBoardStatusId)` | [Journal].[Articles_ReviewBoardMembers] | `ReviewBoardStatusId` | [Journal].[Articles_ReviewBoardStatus] | `PK-Journal.Articles_ReviewBoardStatus` |
| `FK-Journal.Articles_ReviewBoardMembers(RoleId)` | [Journal].[Articles_ReviewBoardMembers] | `RoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_ReviewBoardMembers(SpaceId)` | [Journal].[Articles_ReviewBoardMembers] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewBoardMembers(UserId)` | [Journal].[Articles_ReviewBoardMembers] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardWithdrawals(ArticleId)` | [Journal].[Articles_ReviewBoardWithdrawals] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ReviewBoardWithdrawals(LoggedInUserId)` | [Journal].[Articles_ReviewBoardWithdrawals] | `LoggedInUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewBoardWithdrawals(ReasonId)` | [Journal].[Articles_ReviewBoardWithdrawals] | `ReasonId` | [Journal].[Articles_ReviewActionReason] | `PK-Journal.Articles_ReviewActionReason` |
| `FK-Journal.Articles_ReviewBoardWithdrawals(RoleId)` | [Journal].[Articles_ReviewBoardWithdrawals] | `RoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_ReviewBoardWithdrawals(SpaceId)` | [Journal].[Articles_ReviewBoardWithdrawals] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewBoardWithdrawals(StageId)` | [Journal].[Articles_ReviewBoardWithdrawals] | `StageId` | [Journal].[Articles_Stage] | `PK-Journal.Articles_Stage` |
| `FK-Journal.Articles_ReviewBoardWithdrawals(UserId)` | [Journal].[Articles_ReviewBoardWithdrawals] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewIndependentReports(ArticleId)` | [Journal].[Articles_ReviewIndependentReports] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ReviewIndependentReports(ReviewBoardMemberId)` | [Journal].[Articles_ReviewIndependentReports] | `ReviewBoardMemberId` | [Journal].[Articles_ReviewBoardMembers] | `PK-Journal.Articles_ReviewBoardMembers` |
| `FK-Journal.Articles_ReviewIndependentReports(SpaceId)` | [Journal].[Articles_ReviewIndependentReports] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewPlagiarismCheck(ArticleId)` | [Journal].[Articles_ReviewPlagiarismCheck] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ReviewPlagiarismCheck(SpaceId)` | [Journal].[Articles_ReviewPlagiarismCheck] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewReportAnswers(AnswerTypeId)` | [Journal].[Articles_ReviewReportAnswers] | `AnswerTypeId` | [Journal].[Articles_ReviewReportAnswerType] | `PK-Journal.Articles_ReviewReportAnswerType` |
| `FK-Journal.Articles_ReviewReportAnswers(ArticleId)` | [Journal].[Articles_ReviewReportAnswers] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ReviewReportAnswers(ArticleStageId)` | [Journal].[Articles_ReviewReportAnswers] | `ArticleStageId` | [Journal].[Articles_Stage] | `PK-Journal.Articles_Stage` |
| `FK-Journal.Articles_ReviewReportAnswers(QuestionId)` | [Journal].[Articles_ReviewReportAnswers] | `QuestionId` | [Journal].[Articles_ReviewReportQuestions] | `PK-Journal.Articles_ReviewReportQuestions` |
| `FK-Journal.Articles_ReviewReportAnswers(ReviewBoardMemberId)` | [Journal].[Articles_ReviewReportAnswers] | `ReviewBoardMemberId` | [Journal].[Articles_ReviewBoardMembers] | `PK-Journal.Articles_ReviewBoardMembers` |
| `FK-Journal.Articles_ReviewReportAnswers(ReviewReportId)` | [Journal].[Articles_ReviewReportAnswers] | `ReviewReportId` | [Journal].[Articles_ReviewReports] | `PK-Journal.Articles_ReviewReports` |
| `FK-Journal.Articles_ReviewReportAnswers(SpaceId)` | [Journal].[Articles_ReviewReportAnswers] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewReportAnswers(SubQuestionId)` | [Journal].[Articles_ReviewReportAnswers] | `SubQuestionId` | [Journal].[Articles_ReviewReportSubQuestions] | `PK-Journal.Articles_ReviewReportSubQuestions` |
| `FK-Journal.Articles_ReviewReportDiscussions(ArticleId)` | [Journal].[Articles_ReviewReportDiscussions] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ReviewReportDiscussions(ArticleStageId)` | [Journal].[Articles_ReviewReportDiscussions] | `ArticleStageId` | [Journal].[Articles_Stage] | `PK-Journal.Articles_Stage` |
| `FK-Journal.Articles_ReviewReportDiscussions(JournalRoleId)` | [Journal].[Articles_ReviewReportDiscussions] | `JournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.Articles_ReviewReportDiscussions(OriginalRoleId)` | [Journal].[Articles_ReviewReportDiscussions] | `OriginalRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_ReviewReportDiscussions(ParentDiscussionId)` | [Journal].[Articles_ReviewReportDiscussions] | `ParentDiscussionId` | [Journal].[Articles_ReviewReportDiscussions] | `PK-Journal.Articles_ReviewReportDiscussions` |
| `FK-Journal.Articles_ReviewReportDiscussions(QuestionId)` | [Journal].[Articles_ReviewReportDiscussions] | `QuestionId` | [Journal].[Articles_ReviewReportQuestions] | `PK-Journal.Articles_ReviewReportQuestions` |
| `FK-Journal.Articles_ReviewReportDiscussions(ReviewBoardMemberId)` | [Journal].[Articles_ReviewReportDiscussions] | `ReviewBoardMemberId` | [Journal].[Articles_ReviewBoardMembers] | `PK-Journal.Articles_ReviewBoardMembers` |
| `FK-Journal.Articles_ReviewReportDiscussions(ReviewReportId)` | [Journal].[Articles_ReviewReportDiscussions] | `ReviewReportId` | [Journal].[Articles_ReviewReports] | `PK-Journal.Articles_ReviewReports` |
| `FK-Journal.Articles_ReviewReportDiscussions(RoleId)` | [Journal].[Articles_ReviewReportDiscussions] | `RoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_ReviewReportDiscussions(SpaceId)` | [Journal].[Articles_ReviewReportDiscussions] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewReportDiscussions(UserId)` | [Journal].[Articles_ReviewReportDiscussions] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewReportQuestions(ArticleTypeId)` | [Journal].[Articles_ReviewReportQuestions] | `ArticleTypeId` | [Journal].[Articles_Type] | `PK-Journal.Articles_Type` |
| `FK-Journal.Articles_ReviewReportQuestions(SpaceId)` | [Journal].[Articles_ReviewReportQuestions] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewReportRatings(ArticleId)` | [Journal].[Articles_ReviewReportRatings] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ReviewReportRatings(EvaluatorRoleId)` | [Journal].[Articles_ReviewReportRatings] | `EvaluatorRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_ReviewReportRatings(EvaluatorUserId)` | [Journal].[Articles_ReviewReportRatings] | `EvaluatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewReportRatings(ReviewBoardMemberId)` | [Journal].[Articles_ReviewReportRatings] | `ReviewBoardMemberId` | [Journal].[Articles_ReviewBoardMembers] | `PK-Journal.Articles_ReviewBoardMembers` |
| `FK-Journal.Articles_ReviewReportRatings(ReviewerUserId)` | [Journal].[Articles_ReviewReportRatings] | `ReviewerUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewReportRatings(SpaceId)` | [Journal].[Articles_ReviewReportRatings] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewReports(ArticleId)` | [Journal].[Articles_ReviewReports] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ReviewReports(ArticleStageId)` | [Journal].[Articles_ReviewReports] | `ArticleStageId` | [Journal].[Articles_Stage] | `PK-Journal.Articles_Stage` |
| `FK-Journal.Articles_ReviewReports(CreatorUserId)` | [Journal].[Articles_ReviewReports] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_ReviewReports(ReviewBoardMemberId)` | [Journal].[Articles_ReviewReports] | `ReviewBoardMemberId` | [Journal].[Articles_ReviewBoardMembers] | `PK-Journal.Articles_ReviewBoardMembers` |
| `FK-Journal.Articles_ReviewReports(SpaceId)` | [Journal].[Articles_ReviewReports] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ReviewReports(StageStatusId)` | [Journal].[Articles_ReviewReports] | `StageStatusId` | [Journal].[Articles_StageStatus] | `PK-Journal.Articles_StageStatus` |
| `FK-Journal.Articles_ReviewReportSubQuestions(AnswerTypeId)` | [Journal].[Articles_ReviewReportSubQuestions] | `AnswerTypeId` | [Journal].[Articles_ReviewReportAnswerType] | `PK-Journal.Articles_ReviewReportAnswerType` |
| `FK-Journal.Articles_ReviewReportSubQuestions(QuestionId)` | [Journal].[Articles_ReviewReportSubQuestions] | `QuestionId` | [Journal].[Articles_ReviewReportQuestions] | `PK-Journal.Articles_ReviewReportQuestions` |
| `FK-Journal.Articles_ReviewReportSubQuestions(SpaceId)` | [Journal].[Articles_ReviewReportSubQuestions] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_StageDates.Pivot(ArticleId)` | [Journal].[Articles_StageDates.Pivot] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_StageDates.Pivot(SpaceId)` | [Journal].[Articles_StageDates.Pivot] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Stages(ArticleId)` | [Journal].[Articles_Stages] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_Stages(ModifierUserId)` | [Journal].[Articles_Stages] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_Stages(SpaceId)` | [Journal].[Articles_Stages] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Stages(StageId)` | [Journal].[Articles_Stages] | `StageId` | [Journal].[Articles_Stage] | `PK-Journal.Articles_Stage` |
| `FK-Journal.Articles_StagesHistory(ArticleId)` | [Journal].[Articles_StagesHistory] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_StagesHistory(ModifierUserId)` | [Journal].[Articles_StagesHistory] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_StagesHistory(SpaceId)` | [Journal].[Articles_StagesHistory] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_StagesHistory(StageId)` | [Journal].[Articles_StagesHistory] | `StageId` | [Journal].[Articles_Stage] | `PK-Journal.Articles_Stage` |
| `FK-Journal.Articles_SubmissionHistory(ArticleId)` | [Journal].[Articles_SubmissionHistory] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_SubmissionHistory(SpaceId)` | [Journal].[Articles_SubmissionHistory] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_SubmissionHistory(SubmittingUserId)` | [Journal].[Articles_SubmissionHistory] | `SubmittingUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_SubmissionStatementAnswers(QuestionId,QuestionCode,QuestionVersion)` | [Journal].[Articles_SubmissionStatementAnswers] | `QuestionCode` | [Journal].[Articles_SubmissionStatementQuestion] | `PK-Journal.Articles_SubmissionStatementQuestion` |
| `FK-Journal.Articles_SubmissionStatementAnswers(QuestionId,QuestionCode,QuestionVersion)` | [Journal].[Articles_SubmissionStatementAnswers] | `QuestionId` | [Journal].[Articles_SubmissionStatementQuestion] | `PK-Journal.Articles_SubmissionStatementQuestion` |
| `FK-Journal.Articles_SubmissionStatementAnswers(QuestionId,QuestionCode,QuestionVersion)` | [Journal].[Articles_SubmissionStatementAnswers] | `QuestionVersion` | [Journal].[Articles_SubmissionStatementQuestion] | `PK-Journal.Articles_SubmissionStatementQuestion` |
| `FK-Journal.Articles_SubmissionStatementAnswers(SpaceId)` | [Journal].[Articles_SubmissionStatementAnswers] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_SubmissionStatementAnswers(SubmissionStatementId)` | [Journal].[Articles_SubmissionStatementAnswers] | `SubmissionStatementId` | [Journal].[Articles_SubmissionStatements] | `PK-Journal.Articles_SubmissionStatements` |
| `FK-Journal.Articles_SubmissionStatementQuestion(SpaceId)` | [Journal].[Articles_SubmissionStatementQuestion] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_SubmissionStatements(ArticleId)` | [Journal].[Articles_SubmissionStatements] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_SubmissionStatements(SpaceId)` | [Journal].[Articles_SubmissionStatements] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Surveys.NetPromoterScore(ArticleId)` | [Journal].[Articles_Surveys.NetPromoterScore] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_Surveys.NetPromoterScore(CountryId)` | [Journal].[Articles_Surveys.NetPromoterScore] | `CountryId` | [Common].[Countries] | `PK-Common.Countries` |
| `FK-Journal.Articles_Surveys.NetPromoterScore(ParticipantRoleId)` | [Journal].[Articles_Surveys.NetPromoterScore] | `ParticipantRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Articles_Surveys.NetPromoterScore(SpaceId)` | [Journal].[Articles_Surveys.NetPromoterScore] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_Surveys.NetPromoterScore(SurveyTypeId)` | [Journal].[Articles_Surveys.NetPromoterScore] | `SurveyTypeId` | [Common].[SurveyTypes] | `PK-Common.SurveyTypes` |
| `FK-Journal.Articles_Surveys.NetPromoterScore(TaxonomyId)` | [Journal].[Articles_Surveys.NetPromoterScore] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.Articles_Surveys.NetPromoterScore(UserId)` | [Journal].[Articles_Surveys.NetPromoterScore] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Articles_Translations(ArticleId)` | [Journal].[Articles_Translations] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_Type(SpaceId)` | [Journal].[Articles_Type] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Articles_ViewsAndDownloads(ArticleId)` | [Journal].[Articles_ViewsAndDownloads] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Articles_ViewsAndDownloads(ImpactActionId)` | [Journal].[Articles_ViewsAndDownloads] | `ImpactActionId` | [Common].[Impacts_Action] | `PK-Common.Impacts_Action` |
| `FK-Journal.Articles_ViewsAndDownloads(ImpactAggregationId)` | [Journal].[Articles_ViewsAndDownloads] | `ImpactAggregationId` | [Common].[Impacts_Aggregation] | `PK-Common.Impacts_Aggregation` |
| `FK-Journal.Articles_ViewsAndDownloads(ProviderId)` | [Journal].[Articles_ViewsAndDownloads] | `ProviderId` | [Common].[Impacts_Provider] | `PK-Common.Impacts_Provider` |
| `FK-Journal.Articles_ViewsAndDownloads(SpaceId)` | [Journal].[Articles_ViewsAndDownloads] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.EBooks(ResearchTopicId)` | [Journal].[EBooks] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.EBooks(SpaceId)` | [Journal].[EBooks] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.EBooks(StatusId)` | [Journal].[EBooks] | `StatusId` | [Journal].[EBooks_Status] | `PK-Journal.EBooks_Status` |
| `FK-Journal.EditorialBoard.Activities(SpaceId)` | [Journal].[EditorialBoard.Activities] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.EditorialBoard.Activities(TaxonomyId)` | [Journal].[EditorialBoard.Activities] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.EditorialBoard.Activities(UserId)` | [Journal].[EditorialBoard.Activities] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.EditorialBoard.Appointments(CreatorUserId)` | [Journal].[EditorialBoard.Appointments] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.EditorialBoard.Appointments(EndReasonId)` | [Journal].[EditorialBoard.Appointments] | `EndReasonId` | [Journal].[EditorialBoard.Reason] | `PK-Journal.EditorialBoard.Reason` |
| `FK-Journal.EditorialBoard.Appointments(InvitationId)` | [Journal].[EditorialBoard.Appointments] | `InvitationId` | [Journal].[EditorialBoard.Invitations] | `PK-Journal.EditorialBoard.Invitations` |
| `FK-Journal.EditorialBoard.Appointments(JournalRoleId)` | [Journal].[EditorialBoard.Appointments] | `JournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.EditorialBoard.Appointments(ModifierUserId)` | [Journal].[EditorialBoard.Appointments] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.EditorialBoard.Appointments(OnboardingStatusId)` | [Journal].[EditorialBoard.Appointments] | `OnboardingStatusId` | [Journal].[EditorialBoard.OnboardingStatus] | `PK-Journal.EditorialBoard.Status` |
| `FK-Journal.EditorialBoard.Appointments(RemoveReasonId)` | [Journal].[EditorialBoard.Appointments] | `RemoveReasonId` | [Journal].[EditorialBoard.Reason] | `PK-Journal.EditorialBoard.Reason` |
| `FK-Journal.EditorialBoard.Appointments(RemoverUserId)` | [Journal].[EditorialBoard.Appointments] | `RemoverUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.EditorialBoard.Appointments(RoleId)` | [Journal].[EditorialBoard.Appointments] | `RoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.EditorialBoard.Appointments(SpaceId)` | [Journal].[EditorialBoard.Appointments] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.EditorialBoard.Appointments(TaxonomyId)` | [Journal].[EditorialBoard.Appointments] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.EditorialBoard.Appointments(UserId)` | [Journal].[EditorialBoard.Appointments] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.EditorialBoard.Invitations(DeclinationReasonId)` | [Journal].[EditorialBoard.Invitations] | `DeclinationReasonId` | [Journal].[EditorialBoard.Reason] | `PK-Journal.EditorialBoard.Reason` |
| `FK-Journal.EditorialBoard.Invitations(InvitationReviewDecisionTypeId)` | [Journal].[EditorialBoard.Invitations] | `InvitationReviewDecisionTypeId` | [Journal].[EditorialBoard.InvitationReviewDecisionType] | `PK-Journal.EditorialBoard.InvitationReviewDecisionType` |
| `FK-Journal.EditorialBoard.Invitations(InvitationReviewInvalidReasonId)` | [Journal].[EditorialBoard.Invitations] | `InvitationReviewInvalidReasonId` | [Journal].[EditorialBoard.Reason] | `PK-Journal.EditorialBoard.Reason` |
| `FK-Journal.EditorialBoard.Invitations(InvitationReviewRejectionReasonId)` | [Journal].[EditorialBoard.Invitations] | `InvitationReviewRejectionReasonId` | [Journal].[EditorialBoard.Reason] | `PK-Journal.EditorialBoard.Reason` |
| `FK-Journal.EditorialBoard.Invitations(InvitationReviewStatusId)` | [Journal].[EditorialBoard.Invitations] | `InvitationReviewStatusId` | [Journal].[EditorialBoard.InvitationReviewStatus] | `PK-Journal.EditorialBoard.InvitationReviewStatus` |
| `FK-Journal.EditorialBoard.Invitations(InvitationSourceId)` | [Journal].[EditorialBoard.Invitations] | `InvitationSourceId` | [Journal].[EditorialBoard.InvitationSource] | `PK-Journal.EditorialBoard.InvitationSource` |
| `FK-Journal.EditorialBoard.Invitations(InvitationStatusId)` | [Journal].[EditorialBoard.Invitations] | `InvitationStatusId` | [Journal].[EditorialBoard.InvitationStatus] | `PK-Journal.EditorialBoard.InvitationStatus` |
| `FK-Journal.EditorialBoard.Invitations(InvitationTypeId)` | [Journal].[EditorialBoard.Invitations] | `InvitationTypeId` | [Journal].[EditorialBoard.InvitationType] | `PK-Journal.EditorialBoard.InvitationType` |
| `FK-Journal.EditorialBoard.Invitations(InviteeUserId)` | [Journal].[EditorialBoard.Invitations] | `InviteeUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.EditorialBoard.Invitations(InviterUserId)` | [Journal].[EditorialBoard.Invitations] | `InviterUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.EditorialBoard.Invitations(JournalRoleId)` | [Journal].[EditorialBoard.Invitations] | `JournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.EditorialBoard.Invitations(SpaceId)` | [Journal].[EditorialBoard.Invitations] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.EditorialBoard.Invitations(SuggestedEditorId)` | [Journal].[EditorialBoard.Invitations] | `SuggestedEditorId` | [Journal].[EditorialBoard.SuggestedEditors] | `PK-Journal.EditorialBoard.SuggestedEditors` |
| `FK-Journal.EditorialBoard.Invitations(TaxonomyId)` | [Journal].[EditorialBoard.Invitations] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.EditorialBoard.Invitations.Blocked(CreatorUserId)` | [Journal].[EditorialBoard.Invitations.Blocked] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.EditorialBoard.Invitations.Blocked(InviteeAffiliationId)` | [Journal].[EditorialBoard.Invitations.Blocked] | `InviteeAffiliationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Journal.EditorialBoard.Invitations.Blocked(InviteeRosstId)` | [Journal].[EditorialBoard.Invitations.Blocked] | `InviteeRosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Journal.EditorialBoard.Invitations.Blocked(InviteeUserId)` | [Journal].[EditorialBoard.Invitations.Blocked] | `InviteeUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.EditorialBoard.Invitations.Blocked(InviterUserId)` | [Journal].[EditorialBoard.Invitations.Blocked] | `InviterUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.EditorialBoard.Invitations.Blocked(SpaceId)` | [Journal].[EditorialBoard.Invitations.Blocked] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.EditorialBoard.Invitations.Blocked(TaxonomyId)` | [Journal].[EditorialBoard.Invitations.Blocked] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.EditorialBoard.SuggestedEditors(AlgorithmSourceId)` | [Journal].[EditorialBoard.SuggestedEditors] | `AlgorithmSourceId` | [Journal].[EditorialBoard.AlgorithmSource] | `PK-Journal.EditorialBoard.AlgorithmSource` |
| `FK-Journal.EditorialBoard.SuggestedEditors(DiscardReasonId)` | [Journal].[EditorialBoard.SuggestedEditors] | `DiscardReasonId` | [Journal].[EditorialBoard.SuggestedEditors.DiscardReason] | `PK-Journal.EditorialBoard.SuggestedEditors.DiscardReason` |
| `FK-Journal.EditorialBoard.SuggestedEditors(JournalRoleId)` | [Journal].[EditorialBoard.SuggestedEditors] | `JournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.EditorialBoard.SuggestedEditors(MethodId)` | [Journal].[EditorialBoard.SuggestedEditors] | `MethodId` | [Journal].[EditorialBoard.SuggestedEditors.Method] | `PK-Journal.EditorialBoard.SuggestedEditors.Method` |
| `FK-Journal.EditorialBoard.SuggestedEditors(RoleId)` | [Journal].[EditorialBoard.SuggestedEditors] | `RoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.EditorialBoard.SuggestedEditors(SourceId)` | [Journal].[EditorialBoard.SuggestedEditors] | `SourceId` | [Journal].[EditorialBoard.SuggestedEditors.Source] | `PK-Journal.EditorialBoard.SuggestedEditors.Source` |
| `FK-Journal.EditorialBoard.SuggestedEditors(SpaceId)` | [Journal].[EditorialBoard.SuggestedEditors] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.EditorialBoard.SuggestedEditors(StatusId)` | [Journal].[EditorialBoard.SuggestedEditors] | `StatusId` | [Journal].[EditorialBoard.SuggestedEditors.Status] | `PK-Journal.EditorialBoard.SuggestedEditors.Status` |
| `FK-Journal.EditorialBoard.SuggestedEditors(SuggesterUserId)` | [Journal].[EditorialBoard.SuggestedEditors] | `SuggesterUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.EditorialBoard.SuggestedEditors(SuggestionRecipientUserId)` | [Journal].[EditorialBoard.SuggestedEditors] | `SuggestionRecipientUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.EditorialBoard.SuggestedEditors(TaxonomyId)` | [Journal].[EditorialBoard.SuggestedEditors] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.EditorialBoard.SuggestedEditors(UserId)` | [Journal].[EditorialBoard.SuggestedEditors] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.EditorialBoard.SuggestedEditors.DiscardReason(SpaceId)` | [Journal].[EditorialBoard.SuggestedEditors.DiscardReason] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.EditorialBoard.SuggestedEditors.Method(SpaceId)` | [Journal].[EditorialBoard.SuggestedEditors.Method] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.EditorialBoard.SuggestedEditors.Source(SpaceId)` | [Journal].[EditorialBoard.SuggestedEditors.Source] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.EditorialOffice_ArticlesPrograms(ArticleId)` | [Journal].[EditorialOffice_ArticlesPrograms] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.EditorialOffice_Journals(TaxonomyId)` | [Journal].[EditorialOffice_Journals] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.EditorialOffice_Journals_Archive(TaxonomyId)` | [Journal].[EditorialOffice_Journals_Archive] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.EditorialOffice_Journals_History_Archive(TaxonomyId)` | [Journal].[EditorialOffice_Journals_History_Archive] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.EditorialOffice_Roles(TaxonomyId)` | [Journal].[EditorialOffice_Roles] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.EditorialOffice_SegmentsHistory(TaxonomyId)` | [Journal].[EditorialOffice_SegmentsHistory] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.JournalRole(RoleId)` | [Journal].[JournalRole] | `RoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.Journals_ArticleTypes(ArticleTypeId)` | [Journal].[Journals_ArticleTypes] | `ArticleTypeId` | [Journal].[Articles_Type] | `PK-Journal.Articles_Type` |
| `FK-Journal.Journals_ArticleTypes(SpaceId)` | [Journal].[Journals_ArticleTypes] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Journals_ArticleTypes(TaxonomyId)` | [Journal].[Journals_ArticleTypes] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.Journals_CostCenters(CostCenterId)` | [Journal].[Journals_CostCenters] | `CostCenterId` | [Common].[CostCenters] | `PK-Common.CostCenters` |
| `FK-Journal.Journals_CostCenters(SpaceId)` | [Journal].[Journals_CostCenters] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Journals_CostCenters(SpaceId,JournalId)` | [Journal].[Journals_CostCenters] | `JournalId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-Journal.Journals_CostCenters(SpaceId,JournalId)` | [Journal].[Journals_CostCenters] | `SpaceId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-Journal.Journals_Details(SpaceId)` | [Journal].[Journals_Details] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Journals_Details(TypeId)` | [Journal].[Journals_Details] | `TypeId` | [Journal].[Journals_Type] | `PK-Journal.Journals_Type` |
| `FK-Journal.Journals_Details(TypeSetterUserId)` | [Journal].[Journals_Details] | `TypeSetterUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Journals_DetailsTaxonomy(SpaceId)` | [Journal].[Journals_DetailsTaxonomy] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Journals_DetailsTaxonomy(SpaceId,JournalId)` | [Journal].[Journals_DetailsTaxonomy] | `JournalId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-Journal.Journals_DetailsTaxonomy(SpaceId,JournalId)` | [Journal].[Journals_DetailsTaxonomy] | `SpaceId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-Journal.Journals_DetailsTaxonomy(SpaceId,SectionId)` | [Journal].[Journals_DetailsTaxonomy] | `SectionId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-Journal.Journals_DetailsTaxonomy(SpaceId,SectionId)` | [Journal].[Journals_DetailsTaxonomy] | `SpaceId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-Journal.Journals_ImpactFactorHistory(SpaceId)` | [Journal].[Journals_ImpactFactorHistory] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Journals_JCREditions(EditionId)` | [Journal].[Journals_JCREditions] | `EditionId` | [Journal].[JCREditions] | `PK-Journal.JCREditions` |
| `FK-Journal.Journals_JCREditions(SpaceId)` | [Journal].[Journals_JCREditions] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.JournalsIndexing.Eligibility(SpaceId)` | [Journal].[JournalsIndexing.Eligibility] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.JournalsIndexing.Eligibility(SpaceId,JournalId)` | [Journal].[JournalsIndexing.Eligibility] | `JournalId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-Journal.JournalsIndexing.Eligibility(SpaceId,JournalId)` | [Journal].[JournalsIndexing.Eligibility] | `SpaceId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-Journal.JournalsIndexing.Eligibility(TaxonomyId)` | [Journal].[JournalsIndexing.Eligibility] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.JournalsIndexing.Journals(IndexingServiceId)` | [Journal].[JournalsIndexing.Journals] | `IndexingServiceId` | [Journal].[JournalsIndexing.Services] | `PK-Journal.JournalsIndexing.Services` |
| `FK-Journal.JournalsIndexing.Journals(TaxonomyId)` | [Journal].[JournalsIndexing.Journals] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.Keywords(SpaceId)` | [Journal].[Keywords] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.LaunchResearchTopics(CampaignId)` | [Journal].[LaunchResearchTopics] | `CampaignId` | [CRM].[Campaigns] | `PK-CRM.Campaigns` |
| `FK-Journal.LaunchResearchTopics(CreatedBy)` | [Journal].[LaunchResearchTopics] | `CreatedBy` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.LaunchResearchTopics(GroupId)` | [Journal].[LaunchResearchTopics] | `GroupId` | [Journal].[LaunchResearchTopics_Group] | `PK-Journal.LaunchResearchTopics_Group` |
| `FK-Journal.LaunchResearchTopics(SourceId)` | [Journal].[LaunchResearchTopics] | `SourceId` | [Journal].[LaunchResearchTopics_Source] | `PK-Journal.LaunchResearchTopics_Source` |
| `FK-Journal.LaunchResearchTopics(SpaceId)` | [Journal].[LaunchResearchTopics] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.LaunchResearchTopics(TaxonomyId)` | [Journal].[LaunchResearchTopics] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.LaunchResearchTopics(ThemeId)` | [Journal].[LaunchResearchTopics] | `ThemeId` | [Journal].[LaunchResearchTopics_Theme] | `PK-Journal.LaunchResearchTopics_Theme` |
| `FK-Journal.LaunchResearchTopics_Comments(CommentedByUserId)` | [Journal].[LaunchResearchTopics_Comments] | `CommentedByUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.LaunchResearchTopics_Comments(SpaceId)` | [Journal].[LaunchResearchTopics_Comments] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.LaunchResearchTopics_Comments(TopicId)` | [Journal].[LaunchResearchTopics_Comments] | `TopicId` | [Journal].[LaunchResearchTopics] | `PK-Journal.LaunchResearchTopics` |
| `FK-Journal.LaunchResearchTopics_Editors(PersonId)` | [Journal].[LaunchResearchTopics_Editors] | `PersonId` | [Person].[Persons] | `PK-Person.Persons` |
| `FK-Journal.LaunchResearchTopics_Editors(TopicId)` | [Journal].[LaunchResearchTopics_Editors] | `TopicId` | [Journal].[LaunchResearchTopics] | `PK-Journal.LaunchResearchTopics` |
| `FK-Journal.LaunchResearchTopics_Feedback(FeedbackTypeId)` | [Journal].[LaunchResearchTopics_Feedback] | `FeedbackTypeId` | [Journal].[LaunchResearchTopics_FeedbackType] | `PK-Journal.LaunchResearchTopics_FeedbackType` |
| `FK-Journal.LaunchResearchTopics_Feedback(SpaceId)` | [Journal].[LaunchResearchTopics_Feedback] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.LaunchResearchTopics_Feedback(SubmittedByUserId)` | [Journal].[LaunchResearchTopics_Feedback] | `SubmittedByUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.LaunchResearchTopics_Feedback(TopicId)` | [Journal].[LaunchResearchTopics_Feedback] | `TopicId` | [Journal].[LaunchResearchTopics] | `PK-Journal.LaunchResearchTopics` |
| `FK-Journal.LaunchResearchTopics_Invalidations(InvalidatedByUserId)` | [Journal].[LaunchResearchTopics_Invalidations] | `InvalidatedByUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.LaunchResearchTopics_Invalidations(ReasonId)` | [Journal].[LaunchResearchTopics_Invalidations] | `ReasonId` | [Journal].[LaunchResearchTopics_InvalidationReasons] | `PK-Journal.LaunchResearchTopics_InvalidationReasons` |
| `FK-Journal.LaunchResearchTopics_Invalidations(SpaceId)` | [Journal].[LaunchResearchTopics_Invalidations] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.LaunchResearchTopics_Invalidations(TopicId)` | [Journal].[LaunchResearchTopics_Invalidations] | `TopicId` | [Journal].[LaunchResearchTopics] | `PK-Journal.LaunchResearchTopics` |
| `FK-Journal.LaunchResearchTopics_Merges(MergedByUserId)` | [Journal].[LaunchResearchTopics_Merges] | `MergedByUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.LaunchResearchTopics_Merges(MergedToTopicId)` | [Journal].[LaunchResearchTopics_Merges] | `MergedToTopicId` | [Journal].[LaunchResearchTopics] | `PK-Journal.LaunchResearchTopics` |
| `FK-Journal.LaunchResearchTopics_Merges(SpaceId)` | [Journal].[LaunchResearchTopics_Merges] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.LaunchResearchTopics_TransferHistory(InitiatedBy)` | [Journal].[LaunchResearchTopics_TransferHistory] | `InitiatedBy` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.LaunchResearchTopics_TransferHistory(SpaceId)` | [Journal].[LaunchResearchTopics_TransferHistory] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.LaunchResearchTopics_TransferHistory(TaxonomyId)` | [Journal].[LaunchResearchTopics_TransferHistory] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.LaunchResearchTopics_TransferHistory(TopicId)` | [Journal].[LaunchResearchTopics_TransferHistory] | `TopicId` | [Journal].[LaunchResearchTopics] | `PK-Journal.LaunchResearchTopics` |
| `FK-Journal.LaunchResearchTopics_WorkflowHistory(SpaceId)` | [Journal].[LaunchResearchTopics_WorkflowHistory] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.LaunchResearchTopics_WorkflowHistory(StageId)` | [Journal].[LaunchResearchTopics_WorkflowHistory] | `StageId` | [Journal].[LaunchResearchTopics_Stage] | `PK-Journal.LaunchResearchTopics_Stage` |
| `FK-Journal.LaunchResearchTopics_WorkflowHistory(StartedBy)` | [Journal].[LaunchResearchTopics_WorkflowHistory] | `StartedBy` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.LaunchResearchTopics_WorkflowHistory(TopicId)` | [Journal].[LaunchResearchTopics_WorkflowHistory] | `TopicId` | [Journal].[LaunchResearchTopics] | `PK-Journal.LaunchResearchTopics` |
| `FK-Journal.Recognition.Editors(ArticleId)` | [Journal].[Recognition.Editors] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Recognition.Editors(ReferredUserId)` | [Journal].[Recognition.Editors] | `ReferredUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Recognition.Editors(SpaceID)` | [Journal].[Recognition.Editors] | `SpaceID` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Recognition.Editors(UserId)` | [Journal].[Recognition.Editors] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopicAbstracts(CreatorUserId)` | [Journal].[ResearchTopicAbstracts] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopicAbstracts(ResearchTopicId)` | [Journal].[ResearchTopicAbstracts] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.ResearchTopicAbstracts(SpaceId)` | [Journal].[ResearchTopicAbstracts] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopicAbstracts(StageId)` | [Journal].[ResearchTopicAbstracts] | `StageId` | [Journal].[ResearchTopicAbstracts_Stage] | `PK-Journal.ResearchTopicAbstracts_Stage` |
| `FK-Journal.ResearchTopicAbstracts(TaxonomyId)` | [Journal].[ResearchTopicAbstracts] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.ResearchTopicAbstracts_Affiliations(CountryId)` | [Journal].[ResearchTopicAbstracts_Affiliations] | `CountryId` | [Common].[Countries] | `PK-Common.Countries` |
| `FK-Journal.ResearchTopicAbstracts_Affiliations(SpaceId)` | [Journal].[ResearchTopicAbstracts_Affiliations] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopicAbstracts_Authors(AuthorUserId)` | [Journal].[ResearchTopicAbstracts_Authors] | `AuthorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopicAbstracts_Authors(JournalRoleId)` | [Journal].[ResearchTopicAbstracts_Authors] | `JournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.ResearchTopicAbstracts_Authors(ResearchTopicAbstractId)` | [Journal].[ResearchTopicAbstracts_Authors] | `ResearchTopicAbstractId` | [Journal].[ResearchTopicAbstracts] | `PK-Journal.ResearchTopicAbstracts` |
| `FK-Journal.ResearchTopicAbstracts_Authors(RoleId)` | [Journal].[ResearchTopicAbstracts_Authors] | `RoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.ResearchTopicAbstracts_Authors(SpaceId)` | [Journal].[ResearchTopicAbstracts_Authors] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopicAbstracts_Authors(TitleId)` | [Journal].[ResearchTopicAbstracts_Authors] | `TitleId` | [Network].[Users_Title] | `PK-Network.Users_Title` |
| `FK-Journal.ResearchTopicAbstracts_AuthorsAffiliations(AffiliationId)` | [Journal].[ResearchTopicAbstracts_AuthorsAffiliations] | `AffiliationId` | [Journal].[ResearchTopicAbstracts_Affiliations] | `PK-Journal.ResearchTopicAbstracts_Affiliations` |
| `FK-Journal.ResearchTopicAbstracts_AuthorsAffiliations(AuthorId)` | [Journal].[ResearchTopicAbstracts_AuthorsAffiliations] | `AuthorId` | [Journal].[ResearchTopicAbstracts_Authors] | `PK-Journal.ResearchTopicAbstracts_Authors` |
| `FK-Journal.ResearchTopicAbstracts_AuthorsAffiliations(SpaceId)` | [Journal].[ResearchTopicAbstracts_AuthorsAffiliations] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopicAbstracts_Stages(ModifierUserId)` | [Journal].[ResearchTopicAbstracts_Stages] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopicAbstracts_Stages(ResearchTopicAbstractId)` | [Journal].[ResearchTopicAbstracts_Stages] | `ResearchTopicAbstractId` | [Journal].[ResearchTopicAbstracts] | `PK-Journal.ResearchTopicAbstracts` |
| `FK-Journal.ResearchTopicAbstracts_Stages(SpaceId)` | [Journal].[ResearchTopicAbstracts_Stages] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopicAbstracts_Stages(StageId)` | [Journal].[ResearchTopicAbstracts_Stages] | `StageId` | [Journal].[ResearchTopicAbstracts_Stage] | `PK-Journal.ResearchTopicAbstracts_Stage` |
| `FK-Journal.ResearchTopics(CreatorUserId)` | [Journal].[ResearchTopics] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics(DeletionReasonId)` | [Journal].[ResearchTopics] | `DeletionReasonId` | [Journal].[ResearchTopics_DeletionReason] | `PK-Journal.ResearchTopics_DeletionReason` |
| `FK-Journal.ResearchTopics(OwnerUserId)` | [Journal].[ResearchTopics] | `OwnerUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics(SpaceId)` | [Journal].[ResearchTopics] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics(StageId)` | [Journal].[ResearchTopics] | `StageId` | [Journal].[ResearchTopics_Stage] | `PK-Journal.ResearchTopics_Stage` |
| `FK-Journal.ResearchTopics(TaxonomyId)` | [Journal].[ResearchTopics] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.ResearchTopics_ArticlesAssignments(ArticleId)` | [Journal].[ResearchTopics_ArticlesAssignments] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.ResearchTopics_ArticlesAssignments(CreatorUserId)` | [Journal].[ResearchTopics_ArticlesAssignments] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics_ArticlesAssignments(ModifierUserId)` | [Journal].[ResearchTopics_ArticlesAssignments] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics_ArticlesAssignments(ResearchTopicId)` | [Journal].[ResearchTopics_ArticlesAssignments] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.ResearchTopics_ArticlesAssignments(SpaceId)` | [Journal].[ResearchTopics_ArticlesAssignments] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics_ContributorReferrals(ContributorId)` | [Journal].[ResearchTopics_ContributorReferrals] | `ContributorId` | [Journal].[ResearchTopics_Contributors] | `PK-Journal.ResearchTopics_Contributors` |
| `FK-Journal.ResearchTopics_ContributorReferrals(CreatorUserId)` | [Journal].[ResearchTopics_ContributorReferrals] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics_ContributorReferrals(InboundLeadReferralId)` | [Journal].[ResearchTopics_ContributorReferrals] | `InboundLeadReferralId` | [Journal].[ResearchTopics_ContributorReferrals] | `PK-Journal.ResearchTopics_ContributorReferrals` |
| `FK-Journal.ResearchTopics_ContributorReferrals(ModifierUserId)` | [Journal].[ResearchTopics_ContributorReferrals] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics_ContributorReferrals(ResearchTopicId)` | [Journal].[ResearchTopics_ContributorReferrals] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.ResearchTopics_ContributorReferrals(SourceId)` | [Journal].[ResearchTopics_ContributorReferrals] | `SourceId` | [Journal].[ResearchTopics_ContributorReferralSource] | `PK-Journal.ResearchTopics_ContributorReferralSource` |
| `FK-Journal.ResearchTopics_ContributorReferrals(SpaceId)` | [Journal].[ResearchTopics_ContributorReferrals] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics_ContributorReferrals(StatusId)` | [Journal].[ResearchTopics_ContributorReferrals] | `StatusId` | [Journal].[ResearchTopics_ContributorReferralStatus] | `PK-Journal.ResearchTopics_ContributorReferralStatus` |
| `FK-Journal.ResearchTopics_ContributorReferrals(UserId)` | [Journal].[ResearchTopics_ContributorReferrals] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics_Contributors(Contributor.Creator.UserTypeRoleId)` | [Journal].[ResearchTopics_Contributors] | `Contributor.Creator.UserTypeRoleId` | [Journal].[ResearchTopics_Contributors.UserTypeRoles] | `PK-Journal.ResearchTopics_Contributors.UserTypeRoles` |
| `FK-Journal.ResearchTopics_Contributors(ContributorSecondarySourceId)` | [Journal].[ResearchTopics_Contributors] | `ContributorSecondarySourceId` | [Journal].[ResearchTopics_Contributors.SecondarySource] | `PK-Journal.ResearchTopics_Contributors.SecondarySource` |
| `FK-Journal.ResearchTopics_Contributors(ContributorSourceId)` | [Journal].[ResearchTopics_Contributors] | `ContributorSourceId` | [Journal].[ResearchTopics_ContributorsSource] | `PK-Journal.ResearchTopics_ContributorsSource` |
| `FK-Journal.ResearchTopics_Contributors(Invitation.Initiator.RoleId)` | [Journal].[ResearchTopics_Contributors] | `Invitation.Initiator.RoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.ResearchTopics_Contributors(InvitationStatusId)` | [Journal].[ResearchTopics_Contributors] | `InvitationStatusId` | [Journal].[ResearchTopics_InvitationStatus] | `PK-Journal.ResearchTopics_InvitationStatus` |
| `FK-Journal.ResearchTopics_Contributors(InviterUserId)` | [Journal].[ResearchTopics_Contributors] | `InviterUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics_Contributors(ResearchTopicId)` | [Journal].[ResearchTopics_Contributors] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.ResearchTopics_Contributors(SpaceId)` | [Journal].[ResearchTopics_Contributors] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics_Contributors(UserId)` | [Journal].[ResearchTopics_Contributors] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics_Contributors.Aggregated(ResearchTopicId)` | [Journal].[ResearchTopics_Contributors.Aggregated] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.ResearchTopics_Contributors.Aggregated(SpaceId)` | [Journal].[ResearchTopics_Contributors.Aggregated] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics_ContributorsArticles(ArticleId)` | [Journal].[ResearchTopics_ContributorsArticles] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.ResearchTopics_ContributorsArticles(ContributorId)` | [Journal].[ResearchTopics_ContributorsArticles] | `ContributorId` | [Journal].[ResearchTopics_Contributors] | `PK-Journal.ResearchTopics_Contributors` |
| `FK-Journal.ResearchTopics_ContributorsArticles(SpaceId)` | [Journal].[ResearchTopics_ContributorsArticles] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics_ContributorsArticlesDuplicates(ArticleId)` | [Journal].[ResearchTopics_ContributorsArticlesDuplicates] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.ResearchTopics_ContributorsArticlesDuplicates(ContributorId)` | [Journal].[ResearchTopics_ContributorsArticlesDuplicates] | `ContributorId` | [Journal].[ResearchTopics_Contributors] | `PK-Journal.ResearchTopics_Contributors` |
| `FK-Journal.ResearchTopics_ContributorsDeclinations(ContributorId)` | [Journal].[ResearchTopics_ContributorsDeclinations] | `ContributorId` | [Journal].[ResearchTopics_Contributors] | `PK-Journal.ResearchTopics_Contributors` |
| `FK-Journal.ResearchTopics_ContributorsDeclinations(DeclinationReasonId)` | [Journal].[ResearchTopics_ContributorsDeclinations] | `DeclinationReasonId` | [Journal].[ResearchTopics_DeclinationReason] | `PK-Journal.ResearchTopics_DeclinationReason` |
| `FK-Journal.ResearchTopics_ContributorsDeclinations(SpaceId)` | [Journal].[ResearchTopics_ContributorsDeclinations] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics_ContributorsEvents.Reminders(ContributorId)` | [Journal].[ResearchTopics_ContributorsEvents.Reminders] | `ContributorId` | [Journal].[ResearchTopics_Contributors] | `PK-Journal.ResearchTopics_Contributors` |
| `FK-Journal.ResearchTopics_ContributorsEvents.Reminders(EventId)` | [Journal].[ResearchTopics_ContributorsEvents.Reminders] | `EventId` | [Journal].[ResearchTopics_ContributorsEvent] | `PK-Journal.ResearchTopics_ContributorsEvent` |
| `FK-Journal.ResearchTopics_ContributorsEvents.Reminders(ResearchTopicId)` | [Journal].[ResearchTopics_ContributorsEvents.Reminders] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.ResearchTopics_ContributorsEvents.Reminders(TriggerTypeId)` | [Journal].[ResearchTopics_ContributorsEvents.Reminders] | `TriggerTypeId` | [Journal].[ResearchTopics_ContributorsEventTriggerType] | `PK-Journal.ResearchTopics_ContributorsEventTriggerType` |
| `FK-Journal.ResearchTopics_ContributorsInvitationABTests(ContributorId)` | [Journal].[ResearchTopics_ContributorsInvitationABTests] | `ContributorId` | [Journal].[ResearchTopics_Contributors] | `PK-Journal.ResearchTopics_Contributors` |
| `FK-Journal.ResearchTopics_ContributorsInvitationABTests(CreatorUserId)` | [Journal].[ResearchTopics_ContributorsInvitationABTests] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics_ContributorsInvitationABTests(SenderUserId)` | [Journal].[ResearchTopics_ContributorsInvitationABTests] | `SenderUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics_ContributorsInvitationABTests(SpaceId)` | [Journal].[ResearchTopics_ContributorsInvitationABTests] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics_ContributorTracking(ContributorId)` | [Journal].[ResearchTopics_ContributorTracking] | `ContributorId` | [Journal].[ResearchTopics_Contributors] | `PK-Journal.ResearchTopics_Contributors` |
| `FK-Journal.ResearchTopics_ContributorTracking(SpaceId)` | [Journal].[ResearchTopics_ContributorTracking] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics_Editors(EditorUserId)` | [Journal].[ResearchTopics_Editors] | `EditorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics_Editors(ResearchTopicId)` | [Journal].[ResearchTopics_Editors] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.ResearchTopics_Editors(SpaceId)` | [Journal].[ResearchTopics_Editors] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics_Keywords(ResearchTopicId)` | [Journal].[ResearchTopics_Keywords] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.ResearchTopics_Keywords(SpaceId)` | [Journal].[ResearchTopics_Keywords] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics_ParticipatingJournals(ResearchTopicId)` | [Journal].[ResearchTopics_ParticipatingJournals] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.ResearchTopics_ParticipatingJournals(SpaceId)` | [Journal].[ResearchTopics_ParticipatingJournals] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics_ParticipatingJournals(TaxonomyId)` | [Journal].[ResearchTopics_ParticipatingJournals] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.ResearchTopics_SocialCounts(ResearchTopicId)` | [Journal].[ResearchTopics_SocialCounts] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.ResearchTopics_SocialCounts(SocialCountSourceId)` | [Journal].[ResearchTopics_SocialCounts] | `SocialCountSourceId` | [Common].[SocialCounts_Source] | `PK-Common.SocialCounts_Source` |
| `FK-Journal.ResearchTopics_SocialCounts(SpaceId)` | [Journal].[ResearchTopics_SocialCounts] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics_Stages(ResearchTopicId)` | [Journal].[ResearchTopics_Stages] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.ResearchTopics_Stages(SpaceId)` | [Journal].[ResearchTopics_Stages] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics_Stages(StageId)` | [Journal].[ResearchTopics_Stages] | `StageId` | [Journal].[ResearchTopics_Stage] | `PK-Journal.ResearchTopics_Stage` |
| `FK-Journal.ResearchTopics_Surveys.NetPromoterScore(CountryId)` | [Journal].[ResearchTopics_Surveys.NetPromoterScore] | `CountryId` | [Common].[Countries] | `PK-Common.Countries` |
| `FK-Journal.ResearchTopics_Surveys.NetPromoterScore(ParticipantRoleId)` | [Journal].[ResearchTopics_Surveys.NetPromoterScore] | `ParticipantRoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Journal.ResearchTopics_Surveys.NetPromoterScore(ResearchTopicId)` | [Journal].[ResearchTopics_Surveys.NetPromoterScore] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.ResearchTopics_Surveys.NetPromoterScore(SpaceId)` | [Journal].[ResearchTopics_Surveys.NetPromoterScore] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics_Surveys.NetPromoterScore(SurveyTypeId)` | [Journal].[ResearchTopics_Surveys.NetPromoterScore] | `SurveyTypeId` | [Common].[SurveyTypes] | `PK-Common.SurveyTypes` |
| `FK-Journal.ResearchTopics_Surveys.NetPromoterScore(TaxonomyId)` | [Journal].[ResearchTopics_Surveys.NetPromoterScore] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.ResearchTopics_Surveys.NetPromoterScore(UserId)` | [Journal].[ResearchTopics_Surveys.NetPromoterScore] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics_TopicCoordinators(CreatorUserid)` | [Journal].[ResearchTopics_TopicCoordinators] | `CreatorUserid` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics_TopicCoordinators(LoginUserId)` | [Journal].[ResearchTopics_TopicCoordinators] | `LoginUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics_TopicCoordinators(ModifierUserId)` | [Journal].[ResearchTopics_TopicCoordinators] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics_TopicCoordinators(ResearchTopicId)` | [Journal].[ResearchTopics_TopicCoordinators] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.ResearchTopics_TopicCoordinators(SpaceId)` | [Journal].[ResearchTopics_TopicCoordinators] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopics_TopicCoordinators(UserId)` | [Journal].[ResearchTopics_TopicCoordinators] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopics_ViewsAndDownloads(ImpactActionId)` | [Journal].[ResearchTopics_ViewsAndDownloads] | `ImpactActionId` | [Common].[Impacts_Action] | `PK-Common.Impacts_Action` |
| `FK-Journal.ResearchTopics_ViewsAndDownloads(ImpactAggregationId)` | [Journal].[ResearchTopics_ViewsAndDownloads] | `ImpactAggregationId` | [Common].[Impacts_Aggregation] | `PK-Common.Impacts_Aggregation` |
| `FK-Journal.ResearchTopics_ViewsAndDownloads(ProviderId)` | [Journal].[ResearchTopics_ViewsAndDownloads] | `ProviderId` | [Common].[Impacts_Provider] | `PK-Common.Impacts_Provider` |
| `FK-Journal.ResearchTopics_ViewsAndDownloads(ResearchTopicId)` | [Journal].[ResearchTopics_ViewsAndDownloads] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.ResearchTopics_ViewsAndDownloads(SpaceId)` | [Journal].[ResearchTopics_ViewsAndDownloads] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopicSuggestedContributors(AlgorithmTypeId)` | [Journal].[ResearchTopicSuggestedContributors] | `AlgorithmTypeId` | [Journal].[ResearchTopicSuggestedContributors_AlgorithmType] | `PK-Journal.ResearchTopicSuggestedContributors_AlgorithmType` |
| `FK-Journal.ResearchTopicSuggestedContributors(ContributorId)` | [Journal].[ResearchTopicSuggestedContributors] | `ContributorId` | [Journal].[ResearchTopics_Contributors] | `PK-Journal.ResearchTopics_Contributors` |
| `FK-Journal.ResearchTopicSuggestedContributors(CreateUserId)` | [Journal].[ResearchTopicSuggestedContributors] | `CreateUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopicSuggestedContributors(EOfDecisionReasonId)` | [Journal].[ResearchTopicSuggestedContributors] | `EOfDecisionReasonId` | [Journal].[ResearchTopicSuggestedContributors_Action] | `PK-Journal.ResearchTopicSuggestedContributors_Action` |
| `FK-Journal.ResearchTopicSuggestedContributors(EOfEvaluationStatusId)` | [Journal].[ResearchTopicSuggestedContributors] | `EOfEvaluationStatusId` | [Journal].[ResearchTopicSuggestedContributors_Action] | `PK-Journal.ResearchTopicSuggestedContributors_Action` |
| `FK-Journal.ResearchTopicSuggestedContributors(ModifyUserId)` | [Journal].[ResearchTopicSuggestedContributors] | `ModifyUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.ResearchTopicSuggestedContributors(NessieVersionId)` | [Journal].[ResearchTopicSuggestedContributors] | `NessieVersionId` | [Journal].[ResearchTopicSuggestedContributors_NessieVersion] | `PK-Journal.ResearchTopicSuggestedContributors_NessieVersion` |
| `FK-Journal.ResearchTopicSuggestedContributors(ResearchTopicId)` | [Journal].[ResearchTopicSuggestedContributors] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.ResearchTopicSuggestedContributors(SpaceId)` | [Journal].[ResearchTopicSuggestedContributors] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.ResearchTopicSuggestedContributors(TEDecisionReasonId)` | [Journal].[ResearchTopicSuggestedContributors] | `TEDecisionReasonId` | [Journal].[ResearchTopicSuggestedContributors_Action] | `PK-Journal.ResearchTopicSuggestedContributors_Action` |
| `FK-Journal.ResearchTopicSuggestedContributors(TEEvaluationStatusId)` | [Journal].[ResearchTopicSuggestedContributors] | `TEEvaluationStatusId` | [Journal].[ResearchTopicSuggestedContributors_Action] | `PK-Journal.ResearchTopicSuggestedContributors_Action` |
| `FK-Journal.ResearchTopicSuggestedContributors(TEHideReasonId)` | [Journal].[ResearchTopicSuggestedContributors] | `TEHideReasonId` | [Journal].[ResearchTopicSuggestedContributors_Action] | `PK-Journal.ResearchTopicSuggestedContributors_Action` |
| `FK-Journal.ResearchTopicSuggestedContributors(UploadTypeId)` | [Journal].[ResearchTopicSuggestedContributors] | `UploadTypeId` | [Journal].[ResearchTopicSuggestedContributors_UploadType] | `PK-Journal.ResearchTopicSuggestedContributors_UploadType` |
| `FK-Journal.ResearchTopicSuggestedContributors(UserId)` | [Journal].[ResearchTopicSuggestedContributors] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Submissions(ArticleId)` | [Journal].[Submissions] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Submissions(ArticleTypeId)` | [Journal].[Submissions] | `ArticleTypeId` | [Journal].[Articles_Type] | `PK-Journal.Articles_Type` |
| `FK-Journal.Submissions(CreatorUserId)` | [Journal].[Submissions] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Submissions(LoginUserId)` | [Journal].[Submissions] | `LoginUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Submissions(ModifierUserId)` | [Journal].[Submissions] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Submissions(PreferredEditorId)` | [Journal].[Submissions] | `PreferredEditorId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Submissions(ResearchTopicId)` | [Journal].[Submissions] | `ResearchTopicId` | [Journal].[ResearchTopics] | `PK-Journal.ResearchTopics` |
| `FK-Journal.Submissions(SourceId)` | [Journal].[Submissions] | `SourceId` | [Journal].[Submissions_Source] | `PK-Journal.Submissions_Source` |
| `FK-Journal.Submissions(SourceTypeId)` | [Journal].[Submissions] | `SourceTypeId` | [Journal].[Submissions_SourceType] | `PK-Journal.Submissions_SourceType` |
| `FK-Journal.Submissions(SpaceId)` | [Journal].[Submissions] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Submissions(StageId)` | [Journal].[Submissions] | `StageId` | [Journal].[Articles_Stage] | `PK-Journal.Articles_Stage` |
| `FK-Journal.Submissions(StatusId)` | [Journal].[Submissions] | `StatusId` | [Journal].[Submissions_Status] | `PK-Journal.Submissions_Status` |
| `FK-Journal.Submissions(TaxonomyId)` | [Journal].[Submissions] | `TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.Submissions(TransferredFromExternalPartner.ExternalPartnerId)` | [Journal].[Submissions] | `TransferredFromExternalPartner.ExternalPartnerId` | [Journal].[Submissions.ExternalPartners] | `PK-Journal.Submissions.ExternalPartners` |
| `FK-Journal.Submissions_Authors(AuthorAffiliationId)` | [Journal].[Submissions_Authors] | `AuthorAffiliationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Journal.Submissions_Authors(AuthorRosstId)` | [Journal].[Submissions_Authors] | `AuthorRosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Journal.Submissions_Authors(CreatorUserId)` | [Journal].[Submissions_Authors] | `CreatorUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Submissions_Authors(LoginUserId)` | [Journal].[Submissions_Authors] | `LoginUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Submissions_Authors(ModifierUserId)` | [Journal].[Submissions_Authors] | `ModifierUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Submissions_Authors(SpaceId)` | [Journal].[Submissions_Authors] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Submissions_Authors(SubmissionId)` | [Journal].[Submissions_Authors] | `SubmissionId` | [Journal].[Submissions] | `PK-Journal.Submissions` |
| `FK-Journal.Submissions_Authors(TitleId)` | [Journal].[Submissions_Authors] | `TitleId` | [Network].[Users_Title] | `PK-Network.Users_Title` |
| `FK-Journal.Users(JournalRole.FirstAssigned.JournalRoleId)` | [Journal].[Users] | `JournalRole.FirstAssigned.JournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.Users(JournalRole.FirstAssigned.TaxonomyId)` | [Journal].[Users] | `JournalRole.FirstAssigned.TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.Users(JournalRole.HighestRankArticle.FirstAssigned.JournalRoleId)` | [Journal].[Users] | `JournalRole.HighestRankArticle.FirstAssigned.JournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.Users(JournalRole.HighestRankArticle.FirstAssigned.TaxonomyId)` | [Journal].[Users] | `JournalRole.HighestRankArticle.FirstAssigned.TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.Users(JournalRole.HighestRankResearchTopic.FirstAssigned.JournalRoleId)` | [Journal].[Users] | `JournalRole.HighestRankResearchTopic.FirstAssigned.JournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.Users(JournalRole.HighestRankResearchTopic.FirstAssigned.TaxonomyId)` | [Journal].[Users] | `JournalRole.HighestRankResearchTopic.FirstAssigned.TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.Users(SpaceId)` | [Journal].[Users] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Users(UserId)` | [Journal].[Users] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Users_JournalRoles(JournalRole.FirstAssigned.TaxonomyId)` | [Journal].[Users_JournalRoles] | `JournalRole.FirstAssigned.TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.Users_JournalRoles(JournalRole.LastAssigned.TaxonomyId)` | [Journal].[Users_JournalRoles] | `JournalRole.LastAssigned.TaxonomyId` | [Common].[Taxonomy] | `PK-Common.Taxonomy` |
| `FK-Journal.Users_JournalRoles(JournalRoleId)` | [Journal].[Users_JournalRoles] | `JournalRoleId` | [Journal].[JournalRole] | `PK-Journal.JournalRole` |
| `FK-Journal.Users_JournalRoles(SpaceId)` | [Journal].[Users_JournalRoles] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Users_JournalRoles(UserId)` | [Journal].[Users_JournalRoles] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Workflows(PipelineStageId)` | [Journal].[Workflows] | `PipelineStageId` | [Journal].[Workflows_PipelineStage] | `PK-Journal.Workflows_PipelineStage` |
| `FK-Journal.Workflows_Emails(MessageTypeId)` | [Journal].[Workflows_Emails] | `MessageTypeId` | [Journal].[Workflows_MessageType] | `PK-Journal.Workflows_MessageType` |
| `FK-Journal.Workflows_Emails(SpaceId)` | [Journal].[Workflows_Emails] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Workflows_Emails(TimeoutId)` | [Journal].[Workflows_Emails] | `TimeoutId` | [Journal].[Workflows_Timeouts] | `PK-Journal.Workflows_Timeouts` |
| `FK-Journal.Workflows_Emails(WorkflowId)` | [Journal].[Workflows_Emails] | `WorkflowId` | [Journal].[Workflows] | `PK-Journal.Workflows` |
| `FK-Journal.Workflows_NotificationSalutation(SpaceId)` | [Journal].[Workflows_NotificationSalutation] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Workflows_NotificationTemplates(SalutationId)` | [Journal].[Workflows_NotificationTemplates] | `SalutationId` | [Journal].[Workflows_NotificationSalutation] | `PK-Journal.Workflows_NotificationSalutation` |
| `FK-Journal.Workflows_NotificationTemplates(SpaceId)` | [Journal].[Workflows_NotificationTemplates] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Workflows_PipelineStage(ModuleId)` | [Journal].[Workflows_PipelineStage] | `ModuleId` | [Journal].[Workflows_Module] | `PK-Journal.Workflows_Module` |
| `FK-Journal.Workflows_Tasks(ArticleId)` | [Journal].[Workflows_Tasks] | `ArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Journal.Workflows_Tasks(InvoiceId)` | [Journal].[Workflows_Tasks] | `InvoiceId` | [Accounting].[Invoices] | `PK-Accounting.Invoices` |
| `FK-Journal.Workflows_Tasks(LastUsedTimeoutId)` | [Journal].[Workflows_Tasks] | `LastUsedTimeoutId` | [Journal].[Workflows_Timeouts] | `PK-Journal.Workflows_Timeouts` |
| `FK-Journal.Workflows_Tasks(ModuleId)` | [Journal].[Workflows_Tasks] | `ModuleId` | [Journal].[Workflows_Module] | `PK-Journal.Workflows_Module` |
| `FK-Journal.Workflows_Tasks(NextTimeoutId)` | [Journal].[Workflows_Tasks] | `NextTimeoutId` | [Journal].[Workflows_Timeouts] | `PK-Journal.Workflows_Timeouts` |
| `FK-Journal.Workflows_Tasks(SpaceId)` | [Journal].[Workflows_Tasks] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Workflows_Tasks(UserId)` | [Journal].[Workflows_Tasks] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Journal.Workflows_Tasks(WorkflowId)` | [Journal].[Workflows_Tasks] | `WorkflowId` | [Journal].[Workflows] | `PK-Journal.Workflows` |
| `FK-Journal.Workflows_Tasks(WorkflowStatusId)` | [Journal].[Workflows_Tasks] | `WorkflowStatusId` | [Journal].[Workflows_Status] | `PK-Journal.Workflows_Status` |
| `FK-Journal.Workflows_Timeouts(SpaceId)` | [Journal].[Workflows_Timeouts] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Journal.Workflows_Timeouts(WorkflowId)` | [Journal].[Workflows_Timeouts] | `WorkflowId` | [Journal].[Workflows] | `PK-Journal.Workflows` |
| `FK-Network.Employees(CurrentJobProfileId)` | [Network].[Employees] | `CurrentJobProfileId` | [Common].[JobProfiles] | `PK-Common.JobProfiles` |
| `FK-Network.Employees(LoopUserId)` | [Network].[Employees] | `LoopUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Network.Users.Recognition(EnrollmentArticleId)` | [Network].[Users.Recognition] | `EnrollmentArticleId` | [Journal].[Articles] | `PK-Journal.Articles` |
| `FK-Network.Users.Recognition(SpaceId)` | [Network].[Users.Recognition] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Network.Users.Recognition(SpaceId,EnrollmentJournalId)` | [Network].[Users.Recognition] | `EnrollmentJournalId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-Network.Users.Recognition(SpaceId,EnrollmentJournalId)` | [Network].[Users.Recognition] | `SpaceId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-Network.Users.Recognition(SpaceId,EnrollmentSectionId)` | [Network].[Users.Recognition] | `EnrollmentSectionId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-Network.Users.Recognition(SpaceId,EnrollmentSectionId)` | [Network].[Users.Recognition] | `SpaceId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-Network.Users.Recognition(UserId)` | [Network].[Users.Recognition] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Network.Users_Addresses(CountryId)` | [Network].[Users_Addresses] | `CountryId` | [Common].[Countries] | `PK-Common.Countries` |
| `FK-Network.Users_Addresses(OrganizationTypeId)` | [Network].[Users_Addresses] | `OrganizationTypeId` | [Network].[Users_OrganizationType] | `PK-Network.Users_OrganizationType` |
| `FK-Network.Users_Addresses(UserId)` | [Network].[Users_Addresses] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Network.Users_AIRA(PersonId)` | [Network].[Users_AIRA] | `PersonId` | [Person].[Persons] | `PK-Person.Persons` |
| `FK-Network.Users_AIRA(UserId)` | [Network].[Users_AIRA] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Network.Users_Educations(DegreeId)` | [Network].[Users_Educations] | `DegreeId` | [Network].[Users_Degree] | `PK-Network.Users_Degree` |
| `FK-Network.Users_Educations(UserId)` | [Network].[Users_Educations] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Network.Users_Emails(UserId)` | [Network].[Users_Emails] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Network.Users_Experiences(AddressId)` | [Network].[Users_Experiences] | `AddressId` | [Network].[Users_Addresses] | `PK-Network.Users_Addresses` |
| `FK-Network.Users_Experiences(PositionId)` | [Network].[Users_Experiences] | `PositionId` | [Network].[Users_Position] | `PK-Network.Users_Position` |
| `FK-Network.Users_Experiences(UserId)` | [Network].[Users_Experiences] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Network.Users_Organizations(OrganizationId)` | [Network].[Users_Organizations] | `OrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Network.Users_Organizations(RosstId)` | [Network].[Users_Organizations] | `RosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Network.Users_Organizations(UserId)` | [Network].[Users_Organizations] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Network.Users_ProfileMetrics(UserId)` | [Network].[Users_ProfileMetrics] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Network.Users_Roles(RoleId)` | [Network].[Users_Roles] | `RoleId` | [Common].[Role] | `PK-Common.Role` |
| `FK-Network.Users_Roles(SpaceId)` | [Network].[Users_Roles] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Network.Users_Roles(UserId)` | [Network].[Users_Roles] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Network.Users_Titles(TitleId)` | [Network].[Users_Titles] | `TitleId` | [Network].[Users_Title] | `PK-Network.Users_Title` |
| `FK-Network.Users_Titles(UserId)` | [Network].[Users_Titles] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Person.Emails(PersonId)` | [Person].[Emails] | `PersonId` | [Person].[Persons] | `PK-Person.Persons` |
| `FK-Person.FieldStudies(FieldStudyId)` | [Person].[FieldStudies] | `FieldStudyId` | [Person].[FieldStudy] | `PK-Person.FieldStudy` |
| `FK-Person.FieldStudies(PersonId)` | [Person].[FieldStudies] | `PersonId` | [Person].[Persons] | `PK-Person.Persons` |
| `FK-Person.Metrics(CountryId)` | [Person].[Metrics] | `CountryId` | [Common].[Countries] | `PK-Common.Countries` |
| `FK-Person.Metrics(OrganizationId)` | [Person].[Metrics] | `OrganizationId` | [Common].[Organizations] | `PK-Common.Organizations` |
| `FK-Person.Metrics(PersonId)` | [Person].[Metrics] | `PersonId` | [Person].[Persons] | `PK-Person.Persons` |
| `FK-Person.Metrics(RosstId)` | [Person].[Metrics] | `RosstId` | [Common].[ResearchOrganizations] | `PK-Common.ResearchOrganizations` |
| `FK-Person.Users(PersonId)` | [Person].[Users] | `PersonId` | [Person].[Persons] | `PK-Person.Persons` |
| `FK-Person.Users(UserId)` | [Person].[Users] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Subscription.Subscribers(GloballyUnsubscribedSpaceId)` | [Subscription].[Subscribers] | `GloballyUnsubscribedSpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Subscription.Subscribers(UserId)` | [Subscription].[Subscribers] | `UserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Subscription.Subscriptions(SubscriptionTypeId)` | [Subscription].[Subscriptions] | `SubscriptionTypeId` | [Subscription].[Type] | `PK-Subscription.Type` |
| `FK-Subscription.Type(CategoryId)` | [Subscription].[Type] | `CategoryId` | [Subscription].[Category] | `PK-Subscription.Category` |
| `FK-Subscription.Type(OperationalTypeId)` | [Subscription].[Type] | `OperationalTypeId` | [Subscription].[OperationalType] | `PK-Subscription.OperationalType` |
| `FK-Subscription.Type(SpaceId)` | [Subscription].[Type] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-TransferZone.TransferOpportunity(DestinationSpaceId,DestinationJournalId)` | [TransferZone].[TransferOpportunity] | `DestinationJournalId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-TransferZone.TransferOpportunity(DestinationSpaceId,DestinationJournalId)` | [TransferZone].[TransferOpportunity] | `DestinationSpaceId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-TransferZone.TransferOpportunity(DestinationSpaceId,DestinationJournalId.Recommendation)` | [TransferZone].[TransferOpportunity] | `DestinationJournalId.Recommendation` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-TransferZone.TransferOpportunity(DestinationSpaceId,DestinationJournalId.Recommendation)` | [TransferZone].[TransferOpportunity] | `DestinationSpaceId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-TransferZone.TransferOpportunity(SourceSpaceId,SourceJournalId)` | [TransferZone].[TransferOpportunity] | `SourceJournalId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-TransferZone.TransferOpportunity(SourceSpaceId,SourceJournalId)` | [TransferZone].[TransferOpportunity] | `SourceSpaceId` | [Journal].[Journals_Details] | `UK-Journal.Journals_Details(SpaceId,JournalId)` |
| `FK-TransferZone.TransferOpportunity(StatusId)` | [TransferZone].[TransferOpportunity] | `StatusId` | [TransferZone].[TransferOpportunityStatus] | `PK-TransferZone.TransferOpportunityStatus` |
| `FK-TransferZone.TransferOpportunityHistory(OpportunityId)` | [TransferZone].[TransferOpportunityHistory] | `OpportunityId` | [TransferZone].[TransferOpportunity] | `PK-TransferZone.TransferOpportunity` |
| `FK-TransferZone.TransferOpportunityHistory(StatusId)` | [TransferZone].[TransferOpportunityHistory] | `StatusId` | [TransferZone].[TransferOpportunityStatus] | `PK-TransferZone.TransferOpportunityStatus` |
| `FK-Watchlist.@ContentsSummary(SpaceId)` | [Watchlist].[@ContentsSummary] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Watchlist.Persons(LoopUserId)` | [Watchlist].[Persons] | `LoopUserId` | [Network].[Users] | `PK-Network.Users` |
| `FK-Watchlist.Persons(SpaceId)` | [Watchlist].[Persons] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Watchlist.Persons_Emails(PersonId)` | [Watchlist].[Persons_Emails] | `PersonId` | [Watchlist].[Persons] | `PK-Watchlist.Persons` |
| `FK-Watchlist.Persons_Emails(SpaceId)` | [Watchlist].[Persons_Emails] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Watchlist.Persons_Watchlisting(PersonId)` | [Watchlist].[Persons_Watchlisting] | `PersonId` | [Watchlist].[Persons] | `PK-Watchlist.Persons` |
| `FK-Watchlist.Persons_Watchlisting(SpaceId)` | [Watchlist].[Persons_Watchlisting] | `SpaceId` | [Common].[Spaces] | `PK-Common.Spaces` |
| `FK-Watchlist.Persons_Watchlisting(WatchlistingReasonId)` | [Watchlist].[Persons_Watchlisting] | `WatchlistingReasonId` | [Watchlist].[WatchlistingReason] | `PK-Watchlist.WatchlistingReason` |
| `FK-Watchlist.Persons_Watchlisting(WatchlistingRoleId)` | [Watchlist].[Persons_Watchlisting] | `WatchlistingRoleId` | [Watchlist].[WatchlistingRole] | `PK-Watchlist.WatchlistingRole` |
| `FK-Watchlist.WatchlistingReason(CategoryId)` | [Watchlist].[WatchlistingReason] | `CategoryId` | [Watchlist].[WatchlistingReason_Category] | `PK-Watchlist.WatchlistingReason_Category` |