from clinical_mdr_api.domain_repositories.models.generic import ClinicalMdrNode
from common.neomodel import BooleanProperty, IntegerProperty, StringProperty


class FeatureFlag(ClinicalMdrNode):
    sn = IntegerProperty(unique_index=True)
    name = StringProperty()
    enabled = BooleanProperty()
    description = StringProperty()
