"""Demo script showing how to use the BrightThread Order Support Agent API."""

import json

import requests
from loguru import logger

# Base URL for the API
BASE_URL = "http://localhost:8000"


def demo_health_check() -> None:
    """Check API health."""
    logger.info("=== Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    logger.info(f"Status: {response.status_code}")
    logger.info(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def demo_get_order(order_id: str = "order-001") -> None:
    """Retrieve order details."""
    logger.info(f"=== Get Order: {order_id} ===")
    response = requests.get(f"{BASE_URL}/orders/{order_id}")
    logger.info(f"Status: {response.status_code}")
    order = response.json()
    logger.info(f"Order Status: {order['status']}")
    logger.info(f"Line Items: {len(order['line_items'])}")
    logger.info(f"Total Amount: ${order['total_amount']}")
    print()
    return order


def demo_customer_request(order_id: str = "order-001") -> None:
    """Process a customer request for order changes."""
    logger.info(f"=== Customer Request (Chat): {order_id} ===")

    messages = [
        "Can you change 20 of the medium shirts to large?",
        "I need to update my shipping address to our SF office.",
        "Can I add 50 more hoodies before the deadline?",
    ]

    for message in messages:
        logger.info(f"Customer: {message}")

        payload = {
            "order_id": order_id,
            "message": message,
            "conversation_history": [],
        }

        response = requests.post(f"{BASE_URL}/orders/{order_id}/chat", json=payload)

        if response.status_code == 200:
            result = response.json()
            logger.info(f"Agent: {result['agent_message']}")
            logger.info(f"Options: {len(result['options'])}")

            for i, option in enumerate(result["options"], 1):
                logger.info(
                    f"  Option {i}: {option['approval_status'].value} "
                    f"(Cost: ${option['cost_adjustment']}, "
                    f"Delay: {option['estimated_delay_days']} days)"
                )
        else:
            logger.error(f"Error: {response.status_code} - {response.text}")

        print()


def demo_inventory_check(product_id: str = "prod-001") -> None:
    """Check inventory for a product."""
    logger.info(f"=== Inventory Check: {product_id} ===")

    # Get inventory details
    response = requests.get(
        f"{BASE_URL}/inventory/{product_id}",
        params={"color": "Navy Blue", "size": "M"},
    )

    if response.status_code == 200:
        inventory = response.json()
        logger.info(f"Product: {product_id}")
        logger.info(f"Color: {inventory['color']}")
        logger.info(f"Size: {inventory['size']}")
        logger.info(f"Available: {inventory['available_quantity']}")
        logger.info(f"In Production: {inventory['in_production_quantity']}")
        logger.info(f"Total: {inventory['total_quantity']}")
    else:
        logger.error(f"Error: {response.status_code}")

    # Check availability for specific quantity
    response = requests.get(
        f"{BASE_URL}/inventory/{product_id}/check",
        params={
            "color": "Navy Blue",
            "size": "M",
            "quantity": 50,
        },
    )

    if response.status_code == 200:
        check = response.json()
        available = "✓ Available" if check["available"] else "✗ Not Available"
        logger.info(
            f"Can fulfill order of 50: {available} ({check['requested_quantity']})"
        )
    else:
        logger.error(f"Error: {response.status_code}")

    print()


def demo_get_policies() -> None:
    """Retrieve all order change policies."""
    logger.info("=== Order Change Policies ===")

    response = requests.get(f"{BASE_URL}/policies/order-changes")

    if response.status_code == 200:
        policies = response.json()
        logger.info(f"Total Policies: {len(policies)}")

        # Group by stage
        by_stage = {}
        for policy in policies:
            stage = policy["stage"]
            if stage not in by_stage:
                by_stage[stage] = []
            by_stage[stage].append(policy)

        for stage, stage_policies in sorted(by_stage.items()):
            logger.info(f"\n{stage}:")
            for policy in stage_policies:
                status = "✓ Allowed" if policy["allowed"] else "✗ Not Allowed"
                logger.info(
                    f"  {policy['change_type']}: {status} "
                    f"(Cost: {policy['requires_cost_adjustment']}, "
                    f"Delay: {policy['estimated_delay_days']} days)"
                )
    else:
        logger.error(f"Error: {response.status_code}")

    print()


def demo_production_timeline(order_id: str = "order-001") -> None:
    """Get production timeline for an order."""
    logger.info(f"=== Production Timeline: {order_id} ===")

    response = requests.get(f"{BASE_URL}/orders/{order_id}/production-timeline")

    if response.status_code == 200:
        timeline = response.json()
        logger.info(f"Order: {order_id}")

        for stage, date_str in timeline["timeline"].items():
            logger.info(f"  {stage}: {date_str}")
    else:
        logger.error(f"Error: {response.status_code}")

    print()


def demo_operations_dashboard() -> None:
    """Get operations team dashboard."""
    logger.info("=== Operations Dashboard ===")

    response = requests.get(f"{BASE_URL}/operations/dashboard")

    if response.status_code == 200:
        dashboard = response.json()
        logger.info(f"Orders in Production: {dashboard['orders_in_production']}")
        logger.info(f"Pending Alerts: {dashboard['pending_alerts']}")
        logger.info(f"Inventory Issues: {dashboard['inventory_issues']}")
        logger.info(f"Manual Review Needed: {dashboard['manual_review_needed']}")

        if dashboard["recent_alerts"]:
            logger.info("Recent Alerts:")
            for alert in dashboard["recent_alerts"]:
                logger.info(
                    f"  [{alert['severity'].upper()}] {alert['type']}: "
                    f"{alert['message']}"
                )
    else:
        logger.error(f"Error: {response.status_code}")

    print()


def main() -> None:
    """Run all demos."""
    logger.info("BrightThread Order Support Agent - API Demo")
    logger.info("==========================================\n")

    try:
        # Test basic endpoints
        demo_health_check()
        demo_get_order()
        demo_inventory_check()
        demo_get_policies()
        demo_production_timeline()
        demo_operations_dashboard()

        # Test agent interaction
        demo_customer_request()

        logger.info("✓ Demo completed successfully!")

    except requests.exceptions.ConnectionError:
        logger.error(
            "✗ Could not connect to API. Is the server running? (uv run python main.py)"
        )
    except Exception as e:
        logger.error(f"✗ Error during demo: {e}")


if __name__ == "__main__":
    main()
