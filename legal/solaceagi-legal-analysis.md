# SolaceAGI Legal Analysis: API Key Usage, Tip Model, and Compliance

**Prepared:** 2026-02-21
**Jurisdiction:** United States (Delaware C-Corp assumed)
**Status:** Research memorandum -- NOT legal advice. Engage qualified counsel before implementation.
**Scope:** BYOK API key handling, voluntary tip/contribution model for open-source AI training, ToS compatibility, required disclosures

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [API Key Usage: Legal Requirements and Consent](#2-api-key-usage-legal-requirements-and-consent)
3. [Terms of Service Compatibility Analysis](#3-terms-of-service-compatibility-analysis)
4. [Tip/Contribution Model: Legal Structure](#4-tipcontribution-model-legal-structure)
5. [Open Source Funding: Models and Transparency](#5-open-source-funding-models-and-transparency)
6. [API Key Security: Best Practices and Compliance](#6-api-key-security-best-practices-and-compliance)
7. [Key Legal Risks and Mitigations](#7-key-legal-risks-and-mitigations)
8. [Required Disclosures](#8-required-disclosures)
9. [Recommended Consent Flow](#9-recommended-consent-flow)
10. [Template Terms of Service Language](#10-template-terms-of-service-language)
11. [Template Privacy Policy Language](#11-template-privacy-policy-language)
12. [Recommended Tip Tier Structure](#12-recommended-tip-tier-structure)
13. [Sources](#13-sources)

---

## 1. Executive Summary

SolaceAGI operates a BYOK (Bring Your Own Key) model where users supply their own API keys for LLM providers (Anthropic, OpenAI, Together.ai), plus a managed LLM tier where SolaceAGI proxies requests through Together.ai/OpenRouter. The platform proposes a voluntary "tip" mechanism where users consent to a percentage surcharge that funds open-source AI model training (speech synthesis, video generation).

**Core findings:**

1. **BYOK is the safest compliance path** for Anthropic's API terms, which prohibit redistribution/resale but allow value-added applications where users maintain their own billing relationship with the provider.

2. **OpenAI explicitly prohibits buying, selling, or transferring API keys** from/to/with third parties. A BYOK model where users enter their own keys into SolaceAGI's platform is a gray area -- the user is not "transferring" the key, but the platform is using it. OpenAI's terms lack explicit BYOK guidance, creating legal ambiguity.

3. **Together.ai prohibits resale and redistribution** of their services on a standalone basis but does not explicitly address BYOK scenarios. The managed LLM tier (where SolaceAGI uses its own Together.ai key) is permissible if SolaceAGI is building a value-added product, not merely proxying API access.

4. **A "tip" to a for-profit company is legally revenue**, not a donation. It is taxable income, subject to sales tax in applicable jurisdictions, and must be disclosed transparently under FTC guidelines. It cannot be characterized as a "charitable donation" unless routed through a 501(c)(3).

5. **CCPA classifies API keys as sensitive personal information** when combined with credentials that allow account access. This triggers enhanced disclosure, security, and breach notification requirements.

6. **FTC Section 5** prohibits unfair or deceptive practices. All fees, including voluntary surcharges, must be clearly disclosed before the user commits to a transaction.

---

## 2. API Key Usage: Legal Requirements and Consent

### 2.1 Federal Law (FTC)

The FTC enforces consumer protection under Section 5 of the FTC Act, which prohibits "unfair or deceptive acts or practices."

**Key principles for SolaceAGI:**

- **No retroactive expansion of data use.** The FTC issued guidance (February 2024) that a business collecting data under one set of privacy commitments cannot unilaterally expand use without affirmative consent. If a user provides an API key for "running AI agent tasks," using that key for any other purpose (e.g., benchmarking, training data generation, internal analytics) without explicit consent is potentially deceptive.

- **Prominent notice required.** Quiet updates to privacy policies do not satisfy FTC requirements. Material changes require affirmative consent. (Source: [FTC Guidelines on Using Consumer Data for New AI Projects](https://quicktakes.loeb.com/post/102j083/ftc-guidelines-on-using-consumer-data-for-new-ai-projects-retroactive-privacy-po))

- **FTC Junk Fees Rule (effective May 12, 2025).** While currently scoped to live-event tickets and short-term lodging, the FTC has warned all industries that deceptive pricing practices remain actionable under Section 5. Penalties: up to $53,088 per violation. (Source: [FTC Rule on Unfair or Deceptive Fees](https://www.ftc.gov/news-events/news/press-releases/2025/05/ftc-rule-unfair-or-deceptive-fees-take-effect-may-12-2025))

### 2.2 State Law (CCPA/CPRA -- California)

**API keys are likely "sensitive personal information" under CCPA.**

The CCPA defines sensitive personal information to include "account log-in, financial account, debit card, or credit card number in combination with any required security code, password, or credentials allowing access to an account." An API key is a credential that allows access to a paid account (Anthropic, OpenAI, Together.ai). When SolaceAGI stores a user's API key, it is storing sensitive personal information.

**CCPA requirements triggered:**

| Requirement | Description |
|---|---|
| Right to know | User can request what API keys are stored and how they are used |
| Right to delete | User can request deletion of stored API keys |
| Right to limit use | User can limit processing of sensitive personal information to what is "necessary and proportionate" |
| Breach notification | If API keys are compromised, California's breach notification law (Cal. Civ. Code 1798.82) requires notification |
| Privacy policy disclosure | Must disclose categories of sensitive personal information collected, purposes, and third parties with whom shared |

(Source: [California Consumer Privacy Act](https://oag.ca.gov/privacy/ccpa), [Jackson Lewis CCPA FAQs](https://www.jacksonlewis.com/insights/navigating-california-consumer-privacy-act-30-essential-faqs-covered-businesses-including-clarifying-regulations-effective-1126))

### 2.3 IAPP Governance Framework

The International Association of Privacy Professionals (IAPP) recommends:

- **Data Processing Agreement (DPA)** between the platform and each API provider, outlining scope of processing, lawful purposes, and data retention.
- **Privacy-enhancing technologies** (anonymization, pseudonymization, zero-data-retention endpoints) before transmitting user data through API keys.
- **Clear contractual responsibilities** and active oversight when deploying AI features via third-party APIs.
- **Affirmative express consent** before transferring sensitive data to AI services.

(Source: [IAPP - Who holds the keys?](https://iapp.org/news/a/who-holds-the-keys-navigating-legal-and-privacy-governance-in-third-party-ai-api-access))

### 2.4 Required Consent Elements

For SolaceAGI to use a customer's API key on their behalf, the following consent elements are required:

1. **Specificity:** Disclose exactly what the key will be used for (e.g., "sending prompts to Anthropic's API on your behalf to execute agent tasks you initiate").
2. **Scope limitation:** Disclose what the key will NOT be used for (e.g., "We will not use your API key for our own research, benchmarking, model training, or any purpose other than executing tasks you explicitly request").
3. **Third-party disclosure:** If the key is transmitted to any party other than the API provider (e.g., a sub-processor), this must be disclosed.
4. **Retention:** How long the key is stored, and the user's ability to revoke/delete.
5. **Security measures:** How the key is protected (encryption standard, access controls).

---

## 3. Terms of Service Compatibility Analysis

### 3.1 Anthropic

| Factor | Assessment |
|---|---|
| **BYOK model** | COMPLIANT (likely). Users maintain their own billing relationship with Anthropic. SolaceAGI stores the key securely and uses it only for user-initiated requests. This is the "most straightforward path to compliance." |
| **Managed LLM tier** | NOT APPLICABLE. SolaceAGI's managed tier uses Together.ai/OpenRouter, not Anthropic's API with SolaceAGI's key for third-party end users. |
| **Wrapper risk** | LOW if SolaceAGI provides substantial value beyond API passthrough (agent orchestration, skill system, OAuth3 vault, twin browser). Products where "removing the Claude API call would leave you with an empty shell" face highest risk. SolaceAGI's architecture (multi-provider, agent orchestration, skill ecosystem) is clearly value-added. |
| **Consumer subscription tokens** | PROHIBITED. Using OAuth tokens from Claude Free/Pro/Max accounts in third-party tools violates Consumer ToS. SolaceAGI must only accept API keys from Claude Console (API tier). |

**Key Anthropic restriction (paraphrased):** Companies cannot use a single organizational API key to funnel access to end users who are not part of the company. Redistribution and resale are prohibited. The BYOK model, where each user authenticates with their own key, is the compliant path.

(Sources: [SitePoint - End of the Wrapper Era](https://www.sitepoint.com/end-wrapper-era-anthropic-api-terms-saas/), [VentureBeat - Anthropic cracks down](https://venturebeat.com/technology/anthropic-cracks-down-on-unauthorized-claude-usage-by-third-party-harnesses))

### 3.2 OpenAI

| Factor | Assessment |
|---|---|
| **BYOK model** | AMBIGUOUS. OpenAI states: "Customer will not, and will not permit End Users to: (g) buy, sell, or transfer API keys from, to, or with a third party." The user entering their own key into SolaceAGI is not "selling" or "buying" the key, but it could be construed as "transferring" it to a third party. |
| **Official guidance** | ABSENT. OpenAI's terms are silent on BYOK implementations. Community forum responses suggest this is a gray area. |
| **Risk level** | MEDIUM. Many products (JetBrains, Cursor, etc.) operate BYOK models with OpenAI keys. No known enforcement actions against legitimate BYOK platforms, but the terms do not explicitly permit it. |
| **Mitigation** | Consider reaching out to OpenAI's partnerships team for written confirmation. Alternatively, users can be advised to use OpenAI through OpenRouter (where the contractual relationship is between the user and OpenRouter). |

(Sources: [OpenAI Services Agreement](https://openai.com/policies/services-agreement/), [OpenAI BYOK Policy Discussion](https://community.openai.com/t/bring-your-own-key-policy/446168), [OpenAI Best Practices for API Key Safety](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety))

### 3.3 Together.ai

| Factor | Assessment |
|---|---|
| **Managed LLM tier (SolaceAGI's key)** | LIKELY COMPLIANT if SolaceAGI is building a value-added product, not offering Together.ai "on a standalone basis." The prohibition is: "transfer, distribute, resell, lease, license, or assign the Services or otherwise offer the Services on a standalone basis." SolaceAGI's agent orchestration + skill system + OAuth3 = substantial value-add. |
| **BYOK model** | NOT EXPLICITLY ADDRESSED. Terms do not mention BYOK. Same analysis as Anthropic: user maintains billing relationship, SolaceAGI uses key only for user-initiated requests. |
| **Third-party model terms** | IMPORTANT. Together.ai hosts third-party models (Llama, etc.) with their own licenses. SolaceAGI must ensure compliance with underlying model licenses (e.g., Llama's community license). |

(Source: [Together.ai Terms of Service](https://www.together.ai/terms-of-service))

### 3.4 Compatibility Summary

| Provider | BYOK | Managed (SolaceAGI key) | Risk |
|---|---|---|---|
| Anthropic | Compliant | Prohibited (resale) | LOW (BYOK) |
| OpenAI | Ambiguous | Prohibited (resale) | MEDIUM (BYOK) |
| Together.ai | Not addressed | Likely compliant (value-add) | LOW-MEDIUM |
| OpenRouter | Compliant | Compliant (designed for this) | LOW |

---

## 4. Tip/Contribution Model: Legal Structure

### 4.1 Critical Distinction: "Tip" vs. "Donation" vs. "Fee"

**A for-profit Delaware C-Corp cannot receive tax-deductible "donations."** The term "donation" implies charitable giving to a tax-exempt entity (501(c)(3)). SolaceAGI must use language that does not create this false impression.

| Term | Legal Meaning | Tax Treatment | Appropriate? |
|---|---|---|---|
| **Donation** | Gift to tax-exempt org | Tax-deductible for donor | NO -- misleading if SolaceAGI is for-profit |
| **Tip/Gratuity** | Voluntary payment above price | Taxable revenue to recipient | PARTIALLY -- "tip" implies service worker compensation |
| **Voluntary contribution** | Optional payment for stated purpose | Taxable revenue to recipient | YES -- accurate and clear |
| **Platform tip** | Voluntary surcharge to support platform | Taxable revenue to recipient | YES -- precedent from Open Collective |
| **Open-source development fund contribution** | Earmarked voluntary payment | Taxable revenue, earmarked | YES -- most precise |
| **Fee/Surcharge** | Mandatory charge | Taxable revenue | NO -- the payment is voluntary |

**Recommended terminology:** "Open-Source AI Contribution" or "Community Development Contribution"

### 4.2 Tax Treatment

- **Federal income tax:** Voluntary contributions to a for-profit company are taxable revenue. Report as ordinary business income on corporate tax return.
- **Self-employment tax:** Not applicable to C-Corp (paid through corporate income tax).
- **Sales tax:** Varies by state. If the contribution is tied to the provision of a service (e.g., added during checkout for an AI task), it may be subject to sales tax in states that tax SaaS. If it is truly voluntary and not tied to a specific deliverable, it is more likely exempt. Consult a state tax advisor for each jurisdiction.
- **1099 reporting:** Not applicable (SolaceAGI receives the money, not pays it out).

(Sources: [GitHub Sponsors Tax Information](https://docs.github.com/en/sponsors/receiving-sponsorships-through-github-sponsors/tax-information-for-github-sponsors), [Buy Me a Coffee Tax Treatment](https://help.buymeacoffee.com/en/articles/8039657-understanding-the-tax-process-on-buy-me-a-coffee))

### 4.3 What Makes a "Tip" Legally Distinct from a "Fee"

Under FTC guidance and state consumer protection law:

1. **Voluntary:** The user must be able to set the amount to $0 without losing access to any functionality. If any feature is gated behind the tip, it is a fee.
2. **Default disclosure:** If a default tip percentage is pre-selected, this must be clearly disclosed and easily changeable. Pre-checked boxes that increase the price are scrutinized under FTC deceptive practices doctrine.
3. **No penalty for opting out:** The user experience must not degrade for users who decline the contribution.
4. **Clear purpose:** The user must know exactly what the money funds.

**Can a platform require a minimum tip?** A mandatory minimum "tip" is legally a fee, not a tip. You cannot require a minimum and call it voluntary. However, you CAN set minimum denominations (e.g., "contributions start at $1") as long as $0 is also an option.

### 4.4 Open Collective Precedent

Open Collective's "Platform Tips" provide a strong precedent:

- Platform Tips are "voluntary contributions added at checkout"
- They are "totally optional, and the amount can be changed to any amount you wish"
- They are "accounted for separately from Collective Funds"
- The platform "relies primarily on voluntary Platform Tips to sustain its operation"

SolaceAGI should adopt a similar structure: voluntary, clearly labeled, separately accounted, with a stated purpose.

(Source: [Open Collective Platform Tips Documentation](https://documentation.opencollective.com/giving-to-collectives/platform-tips))

---

## 5. Open Source Funding: Models and Transparency

### 5.1 Established Models

| Organization | Structure | Funding Model | Transparency |
|---|---|---|---|
| **Apache Software Foundation** | 501(c)(3) | Corporate sponsorships + individual donations | GuideStar Gold Seal, <10% overhead, public financials |
| **Linux Foundation** | 501(c)(6) | Membership fees + event revenue + training | Public ledger of donations, LFX Crowdfunding platform |
| **Mozilla Foundation** | 501(c)(3) + for-profit subsidiary (Mozilla Corp) | Google search deal + donations + grants | Charity Navigator rated, public 990 filings |
| **Open Collective** | For-profit platform + fiscal hosts | Platform tips (voluntary) + host fees | Full transaction transparency on platform |
| **Nari Labs** | For-profit | Google TPU Research Cloud + HuggingFace ZeroGPU grant | MIT/Apache licensed outputs |

(Sources: [Apache Software Foundation](https://www.apache.org/foundation/individual-supporters), [Linux Foundation Crowdfunding](https://docs.linuxfoundation.org/lfx/crowdfunding/donate-sponsor), [Mozilla Foundation - Wikipedia](https://en.wikipedia.org/wiki/Mozilla_Foundation))

### 5.2 SolaceAGI's Position

SolaceAGI is a **for-profit company** collecting voluntary contributions for open-source AI development. This is analogous to:

- **Open Collective** (for-profit platform sustaining itself through voluntary platform tips)
- **Mozilla Corporation** (for-profit subsidiary of a nonprofit, using commercial revenue to fund open-source development)
- **GitHub Sponsors** (for-profit platform facilitating funding for developers)

### 5.3 Transparency Requirements

Since SolaceAGI is for-profit, it has no legal obligation to publish financials publicly. However, for trust and competitive positioning, the following transparency measures are recommended:

1. **Public ledger of open-source fund allocations.** Show how tip revenue is spent (compute costs, researcher compensation, model training infrastructure).
2. **Quarterly transparency reports.** Publish total contributions received, total allocated to open-source training, and specific models/projects funded.
3. **Open-source deliverables.** All models trained with contribution funds should be released under permissive licenses (Apache 2.0, MIT).
4. **Earmarking discipline.** Contributions designated for open-source AI training should be tracked separately in accounting and used only for that purpose. Commingling with general revenue, while legal, would undermine trust and create FTC risk if the stated purpose was specific.

### 5.4 IRS Consideration: Private Inurement

In July 2025, the IRS denied 501(c)(3) status to an open-source software organization because a for-profit company owned by the founder was managing operations, creating "private inurement." This is relevant if SolaceAGI ever considers creating a nonprofit arm:

- Keep the for-profit and any future nonprofit arm at arm's length.
- Do not route nonprofit funds through the for-profit without fair-market-value contracts.
- If creating a 501(c)(3) to receive tax-deductible donations, ensure genuine independence.

---

## 6. API Key Security: Best Practices and Compliance

### 6.1 Storage

| Practice | Requirement Level | Implementation |
|---|---|---|
| **Encryption at rest** | MANDATORY | AES-256-GCM (already in SolaceAGI's OAuth3 vault design) |
| **Key Management Service** | STRONGLY RECOMMENDED | AWS KMS, Azure Key Vault, HashiCorp Vault, or self-hosted HSM |
| **No plaintext storage** | MANDATORY | Keys must never be stored in plaintext in databases, logs, or config files |
| **Environment variable isolation** | MANDATORY | API keys must not be in source code, version control, or build artifacts |

### 6.2 Access Control

| Practice | Requirement Level |
|---|---|
| Role-based access control (RBAC) | MANDATORY |
| Multi-factor authentication for admin access to key vault | STRONGLY RECOMMENDED |
| Per-user key isolation (user A cannot access user B's keys) | MANDATORY |
| Principle of least privilege for service accounts | MANDATORY |

### 6.3 Logging and Auditing

| Log Field | Purpose |
|---|---|
| Timestamp | When the key was used |
| User ID | Which user's key was invoked |
| API provider | Which provider was called |
| Endpoint/model | What was requested |
| Request size (tokens) | Resource consumption tracking |
| Response status code | Success/failure monitoring |
| Source IP | Anomaly detection |

**Critical:** Logs must NEVER contain the API key itself, prompt content, or response content. Log metadata only.

**Retention:** Minimum 12 months for SOC 2 compliance. California breach notification requires prompt detection, so real-time monitoring is recommended.

### 6.4 Key Rotation and Lifecycle

- Notify users if their key has not been rotated in 90 days.
- Provide one-click key deletion from the platform.
- On account deletion, immediately and irrevocably purge all stored keys.
- If a breach is detected, automatically invalidate all stored keys and notify users.

### 6.5 Compliance Standards

| Standard | Relevance |
|---|---|
| **SOC 2 Type II** | Evaluates protection of customer data including API credentials |
| **OWASP Secrets Management** | Cheat sheet for secure key storage and handling |
| **PCI DSS** | Relevant if storing payment credentials alongside API keys |
| **CCPA/CPRA** | API keys = sensitive personal information; triggers enhanced protections |

(Sources: [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html), [OWASP Key Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Key_Management_Cheat_Sheet.html), [Anthropic API Key Best Practices](https://support.claude.com/en/articles/9767949-api-key-best-practices-keeping-your-keys-safe-and-secure))

---

## 7. Key Legal Risks and Mitigations

### Risk 1: OpenAI ToS Violation (API Key Transfer)

- **Risk:** OpenAI's terms prohibit "transferring" API keys to third parties. A user entering their key into SolaceAGI could be construed as a transfer.
- **Likelihood:** MEDIUM. Many BYOK products exist without enforcement, but no explicit safe harbor.
- **Mitigation:** (a) Seek written confirmation from OpenAI's partnerships team. (b) Route OpenAI access through OpenRouter instead of direct BYOK. (c) Frame the architecture so the user's browser/client makes the API call directly (client-side BYOK) rather than SolaceAGI's server.

### Risk 2: Anthropic Wrapper Classification

- **Risk:** If SolaceAGI is classified as a "pure wrapper" rather than a value-added product, it could violate Anthropic's terms.
- **Likelihood:** LOW. SolaceAGI's skill ecosystem, agent orchestration, OAuth3 vault, and twin browser provide substantial independent value.
- **Mitigation:** Ensure marketing and documentation emphasize the platform's value-add beyond LLM access. Never position the product as "cheaper Claude access."

### Risk 3: "Tip" Characterized as Deceptive Fee

- **Risk:** If the tip is pre-selected or hard to decline, the FTC could characterize it as a deceptive fee under Section 5.
- **Likelihood:** MEDIUM if default is non-zero; LOW if default is $0.
- **Mitigation:** (a) Default to $0 or clearly show the tip as optional with one-click removal. (b) Never gate any functionality behind the tip. (c) Clearly label the purpose.

### Risk 4: Tip Funds Misused / Commingling

- **Risk:** If SolaceAGI states that tips fund "open-source AI model training" but uses the money for general operations, this is potentially deceptive under FTC Section 5.
- **Likelihood:** LOW if proper accounting controls are in place.
- **Mitigation:** (a) Maintain a separate accounting ledger for contribution funds. (b) Publish quarterly transparency reports. (c) Ensure all funded outputs are actually released as open source.

### Risk 5: CCPA Breach Notification

- **Risk:** A breach of stored API keys triggers California's breach notification requirements.
- **Likelihood:** Depends on security posture.
- **Mitigation:** (a) AES-256-GCM encryption at rest. (b) HSM/KMS for encryption key management. (c) Real-time anomaly detection on key usage. (d) Incident response plan with 72-hour notification capability.

### Risk 6: Together.ai Terms Violation (Managed LLM Tier)

- **Risk:** Together.ai prohibits offering their services "on a standalone basis." If SolaceAGI's managed tier is perceived as merely proxying Together.ai API access, this could violate terms.
- **Likelihood:** LOW. SolaceAGI's managed tier includes agent orchestration, skill system, and platform features -- clearly not standalone API access.
- **Mitigation:** Never market the managed tier as "Together.ai access." Position it as "SolaceAGI's managed AI agent service."

### Risk 7: Misleading "Donation" Language

- **Risk:** Using the word "donation" for a payment to a for-profit company could be deceptive, as it implies tax-deductibility.
- **Likelihood:** MEDIUM if "donation" is used; LOW if "contribution" is used.
- **Mitigation:** Never use "donation," "charity," or "tax-deductible" in connection with the voluntary contribution. Use "contribution" or "tip."

---

## 8. Required Disclosures

### 8.1 At Point of API Key Entry

The following must be displayed when a user enters their API key:

```
YOUR API KEY USAGE

By providing your [Provider] API key, you authorize SolaceAGI to:
- Send requests to [Provider]'s API on your behalf to execute tasks you initiate
- Store your key using AES-256-GCM encryption in our secure vault

We will NOT:
- Use your API key for any purpose other than executing tasks you explicitly request
- Share your API key with any third party
- Use your API key for our own research, benchmarking, or model training
- Retain your API key after you delete your account

You can revoke access and delete your stored key at any time from Settings > API Keys.

Your API key is classified as sensitive personal information under applicable privacy
laws. See our Privacy Policy for details on how we protect and handle this data.
```

### 8.2 At Point of Voluntary Contribution

```
COMMUNITY DEVELOPMENT CONTRIBUTION (OPTIONAL)

You may add a voluntary contribution to support open-source AI model development.
This is entirely optional and does not affect your access to any SolaceAGI features.

Your contribution funds:
- Open-source speech synthesis model training
- Open-source video generation model development
- Compute infrastructure for community AI research

All models trained with contribution funds are released under permissive open-source
licenses (Apache 2.0 or MIT).

This is NOT a tax-deductible charitable donation. SolaceAGI, Inc. is a for-profit
corporation. Contributions are processed as revenue and subject to applicable taxes.

Contribution amount: [slider: $0 -- custom amount]
[  ] Add $X.XX (Y%) to this transaction
[  ] No contribution this time

You can change your default contribution preference in Settings > Contributions.
```

### 8.3 In Privacy Policy

- Categories of sensitive personal information collected (API keys = "credentials allowing access to an account")
- Purposes of collection (executing user-initiated AI tasks)
- Third parties receiving the data (API providers: Anthropic, OpenAI, Together.ai, OpenRouter)
- Retention period
- User rights (access, deletion, portability)
- Security measures

### 8.4 In Terms of Service

- API key usage scope and limitations
- Voluntary contribution terms (not a donation, not tax-deductible, refund policy)
- User's responsibility for their API key security
- SolaceAGI's liability limitations for API provider actions

---

## 9. Recommended Consent Flow

### Step 1: Account Creation
```
[ ] I agree to SolaceAGI's Terms of Service and Privacy Policy
    [Link: Terms of Service] [Link: Privacy Policy]
```

### Step 2: API Key Entry (per provider)
```
Add your Anthropic API Key
[Input field]

By clicking "Save Key," you consent to SolaceAGI storing this key
securely and using it exclusively to execute AI tasks you initiate.

[Link: How we protect your API key]
[Link: View our API Key Usage Policy]

[Save Key]  [Cancel]
```

### Step 3: First Task with Contribution Prompt
```
Before running your first task:

Would you like to support open-source AI development?

SolaceAGI offers a voluntary Community Development Contribution that
funds training of open-source speech synthesis and video generation models.

All funded models are released under permissive open-source licenses.
This is NOT a tax-deductible donation.

Choose your preference:
( ) No contribution
( ) 5% of API costs -- Supporter
( ) 10% of API costs -- Builder
( ) 15% of API costs -- Champion
( ) Custom: ____%

[x] Remember my choice (changeable anytime in Settings)

[Continue]
```

### Step 4: Per-Transaction Confirmation (first 3 transactions)
```
Task cost estimate: $0.12 (API tokens)
Community contribution (10%): $0.012
Total: $0.132

[Run Task]  [Change contribution]
```

### Step 5: Ongoing (after 3 transactions)
```
Contribution amount shown in task receipt.
Monthly summary email with total contributions and funded projects.
```

---

## 10. Template Terms of Service Language

### Section: API Key Usage

```
7. API KEY USAGE

7.1 Authorization. By providing a third-party API key ("Your Key") to
SolaceAGI, you grant SolaceAGI a limited, revocable, non-transferable
license to use Your Key solely for the purpose of making API calls to
the applicable third-party provider on your behalf, in response to
tasks you initiate through the Service.

7.2 Scope Limitation. SolaceAGI will use Your Key exclusively to
execute tasks you explicitly request. SolaceAGI will not use Your Key
for any other purpose, including but not limited to: internal research,
benchmarking, model training, analytics, or any purpose that does not
directly serve a task you initiated.

7.3 Security. SolaceAGI stores Your Key using AES-256-GCM encryption
at rest within an isolated key vault. Access to stored keys is
restricted to automated service processes necessary to execute your
tasks. No SolaceAGI employee has access to Your Key in plaintext.

7.4 Your Responsibility. You are solely responsible for the security
of Your Key prior to providing it to SolaceAGI, and for any charges
incurred on your third-party provider account as a result of tasks you
initiate through the Service. You represent that you have the right to
use Your Key with third-party applications and that such use does not
violate the terms of service of the applicable provider.

7.5 Revocation. You may delete Your Key from SolaceAGI at any time
via Settings > API Keys. Upon deletion, SolaceAGI will irrevocably
purge Your Key from all storage systems within 24 hours.

7.6 No Guarantee. SolaceAGI does not guarantee the availability,
accuracy, or performance of any third-party API provider. SolaceAGI is
not liable for any actions taken by a third-party provider, including
suspension or termination of your account with such provider.
```

### Section: Managed LLM Service

```
8. MANAGED LLM SERVICE

8.1 Description. SolaceAGI's Managed LLM tier routes your AI tasks
through SolaceAGI's accounts with third-party LLM providers (currently
Together.ai and OpenRouter). You do not need to provide your own API key.

8.2 Pricing. The Managed LLM tier is priced at a flat monthly fee
plus a markup on actual token costs incurred. Current pricing is
published at solaceagi.com/pricing and may be updated with 30 days'
notice.

8.3 No Direct Relationship. When using the Managed LLM tier, your
prompts and responses are processed through SolaceAGI's provider
accounts. You do not have a direct contractual relationship with the
underlying LLM provider for these requests.
```

### Section: Community Development Contribution

```
9. COMMUNITY DEVELOPMENT CONTRIBUTION

9.1 Voluntary Nature. SolaceAGI offers an optional Community
Development Contribution ("Contribution") that you may add to your
transactions. The Contribution is entirely voluntary. No SolaceAGI
feature, functionality, or service level is conditioned on making a
Contribution. You may set your Contribution to zero at any time.

9.2 Purpose. Contributions are earmarked for the development and
training of open-source AI models, including but not limited to speech
synthesis and video generation models. All models funded by
Contributions will be released under permissive open-source licenses
(Apache 2.0 or MIT).

9.3 Not a Charitable Donation. SolaceAGI, Inc. is a for-profit
Delaware C-Corporation. Contributions are NOT tax-deductible charitable
donations. Contributions are processed as revenue to SolaceAGI and are
subject to applicable taxes.

9.4 Transparency. SolaceAGI will publish quarterly reports detailing
total Contributions received and their allocation to specific
open-source projects and compute infrastructure.

9.5 Refunds. Contributions are non-refundable once processed, as they
are allocated to ongoing open-source development activities. You may
change your Contribution preference at any time for future transactions.

9.6 Default. Your Contribution percentage defaults to 0% unless you
affirmatively select a different amount. Pre-selected Contribution
amounts will be clearly displayed and modifiable before any transaction.
```

---

## 11. Template Privacy Policy Language

### Section: API Keys and Credentials

```
SENSITIVE PERSONAL INFORMATION: API KEYS

What We Collect:
We collect and store API keys ("Credentials") that you voluntarily
provide for third-party AI service providers (e.g., Anthropic, OpenAI,
Together.ai). Under California law (CCPA/CPRA), Credentials are
classified as sensitive personal information.

How We Use Credentials:
We use your Credentials solely to make API calls to the applicable
third-party provider on your behalf, in response to tasks you initiate
through our Service. We do not use your Credentials for any other
purpose.

How We Protect Credentials:
- Encryption at rest: AES-256-GCM
- Encryption in transit: TLS 1.3
- Access control: Role-based, principle of least privilege
- Key isolation: Each user's Credentials are stored in an isolated
  vault partition
- Monitoring: Real-time anomaly detection on all Credential usage
- No plaintext access: No employee can view your Credentials in
  plaintext

What We Log:
When your Credentials are used, we log: timestamp, user ID, provider
name, model used, token count, and response status. We do NOT log your
Credentials, prompt content, or response content.

Third Parties:
Your Credentials are transmitted only to the applicable API provider
(e.g., Anthropic, OpenAI) for the purpose of executing your tasks.
We do not share your Credentials with any other third party.

Retention:
Your Credentials are stored for as long as your account is active and
you have not deleted them. Upon account deletion or Credential
deletion, we irrevocably purge your Credentials from all systems within
24 hours.

Your Rights:
Under CCPA/CPRA, you have the right to:
- Know what Credentials we store and how they are used
- Delete your stored Credentials at any time
- Limit the use of your sensitive personal information
- Opt out of the sale or sharing of your personal information
  (Note: We do not sell or share your Credentials)

Breach Notification:
In the event of a security incident affecting your Credentials, we
will notify you within 72 hours via email and in-app notification,
and will provide guidance on rotating your API keys with the affected
provider.
```

### Section: Voluntary Contributions

```
FINANCIAL INFORMATION: COMMUNITY DEVELOPMENT CONTRIBUTIONS

What We Collect:
If you elect to make a voluntary Community Development Contribution,
we collect the Contribution amount and your payment information
(processed by our payment processor; we do not store full credit card
numbers).

How We Use This Information:
Contribution amounts are recorded for accounting, tax reporting, and
transparency reporting purposes. We publish aggregate Contribution
data in quarterly transparency reports (no individual amounts are
disclosed).

Retention:
Financial records including Contribution amounts are retained for
7 years as required by tax law.
```

---

## 12. Recommended Tip Tier Structure

### 12.1 Tier Design

| Tier Name | Percentage | Monthly Cap | Target User |
|---|---|---|---|
| **None** | 0% | $0 | Users who prefer not to contribute |
| **Supporter** | 5% of API costs | $5/month | Casual users, budget-conscious |
| **Builder** | 10% of API costs | $15/month | Regular users, OSS advocates |
| **Champion** | 15% of API costs | $30/month | Power users, community leaders |
| **Custom** | User-defined | User-defined | Any |

### 12.2 Design Principles

1. **Default is $0 / None.** The user must affirmatively opt in. Never pre-select a non-zero tier.
2. **Percentage-based, not flat.** Ties the contribution to actual usage, making it proportional and fair. Light users pay less; heavy users contribute more.
3. **Monthly cap.** Prevents bill shock. Users know their maximum exposure. The cap can be adjusted.
4. **No minimum.** Custom tier allows any percentage, including 0.1%. This ensures the contribution is genuinely voluntary.
5. **Visible in every receipt.** Each task receipt shows: API cost, contribution amount, total.
6. **Monthly summary.** Email or dashboard showing total monthly contributions and what they funded.

### 12.3 Recognition (Non-Financial Incentives)

To encourage contributions without gating features:

| Tier | Recognition |
|---|---|
| Supporter | "OSS Supporter" badge on profile |
| Builder | Named in quarterly transparency report |
| Champion | Named + vote on which open-source model to prioritize next |
| Custom ($50+/mo) | "Founding Contributor" designation in perpetuity |

**Critical:** Badges and recognition are cosmetic only. No functional features are gated behind contribution tiers. This maintains the legal distinction between "voluntary contribution" and "fee."

### 12.4 Revenue Projection

Based on SolaceAGI's economic model (20% markup on ~$0.59/M tokens, ~$3/mo average managed LLM cost per user):

| Scenario | Avg. Contribution Rate | Per-User/Month | At 1,000 Users |
|---|---|---|---|
| Conservative | 5% opt-in, 5% avg | $0.15 | $150/mo |
| Moderate | 15% opt-in, 8% avg | $0.36 | $360/mo |
| Optimistic | 30% opt-in, 10% avg | $0.90 | $900/mo |

This revenue is modest initially but scales with usage. At 10,000 users with moderate opt-in, it generates $3,600/month for open-source AI training -- enough for meaningful compute allocations.

---

## 13. Sources

### FTC and Consumer Protection
- [FTC Safeguards Rule](https://www.ftc.gov/business-guidance/resources/ftc-safeguards-rule-what-your-business-needs-know)
- [FTC Guidelines on Using Consumer Data for New AI Projects](https://quicktakes.loeb.com/post/102j083/ftc-guidelines-on-using-consumer-data-for-new-ai-projects-retroactive-privacy-po)
- [FTC Rule on Unfair or Deceptive Fees (effective May 12, 2025)](https://www.ftc.gov/news-events/news/press-releases/2025/05/ftc-rule-unfair-or-deceptive-fees-take-effect-may-12-2025)
- [FTC Unfair or Deceptive Fees FAQs](https://www.ftc.gov/business-guidance/resources/rule-unfair-or-deceptive-fees-frequently-asked-questions)
- [Fenwick - FTC Rule on Unfair or Deceptive Fees: FAQs and Guidance](https://www.fenwick.com/insights/publications/the-ftc-rule-on-unfair-or-deceptive-fees-faqs-and-guidance)

### Privacy Law (CCPA/CPRA)
- [California Consumer Privacy Act (CCPA)](https://oag.ca.gov/privacy/ccpa)
- [Jackson Lewis - CCPA FAQs for Covered Businesses](https://www.jacksonlewis.com/insights/navigating-california-consumer-privacy-act-30-essential-faqs-covered-businesses-including-clarifying-regulations-effective-1126)
- [Collibra - What is Personal Information Under the CCPA](https://www.collibra.com/us/en/blog/what-is-personal-information-under-the-ccpa)
- [IAPP - Who Holds the Keys? Third-Party AI API Access Governance](https://iapp.org/news/a/who-holds-the-keys-navigating-legal-and-privacy-governance-in-third-party-ai-api-access)

### API Provider Terms of Service
- [Anthropic - Expanded Legal Protections](https://www.anthropic.com/news/expanded-legal-protections-api-improvements)
- [SitePoint - The End of the Wrapper Era? Anthropic's New API Terms](https://www.sitepoint.com/end-wrapper-era-anthropic-api-terms-saas/)
- [VentureBeat - Anthropic Cracks Down on Unauthorized Claude Usage](https://venturebeat.com/technology/anthropic-cracks-down-on-unauthorized-claude-usage-by-third-party-harnesses)
- [The Register - Anthropic Clarifies Ban on Third-Party Tool Access](https://www.theregister.com/2026/02/20/anthropic_clarifies_ban_third_party_claude_access/)
- [OpenAI Services Agreement](https://openai.com/policies/services-agreement/)
- [OpenAI Business Terms (May 2025)](https://openai.com/policies/may-2025-business-terms/)
- [OpenAI BYOK Policy Discussion](https://community.openai.com/t/bring-your-own-key-policy/446168)
- [OpenAI Best Practices for API Key Safety](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)
- [Together.ai Terms of Service](https://www.together.ai/terms-of-service)

### Tip/Donation Models and Tax Treatment
- [GitHub Sponsors Tax Information](https://docs.github.com/en/sponsors/receiving-sponsorships-through-github-sponsors/tax-information-for-github-sponsors)
- [Buy Me a Coffee Tax Process](https://help.buymeacoffee.com/en/articles/8039657-understanding-the-tax-process-on-buy-me-a-coffee)
- [Open Collective Platform Tips](https://documentation.opencollective.com/giving-to-collectives/platform-tips)
- [Open Collective Terms of Service](https://opencollective.com/tos)
- [Open Source Collective Tax Info](https://docs.oscollective.org/how-it-works/tax-info)

### Open Source Funding Models
- [Apache Software Foundation](https://www.apache.org/foundation/individual-supporters)
- [Linux Foundation Crowdfunding](https://docs.linuxfoundation.org/lfx/crowdfunding/donate-sponsor)
- [Mozilla Foundation](https://en.wikipedia.org/wiki/Mozilla_Foundation)
- [IRS Denies Open-Source Software Organization Tax-Exempt Status (2025)](https://990reasons.com/irs-denies-open-source-software-organizations-request-for-tax-exempt-status/)

### API Key Security
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [OWASP Key Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Key_Management_Cheat_Sheet.html)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [Anthropic API Key Best Practices](https://support.claude.com/en/articles/9767949-api-key-best-practices-keeping-your-keys-safe-and-secure)
- [LegitSecurity - API Key Security Best Practices](https://www.legitsecurity.com/aspm-knowledge-base/api-key-security-best-practices)

---

## Appendix A: Action Items

| Priority | Action | Owner | Deadline |
|---|---|---|---|
| P0 | Engage SaaS/privacy attorney for formal legal review | Founder | Before launch |
| P0 | Implement AES-256-GCM key vault | Engineering | Before launch |
| P0 | Draft and publish Terms of Service + Privacy Policy | Legal/Founder | Before launch |
| P1 | Contact OpenAI partnerships for BYOK written confirmation | Founder | Before launch |
| P1 | Implement consent flow (API key entry + contribution opt-in) | Engineering | Before launch |
| P1 | Set up separate accounting ledger for contributions | Finance | Before launch |
| P2 | Implement real-time key usage anomaly detection | Engineering | Within 90 days |
| P2 | Publish first quarterly transparency report | Founder | Q1 after launch |
| P2 | Evaluate 501(c)(3) arm for tax-deductible contributions | Legal | Within 6 months |
| P3 | Achieve SOC 2 Type II certification | Engineering | Within 12 months |
| P3 | State-by-state sales tax analysis for contributions | Tax advisor | Within 6 months |

---

*This document is a research memorandum and does not constitute legal advice. SolaceAGI should engage qualified legal counsel (SaaS attorney, privacy attorney, tax advisor) to review and refine these recommendations before implementation.*
