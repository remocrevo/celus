from ..models import DimensionText, Dimension


def remap_dicts(dimension: Dimension, records: [dict], key):
    mapping = {dt.pk: dt.text for dt in DimensionText.objects.filter(dimension=dimension)}
    for record in records:
        record[key] = mapping.get(record.get(key))