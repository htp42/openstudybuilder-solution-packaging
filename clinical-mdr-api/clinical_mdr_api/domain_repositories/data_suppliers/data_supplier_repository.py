from neomodel import NodeSet
from neomodel.sync_.match import (
    Collect,
    Last,
    NodeNameResolver,
    Path,
    RawCypher,
    RelationNameResolver,
)

from clinical_mdr_api.domain_repositories.controlled_terminologies.ct_codelist_attributes_repository import (
    CTCodelistAttributesRepository,
)
from clinical_mdr_api.domain_repositories.library_item_repository import (
    LibraryItemRepositoryImplBase,
    _AggregateRootType,
)
from clinical_mdr_api.domain_repositories.models.controlled_terminology import (
    CTTermRoot,
)
from clinical_mdr_api.domain_repositories.models.data_suppliers import (
    DataSupplierRoot,
    DataSupplierValue,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
)
from clinical_mdr_api.domain_repositories.neomodel_ext_item_repository import (
    NeomodelExtBaseRepository,
)
from clinical_mdr_api.domains.data_suppliers.data_supplier import (
    DataSupplierAR,
    DataSupplierVO,
)
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.models.data_suppliers.data_supplier import DataSupplier
from common.config import settings


class DataSupplierRepository(  # type: ignore[misc]
    NeomodelExtBaseRepository, LibraryItemRepositoryImplBase[_AggregateRootType]
):

    root_class = DataSupplierRoot
    value_class = DataSupplierValue
    return_model = DataSupplier

    def get_neomodel_extension_query(self) -> NodeSet:
        return DataSupplierRoot.nodes.traverse(
            "has_latest_value",
            "has_library",
            Path(
                value="has_latest_value__has_data_supplier_type__has_selected_term",
                optional=True,
                include_rels_in_return=False,
            ),
            Path(
                value="has_latest_value__has_data_supplier_type__has_selected_term__has_name_root__has_latest_value",
                optional=True,
                include_rels_in_return=False,
            ),
            Path(
                value="has_latest_value__has_origin_source__has_selected_term",
                optional=True,
                include_rels_in_return=False,
            ),
            Path(
                value="has_latest_value__has_origin_source__has_selected_term__has_name_root__has_latest_value",
                optional=True,
                include_rels_in_return=False,
            ),
            Path(
                value="has_latest_value__has_origin_type__has_selected_term",
                optional=True,
                include_rels_in_return=False,
            ),
            Path(
                value="has_latest_value__has_origin_type__has_selected_term__has_name_root__has_latest_value",
                optional=True,
                include_rels_in_return=False,
            ),
        ).subquery(
            DataSupplierRoot.nodes.traverse(latest_version="has_version")
            .intermediate_transform(
                {"rel": {"source": RelationNameResolver("has_version")}},
                ordering=[
                    RawCypher("toInteger(split(rel.version, '.')[0])"),
                    RawCypher("toInteger(split(rel.version, '.')[1])"),
                    "rel.end_date",
                    "rel.start_date",
                ],
            )
            .annotate(latest_version=Last(Collect("rel"))),
            ["latest_version"],
            initial_context=[NodeNameResolver("self")],
        )

    def extend_distinct_headers_query(self, nodeset: NodeSet) -> NodeSet:
        return nodeset.subquery(
            self.root_class.nodes.fetch_relations("has_version")
            .intermediate_transform(
                {"rel": {"source": RelationNameResolver("has_version")}},
                ordering=[
                    RawCypher("toInteger(split(rel.version, '.')[0])"),
                    RawCypher("toInteger(split(rel.version, '.')[1])"),
                    "rel.end_date",
                    "rel.start_date",
                ],
            )
            .annotate(latest_version=Last(Collect("rel"))),
            ["latest_version"],
            initial_context=[NodeNameResolver("self")],
        )

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        root: DataSupplierRoot,
        library: Library,
        relationship: VersionRelationship,
        value: DataSupplierValue,
        **_kwargs,
    ) -> _AggregateRootType:
        supplier_type_uid = (
            value.has_data_supplier_type.single().has_selected_term.single().uid
        )
        origin_source_uid = None
        if origin_source := value.has_origin_source.get_or_none():
            origin_source_uid = origin_source.has_selected_term.single().uid
        origin_type_uid = None
        if origin_type := value.has_origin_type.get_or_none():
            origin_type_uid = origin_type.has_selected_term.single().uid

        return DataSupplierAR.from_repository_values(
            uid=root.uid,
            data_supplier_vo=DataSupplierVO(
                name=value.name,
                order=value.order,
                description=value.description,
                supplier_type_uid=supplier_type_uid,
                origin_source_uid=origin_source_uid,
                origin_type_uid=origin_type_uid,
                api_base_url=value.api_base_url,
                ui_base_url=value.ui_base_url,
            ),
            library=LibraryVO.from_input_values_2(
                library.name, lambda _: library.is_editable
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
        )

    def _has_data_changed(self, ar: DataSupplierAR, value: DataSupplierValue) -> bool:
        supplier_type_uid = None
        if supplier_type := value.has_data_supplier_type.get_or_none():
            supplier_type_uid = supplier_type.has_selected_term.single().uid
        origin_source_uid = None
        if origin_source := value.has_origin_source.get_or_none():
            origin_source_uid = origin_source.has_selected_term.single().uid
        origin_type_uid = None
        if origin_type := value.has_origin_type.get_or_none():
            origin_type_uid = origin_type.has_selected_term.single().uid
        return (
            ar.data_supplier_vo.name != value.name
            or ar.data_supplier_vo.order != value.order
            or ar.data_supplier_vo.description != value.description
            or ar.data_supplier_vo.supplier_type_uid != supplier_type_uid
            or ar.data_supplier_vo.origin_source_uid != origin_source_uid
            or ar.data_supplier_vo.origin_type_uid != origin_type_uid
            or ar.data_supplier_vo.api_base_url != value.api_base_url
            or ar.data_supplier_vo.ui_base_url != value.ui_base_url
        )

    def _get_or_create_value(
        self,
        root: DataSupplierRoot,
        ar: DataSupplierAR,
        force_new_value_node: bool = False,
    ) -> DataSupplierValue:
        if not force_new_value_node:
            for itm in root.has_version.all():
                if not self._has_data_changed(ar, itm):
                    return itm
            latest_draft = root.latest_draft.get_or_none()
            if latest_draft and not self._has_data_changed(ar, latest_draft):
                return latest_draft
            latest_final = root.latest_final.get_or_none()
            if latest_final and not self._has_data_changed(ar, latest_final):
                return latest_final
            latest_retired = root.latest_retired.get_or_none()
            if latest_retired and not self._has_data_changed(ar, latest_retired):
                return latest_retired

        new_value = DataSupplierValue(
            name=ar.data_supplier_vo.name,
            order=ar.data_supplier_vo.order,
            description=ar.data_supplier_vo.description,
            api_base_url=ar.data_supplier_vo.api_base_url,
            ui_base_url=ar.data_supplier_vo.ui_base_url,
        )

        self._db_save_node(new_value)

        if ar.data_supplier_vo.supplier_type_uid:
            origin_source = CTTermRoot.nodes.get_or_none(
                uid=ar.data_supplier_vo.supplier_type_uid
            )
            if origin_source is None:
                raise ValueError(
                    f"CTTerm with UID '{ar.data_supplier_vo.supplier_type_uid}' not found"
                )
            selected_term_node = (
                CTCodelistAttributesRepository().get_or_create_selected_term(
                    origin_source,
                    codelist_submission_value=settings.data_supplier_type_cl_submval,
                )
            )
            new_value.has_data_supplier_type.connect(selected_term_node)

        if ar.data_supplier_vo.origin_source_uid:
            origin_source = CTTermRoot.nodes.get_or_none(
                uid=ar.data_supplier_vo.origin_source_uid
            )
            if origin_source is None:
                raise ValueError(
                    f"CTTerm with UID '{ar.data_supplier_vo.origin_source_uid}' not found"
                )
            selected_term_node = (
                CTCodelistAttributesRepository().get_or_create_selected_term(
                    origin_source,
                    codelist_submission_value=settings.origin_source_cl_submval,
                )
            )
            new_value.has_origin_source.connect(selected_term_node)

        if ar.data_supplier_vo.origin_type_uid:
            origin_type = CTTermRoot.nodes.get_or_none(
                uid=ar.data_supplier_vo.origin_type_uid
            )
            if origin_type is None:
                raise ValueError(
                    f"CTTerm with UID '{ar.data_supplier_vo.origin_type_uid}' not found"
                )
            selected_term_node = (
                CTCodelistAttributesRepository().get_or_create_selected_term(
                    origin_type,
                    codelist_submission_value=settings.origin_type_cl_submval,
                )
            )
            new_value.has_origin_type.connect(selected_term_node)

        return new_value

    def _maintain_parameters(
        self,
        versioned_object: _AggregateRootType,
        root: DataSupplierRoot,
        value: DataSupplierValue,
    ) -> None:
        # This method from parent repo is not needed for this repo
        # So we use pass to skip implementation
        pass

    def generate_uid(self) -> str:
        return DataSupplierRoot.get_next_free_uid_and_increment_counter()
