# BrightThread Order Change & Cancellation Policy

**Effective Date**: January 1, 2025
**Version**: 1.2
**Last Updated**: December 22, 2024

**Note (system design):** In production, this policy lives in a **versioned internal document repository** (e.g., Confluence). A scheduled ingestion job exports policy documents, chunks and embeds them, and uploads them to **OpenSearch** for vector retrieval. The agent uses OpenSearch retrieval to *explain* service-enforced decisions. The PoC may load this entire markdown document directly into agent context instead of using embeddings/vector search.

---

## Purpose

This document defines the official policies governing order modifications and cancellations for BrightThread custom apparel orders. These policies are:

- **Binding** for all customer orders placed through the BrightThread portal
- **Executable** by the AI Order Support Agent and human CX representatives
- **Transparent** to customers viewing their order details

---

## Order Lifecycle

Orders progress through the following states. The primary path is sequential, but orders may transition to CANCELLED from early states.

```
                              ┌──────────┐
                              │CANCELLED │ (Terminal)
                              └──────────┘
                                   ↑
        ┌──────────────────────────┼──────────────────────┐
        │                          │                      │
        │                          │                      │
CREATED → APPROVED → IN_PRODUCTION → READY_TO_SHIP → SHIPPED → DELIVERED
                                                                    ↓
                                                                RETURNED (Terminal)
```

### Valid State Transitions

| From State | To State | Trigger |
|:-----------|:---------|:--------|
| CREATED | APPROVED | Customer confirms order |
| CREATED | CANCELLED | Customer cancels (100% refund) |
| APPROVED | IN_PRODUCTION | Production starts |
| APPROVED | CANCELLED | Customer cancels ($25 fee) |
| IN_PRODUCTION | READY_TO_SHIP | Production complete |
| IN_PRODUCTION | CANCELLED | Customer cancels (50% refund) |
| READY_TO_SHIP | SHIPPED | Carrier pickup |
| SHIPPED | DELIVERED | Delivery confirmed |
| DELIVERED | RETURNED | Return processed |

### Terminal States

- **DELIVERED**: Order successfully completed
- **RETURNED**: Order returned and refunded
- **CANCELLED**: Order terminated before completion

---

## State Descriptions

| State | Description | Typical Duration |
|:------|:------------|:-----------------|
| **CREATED** | Order placed, pending customer confirmation | Minutes to hours |
| **APPROVED** | Customer confirmed, awaiting production scheduling | Hours to 1-2 days |
| **IN_PRODUCTION** | Garments are being printed/embroidered | 2-5 days |
| **READY_TO_SHIP** | Production complete, awaiting carrier pickup | 1-2 days |
| **SHIPPED** | Order in transit to customer | 2-7 days |
| **DELIVERED** | Delivery confirmed | Terminal state |
| **RETURNED** | Return processed, refund issued | Terminal state |
| **CANCELLED** | Order cancelled before completion | Terminal state |

---

## Policy Summary Matrix

| Order Status | Quantity | Size | Color | Artwork | Address | Cancel |
|:-------------|:--------:|:----:|:-----:|:-------:|:-------:|:------:|
| **CREATED** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **APPROVED** | ✅ | ✅ | ✅ | ⚠️ | ✅ | ⚠️ |
| **IN_PRODUCTION** | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ⚠️ |
| **READY_TO_SHIP** | ❌ | ❌ | ❌ | ❌ | ⚠️ | ❌ |
| **SHIPPED** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **DELIVERED** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **RETURNED** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **CANCELLED** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Legend**: ✅ Allowed | ⚠️ Conditional (see details) | ❌ Not Allowed

---

## Detailed Policies by Order State

### CREATED State

Orders in CREATED status have not yet been confirmed by the customer. Full flexibility is available.

| Change Type | Allowed | Cost Impact | Delivery Impact | Notes |
|:------------|:-------:|:------------|:----------------|:------|
| Quantity increase | ✅ Yes | None | None | Subject to inventory availability |
| Quantity decrease | ✅ Yes | None | None | — |
| Size change | ✅ Yes | None | None | Subject to inventory availability |
| Color change | ✅ Yes | None | None | Subject to inventory availability |
| Artwork change | ✅ Yes | None | None | — |
| Address change | ✅ Yes | None | None | — |
| Order cancellation | ✅ Yes | **100% refund** | N/A | Full refund, no penalty → CANCELLED |

**Agent Behavior**: Execute all changes immediately upon customer confirmation. No escalation required.

---

### APPROVED State

Orders in APPROVED status are confirmed and scheduled for production but have not yet started.

| Change Type | Allowed | Cost Impact | Delivery Impact | Notes |
|:------------|:-------:|:------------|:----------------|:------|
| Quantity increase | ✅ Yes | None | None | Subject to inventory availability |
| Quantity decrease | ✅ Yes | None | None | — |
| Size change | ✅ Yes | None | None | Subject to inventory availability |
| Color change | ✅ Yes | None | None | Subject to inventory availability |
| Artwork change | ⚠️ Conditional | **+15%** of affected line items | **+2 days** | Requires production reschedule |
| Address change | ✅ Yes | None | None | — |
| Order cancellation | ⚠️ Conditional | **$25 processing fee** | N/A | Refund = Order Total - $25 → CANCELLED |

**Agent Behavior**:
- Execute quantity, size, color, and address changes immediately
- For artwork changes: Inform customer of +15% cost and +2 day delay, require explicit confirmation
- For cancellation: Inform customer of $25 processing fee, require confirmation, transition to CANCELLED

---

### IN_PRODUCTION State

Orders in IN_PRODUCTION status are actively being printed or embroidered. Product modifications are possible but incur significant cost and delay penalties.

| Change Type | Allowed | Cost Impact | Delivery Impact | Notes |
|:------------|:-------:|:------------|:----------------|:------|
| Quantity increase | ⚠️ Conditional | **+25%** of new items | **+5 days** | Subject to inventory; new batch required |
| Quantity decrease | ⚠️ Conditional | **No refund** for removed items | None | Materials already committed |
| Size change | ⚠️ Conditional | **+30%** of affected items | **+5 days** | Requires new garments; subject to inventory |
| Color change | ⚠️ Conditional | **+30%** of affected items | **+5 days** | Requires new garments; subject to inventory |
| Artwork change | ⚠️ Conditional | **+50%** of affected items | **+7 days** | Requires reprint; original items discarded |
| Address change | ✅ Yes | **$15 redirect fee** | **+1 day** | Carrier coordination required |
| Order cancellation | ⚠️ Conditional | **50% of order total** | N/A | Partial refund only → CANCELLED |

**Agent Behavior**:
- For quantity increase: Inform customer of +25% cost and +5 day delay, check inventory, require confirmation
- For quantity decrease: Inform customer there is no refund for removed items (materials already committed), require confirmation
- For size/color changes: Inform customer of +30% cost and +5 day delay, check inventory, require confirmation
- For artwork changes: Inform customer of +50% cost and +7 day delay (highest penalty), require confirmation
- For address changes: Inform customer of $15 fee and +1 day delay, require confirmation
- For cancellation: Inform customer they will receive only 50% refund, require explicit confirmation, transition to CANCELLED
- Escalate to human support if customer is dissatisfied or if change is complex

---

### READY_TO_SHIP State

Orders in READY_TO_SHIP status are complete and packaged, awaiting carrier pickup.

| Change Type | Allowed | Cost Impact | Delivery Impact | Notes |
|:------------|:-------:|:------------|:----------------|:------|
| Quantity increase | ❌ No | N/A | N/A | Order already packaged |
| Quantity decrease | ❌ No | N/A | N/A | Order already packaged |
| Size change | ❌ No | N/A | N/A | Order already packaged |
| Color change | ❌ No | N/A | N/A | Order already packaged |
| Artwork change | ❌ No | N/A | N/A | Order already complete |
| Address change | ⚠️ Conditional | **$25 carrier redirect fee** | **+1-2 days** | Subject to carrier availability |
| Order cancellation | ❌ No | N/A | N/A | **Escalate to support** |

**Agent Behavior**:
- Deny all product modification requests
- For address changes: Inform customer of $25 carrier redirect fee and +1-2 day delay, require confirmation
- For cancellation requests: Escalate immediately to human support with full context (order already complete, no automatic cancellation)

---

### SHIPPED State

Orders in SHIPPED status are in transit with the carrier. No modifications are possible.

| Change Type | Allowed | Cost Impact | Delivery Impact | Notes |
|:------------|:-------:|:------------|:----------------|:------|
| All changes | ❌ No | N/A | N/A | Order in transit |
| Order cancellation | ❌ No | N/A | N/A | Cannot intercept shipment |

**Agent Behavior**:
- Deny all modification requests
- Provide tracking information
- Inform customer that return policy applies after delivery
- Escalate to human support if customer has urgent concerns

---

### DELIVERED State

Orders in DELIVERED status have been confirmed delivered. The order lifecycle is complete.

| Change Type | Allowed | Cost Impact | Delivery Impact | Notes |
|:------------|:-------:|:------------|:----------------|:------|
| All changes | ❌ No | N/A | N/A | Order complete |
| Return request | ✅ Yes | See return policy | N/A | 30-day return window → RETURNED |

**Agent Behavior**:
- Provide order summary and receipt
- Inform customer of 30-day return policy if they wish to return items
- No modifications possible

---

### RETURNED State

Orders in RETURNED status have been returned and refunded. No further actions available.

**Agent Behavior**:
- Confirm refund has been processed
- Provide refund confirmation details
- Order archived for records
- No further transitions possible (terminal state)

---

### CANCELLED State

Orders in CANCELLED status have been terminated before completion. Refund has been issued per policy.

**Agent Behavior**:
- Confirm cancellation has been processed
- Provide refund confirmation details (amount varies by previous state)
- Confirm inventory has been released
- Order archived for records
- No further transitions possible (terminal state)

---

## Cancellation & Refund Policy

| Order Status | Can Cancel? | Refund Amount | Processing Time | Resulting State |
|:-------------|:-----------:|:--------------|:----------------|:----------------|
| **CREATED** | ✅ Yes | 100% of order total | 3-5 business days | CANCELLED |
| **APPROVED** | ⚠️ Yes (fee) | Order total minus $25 processing fee | 3-5 business days | CANCELLED |
| **IN_PRODUCTION** | ⚠️ Yes (partial) | 50% of order total | 5-7 business days | CANCELLED |
| **READY_TO_SHIP** | ❌ No | Not available | Escalate to support | — |
| **SHIPPED** | ❌ No | Not available | Use return policy | — |
| **DELIVERED** | ❌ No | Per return policy | Per return policy | RETURNED |
| **RETURNED** | ❌ N/A | Refund already issued | — | — |
| **CANCELLED** | ❌ N/A | Refund already issued | — | — |

### Return Policy (DELIVERED Orders)

- **Return window**: 30 days from delivery date
- **Condition**: Items must be unworn, unwashed, with original packaging
- **Custom items**: Custom-printed items are **not eligible** for return unless defective
- **Defective items**: Full refund or replacement at customer's choice
- **Return shipping**: Customer pays return shipping unless item is defective
- **Resulting state**: DELIVERED → RETURNED

---

## Cost Impact Calculations

All cost impacts are calculated as a **percentage of the affected line item(s)**, not the entire order.

### Examples

**Example 1: Artwork change on APPROVED order**
- Order total: $5,000
- Line item being modified: $1,000 (100 t-shirts)
- Cost impact: $1,000 × 15% = **$150 additional charge**

**Example 2: Cancellation of IN_PRODUCTION order**
- Order total: $5,000
- Refund amount: $5,000 × 50% = **$2,500 refund**
- Order transitions to: **CANCELLED**

**Example 3: Address change on IN_PRODUCTION order**
- Flat fee: **$15**
- No percentage calculation

**Example 4: Address change on READY_TO_SHIP order**
- Flat fee: **$25**
- No percentage calculation

**Example 5: Cancellation of APPROVED order**
- Order total: $5,000
- Refund amount: $5,000 - $25 = **$4,975 refund**
- Order transitions to: **CANCELLED**

**Example 6: Size change on IN_PRODUCTION order**
- Order total: $5,000
- Line item being modified: $800 (80 t-shirts changing from M to L)
- Cost impact: $800 × 30% = **$240 additional charge**
- Delivery impact: **+5 days**

**Example 7: Artwork change on IN_PRODUCTION order**
- Order total: $5,000
- Line item being modified: $1,500 (150 hoodies with new logo)
- Cost impact: $1,500 × 50% = **$750 additional charge**
- Delivery impact: **+7 days**

**Example 8: Quantity increase on IN_PRODUCTION order**
- Order total: $5,000
- Adding 50 new t-shirts at $10 each = $500
- Cost impact: $500 × 25% = **$125 additional charge** (on top of base cost)
- Total additional cost: $500 + $125 = **$625**
- Delivery impact: **+5 days**

**Example 9: Quantity decrease on IN_PRODUCTION order**
- Order total: $5,000
- Removing 30 t-shirts worth $300
- Cost impact: **No refund** (materials already committed)
- New order total remains: **$5,000**

---

## Delivery Impact Calculations

| Change Type | Order Status | Days Added to Delivery |
|:------------|:-------------|:-----------------------|
| Artwork change | APPROVED | +2 days |
| Quantity increase | IN_PRODUCTION | +5 days |
| Size change | IN_PRODUCTION | +5 days |
| Color change | IN_PRODUCTION | +5 days |
| Artwork change | IN_PRODUCTION | +7 days |
| Address change | IN_PRODUCTION | +1 day |
| Address change | READY_TO_SHIP | +1-2 days |

**Note**: Delivery delays are added to the current estimated delivery date, not the original requested date.

---

## Inventory Constraints

All changes that modify product quantities, sizes, or colors are **subject to inventory availability**.

### Rules

1. **Inventory check required**: Agent must verify inventory before confirming any product change
2. **Insufficient inventory**: If requested quantity exceeds available inventory, agent must:
   - Inform customer of available quantity
   - Offer partial fulfillment if acceptable
   - Suggest alternative sizes/colors if available
3. **Reservation**: Upon order creation, inventory is reserved (decremented from available, added to reserved)
4. **Release on cancellation**: When order transitions to CANCELLED, reserved inventory is released back to available

---

## Lead Time Requirements

Orders must maintain minimum lead times based on their current state.

| Order Status | Minimum Lead Time to Delivery |
|:-------------|:------------------------------|
| CREATED | 14 days |
| APPROVED | 12 days |
| IN_PRODUCTION | 7 days |

**Rule**: If a change would cause the delivery date to fall below the minimum lead time, the agent must:
1. Inform customer of the required delivery date extension
2. Require explicit confirmation before proceeding

---

## Escalation Triggers

The following scenarios require **immediate escalation to human CX support**:

| Trigger | Reason |
|:--------|:-------|
| Cancellation request for READY_TO_SHIP order | Order already complete, requires manual intervention |
| Cancellation request for SHIPPED order | Order in transit, requires carrier coordination |
| Any modification request for SHIPPED order | Requires carrier coordination |
| Refund amount exceeds $500 | Financial approval required |
| Split shipment request | Complex logistics |
| Rush order modification | Production scheduling impact |
| Customer expresses frustration | Customer satisfaction priority |
| Request involves policy exception | Human judgment required |
| Technical error occurs | Investigation required |
| Customer explicitly requests human support | Customer preference |

---

## Agent Decision Logic

### For Any Modification Request

```
1. Retrieve order details and current status
2. Check if order is in terminal state (DELIVERED, RETURNED, CANCELLED)
   - If yes: Inform customer no modifications possible, provide status details
3. Identify change type (quantity, size, color, artwork, address, cancel)
4. Look up policy for (order_status, change_type)
5. IF policy.allowed == false:
     - Inform customer change is not possible
     - Explain reason based on order status
     - Offer alternatives if available
     - Escalate if customer dissatisfied
6. IF policy.allowed == conditional:
     - Check any constraints (inventory, lead time)
     - Calculate cost impact
     - Calculate delivery impact
     - Present all impacts to customer
     - Require explicit confirmation ("yes" or "confirm")
     - Execute only after confirmation
     - For cancellations: Transition order to CANCELLED state
7. IF policy.allowed == true:
     - Check any constraints (inventory, lead time)
     - Execute change
     - Confirm completion to customer
     - For cancellations: Transition order to CANCELLED state
```

### Confirmation Requirements

For any change with cost or delivery impact, the agent **must**:
1. Clearly state the cost impact (exact dollar amount)
2. Clearly state the delivery impact (exact number of days)
3. For cancellations: Clearly state the refund amount and that order will be cancelled
4. Ask for explicit confirmation
5. Only execute after receiving "yes", "confirm", or equivalent affirmation
6. If customer says "no" or declines, cancel the pending change

---

## Policy Enforcement

These policies are **programmatically enforced** in the BrightThread system:

- **Hard blocks**: System will reject disallowed changes (e.g., size change on IN_PRODUCTION order)
- **Soft blocks**: System will warn but allow with confirmation (e.g., artwork change on APPROVED order)
- **State transitions**: Cancellations automatically transition order to CANCELLED state
- **Inventory management**: Cancellations automatically release reserved inventory
- **Audit trail**: All modification attempts and state transitions are logged
- **Consistency**: AI agent and human CX follow identical policies

---

## Customer Communication Templates

### Approved Change
> "I've successfully updated your order. [Change description]. Your estimated delivery date remains [date]."

### Conditional Change (Pending Confirmation)
> "I can make this change, but it will [cost impact] and [delivery impact]. Would you like me to proceed?"

### Cancellation Confirmation (Pending)
> "I can cancel your order. You will receive a refund of [amount] within [timeframe]. Would you like me to proceed with the cancellation?"

### Cancellation Complete
> "Your order has been cancelled. A refund of [amount] will be processed within [timeframe]. Your confirmation number is [number]."

### Denied Change
> "I'm sorry, but [change type] changes are not available for orders that are [status] because [reason]. [Alternative if available]."

### Denied Cancellation
> "I'm sorry, but your order cannot be cancelled because it is [status]. [Alternative: return policy information or escalation offer]."

### Terminal State
> "This order has been [cancelled/returned/delivered] and no further modifications are possible. [Provide relevant details]."

### Escalation
> "I understand this is important to you. Let me connect you with a member of our support team who can help with this request. They'll be in touch within [timeframe]."

---

## Document Control

| Version | Date | Author | Changes |
|:--------|:-----|:-------|:--------|
| 1.0 | 2024-12-22 | BrightThread | Initial policy document |
| 1.1 | 2024-12-22 | BrightThread | Added CANCELLED as first-class order status |
| 1.2 | 2024-12-22 | BrightThread | Made IN_PRODUCTION state more flexible with cost/delay penalties |

---

**For questions about these policies, contact**: support@brightthread.com
