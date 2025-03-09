import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.support import SupportManagementClient

def get_open_support_tickets():
    credential = DefaultAzureCredential()
    subscription_client = SubscriptionClient(credential)
    open_tickets = []

    for subscription in subscription_client.subscriptions.list():
        subscription_id = subscription.subscription_id
        support_client = SupportManagementClient(credential, subscription_id)
        
        for ticket in support_client.support_tickets.list():
            if ticket.status == 'Open':
                open_tickets.append({
                    'subscription_id': subscription_id,
                    'ticket_id': ticket.name,
                    'title': ticket.title,
                    'description': ticket.description,
                    'status': ticket.status,
                    'created_date': ticket.created_date
                })

    return open_tickets

if __name__ == "__main__":
    open_tickets = get_open_support_tickets()
    for ticket in open_tickets:
        print(f"Subscription ID: {ticket['subscription_id']}")
        print(f"Ticket ID: {ticket['ticket_id']}")
        print(f"Title: {ticket['title']}")
        print(f"Description: {ticket['description']}")
        print(f"Status: {ticket['status']}")
        print(f"Created Date: {ticket['created_date']}")
        print("-" * 40)