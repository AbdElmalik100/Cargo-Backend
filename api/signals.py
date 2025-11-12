from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import InShipment, OutShipment, Destination, Company


MODEL_LABELS = {
    "in_shipment": "الشحنة الواردة",
    "out_shipment": "الشحنة الصادرة",
    "destination": "الوجهة",
    "company": "الشركة",
}

ACTION_LABELS = {
    "created": "تم إنشاء",
    "updated": "تم تحديث",
    "deleted": "تم حذف",
}

def make_message(model_key: str, action_key: str) -> str:
    model_name = MODEL_LABELS.get(model_key, model_key)
    action_name = ACTION_LABELS.get(action_key, action_key)
    return f"{action_name} {model_name} بنجاح"


def broadcast_event(model: str, action: str, instance_id=None):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    payload = {
        "type": "shipments.event",
        "model": model,
        "action": action,
        "message": make_message(model, action),
    }
    if instance_id is not None:
        payload["id"] = instance_id

    async_to_sync(channel_layer.group_send)("shipments", payload)


# InShipments
@receiver(post_save, sender=InShipment)
def handle_in_shipment_save(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    broadcast_event("in_shipment", action, instance.id)


@receiver(post_delete, sender=InShipment)
def handle_in_shipment_delete(sender, instance, **kwargs):
    broadcast_event("in_shipment", "deleted", instance.id)


# OutShipments
@receiver(post_save, sender=OutShipment)
def handle_out_shipment_save(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    broadcast_event("out_shipment", action, instance.id)


@receiver(pre_delete, sender=OutShipment)
def cache_related_in_shipments(sender, instance, **kwargs):
    instance._in_shipment_ids = list(instance.in_shipments.values_list('id', flat=True))


@receiver(post_delete, sender=OutShipment)
def handle_out_shipment_delete(sender, instance, **kwargs):
    related_ids = getattr(instance, "_in_shipment_ids", [])
    if related_ids:
        InShipment.objects.filter(id__in=related_ids).update(export=False)
    broadcast_event("out_shipment", "deleted", instance.id)


# Destinations
@receiver(post_save, sender=Destination)
def handle_destination_save(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    broadcast_event("destination", action, instance.id)


@receiver(post_delete, sender=Destination)
def handle_destination_delete(sender, instance, **kwargs):
    broadcast_event("destination", "deleted", instance.id)


# Companies
@receiver(post_save, sender=Company)
def handle_company_save(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    broadcast_event("company", action, instance.id)


@receiver(post_delete, sender=Company)
def handle_company_delete(sender, instance, **kwargs):
    broadcast_event("company", "deleted", instance.id)
