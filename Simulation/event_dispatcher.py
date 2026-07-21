#Route orchestration graph to appropriate next state

from store_event_generator import simulate_sale
from Database.models import CreateStoreEventInput
from Store_Logic.sale_event import process_sale_event


def process_event(event: CreateStoreEventInput):

    if event.event_type == "Sale_Made":
        return process_sale_event(event)

    elif event.event_type == 
    else:
        ValueError(f"Unknown event type of: {event.event_type}")